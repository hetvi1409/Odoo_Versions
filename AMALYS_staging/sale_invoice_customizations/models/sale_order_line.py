# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    item_number = fields.Integer('#', compute='_set_sequence', default=0)
    sequence = fields.Integer(default=1)

    quantity_available = fields.Float(
        string='Available Quantity',
        compute='_compute_quantity_available',
        store=False,
        readonly=False,
    )

    @api.depends('order_id.order_line')
    def _set_sequence(self):
        for rec in self:
            index = 1
            for line in rec.order_id.order_line.sorted('sequence'):
                if not line.display_type:
                    line.item_number = index
                    index += 1
                else:
                    line.item_number = 0

    @api.depends('product_id', 'order_id.default_location_id')
    def _compute_quantity_available(self):
        StockQuant = self.env['stock.quant']
        for line in self:
            line.quantity_available = 0.0
            if line.product_id and line.order_id.default_location_id:
                domain = [
                    ('product_id', '=', line.product_id.id),
                    ('location_id', '=', line.order_id.default_location_id.id),
                ]
                quants = StockQuant.read_group(domain, ['quantity:sum'], ['product_id'])
                if quants and quants[0].get('quantity') is not None:
                    line.quantity_available = quants[0]['quantity']
                else:
                    line.quantity_available = 0.0