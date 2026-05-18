from odoo import models, fields


class FuelType(models.Model):
    _name = 'fuel.type'
    _description = 'Fuel Type'

    name = fields.Char(string='Type of Fuel')