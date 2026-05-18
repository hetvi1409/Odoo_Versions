
from odoo import models, fields, api, _
from datetime import timedelta

LEVEL_SELECTION = [
    ('basic', 'Basic'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
    ('expert', 'Expert'),
]

LEVEL_RANK = {'basic':1, 'intermediate':2, 'advanced':3, 'expert':4}

class ScsAssessment(models.Model):
    _name = 'scs.assessment'
    _description = 'SCM Assessment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'


    name = fields.Char(compute='_compute_name', store=True)
    # name = fields.Char(default=_compute_name, store=True)
    # name = fields.Char(default=lambda self: _('SCM Assessment'), compute='_compute_name', store=True)
    # name = fields.Char(default=lambda self: _('SCM Assessment'))
    profile_id = fields.Many2one('scs.employee.profile', required=True)
    employee_id = fields.Many2one(related='profile_id.employee_id', store=True)
    role_id = fields.Many2one(related='profile_id.role_id', store=True)

    line_ids = fields.One2many('scs.assessment.line', 'assessment_id', string='Lines')
    state = fields.Selection([
        ('draft','Draft'),
        ('submitted','Submitted'),
        ('validated','Validated'),
        ('done','Done')
    ], default='draft', tracking=True)

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_validate(self):
        self.write({'state': 'validated'})

    def action_done(self):
        self.write({'state': 'done'})

    def _populate_lines_from_role(self):
        for rec in self:
            reqs = rec.profile_id.role_id.requirement_ids
            lines = []
            for r in reqs:
                lines.append((0, 0, {
                    'competency_id': r.competency_id.id,
                    'required_level': r.required_level,
                }))
            rec.line_ids = lines

    @api.depends('employee_id', 'role_id')
    def _compute_name(self):
        for rec in self:
            rec.name = '%s - %s - SCM Assessment' % (rec.employee_id.name or '', rec.role_id.name or '')

    @api.model
    def _cron_remind_pending(self):
        pending = self.search([('state','in',['draft','submitted'])])
        for a in pending:
            a.activity_schedule('mail.mail_activity_data_todo', summary=_('Assessment reminder'), note=_('Please complete your assessment.'), user_id=a.employee_id.user_id.id or self.env.user.id)

class ScsAssessmentLine(models.Model):
    _name = 'scs.assessment.line'
    _description = 'SCM Assessment Line'
    _order = 'competency_id'

    assessment_id = fields.Many2one('scs.assessment', required=True, ondelete='cascade')
    competency_id = fields.Many2one('scs.competency', required=True)

    required_level = fields.Selection(LEVEL_SELECTION, required=True)
    self_level = fields.Selection(LEVEL_SELECTION)
    manager_level = fields.Selection(LEVEL_SELECTION)
    final_level = fields.Selection(LEVEL_SELECTION)

    gap = fields.Char(compute='_compute_gap', store=True)
    gap_delta = fields.Integer(compute='_compute_gap', store=True)

    evidence = fields.Text()
    comment = fields.Text()

    @api.depends('required_level', 'final_level')
    def _compute_gap(self):
        for rec in self:
            rl = LEVEL_RANK.get(rec.required_level or '', 0)
            fl = LEVEL_RANK.get(rec.final_level or '', 0)
            delta = max(rl - fl, 0)
            rec.gap_delta = delta
            if rec.final_level:
                if delta <= 0:
                    rec.gap = _('Met')
                else:
                    rec.gap = _('%s level(s) short') % delta
            else:
                rec.gap = _('Not assessed')
