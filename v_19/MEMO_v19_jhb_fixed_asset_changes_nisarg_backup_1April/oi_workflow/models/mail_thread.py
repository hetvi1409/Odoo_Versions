from odoo import models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    # def message_subscribe(self, partner_ids=None, subtype_ids=None):
    #     if self.env.context("disable_message_subscribe"):
    #         return
    #     return super(MailThread, self).message_subscribe(partner_ids=partner_ids, subtype_ids=subtype_ids)
