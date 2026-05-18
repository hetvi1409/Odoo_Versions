# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    template_id = fields.Many2one('project.template', string="Templates",
                                  config_parameter='internal_audit_management.template_id',)