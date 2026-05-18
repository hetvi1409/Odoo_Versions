# See LICENSE file for full copyright and licensing details.

from odoo import _, api, models,fields, models
from odoo.exceptions import UserError 


class SaleOrder(models.Model):
    _inherit = "sale.order"

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
            self.reference = self.partner_id.ref