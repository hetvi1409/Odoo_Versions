from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError
from markupsafe import Markup


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    employee_id = fields.Many2one('hr.employee', string="Employee", help="Employee linked to the applicant.", copy=False)
    candidate_pool = fields.Selection([
        ('internal', 'Internal COJ Employee'),
        ('external', 'External Candidate'),
    ], default='external', tracking=True)
    ee_category = fields.Selection([
        ('youth', 'Youth'),
        ('women', 'Women'),
        ('pwd', 'PWD'),
        ('other', 'Other'),
    ], tracking=True)
    applicant_id = fields.Many2one('applicant.profile', string="Candidate")
    declaration_conflict_of_interest = fields.Boolean()
    declaration_conflict_details = fields.Text()
    declaration_information_accurate = fields.Boolean()
    declaration_interview_fair = fields.Boolean()
    title_id = fields.Many2one('res.partner', string="Title")
    initial = fields.Char(string="Initial")
    surname = fields.Char(string="Surname")
    passport = fields.Char(string="ID / Passport / Visa Number", copy=False)
    country_id = fields.Many2one('res.country', string="Nationality",
                                 default=lambda self: self.env.ref(
                                     'base.za').id, ondelete='restrict')
    date_of_birth = fields.Date(string="Date of Birth")
    gender = fields.Selection(
        [('female', 'Female'), ('male', 'Male'), ('other', 'Other')],
        string="Gender")
    disability = fields.Selection([('yes', 'Yes'), ('no', 'No')])
    desc_disability = fields.Char(string="Description of Disability")
    cv = fields.Binary(string="Cv")
    race = fields.Selection([('african', 'African'), ('white', 'White'),
                             ('coloured', 'Coloured'), ('indian', 'Indian'),
                             ('other', 'Other')], string="Race")
    language_id = fields.Many2one('res.lang', string="Home Language")
    higher_qualification = fields.Selection(
        [('grade', 'Grade 11 & Lower'),
         ('national', 'National Certificate (NFQ Level 4)'),
         ('higher', 'Higher Certificate (NFQ Level 5)'),
         ('diploma', 'Diploma / Advanced Certificate (NFQ Level 6)'),
         ('bachelor', "Bachelor's Degree / Advanced Diploma (NFQ Level 7)"),
         ('honours',
          "Bachelor Honours Degree / Postgraduate Diploma / Bachelor's Degree (NFQ Level 8)"),
         ('master', "Master's Degree (NFQ Level 9)"),
         ('doctoral', 'Doctoral Degree (NFQ Level 10)'),
         ('other', 'Other')],
        string="Higher Qualification")
    terms_conditions = fields.Boolean(
        string="Do you agree to Terms and Conditions?")
    employee_status = fields.Selection(
        [('internal', 'Internal'), ('external', 'External')],
        string='Employee Status')
    motivation_description = fields.Html("Description")
    current_salary = fields.Char(string="Current Salary (Total cost to company)")
    relocate = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Willing to Relocate?")
    notice_period = fields.Selection(
        [('days', '30 Days'), ('month', '1 Calender Month'),
         ('immediate', 'Immediately'),
         ('other', 'Other')], string="Notice Period")
    access_token = fields.Char(string='Access Token', readonly=True)
    work_experience = fields.Selection([('1_5', '1-5 Years'),
                                        ('6_10', '6-10 Years'),
                                        ('11_15', '11-15 Years'),
                                        ('16_20', '16-20 Years'),
                                        ('21_25', '21-25 Years'),
                                        ('26_30', '26-30 Years'),
                                        ('30_above', '30-above')],
                                       string="Work Experience")
    last_role = fields.Text(string="Last/current role & Company with time period")
    exp_by_role = fields.Text(string='Number of years of experience in different roles/fields if any - Please specify')
    have_honours = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Do you have honours?')
    have_master = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Do you have Masters?')
    professional_body = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                         string='Are registered with any professional body?')
    cv_id = fields.Many2one('ir.attachment', string='CV')
    qualification_id = fields.Many2one('ir.attachment', string='Qualification')

    background_check_count = fields.Integer(compute='_compute_background_check_count')

    screening_point = fields.Float(string="Screening Point", compute="_compute_screening_point", store=True)
    pre_screening_state = fields.Selection([('new', 'Not started yet'),
                                            ('in_progress', 'In Progress'),
                                            ('done', 'Completed')],
                                           string='Pre-Screening Status',
                                           compute='_compute_pre_screening_state')
    user_role_id = fields.Many2one(
        'hr.employee', "Recruiter", compute='_compute_user',
        tracking=True, store=True, readonly=False)
    overall_performance = fields.Float(string="Overall Performance",
                                       compute="_compute_performance",
                                       store=True)
    performance_ids = fields.One2many('hr.performance', 'applicant_id',
                                      string="Performance")
    approved_by = fields.Many2one('res.users', string="Approved By", readonly=True)
    interview_count = fields.Integer(compute='_compute_interview_count', string="Interview Count")
    meeting_count = fields.Integer(compute='_compute_meeting_count', string="Meeting Count")
    is_contract_proposal_stage = fields.Boolean(
        compute='_compute_is_contract_proposal_stage',
        store=True
    )
    has_shortlisted_second_interview = fields.Boolean(
        string='Has Shortlisted Second Interview',
        compute='_compute_has_shortlisted_second_interview',
        store=False,
    )
    evaluation_ids = fields.One2many(
        "interview.evaluation",
        "applicant_id"
    )

    final_score = fields.Float(compute="_compute_final_score", store=True)
    final_recommendation = fields.Selection([
        ('hire', 'Hire'),
        ('reject', 'Reject'),
        ('hold', 'Hold')
    ])
    evaluation_line_ids = fields.One2many("interview.evaluation", "applicant_id", string="Evaluation")
    requisition_id = fields.Many2one('recruitment.requisition',string='Requisition')

    # missing in v_16
    applicant_skill_ids = fields.One2many(
        "hr.applicant.skill", "applicant_id", string="Skills", copy=True
    )
    current_applicant_skill_ids = fields.One2many(
        comodel_name="hr.applicant.skill",
        inverse_name="applicant_id",
        compute="_compute_current_applicant_skill_ids",
        readonly=False,
    )
    skill_ids = fields.Many2many("hr.skill", compute="_compute_skill_ids", store=True)
    matching_skill_ids = fields.Many2many(
        comodel_name="hr.skill",
        string="Matching Skills",
        compute="_compute_matching_skill_ids",
    )
    missing_skill_ids = fields.Many2many(
        comodel_name="hr.skill",
        string="Missing Skills",
        compute="_compute_matching_skill_ids",
    )
    matching_score = fields.Integer(string="Matching Score", compute="_compute_matching_skill_ids",store=True)

    @api.depends("applicant_skill_ids")
    def _compute_current_applicant_skill_ids(self):
        current_applicant_skill_by_applicant = self.applicant_skill_ids._get_current_skills_by_applicant()
        for applicant in self:
            applicant.current_applicant_skill_ids = current_applicant_skill_by_applicant[applicant.id]

    @api.depends_context("matching_job_id")
    @api.depends("current_applicant_skill_ids", "type_id", "job_id", "job_id.job_skill_ids", "job_id.expected_degree")
    def _compute_matching_skill_ids(self):
        matching_job_id = self.env.context.get("matching_job_id")
        job_id = self.job_id
        matching_job = self.env["hr.job"].browse(matching_job_id)
        for applicant in self:
            job = matching_job or applicant.job_id
            if not job or not (job.job_skill_ids or job.expected_degree):
                applicant.matching_skill_ids = False
                applicant.missing_skill_ids = False
                applicant.matching_score = False
                continue
            job_skills = job.job_skill_ids
            job_degree = job.expected_degree.sudo().score * 100
            job_total = sum(job_skills.mapped("level_progress")) + job_degree
            job_skill_map = {js.skill_id: js.level_progress for js in job_skills}

            matching_applicant_skills = applicant.current_applicant_skill_ids.filtered(
                lambda a: a.skill_id in job_skill_map,
            )
            applicant_degree = applicant.type_id.score * 100 if job_degree > 1 else 0
            applicant_total = (
                sum(min(skill.level_progress, job_skill_map[skill.skill_id] * 2) for skill in matching_applicant_skills)
                + applicant_degree
            )

            matching_skill_ids = matching_applicant_skills.mapped("skill_id")
            missing_skill_ids = job_skills.mapped("skill_id") - matching_applicant_skills.mapped("skill_id")
            matching_score = round(applicant_total / job_total * 100) if job_total else 0

            applicant.matching_skill_ids = matching_skill_ids
            applicant.missing_skill_ids = missing_skill_ids
            applicant.matching_score = matching_score

    def _compute_final_score(self):
        for rec in self:
            if rec.evaluation_ids:
                rec.final_score = sum(rec.evaluation_ids.mapped("total_score")) / len(rec.evaluation_ids)

    def _compute_has_shortlisted_second_interview(self):
        for rec in self:
            rec.has_shortlisted_second_interview = self.env['recruitment.interview'].search_count([
                ('application_id', '=', rec.id),
                ('is_second_interview', '=', True),
                ('state', '=', 'shortlisted'),
            ]) > 0

    @api.depends('stage_id')
    def _compute_is_contract_proposal_stage(self):
        contract_stage = self.env['hr.recruitment.stage'].search([
            ('name', 'ilike', 'Contract Proposal')
        ], limit=1)
        for rec in self:
            rec.is_contract_proposal_stage = (
                rec.stage_id.id == contract_stage.id if contract_stage else False
            )

    def _compute_interview_count(self):
        for rec in self:
            rec.interview_count = self.env['recruitment.interview'].search_count([('application_id', '=', rec.id)])

    def _get_meeting_domain(self):
        self.ensure_one()
        if 'calendar.event' not in self.env:
            return [('id', '=', 0)]
        if 'applicant_id' in self.env['calendar.event']._fields:
            return [('applicant_id', '=', self.id)]
        if self.partner_id:
            return [('partner_ids', 'in', self.partner_id.id)]
        return [('id', '=', 0)]

    def _compute_meeting_count(self):
        if 'calendar.event' not in self.env:
            for rec in self:
                rec.meeting_count = 0
            return
        calendar_event = self.env['calendar.event']
        for rec in self:
            rec.meeting_count = calendar_event.search_count(rec._get_meeting_domain())

    def action_view_interviews(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Interviews',
            'res_model': 'recruitment.interview',
            'view_mode': 'tree,form,calendar',
            'domain': [('application_id', '=', self.id)],
            'context': {'default_application_id': self.id, 'default_job_id': self.job_id.id},
        }

    def action_view_meetings(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('calendar.action_calendar_event')
        action_context = dict(self.env.context or {})
        partner_ids = []
        if self.partner_id:
            partner_ids.append(self.partner_id.id)
        if self.user_id and self.user_id.partner_id:
            partner_ids.append(self.user_id.partner_id.id)

        action_context.update({
            'default_partner_ids': partner_ids,
        })
        if 'calendar.event' in self.env and 'applicant_id' in self.env['calendar.event']._fields:
            action_context.update({
                'default_applicant_id': self.id,
                'search_default_applicant_id': self.id,
            })

        action.update({
            'name': _('Meetings'),
            'domain': self._get_meeting_domain(),
            'context': action_context,
        })
        return action

    def action_makeMeeting(self):
        self.ensure_one()
        action = super().action_makeMeeting()
        if isinstance(action, dict):
            action_context = dict(action.get('context', {}))
            partner_ids = action_context.get('default_partner_ids') or []
            if self.partner_id and self.partner_id.id not in partner_ids:
                partner_ids.append(self.partner_id.id)
            action_context.update({
                'default_applicant_id': self.id,
                'default_partner_ids': partner_ids,
            })
            action['context'] = action_context
        return action

    def approved_button(self):
        self.approved_by = self.env.user.id

    def move_attachments_to_fields(self):
        applicants = self.search([])
        for applicant in applicants:
            attachments = self.env['ir.attachment'].search(
                [('res_model', '=', 'hr.applicant'),
                 ('res_id', '=', applicant.id)], order="id asc")
            if attachments:
                applicant.cv_id = attachments[0].id
                applicant.cv_id.public = True
                if len(attachments) > 1:
                    applicant.qualification_id = attachments[1].id
                    applicant.qualification_id.public = True
        return True

    @api.depends('performance_ids')
    def _compute_performance(self):
        for rec in self:
            overall_performance = 0
            if rec.performance_ids:
                percentage = sum(rec.performance_ids.mapped('percentage'))
                length = len(rec.performance_ids.ids)
                overall_performance = percentage / length if length > 0 else 1
            rec.overall_performance = overall_performance

    @api.depends('job_id')
    def _compute_user(self):
        for applicant in self:
            applicant.user_id = applicant.job_id.user_id.id
            applicant.user_role_id = applicant.job_id.user_role_id.id

    @api.model
    @api.depends()
    def _compute_pre_screening_state(self):
        """Compute the pre screening state"""
        for rec in self:
            pre_screening = rec.env['survey.user_input'].search(
                [('application_id', '=', rec.id)])
            if rec.job_id and rec.job_id.requisition_id.need_prescreening:
                if len(pre_screening) == 1:
                    rec.pre_screening_state = pre_screening.state
                elif len(pre_screening) > 1:
                    rec.pre_screening_state = 'done' if 'done' in pre_screening.mapped(
                        'state') else 'new'
                else:
                    rec.pre_screening_state = 'new'
            else:
                rec.pre_screening_state = ''

    @api.depends('job_id', 'job_id.requisition_id.survey_id', 'job_id.requisition_id.survey_id.user_input_ids')
    def _compute_screening_point(self):
        for record in self:
            record.calculate_screening_point()

    def calculate_screening_point(self):
        for record in self:
            screening_point = 0
            survey = record.job_id.requisition_id.survey_id if record.job_id and record.job_id.requisition_id else False
            record.screening_point = screening_point
            if survey:
                answer = self.env['survey.user_input'].sudo().search([
                    ('survey_id', '=', survey.id),
                    ('application_id', '=', record.id)
                ], limit=1)

                if not answer:
                    record.screening_point = 0
                    continue

                answer.email = record.email_from
                answered_score = sum(answer.mapped('scoring_total'))
                total_score = survey.total_score or 0
                if total_score > 0:
                    screening_point = (answered_score / total_score) * 100

                record.screening_point = screening_point

                elimination_questions = answer.mapped(
                    'user_input_line_ids.question_id'
                ).filtered(lambda q: getattr(q, 'elimination_question', False))

                answered_lines = answer.mapped('user_input_line_ids').filtered(
                    lambda line: line.question_id in elimination_questions
                )

                all_answered = len(answered_lines) == len(elimination_questions)
                all_correct = all(answered_lines.mapped('answer_is_correct')) if all_answered else False
                if elimination_questions:
                    if all_answered and all_correct:
                        record.stage_id = self.env.ref('hr_recruitment.stage_job0').id
                    else:
                        record.stage_id = self.env.ref('recruitment_enhancement.stage_job7').id

    def action_open_pre_screening_answer(self):
        """Open a pre-screening answer"""
        self.ensure_one()
        survey = self.job_id and self.job_id.requisition_id and self.job_id.requisition_id.survey_id
        if not survey:
            return
        answer = self.env['survey.user_input'].sudo().search([
            ('survey_id', '=', survey.id), ('application_id', '=', self.id)], limit=1)
        action = {
            'name': _('Pre-Screening Answer'),
            'type': 'ir.actions.act_window',
            'res_model': 'survey.user_input',
            'context': {'create': False},
        }
        if len(answer) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': answer.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', answer.ids)],
            })
        return action

    def action_open_candidates(self):
        """Open a list of candidates"""
        return True

    def _compute_background_check_count(self):
        grouped = self.env['recruitment.background.check']._read_group(
            [('applicant_id', 'in', self.ids)],
            ['applicant_id'],
            ['applicant_id'],
        )
        count_map = {data['applicant_id'][0]: data['applicant_id_count'] for data in grouped}
        for applicant in self:
            applicant.background_check_count = count_map.get(applicant.id, 0)

    def action_view_background_checks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Background Checks',
            'res_model': 'recruitment.background.check',
            'view_mode': 'tree,form',
            'domain': [('applicant_id', '=', self.id)],
            'context': {
                'default_applicant_id': self.id,
                'default_requisition_id': self.job_id.requisition_id.id,
            },
        }

    def send_manager(self):
        """Send a manager to review the applications"""
        mail_template = self.env.ref(
            'recruitment_enhancement.email_template_send_to_applicant',
            raise_if_not_found=False,
        )
        if not mail_template:
            return False

        recipient_ids = self.env.ref(
            'hr_recruitment.group_hr_recruitment_manager').users
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        return True

    def action_add_performance(self):
        """Add a performance"""
        return {
            'name': _('Performance'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.performance',
            'target': 'new',
            'context': {
                'default_applicant_id': self.id
            }
        }

    @api.model_create_multi
    def create(self, vals_list):
        # CODE ADDED BY KRUPA: showing error
        # for vals in vals_list:
        #     if vals.get('application_sequence', 'New') == 'New':
        #         vals['application_sequence'] = self.env['ir.sequence'].next_by_code('hr.applicant')

        records = super().create(vals_list)

        qualified_stage = self.env['hr.recruitment.stage'].search(
            [('name', 'ilike', 'Initial Qualification')], order='sequence asc', limit=1
        )

        for rec in records:
            if not rec.requisition_id:
                rec.requisition_id = rec.job_id.requisition_id
            if not rec.missing_skill_ids and qualified_stage:
                if rec.stage_id.sequence < qualified_stage.sequence:
                    rec.with_context(skip_stage_update=True).write({'stage_id': qualified_stage.id})
        return records

    def write(self, vals):
        if self.env.context.get('skip_stage_update'):
            return super().write(vals)

        res = super().write(vals)

        qualified_stage = self.env['hr.recruitment.stage'].search(
            [('name', 'ilike', 'Initial Qualification')], order='sequence asc', limit=1
        )

        for rec in self:
            if not rec.missing_skill_ids and qualified_stage:
                if 'stage_id' in vals:
                    continue

                if rec.stage_id.sequence < qualified_stage.sequence:
                    rec.with_context(skip_stage_update=True).write({'stage_id': qualified_stage.id})

            if self.employee_id:
                if self.requisition_id:
                    self.requisition_id.sudo().action_done()
                    self.requisition_id.sudo().write({
                        'hired_employee': self.employee_id.id,
                        'hired_date': fields.Datetime.now()
                    })

            if not self.employee_id:
                if self.requisition_id:
                    self.requisition_id.sudo().write({
                        'state': 'recruitment_in_process',
                        'hired_employee': False,
                        'hired_date': False
                    })

        return res

    @api.constrains('stage_id')
    def _check_evaluation_lines(self):
        contract_signed_stage = self.env['hr.recruitment.stage'].search(
            [('name', 'ilike', 'Contract Signed')], limit=1
        )
        if not contract_signed_stage:
            return
        for rec in self:
            if rec.stage_id != contract_signed_stage:
                continue

            if not rec.evaluation_line_ids:
                raise ValidationError(_(
                    "You cannot move to Contract Signed stage without adding evaluation lines. "
                    "Please add at least one evaluation before proceeding."
                ))

    def action_view_job_offer_letter(self):
        self.ensure_one()
        return self.env.ref('recruitment_enhancement.action_report_offer_letter').report_action(self)

    def action_send_interview_letter(self):
        self.ensure_one()
        return {
            'name': 'Send Interview Letter',
            'type': 'ir.actions.act_window',
            'res_model': 'applicant.interview.letter.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_subject': ' Interview Letter {}'.format(self.job_id.name),
                'default_body_html': self._get_default_interview_letter_body(),
                'default_applicant_id': self.id,
            },
        }

    def send_offer_letter(self):
        """Send offer letter email to applicant"""
        self.ensure_one()

        template = self.env.ref('recruitment_enhancement.email_template_offer_letter', raise_if_not_found=False)
        if not template:
            return False

        try:
            template.send_mail(self.id, force_send=True)
            return True
        except Exception as e:
            return False

    def _get_default_interview_letter_body(self):
        date = datetime.today().strftime('%d %B %Y, %A')
        time = datetime.now().strftime('%I:%M %p')
        company = self.env.user.company_id
        street = company.street or ''
        city = company.city or ''
        state = company.state_id.name or ''
        zip_code = company.zip or ''
        country = company.country_id.name or ''
        full_address = f"{street}, {city}, {state} {zip_code}, {country}"
        return '''
        <p>Good day Mr/Mrs %s </p>
        <p>This mail serves to invite you to the interview for the position of <strong>%s</strong> at %s and the details are as follows:</p>
        <p>Date: %s</p>
        <p>Time: %s</p>
        <p>Venue Address: %s</p>
        <p>Kindly confirm your availability by not later than the %s.</p>
        <p>Regards,</p>
        <p>%s</p>
        <p>%s</p>
        ''' % (
            self.partner_name, self.job_id.name, getattr(self.job_id, 'job_location_id', False) and self.job_id.job_location_id.name or '',
            date, time, full_address, date, self.env.user.partner_id.name,
            self.env.user.partner_id.email)

    def cron_reject_old_applicants(self):
        date_limit = fields.Datetime.now() - timedelta(days=7)

        rejected_stage = self.env['hr.recruitment.stage'].search([
            ('name', '=', 'Rejected')
        ], limit=1)

        if not rejected_stage:
            return

        applicants = self.search([
            ('create_date', '<=', date_limit),
            ('stage_id', '!=', rejected_stage.id),
        ])

        template = self.env.ref('recruitment_enhancement.email_template_applicant_rejected', raise_if_not_found=False)
        if not template:
            return False
        try:
            for applicant in applicants:
                if template and applicant.email_from:
                    template.send_mail(applicant.id, force_send=True)

            applicant.stage_id = rejected_stage.id
        except Exception as e:
            return False

    def change_stage_to_qualify(self):
        qualified_stage = self.env['hr.recruitment.stage'].search(
            [('name', 'ilike', 'Initial Qualification')], order='sequence asc', limit=1
        )

        for rec in self:
            # if rec.stage_id.sequence < qualified_stage.sequence:
            rec.write({
                'stage_id': qualified_stage.id
            })

    is_offer_stage = fields.Boolean(compute='_compute_is_offer_stage')

    def _compute_is_offer_stage(self):
        offer_stage = self.env.ref('hr_recruitment.stage_job5', raise_if_not_found=False)
        if self.stage_id == offer_stage:
            self.is_offer_stage = True
        else:
            self.is_offer_stage = False

    def action_generate_urls(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.cv_id and record.cv_id.local_url:
                record.cv_url = f"{base_url}{record.cv_id.local_url}"
            else:
                record.cv_url = False
            if record.qualification_id and record.qualification_id.local_url:
                record.qualification_url = f"{base_url}{record.qualification_id.local_url}"
            else:
                record.qualification_url = False

    @api.depends('cv_id', 'qualification_id')
    def _compute_urls(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.cv_id and record.cv_id.local_url:
                record.cv_url = f"{base_url}{record.cv_id.local_url}"
            else:
                record.cv_url = False
            if record.qualification_id and record.qualification_id.local_url:
                record.qualification_url = f"{base_url}{record.qualification_id.local_url}"
            else:
                record.qualification_url = False

    @api.depends_context('active_id')
    @api.depends('skill_ids')
    def compute_skill_details(self):
        job_id = self.job_id
        if not job_id:
            self.matching_skill_ids = False
            self.missing_skill_ids = False
        else:
            for candidate in self:
                skill = job_id.skill_ids
                candidate.matching_skill_ids = skill & candidate.skill_ids
                candidate.missing_skill_ids = skill - candidate.skill_ids


class HrPerformance(models.Model):
    _name = 'hr.performance'
    _description = "Hr Performance"

    applicant_id = fields.Many2one('hr.applicant', string="Applicant")
    skill_type_id = fields.Many2one('hr.skill.type',
                                    default=lambda self: self.env[
                                        'hr.skill.type'].search([], limit=1),
                                    required=True, ondelete='cascade')
    skill_id = fields.Many2one('hr.skill',
                               store=True,
                               domain="[('skill_type_id', '=', skill_type_id)]",
                               readonly=False, required=True,
                               ondelete='cascade')
    description = fields.Char(string="Description", required=True)
    percentage = fields.Float(string="Performance", required=True)

    @api.constrains('percentage')
    def constrains_percentage(self):
        """Constrains functionality used to indicate or raise an
        UserError when we adding Percentage """
        if self.percentage > 100:
            raise ValidationError(_(
                "The performance must be less that or equal to 100"))
