from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    kanban_product_summary = fields.Char(
        string='Product Summary',
        compute='_compute_kanban_product_summary',
        store=False,
    )

    @api.depends('move_ids_without_package',
                 'move_ids_without_package.product_id',
                 'move_ids_without_package.product_qty')
    def _compute_kanban_product_summary(self):
        for picking in self:
            lines = []
            for move in picking.move_ids_without_package:
                product_name = move.product_id.display_name or ''
                qty = move.product_uom_qty
                lines.append(f"{product_name}: {qty:.2f}")
            picking.kanban_product_summary = ' | '.join(lines) if lines else ''