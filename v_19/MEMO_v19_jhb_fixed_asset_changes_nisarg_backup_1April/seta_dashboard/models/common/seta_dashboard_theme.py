# -*- coding: utf-8 -*-
# Copyright 2022 SETA PT Solusi Usaha Mudah
from odoo import models, fields


class SETADashboardTheme(models.Model):
    _name = 'seta.dashboard.theme'
    _description = 'SETA Dashboard Theme'

    name = fields.Char('Name', required=True)

    _name_unique = models.Constraint(
        'unique(name)',
        'Dashboard Theme Name Already Exist.',
    )
