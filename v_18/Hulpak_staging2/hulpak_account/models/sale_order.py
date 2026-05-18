# models/sale_order.py

from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    
    department = fields.Many2one(
        'account.analytic.account',
        string="Department",
        domain="[('plan_id.name', 'ilike', 'Department')]"
    )

    region = fields.Many2one(
        'account.analytic.account',
        string="Region",
        domain="[('plan_id.name', 'ilike', 'Region')]"
    )
