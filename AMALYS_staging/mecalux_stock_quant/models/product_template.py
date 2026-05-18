# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def create_receipt_for_products(self):
        negative_forecast_products = self.env['product.template'].search(
            [('virtual_available', '<', 0), ('is_storable', '=', True)])

        location_dest = self.env['stock.location'].search([('usage', '=', 'internal'), ('name', '=', 'MANUFAST'), ('location_id.name', '=', 'WH')], limit=1) or self.env.ref('stock.stock_location_stock')
        move_lines = []
        for product in negative_forecast_products:
            qty_needed = abs(product.virtual_available)
            if qty_needed <= 0:
                continue
            vals = {
                'name': product.display_name,
                'product_id': product.id,
                'product_uom_qty': qty_needed,
                'product_uom': product.uom_id.id,
                'location_dest_id': location_dest.id,
            }
            move_lines.append((0, 0, vals))

        if move_lines:
            picking = self.env['stock.picking'].create({
                'picking_type_id': self.env.ref('stock.picking_type_in').id,
                'location_dest_id': location_dest.id,
                'move_ids_without_package': move_lines,
                'origin': 'Auto Receipt for Negative Forecast',
            })
            picking.action_confirm()
            # picking.button_validate()
