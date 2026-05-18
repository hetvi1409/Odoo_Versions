# -*- coding: utf-8 -*-
from odoo import models, fields, api

class EventEvent(models.Model):
    _inherit = 'event.event'

    product_id = fields.Many2one('product.product', string='Product')
    event_image = fields.Binary(string='Event Image', attachment=True)
