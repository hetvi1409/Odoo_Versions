from odoo import api, models, fields, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    compliance = fields.Boolean(string='Complaince',
                                help="Compliance is done or not. If ready to move the next step",
                                copy=False)

    state = fields.Selection(selection_add=[('approve', 'First Approve'),
                                            (
                                                'approve_second',
                                                'Second Approve'),
                                            ("approved", "Approved"),
                                            ('posted',)],
                             ondelete={'approved': 'cascade',
                                       'approve': 'cascade',
                                       'approve_second': 'cascade'})
    is_refused = fields.Boolean(copy=False)

    # invoice_interest_ids = fields.Many2many('account.move', 'invoice_interest')

    # Billing
    pre_bill_report = fields.Boolean(string="Pre billing report",
                                     help="Check the pre billing report", copy=False)
    any_amendments = fields.Boolean(string="Any amendments", copy=False)
    process_pre_billing = fields.Boolean(string="Process pre billing", copy=False)

    def action_checklist_compliance(self):
        """To do the checklist compliance"""
        if not self.line_ids.filtered(lambda line: line.display_type not in (
                'line_section', 'line_note')):
            raise UserError(_('You need to add a line before updating '
                              'the checklist.'))
        return {
            'name': _('Invoice Checklist'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_partner_id': self.partner_id.id,
                        'default_invoice_id': self.id},
            'res_model': "invoice.compliance.wizard",
        }

    def action_post(self):
        """Super the method to check the invoice compliance"""
        if self.move_type == 'entry':
            res = super(AccountMove, self).action_post()
            return res
        if self.move_type == 'out_invoice':
            if self.compliance != True:
                raise UserError(_('Need to check the compliance checklist'))
        if self.move_type == 'out_refund':
            if self.state != 'approved':
                raise UserError(
                    _('The Invoice reversal is not in approved state'))
        if self.move_type == 'in_invoice':
            if self.state != 'approved':
                raise UserError(
                    _('The Bill is not in approved state'))
        res = super(AccountMove, self).action_post()
        return res

    @api.depends('date', 'auto_post')
    def _compute_hide_post_button(self):
        """Overwrite this methode to show the post button in the approve state"""
        for record in self:
            record.hide_post_button = record.state not in ['draft', 'approved'] \
                                      or record.auto_post != 'no' and record.date > fields.Date.today()

    def action_approve_credict_clerk(self):
        """To approve the reversal from the Senior credict clerk"""
        for rec in self:
            if rec.move_type == 'out_refund':
                if not rec.partner_id:
                    raise UserError(_("The field 'Customer' is required,"
                                      " please complete it to validate "
                                      "the Customer Invoice."))
                rec.message_post(
                    body=_('The reversal %s: first approval from the senior '
                           'credict clerk done by %s is Approved.') %
                         (rec.name, rec.env.user.name))
                rec.state = 'approve'

    def action_refuse_credict_clerk(self):
        """To refuse the reversal from the Senior credict clerk.
        Only for credict Notes"""

        for rec in self:
            if rec.move_type == 'out_refund':
                rec.button_cancel()
                rec.is_refused = True
                rec.message_post(
                    body=_('The reversal %s: first approval from the senior '
                           'credict clerk done by %s is failed.') %
                         (rec.name, rec.env.user.name))

    def action_approve_finance_manager(self):
        """Second approval for Invoice reversal"""
        for rec in self:
            if rec.move_type == 'out_refund':
                rec.state = 'approved'
                rec.message_post(
                    body=_('The reversal %s: second approval from the finance '
                           'manager done by %s is Approved.') % (
                             rec.name, rec.env.user.name))

    def action_refuse_finance_manager(self):
        """Second refusal for Invoice reversal"""
        for rec in self:
            if rec.move_type == 'out_refund':
                rec.state = 'approve'
                rec.message_post(
                    body=_('The reversal %s: second approval from the finance '
                           'manager done by %s is refused.') % (
                             rec.name, rec.env.user.name))

    def button_draft(self):
        """Super this method for invoice reversal:
        To show the waring message foe the cancelled invoice reversal"""
        res = super(AccountMove, self).button_draft()
        for rec in self:
            rec.compliance = ""
            rec.any_amendments = ""
            rec.pre_bill_report = ""
            rec.process_pre_billing = ""
            if rec.move_type == 'out_refund':
                if rec.is_refused:
                    raise UserError(_("This is a refused invoice reversal. "
                                      "So we cant set this to draft"))
        return res

    def action_amendments_bill(self):
        """This method is used in bills, to check the amendments bill details"""
        if not self.line_ids:
            raise UserError(_('You need to add a line before posting.'))
        if self.pre_bill_report:
            return {
                'name': _('Amendments Bill'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_partner_id': self.partner_id.id,
                            'default_move_id': self.id},
                'res_model': "amendments.bill",
            }
        else:
            raise UserError(_("The field 'Pre billing report' is"
                              " required,  please complete it to"
                              " validate the Vendor Bill."))

    def action_approve_bill(self):
        """Methode for approve the bills"""
        for rec in self:
            if not rec.invoice_date:
                raise UserError(_("The Bill/Refund date is required to validate this document."))
            if not rec.line_ids:
                raise UserError(_('You need to add a line before posting.'))
            rec.state = 'approve'
            rec.message_post(body=_('The Bill %s: first approval from the '
                                    'finance manager done by %s is '
                                    'approved.') % (rec.name,
                                                  rec.env.user.name))

    def action_refuse_bill(self):
        """Methode for reject the bills"""
        for rec in self:
            rec.state = 'draft'
            rec.message_post(body=_('The Bill %s: second approval from the '
                                    'finance manager done by %s is '
                                    'failed.') % (rec.name,
                                                  rec.env.user.name))
            rec.process_pre_billing = ""

    def action_approve_bill_second(self):
        """Methode for approve the bills"""
        for rec in self:
            if not rec.process_pre_billing:
                raise UserError(_("The Process pre billing is required to "
                                  "validate this document."))
            rec.state = 'approved'
            rec.message_post(body=_('The Bill %s: second approval from the '
                                    'finance manager done by %s is '
                                    'approved.') % (rec.name,
                                                  rec.env.user.name))

    def action_refuse_bill_second(self):
        """Methode for reject the bills"""
        for rec in self:
            if not rec.process_pre_billing:
                raise UserError(_("The Process pre billing is required to "
                                  "validate this document."))
            else:
                rec.state = 'approve'
                rec.message_post(body=_('The Bill %s: second approval from the '
                                        'finance manager done by %s is '
                                        'failed.') % (rec.name,
                                                      rec.env.user.name))
                rec.process_pre_billing = ""

    # def _post(self, soft=True):
    #     for rec in self:
    #         if rec.move_type == 'out_refund':
    #             if rec.state != 'approved':
    #                 raise UserError(
    #                     _('The reversal invoice is not in approved state'))
    #     res = super()._post(soft=soft)
    #     return res
