from odoo import fields, models


class AssetType(models.Model):
    """Model for asset type"""
    _name = 'asset.type'
    _description = "Asset type"

    name = fields.Char(string='Asset Type', required=True)
    category_id = fields.Many2one('asset.category')
