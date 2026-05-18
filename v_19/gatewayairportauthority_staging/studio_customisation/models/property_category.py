from odoo import models, fields

class PropertyCategory(models.Model):
    _name = 'x.property.category'
    _description = 'Property Category'
    _order = "x_sequence asc, name asc"

    name = fields.Char(required=True, tracking=True)
    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Active', default=False)
    x_sequence = fields.Integer(string="Sequence")
