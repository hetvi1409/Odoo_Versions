

from odoo import models, fields, api
from odoo.exceptions import AccessError

class ApprovalForwardWizard(models.TransientModel):
    _name = 'approval.forward.wizard'
    _description = 'Approval Forward Wizard'
    
    @api.model
    def _get_user_id_domain(self):
        if not self._context.get('active_model'):
            return []
        
        model_id = self.env['ir.model']._get(self._context.get('active_model'))
        record = self.env[model_id.model].browse(self._context.get('active_id'))
        
        users = model_id.access_ids.filtered('perm_write').mapped('group_id.users') - record.approval_user_ids
        
        ids = []
        for user in users:
            try:
                record = record.with_user(user.id)
                record.check_access_rule('read')
                record.check_access_rule('write')
                ids.append(user.id)
            except AccessError:
                pass
        return [('id', 'in', ids)]
                
    model = fields.Char(default = lambda self: self._context.get('active_model'), required = True)
    record_id = fields.Integer(default = lambda self: self._context.get('active_id'), required = True, string='Record ID')    
    record_ref = fields.Char('Record', compute = '_calc_record_ref')
    
    reason = fields.Text(required = True)
    user_id = fields.Many2one('res.users', required = True, domain = _get_user_id_domain)
    
    @api.depends('model', 'record_id')
    def _calc_record_ref(self):
        for wizard in self:
            record = self.env[wizard.model].browse(wizard.record_id).exists()
            wizard.record_ref = record and '%s,%d' % (record._name, record.id)            
        
    def action_forward(self):
        record = self.env[self.model].browse(self.record_id)
        action = record._action_forward(self.user_id, self.reason)
        return action or {
            'type' : 'ir.actions.client',
            'tag' : 'trigger_reload'
            }