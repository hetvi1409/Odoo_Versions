'''
Created on Aug 11, 2020

@author: Zuhair Hammadi
'''
from odoo import models

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'
    
    def message_subscribe(self, partner_ids=None, subtype_ids=None):
        if self._context.get("disable_message_subscribe"):
            return
        return super(MailThread, self).message_subscribe(partner_ids = partner_ids, subtype_ids = subtype_ids)