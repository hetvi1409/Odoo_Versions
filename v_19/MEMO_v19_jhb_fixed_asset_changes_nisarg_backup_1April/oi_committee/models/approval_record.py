
from odoo import models, fields, SUPERUSER_ID, _

class ApprovalRecord(models.AbstractModel):
    _inherit ='approval.record'


    def action_approve(self):
        waiting_users = False
        approved = True
        if self._uid != SUPERUSER_ID:                        
            for record in self.filtered('button_approve_enabled'):
                if record.state_id.committee:
                    def is_approved(user):
                        for log_id in record.log_ids:
                            if log_id.old_state != record.state:
                                break
                            if log_id.user_id == user:
                                return True
                        return user.employee_ids[:1].display_name or user.display_name
                    
                    waiting_users = list(filter(lambda item : item is not True,map(is_approved, record.approval_user2_ids - self.env.user)))
                    
                    if waiting_users:
                        if is_approved(self.env.user) is not True and self.env.user in record.approval_user2_ids:
                            self.env['approval.log'].sudo().create({
                                'record_id' : record.id,
                                'user_id' : self.env.user.id,
                                'date' : fields.Datetime.now(),
                                'state' : record.state,
                                'model_id' : self.env['ir.model']._get_id(record._name),
                                'description' : ''
                                })
                            record._remove_approval_activity('approved', old_state_id = record.state_id, user_id = self.env.user.id)
                        approved = False
                        continue
        if approved:
            return super(ApprovalRecord, self).action_approve()                       
        if waiting_users and len(self) == 1:
            return {
                'message' : ', '.join(waiting_users),
                'title'  : _('Waiting User Approval'),
                }