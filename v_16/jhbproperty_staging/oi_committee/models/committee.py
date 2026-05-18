
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_states = {'draft' : [('readonly', False)]}

class Committee(models.Model):
    _name = 'committee'
    _inherit = ['approval.record', 'mail.thread', 'mail.activity.mixin']
    _description = 'Committee'
    
    @api.model
    def _get_models(self):
        models = self.env['committee.type'].search([]).mapped('model_id.model')
        return [(name, name) for name in models]
    
    state = fields.Selection(index = True)
    type_id = fields.Many2one('committee.type', required = True, index = True, readonly =True, states = _states)
    type_xml_id = fields.Char(related='type_id.xml_id', readonly =True)
    name = fields.Char('Number', required = True, readonly =True, default = 'New')
    date_start = fields.Date(required = True, default = fields.Date.today, readonly =True, states = _states)
    date_end = fields.Date(readonly =True, states = _states)
    subject = fields.Char(readonly =True, states = _states)
    description = fields.Text(readonly =True, states = _states)
    
    res_model_id = fields.Many2one('ir.model', related='type_id.model_id', readonly = True)
    res_id = fields.Integer(readonly = True)
    ref = fields.Reference(_get_models, 'Record', compute = '_calc_ref')

    record_name = fields.Char(compute = '_calc_ref')
    
    member_ids = fields.One2many('committee.member', 'committee_id', readonly =True, states = _states)
    
    
    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, '%s - %s' % (record.type_id.name, record.name)))
        return res
            
    @api.model
    def _after_approval_states(self):
        return  [('active', _('Active')), ('done',_('Completed')), ('rejected', _('Rejected'))]

    
    def _on_submit(self):
        if self.date_end and self.date_end < fields.Date.today():
            raise ValidationError(_('Date End < Today'))

    
    
    def _on_approve(self):
        super(Committee, self)._on_approve()
        self.type_id.sudo()._update_members()
    
    def _get_sequence_code(self,vals):
        return self._name
    
    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        for vals in vals_list:
            code = self._get_sequence_code(vals)
            vals['name'] = self.env['ir.sequence'].next_by_code(code)
        return super(Committee, self).create(vals_list)
    
    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for record in self:
            if record.date_end and record.date_end < record.date_start:
                raise ValidationError(_('Start Date > End Date'))
    
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
            record.record_name =  record_name   
            record.ref =  ref   
                        
    @api.model
    def _check_completed(self):
        today = fields.Date.today()
        records = self.search([('state','=', 'active'), ('date_end', '<', today)])
        if records:
            records.write({'state' : 'done'})
                
    
    def action_view_record(self):
        record = self.ref
        return {
            'type': 'ir.actions.act_window',
            'name': record._description,
            'res_model': record._name,
            'res_id': record.id,
            'views': [(False, 'form'),],   
            'view_type': 'form',
            'view_mode': 'form',                     
        }
    
    
    def action_close(self):
        self.filtered(lambda record: record.state=='active').write({'state' : 'done'})
        self.mapped('type_id').sudo()._update_members()