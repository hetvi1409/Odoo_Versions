'''
Created on Mar 7, 2021

@author: Zuhair Hammadi
'''
from odoo import models, fields

class MailTemplatePreview(models.TransientModel):
    _inherit = 'mail.template.preview'
    
    needaction_partner_ids = fields.Char(string='Partners with Need Action')