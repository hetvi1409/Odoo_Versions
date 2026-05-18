# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # stock_location_id = fields.Many2one('stock.quant', string='Stock By Location')
    unit_price_before_discount = fields.Float(string='Unit Price Before Discount', related='product_id.lst_price')
    discount_amount = fields.Float(string='Discount Amount', compute='_compute_discount_amount', store=True)
    total_before_discount = fields.Float(string='Total Before Discount', compute='_compute_total_before_discount', store=True)


    @api.depends('price_unit', 'quantity')
    def _compute_discount_amount(self):
        for line in self:
                line.discount_amount = (line.product_id.lst_price - line.price_unit) * line.quantity
                line.discount_amount = abs(line.discount_amount)

    @api.depends('unit_price_before_discount', 'quantity')
    def _compute_total_before_discount(self):
        for line in self:
            line.total_before_discount = line.unit_price_before_discount * line.quantity
