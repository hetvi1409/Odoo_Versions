from odoo import fields, models
from datetime import date

class BOM(models.Model):
    """This class inherits 'mrp.bom' to add fields"""
    _inherit = 'mrp.bom'

    last_sequence = fields.Char(string='Last Serial Numbers',
                               help='Serial numbers associated with the '
                                    'Bill of Materials', default="000")
    year_sequence = fields.Char(
        string="Year Sequence",
        default=lambda self: f"{date.today().year % 100:02d}"
    )

    month_sequence = fields.Char(
        string="Month Sequence",
        default=lambda self: f"{date.today().month:02d}"
    )
    not_quantity_unit = fields.Integer(string="Not Quantity per Unit")
