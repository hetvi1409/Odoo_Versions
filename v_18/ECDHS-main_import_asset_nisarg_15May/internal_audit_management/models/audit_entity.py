from odoo import api, fields, models


class BusinessEntityType(models.Model):
    """Business entity type"""
    _name = 'entity.type'
    _description = 'Entity type'

    name = fields.Char(string="Entity Type", required=True)
