
from odoo import fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    first_name = fields.Char(string="First Name")
