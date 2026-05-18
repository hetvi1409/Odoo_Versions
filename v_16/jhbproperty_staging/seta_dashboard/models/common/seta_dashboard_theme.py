# -*- coding: utf-8 -*-
from odoo import models, fields


class setaDashboardTheme(models.Model):
    _name = 'seta.dashboard.theme'
    _description = 'seta Dashboard Theme'

    name = fields.Char('Name', required=True)

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Dashboard Theme Name Already Exist.')
    ]
