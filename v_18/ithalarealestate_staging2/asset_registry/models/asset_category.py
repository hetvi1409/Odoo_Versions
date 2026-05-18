from odoo import fields, models, _


class AssetCategory(models.Model):
    _name = 'asset.category'

    name = fields.Char('Name', help="Name of the asset category", required=True, copy=False)
    description = fields.Char('Description',
                              help="Description of the asset category")