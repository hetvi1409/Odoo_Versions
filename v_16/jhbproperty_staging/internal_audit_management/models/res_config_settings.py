# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    template_id = fields.Many2one('project.template', string="Templates",
                                  config_parameter='internal_audit_management.template_id',)
    arp_sign_template_id = fields.Many2one('sign.template', string="Sign Template For ARP 3 -year",
                                  config_parameter='internal_audit_management.arp_sign_template_id',)
