# -*- coding: utf-8 -*-
from odoo import models, fields

class StockMove(models.Model):
    _inherit = 'stock.move'

    batch_info = fields.Char(string="Batch Info", help="Custom batch information for this move")
