from odoo import fields, models


class ConfigurationSettings(models.TransientModel):
    """Adding a configuration for the agenda"""
    _inherit = "res.config.settings"

    need_section = fields.Boolean(string="Add More Agenda Section",
                                  config_parameter="board_management_system.need_section")
