from odoo import models, fields, _, api
from odoo.exceptions import AccessError, UserError


class WizardInvoiceDeduction(models.TransientModel):
    _name = 'wizard.invoice.deduction'
    _description = 'Invoice Deduction'

    name = fields.Char("Name")
    partner_id = fields.Many2one('res.partner')
    expense_ids = fields.Many2many("hr.expense")
    fund_ids = fields.Many2many("trust.account")

    @api.model
    def default_get(self, fields):
        res = super(WizardInvoiceDeduction, self).default_get(fields)
        partner_id = res.get('partner_id')
        if partner_id:
            expense_ids = self.env['hr.expense'].search(
                [('partner_id', '=', partner_id), ('move_line_ids', '=', False)]).ids
            trust_fund_ids = self.env['trust.account'].search(
                [('partner_id', '=', partner_id), ('move_line_ids', '=', False)]).ids
            res['expense_ids'] = [(6, 0, expense_ids)]
            res['fund_ids'] = [(6, 0, trust_fund_ids)]
        return res

    def btn_submit_add_lines(self):
        if self.expense_ids or self.fund_ids:
            model = self._context.get('active_model', False)
            id = self._context.get('active_id', [])
            if not model or not id:
                raise UserError("Something missing in context model or id")

            move_id = self.env[model].browse(id)

            invoice_vals = [
                {
                    'name': 'EXPENSE - {}'.format(rec.name),
                    'quantity': 1,
                    'price_unit': -rec.total_amount,
                    'partner_id': self.partner_id.id,
                    'display_type': 'product',
                    'move_id': move_id.id,
                    'expense_id': rec.id,
                } for rec in self.expense_ids
            ]

            if invoice_vals:
                self.env['account.move.line'].create(invoice_vals)

            invoice_vals = [
                {
                    'name': 'Trust Fund - {}'.format(rec.name),
                    'quantity': 1,
                    'price_unit': -rec.amount,
                    'partner_id': self.partner_id.id,
                    'display_type': 'product',
                    'move_id': move_id.id,
                    'trust_account_id': rec.id,
                } for rec in self.fund_ids
            ]

            if invoice_vals:
                self.env['account.move.line'].create(invoice_vals)
