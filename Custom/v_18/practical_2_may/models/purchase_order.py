# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type')
    

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        """overide base button_confirm """
        StockPicking = self.env['stock.picking']

        for order in self:
            picking_groups = {}

            # Group lines by picking type
            for line in order.order_line:
                picking_type = line.picking_type_id or order.picking_type_id

                if picking_type not in picking_groups:
                    picking_groups[picking_type] = []

                picking_groups[picking_type].append(line)

            # Create separate picking for each group
            for picking_type, lines in picking_groups.items():

                picking_vals = order._prepare_picking()
                picking_vals.update({
                    'picking_type_id': picking_type.id,
                })

                picking = StockPicking.create(picking_vals)

                for line in lines:
                    move_vals = line._prepare_stock_moves(picking)
                    for mv in move_vals:
                        mv['picking_id'] = picking.id
                        self.env['stock.move'].create(mv)


        return super(PurchaseOrder, self).button_confirm()