from odoo import fields, models


class HouseSettlement(models.Model):
    """House Settlement"""
    _name = 'house.settlement'
    _description = "House Settlement"

    name = fields.Char(string="Settlement", required=True)


class NaturePropertyRights(models.Model):
    """House Settlement"""
    _name = 'property.nature'
    _description = "Nature Property Rights"

    name = fields.Char(string="Nature Property Rights", required=True)

