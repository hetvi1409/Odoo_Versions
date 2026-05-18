# -*- coding: utf-8 -*-
from odoo import models, fields


class setaVisualConfigValue(models.Model):
    _name = 'seta.visual.config.value'
    _description = 'seta Visual Config Value'

    name = fields.Char('Name', required=True)
    title = fields.Char('Title', required=True)
    value_type = fields.Selection([
        ('string', 'String'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
    ])
    visual_config_ids = fields.Many2many(comodel_name='seta.visual.config', string='Visual Config')
