# -*- coding: utf-8 -*-
from odoo import models, fields, api

class EventNew(models.Model):
    _name = 'event.new'
    _rec_name = 'event_id'

    event_id = fields.Many2one('event.event', string='Event')
    product_id = fields.Many2one('product.product', string='Product')
    event_new_image = fields.Binary(string='New Event Image', attachment=True)