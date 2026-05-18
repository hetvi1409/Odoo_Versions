# python
from odoo import models, api, fields, _
from odoo.tools.safe_eval import safe_eval, test_python_expr
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class ApprovalConfig(models.Model):
    _name = 'approval.config'
    _description = 'Approval Workflow Settings'
    _order = 'sequence,id'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    @api.model
    def _get_sequence(self):
        model_id = self._context.get('default_model_id') or 0
        self._cr.execute('select max(sequence) from %s where model_id =%s' % (self._table, model_id))
        sequence, = self._cr.fetchone()
        return (sequence or 0) + 10
            
    model_id = fields.Many2one('ir.model', string='Object', required = True, ondelete='cascade')
    
    model = fields.Char(related='model_id.model', readonly = True)
    model_name = fields.Char(related='model_id.name', readonly = True)

    state = fields.Char(required = True, copy = False)
    name = fields.Char(required = True, translate = True)
    active = fields.Boolean(default = True)
    sequence = fields.Integer(default = _get_sequence, required = True, copy = False)
    # sequence = fields.Integer(default =1, required = True, copy = False)

    group_ids = fields.Many2many('res.groups', string='Approval Groups', required = True, relation='approval_config_group_ids_rel')
    
    filter_condition = fields.Char('Filter Condition')
        
    condition = fields.Text(string='Required Condition', default = 'True', required = True )
                
    template_ids = fields.Many2many('mail.template', string='Mail Templates', relation='approval_config_mail_template_rel', domain="['|', ('model_id','=', model_id), ('model','=', 'approval.record')]")
    reject_template_ids = fields.Many2many('mail.template', string='Reject Mail Templates', relation='approval_config_reject_template_ids_rel', domain="['|', ('model_id','=', model_id), ('model','=', 'approval.record')]")
    
    auto_subscribe_users = fields.Boolean('Add followers', help='Add Approval Users to the record followers')
    
    auto_subscribe_users_enabled = fields.Boolean(compute = '_calc_auto_subscribe_users_enabled')
    
    schedule_activity = fields.Boolean('Schedule Activity', default = True)
    schedule_activity_field_id = fields.Many2one('ir.model.fields')
    schedule_activity_days = fields.Integer('Activity Days')
    
    schedule_activity_enabled = fields.Boolean('Hours', compute = '_calc_schedule_activity_enabled')
    
    post_approval_msg = fields.Boolean('Post Approval Message')
    post_reject_msg = fields.Boolean('Post Reject Message')

    before_script = fields.Text('Before Script', help='Script to Execute on Enter this State')
    after_script = fields.Text('After Script', help= 'Script to Execute after Exit this State')
    on_script = fields.Text('On Script', help= 'Script to Execute on Exit this State')
    
    reject_script = fields.Text('Reject Script', help= 'Script to Execute on Reject')
    
    approve_button_name = fields.Char(default = 'Approve', translate = True)
    approve_confirm_msg = fields.Char(default = 'Approve ?', translate = True)
    
    reject_button_name = fields.Char(default = 'Reject', translate = True)        
    reject_button_wizard = fields.Boolean(default = True)
    approve_button_wizard = fields.Boolean(default = False)
    reject_confirm_msg = fields.Char(default = 'Reject ?', translate = True)  
    
    escalation_ids = fields.One2many('approval.escalation', 'config_id', domain = ['|', ('active', '=', True), ('active', '=', False)])
    last_state_update_id = fields.Many2one('ir.model.fields', compute = '_calc_last_state_update_id')

    allow_forward = fields.Boolean()
    allow_return = fields.Boolean()
    allow_transfer = fields.Boolean()
    allow_cancel = fields.Boolean()
    
    is_sudo_approve = fields.Boolean(string="Approve as super user", help= 'Enable this option when a user can only approve a record but cannot edit, user access rights: only read.')
    
    cancel_type = fields.Selection([('auto_cancel','Cancel Automatic'),('workflow','Cancel Workflow')], string='Cancel Type')
    tag_ids = fields.Many2many('state.tags', string='Tags')
    auto_approve = fields.Boolean('Automatic Approval')

    _state_uniq = models.Constraint(
        'unique(model_id, state)',
        'The state should be unique !',
    )

    _name_uniq = models.Constraint(
        'unique(model_id, name)',
        'The name should be unique !',
    )

    @api.constrains('before_script', 'after_script', 'on_script')
    def _check_code(self):
        for record in self:
            for name in ('before_script', 'after_script', 'on_script'):
                value = record[name]
                if value:
                    msg = test_python_expr(expr=value.strip(), mode="exec")
                    if msg:
                        raise ValidationError(msg)

    @api.constrains('filter_condition', 'condition')
    def _check_condition(self):
        for record in self:
            for name in ('filter_condition', 'condition'):
                value = record[name]
                if value:
                    msg = test_python_expr(expr=value.strip(), mode="eval")
                    if msg:
                        raise ValidationError(msg)

    def copy(self, default=None):
        default = dict(default or {})
        default.setdefault('state', f"{self.state}_copy")
        default.setdefault('name', _("%s (copy)") % (self.name or ''))
        return super(ApprovalConfig, self).copy(default=default)

    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, '%s %s' % (record.model, record.state)))
        return res

    @api.depends('model')
    def _calc_last_state_update_id(self):
        for record in self:
            record.last_state_update_id = self.env['ir.model.fields'].search(
                [('model', '=', record.model or ''), ('name', '=', 'last_state_update')], limit=1)

    @api.depends('model_id')
    def _calc_auto_subscribe_users_enabled(self):
        for record in self:
            try:
                model_name = record.model_id.model or ''
                model_env = self.env[model_name] if model_name else None
                # detect mail.thread by presence of the common message field
                record.auto_subscribe_users_enabled = bool(model_env) and ('message_ids' in getattr(model_env, '_fields', {}))
            except Exception:
                record.auto_subscribe_users_enabled = False

    @api.depends('model_id')
    def _calc_schedule_activity_enabled(self):
        for record in self:
            try:
                model_name = record.model_id.model or ''
                model_env = self.env[model_name] if model_name else None
                # detect mail.activity.mixin by presence of 'activity_ids' and mail.thread by 'message_ids'
                has_activity = bool(model_env) and ('activity_ids' in getattr(model_env, '_fields', {}))
                has_thread = bool(model_env) and ('message_ids' in getattr(model_env, '_fields', {}))
                record.schedule_activity_enabled = has_activity and has_thread
            except Exception:
                record.schedule_activity_enabled = False

    @api.constrains('auto_subscribe_users')
    def _check_auto_subscribe_users(self):
        for record in self:
            if record.auto_subscribe_users and not record.auto_subscribe_users_enabled:
                raise ValidationError(_('Object must inherit mail.thread'))

    @api.constrains('schedule_activity')
    def _check_schedule_activity(self):
        for record in self:
            if record.schedule_activity and not record.schedule_activity_enabled:
                raise ValidationError(_('Object must inherit mail.activity.mixin'))

    def _get_next(self, record):
        if not self:
            model_id = self.env['ir.model']._get_id(record._name)
            return self.search([('active', '=', True), ('model_id', '=', model_id)], limit=1)._next(record)
        return self._next(record, True)

    def _next(self, record, force=False):
        if not self:
            return self

        self.ensure_one()

        if not force:
            try:
                result = safe_eval(self.condition, record._get_eval_context())
            except Exception as ex:
                _logger.error("Error evaluating workflow condition %s", [record, self.state])
                _logger.error(str(ex))
                result = False

            if result:
                return self

        return self.search(
            [('model_id', '=', self.model_id.id), ('active', '=', True), '|', ('sequence', '>', self.sequence), '&',
             ('sequence', '=', self.sequence), ('id', '>', self.id)], limit=1)._next(record)

    @api.model
    def _update_approval_activity(self):
        for group in self._read_group([('schedule_activity', '=', True)], ['model_id'], ['model_id']):
            model = self.env['ir.model'].browse(group['model_id'][0]).model
            states = self.search(group['__domain']).mapped('state')
            for record in self.env[model].search([('state', 'in', states)]):
                record._update_approval_activity()
            self.env.cr.commit()

    @api.model
    def _run_update_approval_activity(self):
        try:
            with self.env.cr.savepoint():
                # update cron nextcall safely
                self.env.ref('oi_workflow.cron_update_approval_activity').write({'nextcall': fields.Datetime.now()})
        except Exception:
            _logger.exception('Could not update cron nextcall')

    @api.model_create_multi
    def create(self, vals_list):
        self.env.registry.clear_cache()
        return super(ApprovalConfig, self).create(vals_list)

    def write(self, vals):
        self.env.registry.clear_cache()
        return super(ApprovalConfig, self).write(vals)

    def unlink(self):
        self.env.registry.clear_cache()
        return super(ApprovalConfig, self).unlink()
