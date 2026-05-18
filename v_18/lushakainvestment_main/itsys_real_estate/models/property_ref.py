# -*- coding: utf-8 -*-
from odoo import api, fields, models

class PropertyRef(models.Model):
    _name = "property.ref"
    _description = "Property Reference"

    name = fields.Char('Name')
