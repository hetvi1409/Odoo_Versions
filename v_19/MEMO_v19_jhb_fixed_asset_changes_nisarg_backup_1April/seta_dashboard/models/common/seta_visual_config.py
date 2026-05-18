# -*- coding: utf-8 -*-
# Copyright 2022 SETA PT Solusi Usaha Mudah
from odoo import models, fields


class SETAVisualConfig(models.Model):
    _name = 'seta.visual.config'
    _description = 'SETA Visual Config'

    name = fields.Char('Name', required=True)
    title = fields.Char('Title', required=True)
    config_type = fields.Selection([
        ('input_string', 'Input String'),
        ('input_number', 'Input Number'),
        ('selection_string', 'Selection String'),
        ('selection_number', 'Selection Number'),
        ('toggle', 'Toggle'),
    ])
    default_config_value = fields.Char(string='Default Config Value')
    visual_type_ids = fields.Many2many(comodel_name='seta.visual.type', string='Visual Type')
    visual_config_value_ids = fields.Many2many(comodel_name='seta.visual.config.value', string='Visual Config Value')

    _name_unique = models.Constraint(
        'unique (name)',
        'Visual Config Name Already Exist.',
    )
