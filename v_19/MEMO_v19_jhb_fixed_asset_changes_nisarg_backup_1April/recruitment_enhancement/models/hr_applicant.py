from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import timedelta
from markupsafe import Markup


class HrContractSalaryOffer(models.Model):
    _inherit = 'hr.contract.salary.offer'

    contract_type_id = fields.Many2one("hr.contract.type", string="Contract Type")



class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

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
    applicant_id = fields.Many2one('applicant.profile', string="Candidate")
    approved_by = fields.Many2one('res.users', string="Approved By", readonly=True)
    interview_count = fields.Integer(compute='_compute_interview_count', string="Interview Count")
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
    matching_score = fields.Integer(compute="_compute_matching_skill_ids",store=True)
    evaluation_line_ids = fields.One2many("interview.evaluation", "applicant_id", string="Evaluation")
    requisition_id = fields.Many2one('recruitment.requisition',string='Requisition')

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

    def action_view_interviews(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Interviews',
            'res_model': 'recruitment.interview',
            'view_mode': 'list,form',
            'domain': [('application_id', '=', self.id)],
            'context': {'default_application_id': self.id, 'default_job_id': self.job_id.id},
        }

    def approved_button(self):
        self.approved_by = self.env.user.id

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
                'view_mode': 'list,form',
                'domain': [('id', 'in', answer.ids)],
            })
        return action

    def _compute_background_check_count(self):
        grouped = self.env['recruitment.background.check']._read_group(
            [('applicant_id', 'in', self.ids)],
            ['applicant_id'],
            ['__count'],
        )
        count_map = {applicant.id: count for applicant, count in grouped}
        for applicant in self:
            applicant.background_check_count = count_map.get(applicant.id, 0)

    def action_view_background_checks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Background Checks',
            'res_model': 'recruitment.background.check',
            'view_mode': 'list,form',
            'domain': [('applicant_id', '=', self.id)],
            'context': {
                'default_applicant_id': self.id,
                'default_requisition_id': self.job_id.requisition_id.id,
            },
        }

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
        records = super().create(vals_list)

        qualified_stage = self.env['hr.recruitment.stage'].search(
            [('name', '=', 'Qualification')], limit=1
        )

        for rec in records:
            if not rec.missing_skill_ids and qualified_stage:
                if rec.stage_id.sequence < qualified_stage.sequence:
                    rec.with_context(skip_stage_update=True).write({'stage_id': qualified_stage.id })
        return records


    def write(self, vals):
        if self.env.context.get('skip_stage_update'):
            return super().write(vals)

        res = super().write(vals)

        qualified_stage = self.env['hr.recruitment.stage'].search(
            [('name', '=', 'Qualification')], limit=1
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

        template = self.env.ref('recruitment_enhancement.email_template_applicant_rejected',raise_if_not_found=False)
        if not template:
            return False
        try:
            for applicant in applicants:
                print('Processing applicant:', applicant)
                if template and applicant.email_from:
                    template.send_mail(applicant.id, force_send=True)

            applicant.stage_id = rejected_stage.id
        except Exception as e:
            return False


    def change_stage_to_qualify(self):
        qualified_stage = self.env['hr.recruitment.stage'].search(
            [('name', '=', 'Qualification')], limit=1
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
