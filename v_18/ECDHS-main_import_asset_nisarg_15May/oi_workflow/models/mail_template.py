'''
Created on Oct 2, 2018

@author: Zuhair Hammadi
'''
from odoo import models

class MailTemplate(models.Model):
    _inherit = "mail.template"
    
    def generate_email(self, res_ids, fields):
        res= super(MailTemplate, self).generate_email(res_ids, fields)
        
        if isinstance(res_ids, int):
            results = [res]
        else:
            results = res
                    
        for vals in results:
            if isinstance(vals, dict) and vals.get('model') == 'approval.record':
                vals['model'] = self._context.get('active_model')
        
        return res
    

    def _send_check_access(self, res_ids):
        if self.model =='approval.record':
            records = self.env[self._context['active_model']].browse(res_ids)
            records.check_access_rights('read')
            records.check_access_rule('read')
            return
        return super(MailTemplate, self)._send_check_access(res_ids)