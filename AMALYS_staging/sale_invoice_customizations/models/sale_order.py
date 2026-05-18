# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    default_location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
    )

    @api.onchange('default_location_id')
    def _onchange_default_location_id_notify_lines(self):
        for line in self.order_line:
            line._compute_quantity_available()

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id_set_location(self):
        for order in self:
            if order.warehouse_id:
                order.default_location_id = order.warehouse_id.lot_stock_id

    @api.model
    def create(self, vals):
        if not vals.get('default_location_id') and vals.get('warehouse_id'):
            warehouse = self.env['stock.warehouse'].browse(vals['warehouse_id'])
            vals['default_location_id'] = warehouse.lot_stock_id.id
        return super(SaleOrder, self).create(vals)

    def action_confirm(self):
        for order in self:
            carrier = order.env['delivery.carrier'].search([('delivery_type','=','base_on_rule')],limit=1)
            # if not carrier:
            #     raise UserError(_("No delivery carrier found. Please configure one."))
            if carrier:
                matching_rule = carrier.price_rule_ids.filtered(
                    lambda r: r.variable == 'price' and
                            r.operator in ('<=', '<', '=') and
                            order.amount_total <= r.max_value
                )
                if matching_rule:
                    order.order_line.create({
                        'order_id': order.id,
                        'name': carrier.name or _('Shipping'),
                        'product_id': carrier.product_id.id,
                        'product_uom_qty': 1,
                        'price_unit': carrier.price_rule_ids.list_base_price,
                        'tax_id': [(6, 0, carrier.product_id.taxes_id.ids)],
                        'is_delivery': True,
                    })
        res = super().action_confirm()
        return res
