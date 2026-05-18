from odoo import api, models, fields, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    burial_booking_id = fields.Many2one('cemetery.application',
                                        string='Burial Booking')

    @api.model_create_multi
    def create(self, vals_list):
        invoices = super(AccountMove, self).create(vals_list)
        for invoice in invoices:
            sale_order = self.env['sale.order'].search(
                [('name', '=', invoice.invoice_origin)], limit=1)
            if sale_order and sale_order.burial_booking_id:
                sale_order.burial_booking_id.invoice_id = invoice.id
        return invoices
