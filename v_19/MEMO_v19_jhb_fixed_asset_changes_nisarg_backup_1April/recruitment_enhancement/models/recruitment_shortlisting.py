from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RecruitmentShortlisting(models.Model):
    _name = 'recruitment.shortlisting'
    _description = 'Recruitment Shortlisting'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(default='New', copy=False)
    requisition_id = fields.Many2one('recruitment.requisition', required=True, tracking=True)
    job_id = fields.Many2one('hr.job', related='requisition_id.job_id', store=True)
    department_id = fields.Many2one('hr.department', related='requisition_id.department_id', store=True)
    company_id = fields.Many2one('res.company', related='requisition_id.company_id', store=True)

    meeting_datetime = fields.Datetime(required=True)
    venue = fields.Char(required=True)
    purpose = fields.Char()
    ee_compliance_notes = fields.Text()

    panel_line_ids = fields.One2many('recruitment.shortlisting.panel', 'shortlisting_id')
    candidate_line_ids = fields.One2many('recruitment.shortlisting.candidate', 'shortlisting_id')

    shortlisted_count = fields.Integer(compute='_compute_shortlisted_count')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True)

    @api.depends('candidate_line_ids.shortlisted')
    def _compute_shortlisted_count(self):
        for rec in self:
            rec.shortlisted_count = len(rec.candidate_line_ids.filtered('shortlisted'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('recruitment.shortlisting') or 'New'
        return super().create(vals_list)

    def action_start(self):
        for rec in self:
            if not rec.panel_line_ids:
                raise ValidationError(_('Add panel members before starting shortlisting.'))
            rec.state = 'in_progress'

    def action_done(self):
        for rec in self:
            if not rec.candidate_line_ids.filtered('shortlisted'):
                raise ValidationError(_('Select at least one shortlisted candidate before closing shortlisting.'))
            rec.state = 'done'

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_open_interview_sessions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Interview Sessions'),
            'res_model': 'recruitment.interview.session',
            'view_mode': 'list,form',
            'domain': [('shortlisting_id', '=', self.id)],
            'context': {
                'default_requisition_id': self.requisition_id.id,
                'default_shortlisting_id': self.id,
            },
        }


class RecruitmentShortlistingPanel(models.Model):
    _name = 'recruitment.shortlisting.panel'
    _description = 'Shortlisting Panel Register'
    _order = 'id'

    shortlisting_id = fields.Many2one('recruitment.shortlisting', required=True, ondelete='cascade')
    name = fields.Char(required=True)
    surname = fields.Char(required=True)
    department = fields.Char()
    contact_number = fields.Char()
    signature_name = fields.Char()


class RecruitmentShortlistingCandidate(models.Model):
    _name = 'recruitment.shortlisting.candidate'
    _description = 'Shortlisted Candidate'
    _order = 'score desc, id'

    shortlisting_id = fields.Many2one('recruitment.shortlisting', required=True, ondelete='cascade')
    applicant_id = fields.Many2one('hr.applicant', required=True)
    score = fields.Float(digits=(16, 2))
    shortlisted = fields.Boolean(default=False)
    notes = fields.Text()

    _sql_constraints = [
        ('shortlisting_candidate_unique', 'unique(shortlisting_id, applicant_id)', 'Candidate already exists in this shortlisting.'),
    ]
