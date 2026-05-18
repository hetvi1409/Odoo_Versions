# -*- coding: utf-8 -*-
from ast import literal_eval
from datetime import date

import werkzeug
from markupsafe import Markup
from werkzeug import urls
import base64
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrJob(models.Model):
    _inherit = 'hr.job'

    active = fields.Boolean(default=True, tracking=True)
    name = fields.Char(string='Job Title    ', required=True, index='trigram',
                       translate=True)
    user_id = fields.Many2one('res.users', "Role Reporting To",
                              domain="[('share', '=', False), ('company_ids', 'in', company_id)]",
                              tracking=True,
                              help="The Recruiter will be the default value for all Applicants Recruiter's field in this job position. The Recruiter is automatically added to all meetings with the Applicant.")
    user_role_id = fields.Many2one('hr.employee', "Role Reporting To",
                                   tracking=True,
                                   help="The Recruiter will be the default value for all Applicants Recruiter's field in this job position. The Recruiter is automatically added to all meetings with the Applicant.")
    job_grade = fields.Selection(
        [('p1', 'P1'), ('p2', 'P2'), ('p3', 'P3'), ('p4', 'P4'), ('p5', 'P5'),
         ('p6', 'P6'), ('p7', 'P7'), ('p8', 'P8'), ('p9', 'P9'), ('p10', 'P10'),
         ('p11', 'P11'), ('p12', 'P12'), ('p13', 'P13'), ('p14', 'P14'),
         ('p15', 'P15'), ('p16', 'P16'), ('p17', 'P17'), ], string='Job Grade')
    cost_center = fields.Text(string='Cost Center')
    purpose_job_main = fields.Text(
        string='Purpose for the JOB/ MAIN Specifications')
    requisition_state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Approval'),
        ('department_line_manager', 'Approved by Departmental Line Manager'),
        (
            'department_line_executive',
            'Approved by Departmental Line Executive'),
        ('od_manager', 'Approved by OD Manager'), (
            'cost_management_accounting',
            'Approved by Cost & Management Accounting'),
        ('group_executive', 'Approved by Group Executive'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Requisition State', default='draft', tracking=True, copy=False)
    approval_state = fields.Selection([
        ('department_line_manager_approve',
         'Departmental Line Manager Approval'),
        ('department_line_executive_approval',
         'Departmental Line Executive Approval'),
        ('od_manager_approval', 'OD Manager Approval'),
        ('cost_management_accounting_approval',
         'Cost & Management Accounting Approval'),
        ('group_executive_approval', 'Group Executive Approval')
    ], tracking=True, copy=False)
    start_date = fields.Date(string="Envisaged Start Date")
    end_date = fields.Date(string="Envisaged End Date")
    minimum_qualifications = fields.Char(string="Minimum Qualifications")
    required_experience = fields.Char(string="Required Experience")
    employee_replaced_id = fields.Many2one('hr.employee',
                                           string='Employee Replaced')
    position_on_approved_structure = fields.Boolean(
        string='Position On Approved Structure')
    budget_approved = fields.Boolean(string='Position Budgeted For')
    sourcing_method = fields.Selection(
        [('internal', 'Internal'), ('external', 'External'), ('Both', 'Both')])
    survey_id = fields.Many2one('survey.survey', string='Survey', copy=False)
    question_and_page_ids = fields.One2many('survey.question',
                                            related="survey_id.question_and_page_ids",
                                            string='Sections and Questions',
                                            readonly=False, copy=False)
    skill_ids = fields.Many2many(comodel_name='hr.skill',
                                 string="Expected Skills")
    vacancy_reason = fields.Selection(
        [('terminated_contract', 'Resignation Contract Terminated'),
         ('promotion', 'Promotion'), ('transfer', 'Transfer'),
         ('position', 'New Position'), ('retire', 'Retirement'),
         ('deceased', 'Deceased')], string='Reasons For Vacancy', copy=False)
    job_requirements = fields.Binary(
        string='Minimum Job Requirements Guidelines')
    extend_travel = fields.Selection(
        [('minimal', 'Minimal'), ('medium', 'Medium'),
         ('extensive', 'Extensive')], string='Extent of Travel Required')
    requested_by = fields.Many2one('res.users', string='Requested by:',
                                   copy=False)
    requested_date = fields.Date('Date', copy=False)
    position_approval = fields.Many2one('res.users',
                                        string='Position on the approved structure / not on the approved structure:',
                                        copy=False)
    position_approved_date = fields.Date(string='Date:', copy=False)
    budget_approve_not = fields.Many2one('res.users',
                                         string='Budget Approved / Not Approved:',
                                         copy=False)
    budget_approve_date = fields.Date(string='Date:', copy=False)
    position_filled = fields.Many2one('res.users',
                                      string='Position to be filled:',
                                      copy=False)
    position_filled_date = fields.Date(string='Date:', copy=False)
    requisition_approve_not = fields.Many2one('res.users',
                                              string='Requisition Approved / Requisition Not Approved:',
                                              copy=False)
    requisition_approve_date = fields.Date(string='Date:', copy=False)
    salary = fields.Selection(
        [('market_related', 'Market Related'), ('negotiable', 'Negotiable')],
        string='Salary', copy=False)
    work_level = fields.Selection(
        [('executive', 'Executive Management'), ('senior', 'Senior Management'),
         ('middle', 'Middle Management'), ('junior', 'Junior Management'),
         ('skilled', 'Skilled Technical'), ('semi', 'Semi-Skilled'),
         ('unskilled', 'Unskilled')], string='Work Level', copy=False)
    ee_position = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                   string='EE Position', copy=False)
    job_url = fields.Char(string='Job URL', copy=False)
    publish_date = fields.Date(string='Publish Date', tracking=True, copy=False)
    unpublish_date = fields.Date(string='Unpublish Date', tracking=True,
                                 copy=False)
    staging_application_count = fields.Integer(string="Failed Applications Count",
                                               compute="_compute_staging_application_count")

    job_location_id = fields.Many2one(
        'res.partner', "Job Location", domain="[('is_job_location', '=', True)]",
        help="Select the location where the applicant will work. Addresses listed here are defined on the company's contact information.")
    attachment_id = fields.Many2one('ir.attachment', tracking=True, copy=False)
    create_job_advert_pdf = fields.Boolean(string="Create Job Advert PDF", default=False, copy=False,
                                           compute='_compute_job_advert_pdf')
    is_re_advertised = fields.Boolean(string='Is Re-Advertised?', default=False)
    re_advertised_job_id = fields.Many2one('hr.job', string="Re-Advertised Job")
    need_prescreening = fields.Boolean(string="Need Prescreening", default=True)
    approval_line_ids = fields.One2many("approval.team.line", "contract_id", string="Approval Lines")
    approver_role_id = fields.Many2one("approver.role", string="Approver Role")
    approval_date = fields.Datetime(string="Date")
    signature = fields.Binary('Signature')
    status = fields.Selection([('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                              default='pending', string="Status")
    reject_reason = fields.Text(string="Reject Reason")

    def _generate_advert_pdf(self):
        """Generate PDF using QWeb and attach to the job"""

        pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
            "recruitment_enhancement.action_report_hr_job_advert", [self.id])
        filename = 'Job - %s' % (self.name) + '.pdf'
        advert_attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': 'hr.job',
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })

        self.attachment_id = advert_attachment.id

        # Notify Recruitment Officer
        self._notify_recruitment_officer()

    def _notify_recruitment_officer(self):
        """Send notification to Recruitment Officers"""
        hr_officer_group = self.env.ref("hr_recruitment.group_hr_recruitment_manager")
        hr_officers = hr_officer_group.users
        if hr_officers:
            self.env['mail.thread'].sudo().message_notify(
                model=self._name,
                res_id=self.id,
                subject='Job Advert PDF generated',
                body=f"Job Advert PDF generated for {self.name}.",
                partner_ids=hr_officers.mapped("partner_id")[0].ids,
                email_layout_xmlid='mail.mail_notification_light',
            )

    def _compute_job_advert_pdf(self):
        for job in self:
            job._generate_advert_pdf()
            job.create_job_advert_pdf = True

    # @api.onchange('website_published','description')
    # def _onchange_website_published(self):
    #     if self.website_published and self.requisition_state == 'approved':
    #         self._generate_advert_pdf()

    @api.model_create_multi
    def create(self, vals_list):
        jobs = super(HrJob, self).create(vals_list)
        for job in jobs:
            job._generate_advert_pdf()
        return jobs

    # def write(self, vals):
    #     res = super(HrJob, self).write(vals)
    #     self._generate_advert_pdf()
    #     return res

    def action_view_advert_pdf(self):
        """Redirects to PDF attachment when the smart button is clicked."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            # "url": f"/web/content/{self.id}?model=hr.job&field=job_advert_pdf&filename_field=job_advert_pdf_filename",
            "url": f'/web/content/{self.attachment_id.id}?download=true',
            "target": "new",
        }

    @api.onchange('user_role_id')
    def _onchange_user_role_id(self):
        """Onchange User role id based on the"""
        self.user_id = self.user_role_id.user_id.id

    @api.depends('application_count')
    def _compute_staging_application_count(self):
        for job in self:
            job.staging_application_count = self.env[
                'hr.applicant'].search_count([
                ('stage_id.name', 'ilike', 'staging'),
                ('job_id', '=', job.id)])

    def _publish_unpublish_jobs(self):
        today = date.today()
        jobs_to_publish = self.search(
            [('publish_date', '<=', today), ('website_published', '=', False)])
        for publish in jobs_to_publish:
            publish.website_published = True

        jobs_to_unpublish = self.search(
            [('unpublish_date', '<=', today), ('website_published', '=', True)])
        for unpublish in jobs_to_unpublish:
            unpublish.website_published = False

    def action_readvertise_jobs(self):
        today = date.today()
        for job in self:
            if job.requisition_state != 'approved':
                raise ValidationError(_('Job must be approved before re-advertising.'))

            if job.website_published:
                raise ValidationError(_('Job must be unpublished before re-advertising.'))

            if not job.unpublish_date or job.unpublish_date > today:
                raise ValidationError(_('Job can only be re-advertised after the unpublish date has passed.'))

            if job.is_re_advertised:
                raise ValidationError(_('This job has already been re-advertised once.'))

            new_job = job.copy({
                'name': f"{job.name} – Re-advertisement",
                'requisition_state': 'draft',
                'website_published': False,
                'is_re_advertised': False,
                'user_role_id': job.user_role_id.id,
                'job_grade': job.job_grade,
                'cost_center': job.cost_center,
                'department_id': job.department_id.id,
                'contract_type_id': job.contract_type_id.id,
                'start_date': job.start_date,
                'end_date': job.end_date,
                'vacancy_reason': job.vacancy_reason,
                'employee_replaced_id': job.employee_replaced_id.id,
                'interviewer_ids': [(6, 0, job.interviewer_ids.ids)],
                'survey_id': job.survey_id.id,
                'default_contract_id': job.default_contract_id.id,
                'skill_ids': [(6, 0, job.skill_ids.ids)],
                'work_level': job.work_level,
                'ee_position': job.ee_position,
                'job_requirements': job.job_requirements,
                'description': job.description,
            })

            job.is_re_advertised = True
            job.re_advertised_job_id = new_job.id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Re-advertised Job',
            'res_model': 'hr.job',
            'view_mode': 'form',
            'res_id': new_job.id,
            'target': 'current',
        }

    def action_search_matching_candidates(self):
        self.ensure_one()
        help_message_1 = _("No Matching Profiles")
        action = self.env['ir.actions.actions']._for_xml_id('recruitment_enhancement.action_applicant_profile')
        context = literal_eval(action['context'])
        context['active_id'] = self.id
        application = self.env['hr.applicant'].sudo().search(
            [('job_id', '=', self.id)]).mapped('applicant_id')
        matching_candidates = application.search(
            [('skill_ids', 'in', self.skill_ids.ids)])
        action.update({
            'name': _("Matching Profiles"),
            'context': context,
            'domain': [('id', 'in', matching_candidates.ids)],
            'views': [
                (self.env.ref(
                    'recruitment_enhancement.view_applicant_profile_tree_skill').id,
                 'tree'),
                (False, 'kanban'),
                (False, 'form'),
            ],
            'help': Markup(
                "<p class='o_view_nocontent_empty_folder'>%s</p>") % (
                        help_message_1),
        })
        return action

    def action_submit_requisition(self):
        if self.need_prescreening:
            if not self.question_and_page_ids:
                raise ValidationError('Please Add Additional Questions')
        self.write({'requisition_state': 'submitted'})
        mail_template = self.env.ref(
            'recruitment_enhancement.email_template_job_requisition_send_to_departmental_line_manager_group')
        recipient_ids = self.env.ref(
            'recruitment_enhancement.departmental_line_manager_group').users
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
                             'web#id=%s&model=hr.job&view_type=form' % self.id)
        return Urls

    def action_approve_requisition(self):
        self.write({'requisition_state': 'approved'})
        mail_template = self.env.ref(
            'recruitment_enhancement.email_template_job_requisition_send_to_approved')
        recipient_ids = self.env.ref(
            'hr_recruitment.group_hr_recruitment_manager').users
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.website_published = True

    def action_job_advertise(self):
        template_id = self.env.ref(
            'recruitment_enhancement.email_template_job_opportunities')
        if self.website_published:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            full_url = urls.url_join(base_url, self.website_url)
            self.write({'job_url': full_url})
        if template_id:
            template_id.sudo().send_mail(self.id, force_send=True)

    def action_reject_requisition(self):
        self.write({'requisition_state': 'rejected'})

    def action_start_prescreening_survey(self):
        self.ensure_one()

        # Check if a survey already exists for this job
        existing_survey = self.env['survey.survey'].search(
            [('job_id', '=', self.id)], limit=1)
        if existing_survey:
            # If an existing survey is found, open it
            self.survey_id = existing_survey.id

        else:
            # If no survey exists, create a new one and set job_id
            new_survey = self.env['survey.survey'].create({
                'title': f"Additional Questions for {self.name}",
                'job_id': self.id,
                'survey_type': 'custom',
                'questions_layout': 'one_page',
                'access_mode': 'public',
                'scoring_type': 'scoring_with_answers'
            })
            self.survey_id = new_survey.id

    def action_department_line_manager_approve(self):
        """Approve managers department lines"""
        self.requisition_state = 'department_line_manager'
        self.write({'approval_state': 'department_line_manager_approve'})
        mail_template = self.env.ref(
            'recruitment_enhancement.email_template_job_requisition_send_to_departmental_line_manager_group')
        recipient_ids = self.env.ref(
            'recruitment_enhancement.departmental_line_executive_group').users
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.requested_by = self.env.user.id
        self.requested_date = date.today()

    def action_department_line_manager_revert(self):
        return {
            'name': 'Create Lab Test',
            'res_model': 'hr.job.revert',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                'default_job_id': self.id
            }
        }
        self.write({'requisition_state': 'draft'})

    def action_department_line_executive_approval(self):
        """Approve managers department lines"""
        self.requisition_state = 'department_line_executive'
        self.write({'approval_state': 'department_line_executive_approval'})
        mail_template = self.env.ref(
            'recruitment_enhancement.email_template_job_requisition_send_to_departmental_line_manager_group')
        recipient_ids = self.env.ref(
            'recruitment_enhancement.od_manager_group').users
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.position_approval = self.env.user.id
        self.position_approved_date = date.today()

    def action_department_line_executive_revert(self):
        return {
            'name': 'Create Lab Test',
            'res_model': 'hr.job.revert',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                'default_job_id': self.id
            }
        }

    def action_od_manager_approval(self):
        """Approve managers department lines"""
        self.requisition_state = 'od_manager'
        self.write({'approval_state': 'od_manager_approval'})
        mail_template = self.env.ref(
            'recruitment_enhancement.email_template_job_requisition_send_to_departmental_line_manager_group')
        recipient_ids = self.env.ref(
            'recruitment_enhancement.cost_management_accounting_group').users
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.budget_approve_not = self.env.user.id
        self.budget_approve_date = date.today()

    def action_od_manager_revert(self):
        return {
            'name': 'Create Lab Test',
            'res_model': 'hr.job.revert',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                'default_job_id': self.id
            }
        }

    def action_cost_management_accounting_revert(self):
        return {
            'name': 'Create Lab Test',
            'res_model': 'hr.job.revert',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                'default_job_id': self.id
            }
        }

    def action_group_executive_revert(self):
        return {
            'name': 'Create Lab Test',
            'res_model': 'hr.job.revert',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                'default_job_id': self.id
            }
        }

    def action_cost_management_accounting_approval(self):
        """Approve managers department lines"""
        self.requisition_state = 'cost_management_accounting'
        self.write({'approval_state': 'cost_management_accounting_approval'})
        mail_template = self.env.ref(
            'recruitment_enhancement.email_template_job_requisition_send_to_departmental_line_manager_group')
        recipient_ids = self.env.ref(
            'recruitment_enhancement.group_executive_group').users
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.position_filled = self.env.user.id
        self.position_filled_date = date.today()

    def action_group_executive_approval(self):
        """Approve managers department lines"""
        self.requisition_state = 'group_executive'
        self.write({'approval_state': 'group_executive_approval'})
        self.requisition_approve_not = self.env.user.id
        self.requisition_approve_date = date.today()
        self.action_approve_requisition()

    @api.model
    def send_follow_up_mail(self):
        """Send reminder mail for approve the requisition"""
        job = self.env['hr.job'].search(
            [('requisition_state', '=', 'submitted')])
        mail_template = self.env.ref(
            'recruitment_enhancement.email_template_job_requisition_reminder')
        if not self.approval_state:
            recipient_ids = self.env.ref(
                'recruitment_enhancement.departmental_line_manager_group').users
        elif self.approval_state == 'department_line_manager_approve':
            recipient_ids = self.env.ref(
                'recruitment_enhancement.department_line_executive_approval').users
        elif self.approval_state == 'department_line_executive_approval':
            recipient_ids = self.env.ref(
                'recruitment_enhancement.od_manager_group').users
        elif self.approval_state == 'od_manager_approval':
            recipient_ids = self.env.ref(
                'recruitment_enhancement.cost_management_accounting_group').users
        elif self.approval_state == 'cost_management_accounting_approval':
            recipient_ids = self.env.ref(
                'recruitment_enhancement.group_executive_group').users
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)

    def get_survey_url(self):
        job = self
        survey = job.survey_id
        survey.action_send_survey()
        survey_invite = self.env['survey.invite'].search(
            [('survey_id', '=', survey.id)])
        survey_url = werkzeug.urls.url_join(
            survey.get_base_url(),
            survey.get_start_url()) if survey else False
        if not survey:
            return '/job-thank-you'  # Render a 404 page if no survey is found.
        else:
            return survey.get_start_url()

    def action_start_approval_process(self):
        self.ensure_one()
        if not self.approval_line_ids:
            raise ValidationError(_(
                "Please add at least one approval line before starting the approval process."
            ))
        for line in self.approval_line_ids:
            if not line.user_id or not line.approver_role_id:
                raise ValidationError(_(
                    "Please select an approver role and a user for all approval lines "
                    "before starting the approval process."
                ))

        self.approval_status = 'partially_approved'
        # Notify the first pending approver
        self._notify_next_approver()

    def action_approve_requisition_flow(self):
        self.ensure_one()
        login_user = self.env.user

        if login_user != self.current_approver_id:
            raise AccessError(_(
                "You are not authorized to approve this document. "
                "Current approver is %s."
            ) % (self.current_approver_id.name or _("Unknown")))

        approval_line = self.approval_line_ids.filtered(
            lambda l: l.user_id == login_user and l.status == 'pending'
        )[:1]

        if not approval_line:
            raise AccessError(_(
                "No pending approval line found for you or you have already approved it."
            ))

        approval_line.write({
            'approved': True,
            'status': 'approved',
            'approval_date': fields.Datetime.now(),
        })

        self._update_approval_status()
        self._notify_approval_line_users('Approved', login_user)

        # Open signature wizard
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sign Approval'),
            'res_model': 'approval.team.line',
            'view_mode': 'form',
            'view_id': self.env.ref(
                'recruitment_enhancement.approval_team_line_approved_view_form'
            ).id,
            'res_id': approval_line.id,
            'target': 'new',
            'context': {
                'default_contract_id': self.id,
                'default_approval_line_id': approval_line.id,
                'default_user_id': login_user.id,
                'form_view_initial_mode': 'edit',
                'default_approval_signed': approval_line.approval_signed,
                'default_rejected_signed': approval_line.rejected_signed,
            },
        }

    def action_reject_requisition_flow(self):
        self.ensure_one()
        login_user = self.env.user

        if login_user != self.current_approver_id:
            raise AccessError(_(
                "You are not authorized to reject this document. "
                "Current approver is %s."
            ) % (self.current_approver_id.name or _("Unknown")))

        line = self.approval_line_ids.filtered(
            lambda l: l.user_id == login_user and l.status == 'pending'
        )[:1]

        if not line:
            raise AccessError(_("No pending approval line found for you."))

        line.write({
            'status': 'rejected',
            'approval_date': fields.Datetime.now(),
            'approved': False,
        })

        # Reject all remaining pending lines
        self.approval_line_ids.filtered(
            lambda l: l.status == 'pending'
        ).write({'status': 'rejected'})

        self.write({
            'requisition_state': 'rejected',
            'approval_status': 'rejected',
        })

        self._notify_approval_line_users('Rejected', login_user, reason=line.reject_reason)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Reject Requisition'),
            'res_model': 'approval.team.line',
            'view_mode': 'form',
            'view_id': self.env.ref(
                'recruitment_enhancement.approval_team_line_reject_view_form'
            ).id,
            'res_id': line.id,
            'target': 'new',
            'context': {
                'default_contract_id': self.id,
                'default_user_id': login_user.id,
                'form_view_initial_mode': 'edit',
            },
        }

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _update_approval_status(self):
        self.ensure_one()
        pending_count = len(self.approval_line_ids.filtered(lambda l: l.status == 'pending'))
        rejected_count = len(self.approval_line_ids.filtered(lambda l: l.status == 'rejected'))

        if pending_count > 0:
            self.approval_status = 'partially_approved'
            # Notify the next pending approver
            self._notify_next_approver()
        elif rejected_count > 0:
            self.requisition_state = 'rejected'
            self.approval_status = 'rejected'
        else:
            self.requisition_state = 'approved'
            self.approval_status = 'fully_approved'
            self._notify_fully_approved()

    def _notify_next_approver(self):
        """Send email to the next pending approver in sequence."""
        self.ensure_one()
        next_line = self.approval_line_ids.filtered(
            lambda l: l.status == 'pending'
        ).sorted('sequence')[:1]

        if not next_line or not next_line.user_id:
            return

        email_to = next_line.user_id.partner_id.email
        if not email_to:
            return

        url = "%s/web#id=%s&model=%s&view_type=form" % (
            self.get_base_url(), self.id, self._name
        )
        template = self.env.ref(
            'recruitment_enhancement.mail_template_requisition_line_update',
            raise_if_not_found=False
        )
        if template:
            template.with_context(
                status='pending your approval',
                action_user=self.env.user.name,
                reason=False,
                url=url,
            ).sudo().send_mail(
                self.id,
                force_send=True,
                email_values={'email_to': email_to}
            )
        else:
            self.env['mail.mail'].sudo().create({
                'subject': _("Approval Required: %s") % self.name,
                'body_html': _(
                    "<p>Dear %(name)s,</p>"
                    "<p>Job Position <b>%(job)s</b> requires your approval.</p>"
                    "<p><a href='%(url)s'>Open Record</a></p>"
                ) % {
                                 'name': next_line.user_id.name,
                                 'job': self.name,
                                 'url': url,
                             },
                'email_to': email_to,
            }).send()

    def _notify_approval_line_users(self, status, action_user, reason=False):
        """Notify all approvers about the approval status change."""
        self.ensure_one()
        partners = self.approval_line_ids.mapped('user_id.partner_id')
        if not partners:
            return

        url = "%s/web#id=%s&model=%s&view_type=form" % (
            self.get_base_url(), self.id, self._name
        )
        template = self.env.ref(
            'recruitment_enhancement.mail_template_requisition_line_update',
            raise_if_not_found=False
        )
        if template:
            template.with_context(
                status=status,
                action_user=action_user.name,
                reason=reason,
                url=url,
            ).sudo().send_mail(
                self.id,
                force_send=True,
                email_values={'recipient_ids': [(6, 0, partners.ids)]}
            )

    def _notify_fully_approved(self):
        """Notify all approvers when fully approved."""
        self.ensure_one()
        partners = self.approval_line_ids.mapped('user_id.partner_id')
        if not partners:
            return

        url = "%s/web#id=%s&model=%s&view_type=form" % (
            self.get_base_url(), self.id, self._name
        )
        template = self.env.ref(
            'recruitment_enhancement.mail_template_requisition_line_update',
            raise_if_not_found=False
        )
        if template:
            template.with_context(
                status='Fully Approved',
                action_user=self.env.user.name,
                reason=False,
                url=url,
            ).sudo().send_mail(
                self.id,
                force_send=True,
                email_values={'recipient_ids': [(6, 0, partners.ids)]}
            )
