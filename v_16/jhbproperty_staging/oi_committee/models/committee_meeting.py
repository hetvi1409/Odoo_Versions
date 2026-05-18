
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_states = {'draft' : [('readonly', False)]}

class CommitteeMeeting(models.Model):
    _name = 'committee.meeting'
    _inherit = ['approval.record', 'mail.thread', 'mail.activity.mixin']
    _description = 'Committee Meeting'
    
    @api.model
    def _get_models(self):
        return self.env['committee']._get_models()
    
    committee_id = fields.Many2one('committee', required = True, domain = [('state','=', 'active')])
    type_id = fields.Many2one(related='committee_id.type_id', readonly =True)
    type_xml_id = fields.Char(related='committee_id.type_xml_id', readonly =True)
    type_code = fields.Char(related='committee_id.type_id.code', readonly =True)
    
    name = fields.Char('Number', required = True, readonly =True, default = 'New')
    date_start = fields.Datetime(readonly =True, states = _states, required=True)
    date_end = fields.Datetime(readonly =True, states = _states, required=True)
    
    attendance_ids = fields.Many2many('committee.member', required = True, domain = "[('committee_id','=', committee_id)]", readonly =True, states = _states)
    
    subject = fields.Char(readonly =True, states = _states, required=True)
    description = fields.Text(readonly =True, states = _states)
    report = fields.Html(readonly =True, states = _states)
        
    res_model_id = fields.Many2one('ir.model', related='committee_id.type_id.model_id', readonly = True)
    res_id = fields.Integer(readonly = True)
    ref = fields.Reference(_get_models, 'Record', compute = '_calc_ref')

    record_name = fields.Char(compute = '_calc_ref')
    
    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code(self._name)
        return super(CommitteeMeeting, self).create(vals_list)
    
    @api.depends('res_model_id', 'res_id')
    def _calc_ref(self):
        for record in self:
            record_name = False
            ref = False
            if record.res_model_id and record.res_id:
                res=self.env[record.res_model_id.model].browse(record.res_id).exists()
                if res:
                    ref = '%s,%d' % (res._name, res.id)        
                    record_name = res.display_name   
            record.record_name = record_name     
            record.ref = ref    

    
    def action_view_record(self):
        record = self.ref
        if not record:
            return
        return {
            'type': 'ir.actions.act_window',
            'name': record._description,
            'res_model': record._name,
            'res_id': record.id,
            'views': [(False, 'form'),],   
            'view_type': 'form',
            'view_mode': 'form',                     
        }
    
    
    def _on_submit(self):
        if not self.attendance_ids:
            raise ValidationError(_('No Attendances Selected'))            
        if not self.report:
            raise ValidationError(_('Enter Report'))                
        
    
    def action_report(self):               
        return {
          'type' : 'ir.actions.act_window',
          'res_model' : self._name,
          'res_id' : 0,
          'target' : 'current',
          'view_type' : 'form',
          'view_mode' : 'pdf',
          'name' : _('Report'),
          'context' : {
              'report_name' : 'oi_committee.report_committee_meeting',
              'docids' : self.ids
              }
        }                                                                   