
from odoo import models, fields, api

class ChangeDocumentStatus(models.TransientModel):
    _name = 'approval.state.update'
    _description = 'Change Document Status'
    
    @api.model
    def _get_state(self):
        model = self.env.context('active_model')
        if not model:
            model = 'approval.record'
            
        return self.env[model]._fields['state']._description_selection(self.env)
    
    state = fields.Selection(_get_state, required = True, string='Status')
    
    def action_update(self):        
                
        active_model = self.env.context('active_model')
        
        if isinstance(self.env.context('active_domain'), list):
            records = self.env[active_model].search(self.env.context('active_domain'))
        else:
            active_ids = self.env.context('active_ids')
            records = self.env[active_model].browse(active_ids)
                        
        records.write({'state' : self.state})
        if records._isinstance('approval.record'):
            for record in records:
                record._remove_approval_activity()
                record._schedule_approval_activity()
                
        return { 
            'type': "ir.actions.client",
            'tag': 'trigger_reload'
        }