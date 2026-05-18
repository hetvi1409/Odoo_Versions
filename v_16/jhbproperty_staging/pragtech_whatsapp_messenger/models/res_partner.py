import logging
from odoo import api, fields, models, _
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'
    chatId = fields.Char('Chat ID')
    # whatsapp_meta_id = fields.Char('Whatsapp phone id')
    whatsapp_msg_ids = fields.One2many('whatsapp.messages', 'partner_id', 'WhatsApp Messages')

    @api.onchange('mobile')
    def onchange_mobile(self):
        if self.mobile:
            whatsapp_msg_number_without_space = self.mobile.replace(" ", "")
            whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace('+', "")
            self.chatId = whatsapp_msg_number_without_code

    def _get_default_whatsapp_recipients(self):
        """ Override of mail.thread method.
            WhatsApp recipients on partners are the partners themselves.
        """
        return self
