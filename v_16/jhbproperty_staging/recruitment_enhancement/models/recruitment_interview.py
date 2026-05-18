from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from markupsafe import Markup


class RecruitmentInterviewSession(models.Model):
    _name = 'recruitment.interview.session'
    _description = 'Recruitment Interview Session'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(default='New', copy=False)
    requisition_id = fields.Many2one('recruitment.requisition', required=True)
    shortlisting_id = fields.Many2one('recruitment.shortlisting')
    job_id = fields.Many2one('hr.job', related='requisition_id.job_id', store=True)

    interview_datetime = fields.Datetime(required=True)
    venue = fields.Char(required=True)

    panel_line_ids = fields.One2many('recruitment.interview.panel', 'session_id')
    candidate_line_ids = fields.One2many('recruitment.interview.candidate', 'session_id')

    recommendation_applicant_id = fields.Many2one('hr.applicant', domain="[('job_id', '=', job_id)]")
    reserve_applicant_ids = fields.Many2many('hr.applicant', string='Reserve Candidates')
    recommendation_note = fields.Text()

    state = fields.Selection([
        ('draft', 'Draft'),
        ('prepared', 'Prepared'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('recruitment.interview.session') or 'New'
        sessions = super().create(vals_list)
        for session in sessions.filtered('shortlisting_id'):
            for line in session.shortlisting_id.candidate_line_ids.filtered('shortlisted'):
                self.env['recruitment.interview.candidate'].create({
                    'session_id': session.id,
                    'applicant_id': line.applicant_id.id,
                })
        return sessions

    def action_prepare(self):
        for rec in self:
            unsigned = rec.panel_line_ids.filtered(lambda l: not l.confidentiality_signed)
            if unsigned:
                raise ValidationError(_('All panel members must sign confidentiality declarations before preparation.'))
            rec.state = 'prepared'

    def action_start(self):
        for rec in self:
            if not rec.candidate_line_ids:
                raise ValidationError(_('Add candidate interview attendance lines before starting interviews.'))
            rec.state = 'in_progress'

    def action_done(self):
        for rec in self:
            if not rec.recommendation_applicant_id:
                raise ValidationError(_('Set the recommended candidate before finalizing interviews.'))
            rec.state = 'done'

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_create_background_checks(self):
        self.ensure_one()
        if not self.recommendation_applicant_id:
            raise ValidationError(_('Select a recommended candidate first.'))

        check_types = ['credit', 'cv', 'employment', 'criminal', 'identity']
        existing = self.env['recruitment.background.check'].search([
            ('requisition_id', '=', self.requisition_id.id),
            ('applicant_id', '=', self.recommendation_applicant_id.id),
        ])
        existing_types = set(existing.mapped('check_type'))

        for check_type in check_types:
            if check_type not in existing_types:
                self.env['recruitment.background.check'].create({
                    'requisition_id': self.requisition_id.id,
                    'interview_session_id': self.id,
                    'applicant_id': self.recommendation_applicant_id.id,
                    'check_type': check_type,
                })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Background Checks'),
            'res_model': 'recruitment.background.check',
            'view_mode': 'tree,form',
            'domain': [
                ('requisition_id', '=', self.requisition_id.id),
                ('applicant_id', '=', self.recommendation_applicant_id.id),
            ],
        }


class RecruitmentInterviewPanel(models.Model):
    _name = 'recruitment.interview.panel'
    _description = 'Interview Panel Member'
    _order = 'id'

    session_id = fields.Many2one('recruitment.interview.session', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', required=True)
    role = fields.Selection([
        ('chairperson', 'Chairperson'),
        ('panelist', 'Panelist'),
        ('secretariat', 'Secretariat'),
        ('ee_observer', 'EE Observer'),
        ('union_observer', 'Union Observer'),
    ], default='panelist', required=True)

    confidentiality_signed = fields.Boolean()
    no_personal_interest = fields.Boolean()
    no_relationship = fields.Boolean()
    no_conflict_of_interest = fields.Boolean()
    signature_name = fields.Char()
    signed_on = fields.Date()


class RecruitmentInterviewCandidate(models.Model):
    _name = 'recruitment.interview.candidate'
    _description = 'Interview Candidate Attendance & Score'
    _order = 'total_score desc, id'

    session_id = fields.Many2one('recruitment.interview.session', required=True, ondelete='cascade')
    applicant_id = fields.Many2one('hr.applicant', required=True)

    attended = fields.Boolean(default=True)
    arrival_datetime = fields.Datetime()

    score_technical = fields.Float(digits=(16, 2))
    score_competency = fields.Float(digits=(16, 2))
    score_culture = fields.Float(digits=(16, 2))
    total_score = fields.Float(compute='_compute_total_score', store=True)

    declaration_information_accurate = fields.Boolean()
    declaration_role_impact = fields.Text()
    declaration_conflict_of_interest = fields.Boolean()
    conflict_details = fields.Text()
    availability_to_join = fields.Date()
    declaration_interview_fair = fields.Boolean()
    candidate_signed = fields.Boolean()

    notes = fields.Text()

    @api.depends('score_technical', 'score_competency', 'score_culture')
    def _compute_total_score(self):
        for rec in self:
            rec.total_score = (rec.score_technical or 0.0) + (rec.score_competency or 0.0) + (rec.score_culture or 0.0)

    _sql_constraints = [
        ('interview_candidate_unique', 'unique(session_id, applicant_id)',
         'Candidate already exists in this interview session.'),
    ]


class RecruitmentInterview(models.Model):
    _name = 'recruitment.interview'
    _description = 'Recruitment Interview'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    meeting_event_id = fields.Many2one('calendar.event', string='Meeting', copy=False, readonly=True)

    name = fields.Char(string='Reference', compute='_compute_name', store=True)

    application_id = fields.Many2one(
        'hr.applicant',
        string='Application',
        required=True,
        tracking=True
    )
    job_id = fields.Many2one(
        'hr.job',
        string='Job Position',
        required=True,
        tracking=True
    )

    # People
    interviewer_ids = fields.Many2many(
        'res.users',
        string='Panelists',
        required=True,
        tracking=True
    )
    recruiter_id = fields.Many2one(
        'res.users',
        string='Recruiter',
        required=True,
        tracking=True
    )
    recruiter_phone = fields.Char(
        string='Recruiter Phone',
        related='recruiter_id.partner_id.phone',
        readonly=False,
        store=False,
    )

    # Interview Details
    interview_type = fields.Selection(
        selection=[
            ('offline', 'Onsite'),
            ('online', 'Online'),
        ],
        string='Interview Type',
        required=True,
        default='offline',
        tracking=True
    )
    interview_time = fields.Datetime(
        string='Time',
        required=True,
        tracking=True
    )
    duration = fields.Float(
        string='Duration (Hours)',
        digits=(16, 2),
        default=1.0,
        help='Duration of the interview in hours',
        tracking=True
    )

    # HR Note
    hr_note = fields.Html(
        string='HR Note',
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Attachments',
        readonly=False,
        store=True,
    )

    current_applicant_skill_ids = fields.One2many(
        related='application_id.applicant_skill_ids',
        readonly=False,
    )
    is_pool_applicant = fields.Boolean(
        string="Is Pool Applicant",
        compute="_compute_is_pool_applicant",
        store=False,
        readonly=True,
    )
    # matching_score = fields.Integer(
    #     related='application_id.matching_score',
    #     readonly=True,
    #     store = True
    # )

    # Questions (from pre-screening survey)
    question_and_page_ids = fields.Many2many(
        'survey.question',
        string='Questions',
        compute='_compute_prescreening_questions',
        store=False,
    )

    state = fields.Selection(
        selection=[
            ('scheduled', 'Scheduled'),
            ('shortlisted', 'Selected'),
            ('rejected', 'Rejected'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        default='scheduled',
        tracking=True,
    )
    is_second_interview = fields.Boolean(
        string='Is Second Interview',
        default=False,
    )
    interview_email_sent = fields.Boolean(
        string='Interview Email Sent',
        default=False,
        copy=False,
    )
    # ee_representative = fields.Many2one('res.users',string="EE Representative")
    # panelist_representative = fields.Many2one('res.users',string="Panelist Representative")

    @api.depends('application_id', 'interview_time')
    def _compute_name(self):
        for rec in self:
            if rec.application_id and rec.interview_time:
                rec.name = "Interview: %s" % (rec.application_id.partner_name or rec.application_id.name)
            else:
                rec.name = "New Interview"

    @api.depends('application_id')
    def _compute_is_pool_applicant(self):
        """An applicant is considered a 'pool applicant' when it is linked to an applicant.profile."""
        for rec in self:
            rec.is_pool_applicant = bool(rec.application_id.applicant_id)

    @api.depends('application_id')
    def _compute_prescreening_questions(self):
        for rec in self:
            survey = rec.application_id.job_id.requisition_id.survey_id
            if survey:
                rec.question_and_page_ids = survey.question_and_page_ids.filtered(
                    lambda q: q.question_type != 'page'
                )
            else:
                rec.question_and_page_ids = False

    def write(self, vals):
        res = super().write(vals)
        if vals.get('state') == 'shortlisted':
            for rec in self:
                if rec.application_id:
                    contract_stage = self.env['hr.recruitment.stage'].search([
                        ('name', 'ilike', 'Contract Proposal')
                    ], limit=1)
                    if contract_stage:
                        rec.application_id.stage_id = contract_stage.id
                    rec._send_shortlist_survey_email()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec._create_interview_meeting()
            rec._send_interview_created_email()
        return records

    def _create_interview_meeting(self):
        self.ensure_one()
        if 'calendar.event' not in self.env:
            return False
        if self.meeting_event_id or not self.interview_time:
            return False

        start_dt = fields.Datetime.to_datetime(self.interview_time)
        duration_hours = self.duration or 1.0
        stop_dt = start_dt + timedelta(hours=duration_hours)

        partner_ids = (self.interviewer_ids | self.recruiter_id).mapped('partner_id')
        if self.application_id.partner_id:
            partner_ids |= self.application_id.partner_id

        calendar_model = self.env['calendar.event']
        meeting_vals = {
            'name': self.name or _('Interview'),
            'start': fields.Datetime.to_string(start_dt),
            'stop': fields.Datetime.to_string(stop_dt),
            'duration': duration_hours,
            'partner_ids': [(6, 0, partner_ids.ids)],
            'description': self.hr_note or False,
        }
        if 'applicant_id' in calendar_model._fields:
            meeting_vals['applicant_id'] = self.application_id.id

        event = calendar_model.create(meeting_vals)
        self.meeting_event_id = event.id
        return event

    def _send_interview_created_email(self):
        template = self.env.ref(
            'recruitment_enhancement.email_template_interview_created_id',
            raise_if_not_found=False
        )
        if not template:
            return False

        try:
            if self.application_id and (
                self.application_id.partner_id.email or self.application_id.email_from
            ):
                template.send_mail(self.id, force_send=False)
                self.interview_email_sent = True
        except Exception:
            return False

    def action_send_interview_survey(self):
        self.ensure_one()
        self._send_interview_created_email()

    def write(self, vals):
        res = super().write(vals)
        if vals.get('state') == 'shortlisted':
            for rec in self:
                if rec.application_id:
                    contract_stage = self.env['hr.recruitment.stage'].search(
                        [('name', 'ilike', 'Contract Proposal')], limit=1,
                    )
                    if contract_stage:
                        rec.application_id.stage_id = contract_stage.id
                    rec._send_shortlist_survey_email()
        return res

    def _send_shortlist_survey_email(self):
        template = self.env.ref(
            'recruitment_enhancement.email_template_shortlist_interviewer',
            raise_if_not_found=False
        )
        if not template:
            return False

        try:
            if self.application_id and (
                self.application_id.partner_id.email or self.application_id.email_from
            ):
                template.send_mail(self.id, force_send=False)
                self.interview_email_sent = True
        except Exception:
            return False
