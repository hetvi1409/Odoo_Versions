# -*- coding: utf-8 -*-
from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sales_price = fields.Float(string='Sales Price', related = "product_id.lst_price")
