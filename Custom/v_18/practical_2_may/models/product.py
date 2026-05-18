# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Product(models.Model):
    _inherit = 'product.product'


    event_ids = fields.One2many('event.event', 'product_id', string='Events')
    event_new_ids = fields.One2many('event.new', 'product_id', string='New Events')

    event_id = fields.Many2one('event.event', string='Event')


    @api.onchange('event_id')
    def onchange_image(self):
        if self.event_id:
            print('\n\n\n SELF----EVENT_ID===>', self.event_id)
            self.image_1920 = self.event_id.event_image