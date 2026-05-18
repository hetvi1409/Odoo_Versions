# -*- coding: utf-8 -*-
# Copyright 2022 SETA PT Solusi Usaha Mudah
from odoo import models, fields


class SETAAnalysisVisualConfig(models.Model):
    _name = 'seta.analysis.visual.config'
    _description = 'SETA Analysis Visual Config'

    analysis_id = fields.Many2one(comodel_name='seta.analysis', string='Analysis', ondelete='cascade')
    visual_config_id = fields.Many2one(comodel_name='seta.visual.config', string='Visual Config')
    visual_config_value_id = fields.Many2one(comodel_name='seta.visual.config.value', string='Visual Config Value')
    string_value = fields.Text(string='String Value')
