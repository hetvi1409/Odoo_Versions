# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sales_price = fields.Float(string='Sales Price', related="product_id.lst_price")
