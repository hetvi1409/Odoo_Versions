# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    send_mail_before = fields.Integer(string="Send Mail Before (Days)",
                                      config_parameter='performance_contract.send_mail_before',
                                      default=3,
                                      help="Number of days before goal deadiline to send reminder emails to employees.")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('performance_contract.send_mail_before', self.send_mail_before)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        send_mail_before = int(self.env['ir.config_parameter'].sudo().get_param('performance_contract.send_mail_before', default=3))
        res.update(
            send_mail_before=send_mail_before,
        )
        return res

