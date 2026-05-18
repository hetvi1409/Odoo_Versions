from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    
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

    @api.onchange('partner_id')
    def _onchange_partner_id_set_region(self):
        if self.partner_id:
            self.region = self.partner_id.region
            self.partner_ref = self.partner_id.ref