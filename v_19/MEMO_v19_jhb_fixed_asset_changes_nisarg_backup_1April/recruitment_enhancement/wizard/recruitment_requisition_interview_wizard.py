from odoo import models, fields, _
from odoo.exceptions import ValidationError, AccessError
from odoo import api


class RecruitmentRequisitionInterviewWizard(models.TransientModel):
    _name = 'recruitment.requisition.interview.wizard'
    _description = 'Recruitment Requisition Interview Wizard'

    application_id = fields.Many2one(
        'hr.applicant',
        string='Application',
        required=True,
    )
    job_id = fields.Many2one(
        'hr.job',
        string='Job Position',
        required=True,
    )

    # People
    interviewer_ids = fields.Many2many(
        'res.users',
        string='Panellists',
        required=True,
    )
    recruiter_id = fields.Many2one(
        'res.users',
        string='Recruiter',
        required=True,
    )
    recruiter_phone = fields.Char(
        string='Recruiter Phone',
        related='recruiter_id.partner_id.phone',
        readonly=False,
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
    )
    interview_time = fields.Datetime(
        string='Time',
        required=True,
    )
    duration = fields.Float(
        string='Duration (Hours)',
        digits=(16, 2),
        default=1.0,
        help='Duration of the interview in hours',
    )

    # HR Note
    hr_note = fields.Html(
        string='HR Note',
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Attachments',
        readonly=False,
    )

    current_applicant_skill_ids = fields.One2many(
        related='application_id.applicant_skill_ids',
        readonly=False,
    )
    is_pool_applicant = fields.Boolean(
        related='application_id.is_pool_applicant',
        readonly=True,
    )
    matching_score = fields.Integer(
        related='application_id.matching_score',
        readonly=True,
    )

    # Questions (from pre-screening survey)
    question_and_page_ids = fields.Many2many(
        'survey.question',
        string='Questions',
        compute='_compute_prescreening_questions',
    )
    is_second_interview = fields.Boolean(
        string='Is Second Interview', default=False,
    )
    # ee_representative = fields.Many2one('res.users', string="EE Representative")
    # panelist_representative = fields.Many2one('res.users', string="Panelist Representative")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')

        # ── Opened from hr.applicant (original flow) ────────────────
        if active_model == 'hr.applicant' and active_id:
            applicant = self.env['hr.applicant'].browse(active_id)
            res['application_id'] = applicant.id
            if applicant.job_id:
                res['job_id'] = applicant.job_id.id
                res['interviewer_ids'] = [(6, 0, applicant.job_id.interviewer_ids.ids)]
            res['recruiter_id'] = (
                    applicant.user_id.id
                    or (applicant.job_id.user_id.id if applicant.job_id else False)
            )

        # ── Opened from recruitment.interview ("Second Interview" btn) ─
        elif active_model == 'recruitment.interview' and active_id:
            interview = self.env['recruitment.interview'].browse(active_id)
            res['application_id'] = interview.application_id.id
            res['job_id'] = interview.job_id.id
            res['recruiter_id'] = interview.recruiter_id.id
            res['interviewer_ids'] = [(6, 0, interview.interviewer_ids.ids)]
            res['interview_type'] = interview.interview_type
            res['is_second_interview'] = True  # ← flag it as second

        return res

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


    @api.onchange('application_id')
    def _onchange_application_id(self):
        if self.application_id:
            self.job_id = self.application_id.job_id
            self.recruiter_id = self.application_id.user_id

    def action_create_interview(self):
        self.ensure_one()

        if self.is_second_interview:
            # ── Move applicant to Second Interview stage ─────────────
            target_stage = self.env['hr.recruitment.stage'].search(
                [('name', 'ilike', 'Second Interview')], limit=1,
            )
            if not target_stage:
                raise ValidationError(_(
                    'No stage named "Second Interview" found. '
                    'Please create it under Recruitment ▸ Configuration ▸ Stages.'
                ))
        else:
            # ── Move applicant to First Interview stage ──────────────
            target_stage = self.env['hr.recruitment.stage'].search(
                [('name', 'ilike', 'First Interview')], limit=1,
            ) or self.env['hr.recruitment.stage'].search([], order='sequence asc', limit=1)

        if target_stage:
            self.application_id.write({'stage_id': target_stage.id})

        # Create interview record (email is sent inside create())
        interview_record = self.env['recruitment.interview'].create({
            'application_id': self.application_id.id,
            'job_id': self.job_id.id,
            'interviewer_ids': [(6, 0, self.interviewer_ids.ids)],
            # 'ee_representative':self.ee_representative.id,
            # 'panelist_representative':self.panelist_representative.id,
            'recruiter_id': self.recruiter_id.id,
            'interview_type': self.interview_type,
            'interview_time': self.interview_time,
            'duration': self.duration,
            'hr_note': self.hr_note,
            'attachment_ids': [(6, 0, self.attachment_ids.ids)],
            'is_second_interview': self.is_second_interview,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'recruitment.interview',
            'res_id': interview_record.id,
            'view_mode': 'form',
            'target': 'current',
        }