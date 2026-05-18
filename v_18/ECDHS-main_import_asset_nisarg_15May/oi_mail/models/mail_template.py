'''
Created on Oct 2, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields

class MailTemplate(models.Model):
    _inherit = "mail.template"

    needaction_partner_ids = fields.Char(string='Partners with Need Action')
    
    def generate_email(self, res_ids, fields):
        if 'needaction_partner_ids' not in fields:
            fields.append('needaction_partner_ids')
                    
        return super(MailTemplate, self).generate_email(res_ids, fields=fields)
