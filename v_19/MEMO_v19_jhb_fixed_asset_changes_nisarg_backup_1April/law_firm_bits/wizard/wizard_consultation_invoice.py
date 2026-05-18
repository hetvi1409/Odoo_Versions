from odoo import models, fields, _
from odoo.exceptions import AccessError, UserError
from odoo.fields import Command


class WizardConsultationInvoice(models.TransientModel):
    _name = 'wizard.consultation.invoice'
    _description = 'Consultation Invoice'

    invoice_type = fields.Selection(selection=[('fix', 'Fixed'), ('hour', 'Hourly')], default='hour', required=True)
    amount = fields.Float("Amount")

    def btn_create_consultation_invoice(self):
        move_obj = self.env['account.move']
        if not self.invoice_type:
            pass

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
                'calendar_id': rec.id,
                'partner_id': rec.customer_id.id,
                'invoice_origin': rec.name,
                'invoice_line_ids': [],
            })

            qty = 1
            price_unit = self.amount

            if self.invoice_type == 'hour':
                qty = rec.duration

            invoice_vals['invoice_line_ids'] = [
                Command.create({
                    'display_type': 'product',
                    'product_id': self.env.ref("law_firm_bits.product_product_consultation_service").id,
                    'name': rec.description and rec.description or rec.name,
                    'quantity': qty,
                    'price_unit': price_unit,
                })]

            invoice_vals_list.append(invoice_vals)

        if invoice_vals_list:
            return move_obj.sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)
