from odoo import models, fields, api
from odoo.exceptions import UserError


class BuildingType(models.Model):
    _name = "building.type"
    _description = "Building Type"

    name = fields.Char(string="Name")
    description = fields.Text(string="Description")
