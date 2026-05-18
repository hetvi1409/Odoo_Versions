from email import message
from email.policy import default
# from typing_extensions import Self
from odoo import fields, models, _, api


class mailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def check_seen(self, message_id):
        message = self.env['mail.message'].sudo().search([('id', '=', message_id)])
        if message.message_seen:
            return True
        else:
            return False

    whatsapp_message_id = fields.Char('Whatsapp Message Id')
    message_seen = fields.Boolean(string="Message seen", default=False)
