from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError
from odoo.fields import Command
from odoo.tools import float_compare, float_round, float_is_zero


class CreateLawInvoice(models.TransientModel):
    _name = 'wizard.create.law.invoice'
    _description = 'Wizard Create Law Invoice'

    invoice_type = fields.Selection(selection=[('fixed', 'Fixed Cash'),
                                               ('timesheet', 'Based On Timesheet')
                                               ], default='fixed')
    amount = fields.Float("Amount")
    invoice_line_ids = fields.Many2many(comodel_name="account.analytic.line")
    description = fields.Char("Invoice Line Description")

    @api.model
    def default_get(self, fields):
        res = super(CreateLawInvoice, self).default_get(fields)
        model = self.env.context.get('active_model', False)
        ids = self.env.context.get('active_ids', [])
        if model and ids:
            res.update({'invoice_line_ids': [(6, 0, self.env[model].browse(ids).mapped('timesheet_ids').filtered(
                lambda x: not x.move_line_id).ids)]})
        return res

    def btn_create_invoice(self):
        move_obj = self.env['account.move']
        if not self.invoice_type:
            raise UserError("Please Select Invoice Policy")

        if not move_obj.check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                raise UserError("You have been not access to create or edit invoice")

        model = self.env.context.get('active_model', False)
        ids = self.env.context.get('active_ids', [])
        if not model or not ids:
            raise UserError("Something missing in context model or ids")

        invoice_vals_list = []

        invoice_vals = {
            'move_type': 'out_invoice',
            'currency_id': self.env.company.currency_id.id,
            'invoice_user_id': self.env.user.id,
            'company_id': self.env.company.id,
            'invoice_line_ids': [],
        }

        for rec in self.env[model].browse(ids):
            invoice_vals.update({
                'law_task_id': rec.id,
                'partner_id': rec.partner_id.id,
                'invoice_origin': rec.name,
                'invoice_line_ids': [],
            })

            price_unit = self.amount
            if self.invoice_type == 'fixed':
                invoice_vals['invoice_line_ids'] = [Command.create({
                    'display_type': 'product',
                    'name': rec.description and rec.description or rec.name,
                    'quantity': 1,
                    'price_unit': price_unit,
                })]

            elif self.invoice_type == 'timesheet':
                for line in self.invoice_line_ids:
                    invoice_vals['invoice_line_ids'].append(Command.create({
                        'display_type': 'product',
                        'name': line.name,
                        'quantity': line.unit_amount,
                        'price_unit': price_unit,
                        'analytic_line_ids': [Command.link(line.id)]
                    }))

            invoice_vals_list.append(invoice_vals)

        if invoice_vals_list:
            return move_obj.sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)
