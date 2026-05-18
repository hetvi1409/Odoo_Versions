# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from itertools import count

from werkzeug import urls

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    performance_ids = fields.One2many('hr.performance', 'applicant_id',
                                      string="Performance")
    overall_performance = fields.Float(string="Overall Performance",
                                       compute="_compute_performance",
                                       store=True)
    title_id = fields.Many2one('res.partner.title', string="Title")
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
    applicant_id = fields.Many2one('applicant.profile', string="Candidate")
    matching_skill_ids = fields.Many2many(comodel_name='hr.skill',
                                          string="Matching Skills",
                                          compute="compute_skill_details")
    missing_skill_ids = fields.Many2many(comodel_name='hr.skill',
                                         string="Missing Skills",
                                         compute="compute_skill_details")
    screening_point = fields.Float(string="Screening Point")
    current_salary = fields.Char(
        string="Current Salary (Total cost to company)")
    relocate = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                string="Willing to Relocate?")
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
    last_role = fields.Text(
        string="Last/current role & Company with time period")
    exp_by_role = fields.Text(
        string='Number of years of experience in different roles/fields if any - Please specify')
    have_honours = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                    string='Do you have honours?')
    have_master = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                   string='Do you have Masters?')
    professional_body = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                         string='Are registered with any professional body?')
    pre_screening_state = fields.Selection([('new', 'Not started yet'),
                                            ('in_progress', 'In Progress'),
                                            ('done', 'Completed')],
                                           string='Pre-Screening Status',
                                           compute='_compute_pre_screening_state')
    cv_id = fields.Many2one('ir.attachment', string='CV')
    qualification_id = fields.Many2one('ir.attachment', string='Qualification')
    cv_url = fields.Char(string="CV URL", compute="_compute_urls", store=True)
    qualification_url = fields.Char(string="Qualification URL", compute="_compute_urls", store=True)
    user_role_id = fields.Many2one(
        'hr.employee', "Recruiter", compute='_compute_user',
        tracking=True, store=True, readonly=False)

    @api.depends('job_id')
    def _compute_user(self):
        for applicant in self:
            applicant.user_id = applicant.job_id.user_id.id
            applicant.user_role_id = applicant.job_id.user_role_id.id
            
    staging_date = fields.Datetime(string="Staging Date", tracking=True,store=True)

    @api.onchange('stage_id')
    def _onchange_stage(self):
        if self.stage_id.name == 'Staging' and not self.staging_date:
            self.staging_date = fields.Datetime.now()

    @api.model
    def check_staging_applications(self):
        """ Cron Job: Check applications in 'Staging' for more than 4 days and reject them. """
        four_days_ago = datetime.now() - timedelta(days=4)
        applications = self.search([
            ('stage_id.name', '=', 'Staging'),
            ('staging_date', '<=', four_days_ago),
        ])
        rejected_stage = self.env['hr.recruitment.stage'].search(
            [('name', '=', 'Rejected')], limit=1)
        email_template = self.env.ref('hr_recruitment.email_template_data_applicant_refuse', raise_if_not_found=False)

        for application in applications:
            application.write({'stage_id': rejected_stage.id})
            if email_template and application.partner_id.email:
                email_template.send_mail(application.id, force_send=True)

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

    def move_attachments_to_fields(self):
        applicants = self.search([])
        print('Moving attachments', applicants.attachment_ids)
        for applicant in applicants:
            attachments = self.env['ir.attachment'].search(
                [('res_model', '=', 'hr.applicant'),
                 ('res_id', '=', applicant.id)], order="id asc")
            if attachments:
                applicant.cv_id = attachments[0].id
                applicant.cv_id.public = True
                if len(attachments) == 4:
                    applicant.qualification_id = attachments[2].id
                    applicant.qualification_id.public = True
                if len(attachments) == 3:
                    applicant.qualification_id = attachments[1].id
                    applicant.qualification_id.public = True
        return True

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

    @api.model
    @api.depends()
    def _compute_pre_screening_state(self):
        """Compute the pre screening state"""
        for rec in self:
            pre_screening = rec.env['survey.user_input'].search(
                [('application_id', '=', rec.id)])
            if rec.job_id.need_prescreening:
                if len(pre_screening) == 1:
                    rec.pre_screening_state = pre_screening.state
                elif len(pre_screening) > 1:
                    rec.pre_screening_state = 'done' if 'done' in pre_screening.mapped(
                        'state') else 'new'
                else:
                    rec.pre_screening_state = 'new'
            else:
                rec.pre_screening_state = ''

    @api.depends('performance_ids')
    def _compute_performance(self):
        for rec in self:
            overall_performance = 0
            if rec.performance_ids:
                percentage = sum(rec.performance_ids.mapped('percentage'))
                length = len(rec.performance_ids.ids)
                overall_performance = percentage / length if length > 0 else 1
            rec.overall_performance = overall_performance

    def calculate_screening_point(self):
        """Compute screening point"""
        for record in self:
            screening_point = 0
            survey = record.job_id.survey_id
            if record.job_id.survey_id:
                answer = record.env['survey.user_input'].sudo().search([
                    ('survey_id', '=', survey.id),
                    ('application_id', '=', record.id)], limit=1)
                answer.email = record.email_from
                answered_score = sum(answer.mapped('scoring_total'))
                total_score = record.job_id.survey_id.total_score
                if answer and total_score > 0:
                    screening_point = (answered_score / total_score) * 100
            record.screening_point = screening_point
            elimination_questions = answer.mapped(
                'user_input_line_ids.question_id').filtered(
                lambda q: q.elimination_question)
            answered_lines = answer.mapped('user_input_line_ids').filtered(
                lambda line: line.question_id in elimination_questions)
            all_answered = len(answered_lines) == len(elimination_questions)
            all_correct = all_answered and all(
                answered_lines.mapped('answer_is_correct'))
            if all_answered:
                if all_correct:
                    record.stage_id = self.env.ref('hr_recruitment.stage_job0').id
                else:
                    record.stage_id = self.env.ref('recruitment_enhancement.stage_job7').id

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

    def action_open_candidate(self):
        """Open a candidate"""
        return {
            'name': _('Candidates'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'applicant.profile',
            'res_id': self.applicant_id.id,
        }

    def action_open_pre_screening_answer(self):
        """Open a pre-screening answer"""
        survey = self.job_id.survey_id
        answer = self.env['survey.user_input'].sudo().search([
            ('survey_id', '=', survey.id), ('application_id', '=', self.id)], limit=1)
        answer = answer.filtered(lambda x: x.survey_id.job_id == self.job_id)
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
        print('Open candidates')

    def send_manager(self):
        """Send a manager to review the applications"""
        mail_template = self.env.ref(
            'recruitment_enhancement.email_template_send_to_applicant')
        recipient_ids = self.env.ref(
            'hr_recruitment.group_hr_recruitment_manager').users
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)

    def get_list_url(self):
        """To generate the link to redirect to enquiry from the mail"""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=hr.applicant&view_type=form' % self.id)
        return Urls

    @api.onchange('applicant_id')
    def _onchange_applicant(self):
        """Change the applicant"""
        if self.applicant_id:
            self.partner_name = self.applicant_id.name
            self.title_id = self.applicant_id.title_id.id
            self.initial = self.applicant_id.initial
            self.surname = self.applicant_id.surname
            self.email_from = self.applicant_id.email_from
            self.partner_phone = self.applicant_id.phone
            self.id_number = self.applicant_id.id_number
            self.country_id = self.applicant_id.country_id.id
            self.date_of_birth = self.applicant_id.date_of_birth
            self.gender = self.applicant_id.gender
            self.disability = self.applicant_id.disability
            self.race = self.applicant_id.race
            self.applicant_skill_ids = self.applicant_id.applicant_skill_ids
            self.skill_ids = self.applicant_id.skill_ids

    def action_send_feedback(self):
        """ Opens the wizard to edit and send email """
        return {
            'name': 'Send Feedback',
            'type': 'ir.actions.act_window',
            'res_model': 'applicant.interview.feedback.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_subject': ' Interview Feedback {}'.format(
                    self.job_id.name),
                'default_body_html': self._get_default_email_body(),
                'default_applicant_id': self.id,
            },
        }

    def _get_default_email_body(self):
        """ Prepare the default email content for the wizard """
        return '''
        <p>Good day Mr/Mrs  %s,</p>
        <p>Kindly be advised that you have progressed to the next phase of the recruitment process for the position of <strong>%s</strong>.</p>
        <p>Please complete the attached MIE forms for verifications and send the following documents:</p>
                <ul>
                    <li>Your qualifications</li>
                    <li>ID document</li>
                    <li>Most recent payslip</li>
                </ul>
                <p>Please also tick the following:</p>
                <ul>
                    <li>Qualification</li>
                    <li>Credit check</li>
                    <li>Criminal checks</li>
                    <li>Reference checks</li>
                </ul>
                <p><strong>NB:</strong> Please scan your qualification separately.</p>
                <p>Regards,</p>
                <p>%s</p>
        ''' % (
            self.partner_name, self.job_id.name, self.env.user.partner_id.name)

    def action_schedule_interview(self):
        # Create appointment
        appointment_type = self.env['calendar.event.type'].search(
            [('name', '=', 'Interview')], limit=1)
        if not appointment_type:
            raise ValueError("Interview appointment type not found.")

        # Create calendar event
        event_vals = {
            'name': f'Interview with {self.name}',
            'start': fields.Datetime.now() + timedelta(days=1),
            # Example: Schedule for tomorrow
            'stop': fields.Datetime.now() + timedelta(days=1, hours=1),
            # 1 hour duration
            'appointment_type_id': appointment_type.id,
            'user_id': self.env.user.id,
            # Assign to the current user or interviewer
            'partner_ids': [(4, self.partner_id.id)],  # Add candidate
        }
        event = self.env['calendar.event'].create(event_vals)

    def action_send_interview_letter(self):
        return {
            'name': 'Send Interview Letter',
            'type': 'ir.actions.act_window',
            'res_model': 'applicant.interview.letter.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_subject': ' Interview Letter {}'.format(
                    self.job_id.name),
                'default_body_html': self._get_default_interview_letter_body(),
                'default_applicant_id': self.id,
            },
        }

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
        <p>Good day Mr/Mrs %s </p
        <p> This mail serves to invite you to the interview for the position of <strong>%s</strong> at %s and the details are as follows:</p>
        <p>Date: %s</p>
        <p>Time: %s</p>
        <p>Venue Address : %s </p>
        <p>Kindly confirm your availability by not later than the %s.</p>
        
        <p>Regards,</p>
        <p>%s</p>
        <p>%s</p>
        ''' % (
            self.partner_name, self.job_id.name, self.job_id.job_location_id.name,
            date,
            time, full_address, date, self.env.user.partner_id.name,
            self.env.user.partner_id.email)

    def move_to_staging(self):
        new_state = self.env['hr.recruitment.stage'].search([('name', '=', 'New')], limit=1)
        staging_state = self.env['hr.recruitment.stage'].search([('name', '=', 'Staging')], limit=1)
        if not new_state or not staging_state:
            return
        applications = self.search([
            ('stage_id', '=', new_state.id)
        ])
        for application in applications:
            if application.pre_screening_state != 'done' and application.job_id.need_prescreening:
                application.write({'stage_id': staging_state.id})

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
