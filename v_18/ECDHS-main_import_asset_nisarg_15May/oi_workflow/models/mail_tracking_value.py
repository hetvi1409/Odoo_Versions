'''
Created on Feb 1, 2021

@author: Zuhair Hammadi
'''
from odoo import models, api

class MailTracking(models.Model):
    _inherit = 'mail.tracking.value'
    
    @api.model
    def create_tracking_values(self, initial_value, new_value, col_name, col_info, tracking_sequence, model_name):    
        if col_info['type'] == 'selection' and initial_value:
            selection = dict(col_info['selection'])
            if initial_value not in selection:
                col_info['selection'].append((initial_value, initial_value))
        
        return super(MailTracking, self).create_tracking_values(initial_value, new_value, col_name, col_info, tracking_sequence, model_name)