
from odoo import models, fields

class ApprovalRejectWizard(models.TransientModel):
    _name = 'approval.reject.wizard'
    _description = 'Approval Workflow Reject Wizard'
    
    def _get_reject_confirm_msg(self):
        model = self.env.context('active_model')
        record_id = self.env.context('active_id')
        record = self.env[model].browse(record_id)
        assert record._isinstance('approval.record')        
        return record.reject_confirm_msg
        
    
    reason = fields.Text(required = True)
    reject_confirm_msg = fields.Char(default = _get_reject_confirm_msg, readonly = True)
    
    def action_reject(self):
        model = self.env.context('active_model')
        record_id = self.env.context('active_id')
        record = self.env[model].browse(record_id)
        assert record._isinstance('approval.record')
        return record.action_reject(self.reason)