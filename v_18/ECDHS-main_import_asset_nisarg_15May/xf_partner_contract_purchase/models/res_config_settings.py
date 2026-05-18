# -*- coding: utf-8 -*-

from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    use_purchase_contract = fields.Selection([
        ('no', 'No'),
        ('optional', 'Optional'),
        ('required', 'Required')
    ],
        string='Use Contract for Purchase Orders',
        default='no',
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_purchase_contract = fields.Selection(
        string='Use Contract for Purchase Orders',
        related='company_id.use_purchase_contract',
        readonly=False,
    )
