from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Res Config Settings"""
    _inherit = 'res.config.settings'

    servitude_expirations = fields.Integer(string="Servitude Expirations",
                                           config_parameter="servitude_register.do_risk_treatments_have_owner")