# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MeterManufacturer(models.Model):
    _name = "x.meter.manufacturer"
    _description = "Meter Manufacturer"

    x_studio_sequence = fields.Integer(
        string="Sequence"
    )
    x_name = fields.Char(string='Name')
