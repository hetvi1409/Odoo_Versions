from odoo import api, models, fields, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    load_batch = fields.Boolean(string='Load batch on the bank App')
    invoice_id = fields.Many2one('account.move',
                                 domain='[("move_type", "=", "out_invoice"), ("payment_state", "=", "not_paid")]')
    release = fields.Boolean(string='Release the payment from Bank App')
    to_reconcile_ids = fields.Many2many('account.move.line', string="")

    @api.onchange('invoice_id', 'partner_id')
    def _onchange_invoice_id(self):
        if self.invoice_id:
            self.partner_id = self.invoice_id.partner_id
            self.amount = self.invoice_id.amount_total
            self.ref = self.invoice_id.name

    def action_approve(self):
        """Approve and review the payment"""
        for rec in self:
            rec.state = 'approve'
            rec.message_post(body=_('The payment %s first approval done by %s '
                                    'is successfully completed.') % (rec.name,
                                                                     rec.env.user.name))
            rec.message_post(body=_('Check the Load batch on bank app'))

    def action_refuse(self):
        """Approve and review the payment"""
        for rec in self:
            rec.state = 'draft'
            rec.message_post(body=_('The payment %s first review done by %s '
                                    'is failed') % (rec.name,
                                                    rec.env.user.name))

    def action_approve_second(self):
        """second approval"""
        for rec in self:
            if rec.load_batch:
                rec.state = 'approve_second'
                rec.message_post(
                    body=_('The payment %s second approval done by %s '
                           'is successfully completed.') % (rec.name,
                                                            rec.env.user.name))
                rec.message_post(body=_('Release the payment from Bank App'))
            else:
                raise UserError(_('Check the load batch'))

    def action_refuse_second(self):
        """second approval"""
        for rec in self:
            if rec.load_batch:
                rec.state = 'approve'
                rec.message_post(body=_(
                    'The payment %s second approval done by %s is failed') % (
                                      rec.name, rec.env.user.name))

    def action_approve_third(self):
        """second approval"""
        for rec in self:
            if rec.release:
                rec.state = 'approved'
                rec.message_post(
                    body=_('The payment %s third approval done by %s '
                           'is successfully completed.') % (rec.name,
                                                            rec.env.user.name))
            else:
                raise UserError(_('Check the Release of bank account'))

    def action_refuse_third(self):
        """second approval"""
        for rec in self:
            if rec.release:
                rec.state = 'approve_second'
                rec.message_post(body=_(
                    'The payment %s third approval done by %s is failed') % (
                                      rec.name, rec.env.user.name))
            else:
                raise UserError(_('Check the Release of bank account'))

    # def _compute_stat_buttons_from_reconciliation(self):
    #     """Change the invoice_reconciliations_ids based on the invoice field"""
    #     res = super(AccountPayment, self)._compute_stat_buttons_from_reconciliation()
    #     # for rec in self:
    #     #     if rec.invoice_id:
    #     #         rec.reconciled_invoice_ids += rec.invoice_id
    #     return res

    def action_post(self):
        """Add automatically reconciliation when we're creating the payment
        for invoice"""

        if self.payment_type == 'inbound':
            if self.state != 'approved':
                raise UserError(_("Can't post this payment because of the "
                                  "payment is not in approved state. Need to "
                                  "approve by the manager."))
        res = super(AccountPayment, self).action_post()

        if self.payment_type == 'inbound':
            domain = [
                ('parent_state', '=', 'posted'),
                ('account_type', 'in', ('asset_receivable', 'liability_payable')),
                ('reconciled', '=', False),
            ]
            if self.invoice_id:
                payment_lines = self.line_ids.filtered_domain(domain)
                to_reconcile = self.invoice_id.line_ids.filtered_domain([('name', '=', self.invoice_id.name)])
                lines = to_reconcile

                for account in payment_lines.account_id:
                    (payment_lines + lines) \
                        .filtered_domain(
                        [('account_id', '=', account.id), ('reconciled', '=', False)]) \
                        .reconcile()
            elif self.to_reconcile_ids:
                payment_lines = self.line_ids.filtered_domain(domain)
                to_reconcile = self.to_reconcile_ids
                lines = to_reconcile

                for account in payment_lines.account_id:
                    (payment_lines + lines) \
                        .filtered_domain(
                        [('account_id', '=', account.id),
                         ('reconciled', '=', False)]) \
                        .reconcile()
        return res
