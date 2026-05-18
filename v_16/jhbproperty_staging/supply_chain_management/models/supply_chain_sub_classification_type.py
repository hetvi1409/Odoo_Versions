from odoo import models, fields


class SupplyChainSubClassificationType(models.Model):
    _name = 'supply.chain.sub.classification.type'
    _description = 'Supply Chain Sub Classification Type'

    name = fields.Char(string='Name')

