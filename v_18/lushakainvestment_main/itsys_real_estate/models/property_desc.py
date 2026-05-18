# -*- coding: utf-8 -*-
from odoo import api, fields, models

class PropertyDesc(models.Model):
    _name = "property.desc"
    _description = "Property Description"

    name = fields.Char('Name')
