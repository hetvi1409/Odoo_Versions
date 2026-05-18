# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    previous_order_ids = fields.Many2many(
        'sale.order',
        string="Previous Orders",
        compute="_compute_previous_orders"
    )

    @api.depends('partner_id')
    def _compute_previous_orders(self):
        for rec in self:
            if rec.partner_id:
                orders = self.env['sale.order'].search([
                    ('partner_id', '=', rec.partner_id.id),
                    ('state', 'in', ['sale', 'done']),
                    ('id', '!=', rec.id)  # exclude current order
                ], order='date_order desc', limit=5)

                rec.previous_order_ids = orders
            else:
                rec.previous_order_ids = False