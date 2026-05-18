from odoo import fields, models, _
from odoo.exceptions import UserError


class OwnershipContract(models.Model):
    """Inherit the model to add the sell state to the property."""
    _inherit = 'ownership.contract'

    building = fields.Many2one('building', 'Building',
                               required=True,
                               domain=[('state', '=', 'free')])
    building_unit = fields.Many2one('product.template', 'Building Unit',
                                    copy=False, required=False,
                                    domain=[('is_property', '=', True),
                                            ('state', '=', 'free')])

    def action_confirm(self):
        """Overwrite this method for add the property state to the sold"""
        res = super().action_confirm()
        self.building.write({'state': 'sold'})
        return res

    def action_cancel(self):
        """To reset the state of property into free"""
        res = super().action_cancel()
        self.building.write({'state':  'free'})
        return res


class loan_line_rs_own(models.Model):
    _inherit = 'loan.line.rs.own'

    def make_invoice(self):
        """rewrite this method for to create the invoice. Add the compliance in here"""
        for rec in self:
            if not rec.loan_id.partner_id.property_account_receivable_id:
                raise UserError(_('Please set receivable account for partner!'))
            if not rec.loan_id.account_income:
                raise UserError(
                    _('Please set income account for this contract!'))
            account_move_obj = self.env['account.move']
            journal_pool = self.env['account.journal']
            journal = journal_pool.search([('type', '=', 'sale')], limit=1)

            invoice = account_move_obj.create({'ref': rec.name,
                                               'journal_id': journal.id,
                                               'partner_id': rec.contract_partner_id.id,
                                               'move_type': 'out_invoice',
                                               'ownership_line_id': rec.id,
                                               'invoice_date_due': rec.date,
                                               'compliance': True,
                                               'ref': (rec.loan_id.name + ' - ' + rec.name),
                                               'invoice_line_ids': [(0, None, {
                                                'name': (rec.loan_id.name + ' - ' + rec.name),
                                                'quantity': 1,
                                               # 'analytic_account_id':rec.loan_id.account_analytic_id.id,
                                               'price_unit': rec.amount, })]
                                               })
            invoice.action_post()
            self.invoice_id = invoice.id
