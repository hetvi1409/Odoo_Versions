# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.addons.xf_partner_contract.models.selection import UseContract


class Company(models.Model):
    _inherit = 'res.company'

    use_purchase_contract = fields.Selection(
        string='Use Contract for Purchase Orders',
        selection=UseContract.list,
        default=UseContract.default,
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_purchase_contract = fields.Selection(
        string='Use Contract for Purchase Orders',
        related='company_id.use_purchase_contract',
        readonly=False,
    )
