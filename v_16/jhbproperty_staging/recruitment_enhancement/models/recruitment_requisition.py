from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError
import base64
from markupsafe import Markup


class RecruitmentMediaChannel(models.Model):
    _name = 'recruitment.media.channel'
    _description = 'Recruitment Media Channel'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)


class RecruitmentRequisition(models.Model):
    _name = 'recruitment.requisition'
    _description = 'Recruitment Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    STAGE_LABELS = {
        'line_manager': 'Line Manager',
        'general_manager': 'General Manager',
        'cfo': 'Chief Financial Officer',
        'gm_hcm': 'GM Human Capital Management',
    }

    STAGE_STATES = {
        'line_manager': 'to_line_manager',
        'general_manager': 'to_gm',
        'cfo': 'to_cfo',
        'gm_hcm': 'to_hcm',
    }

    STAGE_FIELDS = {
        'line_manager': 'line_manager_ids',
        'general_manager': 'general_manager_ids',
        'cfo': 'cfo_ids',
        'gm_hcm': 'hcm_manager_ids',
    }

    name = fields.Char(default='New', copy=False, tracking=True)
    # state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('to_line_manager', 'Line Manager Approval'),
    #     ('to_gm', 'General Manager Approval'),
    #     ('to_cfo', 'CFO Approval'),
    #     ('to_hcm', 'GM HCM Validation'),
    #     ('approved', 'Approved'),
    #     ('rejected', 'Rejected'),
    #     ('cancelled', 'Cancelled'),
    # ], default='draft', tracking=True)
    active = fields.Boolean(default=True)

    job_id = fields.Many2one('hr.job', readonly=True, tracking=True)
    job_location = fields.Many2one('res.partner', related='job_id.address_id', store=True, string='Job Location')
    department_id = fields.Many2one('hr.department', related='job_id.department_id', store=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    no_of_positions = fields.Integer('Target', related='job_id.no_of_recruitment', store=True)

    position_type = fields.Selection([
        ('existing', 'Existing Position'),
        ('new', 'New Position'),
    ], required=True, default='new', tracking=True)
    job_grade = fields.Char(tracking=True, required=True)
    reports_to_title = fields.Char(tracking=True)
    previous_incumbent = fields.Many2one('hr.employee', string='Previous Incumbent', tracking=True)


    external_advert_required = fields.Boolean(default=True)
    internal_advert_required = fields.Boolean(default=True)
    channel_ids = fields.Many2many('recruitment.media.channel', string='Advertising Channels')
    advert_days = fields.Integer(default=10)

    business_justification = fields.Text(required=False)
    business_strategy_alignment = fields.Text()

    ee_target_youth = fields.Boolean(string='EE Target: Youth')
    ee_target_women = fields.Boolean(string='EE Target: Women')
    ee_target_pwd = fields.Boolean(string='EE Target: PWD')

    hr_coordinator_id = fields.Many2one('hr.employee', related='job_id.user_role_id', string='HR Coordinator', store=True)

    line_manager_date = fields.Datetime(readonly=True)
    gm_date = fields.Datetime(readonly=True)
    cfo_date = fields.Datetime(readonly=True)
    hcm_date = fields.Datetime(readonly=True)

    requisition_form_file = fields.Binary(attachment=True)
    requisition_form_filename = fields.Char()
    job_description_file = fields.Binary(attachment=True)
    job_description_filename = fields.Char()
    organogram_file = fields.Binary(attachment=True)
    organogram_filename = fields.Char()
    budget_file = fields.Binary(attachment=True)
    budget_file_name = fields.Char()

    document_line_ids = fields.One2many(
        'requisition.document',
        'requisition_id',
        string='Documents'
    )
    # document_complete = fields.Boolean(compute='_compute_document_complete', store=True)
    document_complete = fields.Boolean()
    approval_cycle_days = fields.Integer(compute='_compute_approval_cycle_days')

    rejection_reason = fields.Text()
    approval_log_ids = fields.One2many('recruitment.requisition.approval', 'requisition_id', readonly=True)

    # One2many approvals per stage (same style as memo lines)
    line_manager_ids = fields.One2many(
        'recruitment.requisition.line.manager', 'requisition_id', string='Line Manager Approvers', copy=True
    )
    general_manager_ids = fields.One2many(
        'recruitment.requisition.general.manager', 'requisition_id', string='General Manager Approvers', copy=True
    )
    cfo_ids = fields.One2many(
        'recruitment.requisition.cfo', 'requisition_id', string='CFO Approvers', copy=True
    )
    hcm_manager_ids = fields.One2many(
        'recruitment.requisition.hcm', 'requisition_id', string='HCM Approvers', copy=True
    )
    allowed_user_ids = fields.Many2many(
        'res.users',
        'recruitment_requisition_allowed_user_rel',
        'requisition_id',
        'user_id',
        string='Turn-based Allowed Users',
        compute='_compute_allowed_user_ids',
        store=True,
        compute_sudo=True,
    )

    # Stage 4 checklist
    hcm_check_job_description = fields.Boolean(string='Checklist: Job Description Received')
    hcm_check_organogram = fields.Boolean(string='Checklist: Organogram Attached')
    hcm_check_finance_approved = fields.Boolean(string='Checklist: Finance Approval Confirmed')
    hcm_check_gm_approved = fields.Boolean(string='Checklist: GM Approval Confirmed')
    hcm_check_all_signatories = fields.Boolean(string='Checklist: All Signatories Signed')
    hcm_completed_by_id = fields.Many2one('res.users', string='Checklist Completed By')
    hcm_check_date = fields.Datetime(string='Checklist Completion Date')

    # Approval team
    approval_team_id = fields.Many2one('approval.team', string='Approval Team',
                                       domain="[('model','=','recruitment.requisition')]")
    approval_line_ids = fields.One2many("approval.team.line", "contract_id", string="Approval Lines")

    approval_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('partially_approved', 'Partially Approved'),
        ('fully_approved', 'Fully Approved'),
        ('rejected', 'Rejected'),
    ], default='not_started', tracking=True)

    state = fields.Selection([
        ("draft", "Draft"),
        ("in_process", "Submitted for Review"),
        ("approval_in_process", "Submitted for Approval"),
        ("approved", "Approved for Recruitment"),
        ("recruitment_in_process", "Recruitment In Process"),
        ("done", "Position Filled"),
        ("rejected", "Rejected"),
        ('cancelled', 'Cancelled'),
    ], default="draft", tracking=True)
    status = fields.Selection(
        [("position_overview", "Position Overview"), ("business_justification", "Business Justification"),
         ("job_details", "Job Details"), ("requirements_and_competencies", "Requirements & Competencies"),
         ("screening_and_interview_setup", "Screening & Interview Setup"), ("ee_and_compliance", "EE & Compliance"),
         ("documents", "Documents")],
        default="position_overview", tracking=True)
    impact_if_not_filled = fields.Text(string='Impact if Not Filled',)
    budget_availability = fields.Float(string='Budget Availability')
    certifications = fields.Char(string='Certifications')

    current_approver_id = fields.Many2one('res.users', string="Current Approver", compute="_compute_current_approver",
                                          store=True)
    is_current_approver = fields.Boolean(string="Is Current Approver", compute="_compute_is_current_approver")
    group_ids = fields.Many2many("res.groups", string="Groups")
    job_summary = fields.Html(related='job_id.description')
    # summary = fields.Html()
    interviewer_ids = fields.Many2many('res.users',
                                       string='Interviewers', related='job_id.interviewer_ids')
    publish_date = fields.Date(string='Publish Date')
    unpublish_date = fields.Date(string='Unpublish Date', related='job_id.closing_date')
    website_published = fields.Boolean('Published on Website', default=False, related='job_id.website_published')
    sourcing_method = fields.Selection(
        [('internal', 'Internal'), ('external', 'External'), ('Both', 'Both')])
    attachment_id = fields.Many2one('ir.attachment', related='job_id.attachment_id', readonly=True)
    create_job_advert_pdf = fields.Boolean(related='job_id.create_job_advert_pdf')
    job_desc = fields.Text(string="Job Description",required=False)
    years_of_experience = fields.Integer(string="Years of Experience")
    # qualification = fields.Char(string="Qualifications")
    expected_degree = fields.Many2one('hr.recruitment.degree', string="Expected Degree", related='job_id.expected_degree')
    purpose_job_main = fields.Text(
        string='Purpose for the JOB/ MAIN Specifications')
    skill_ids = fields.Many2many(comodel_name='hr.skill',
                                 string="Expected Skills", related='job_id.skill_ids')
    required_experience = fields.Char("Required Experience", related ='job_id.required_experience')
    minimum_qualifications = fields.Char(string="Minimum Qualifications", related='job_id.minimum_qualifications')
    survey_id = fields.Many2one('survey.survey', string='Question template', copy=False, required=True)
    need_prescreening = fields.Boolean(string="Need Prescreening", default=True)
    question_and_page_ids = fields.One2many('survey.question',
                                            related="survey_id.question_and_page_ids",
                                            string='Sections and Questions',
                                            readonly=False, copy=False)
    applicant_ids = fields.One2many('hr.applicant','requisition_id',string='Applicants' )
    hired_employee = fields.Many2one('hr.employee', string="Hired Employee")
    hired_date = fields.Date(string="Hired Date")

    @api.onchange('position_type','job_id')
    def _onchange_position_type(self):
        if self.position_type == 'existing' and self.job_id:
            employee = self.env['hr.employee'].search([('job_id', '=', self.job_id.id)], order='create_date desc', limit=1)
            self.previous_incumbent = employee.id if employee else False
            if not employee:
                raise ValidationError(_("No employee found for Existing Position for the selected job."))
        else:
            self.previous_incumbent = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('recruitment.requisition') or 'New'
            # Set previous_incumbent for existing positions
            if vals.get('position_type') == 'existing' and vals.get('job_id') and not vals.get('previous_incumbent'):
                employee = self.env['hr.employee'].search([('job_id', '=', vals['job_id'])], order='create_date desc', limit=1)
                if employee:
                    vals['previous_incumbent'] = employee.id
        requisitions = super().create(vals_list)
        for requisition in requisitions:
            requisition.job_id.requisition_id = requisition.id
        return requisitions

    def write(self, vals):
        if 'position_type' in vals or 'job_id' in vals:
            for rec in self:
                position_type = vals.get('position_type', rec.position_type)
                job_id = vals.get('job_id', rec.job_id.id)
                if position_type == 'existing' and job_id and 'previous_incumbent' not in vals:
                    employee = self.env['hr.employee'].search([('job_id', '=', job_id)], order='create_date desc', limit=1)
                    vals['previous_incumbent'] = employee.id if employee else False
                elif position_type == 'new' and 'previous_incumbent' not in vals:
                    vals['previous_incumbent'] = False
        return super().write(vals)

    def action_start_prescreening_survey(self):
        self.ensure_one()

        if not self.survey_id:
            new_survey = self.env['survey.survey'].create({
                'title': f"Additional Questions for {self.name}",
                'survey_type': 'custom',
                'questions_layout': 'one_page',
                'access_mode': 'public',
                'scoring_type': 'scoring_with_answers',
            })
            self.survey_id = new_survey.id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Pre-screening Survey',
            'res_model': 'survey.survey',
            'view_mode': 'form',
            'res_id': self.survey_id.id,
            'target': 'current',
        }

    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id and self.position_type == 'existing':
            self.job_summary = self.job_id.description
            # self.job_desc = self.job_id.description
            self.department_id = self.job_id.department_id.id
            self.ee_target_pwd = self.job_id.ee_target_pwd
            self.ee_target_women = self.job_id.ee_target_women
            self.ee_target_youth = self.job_id.ee_target_youth
            self.interviewer_ids = self.job_id.interviewer_ids.ids
            self.minimum_qualifications = self.job_id.minimum_qualifications
            self.required_experience =self.job_id.required_experience
            self.skill_ids = self.job_id.skill_ids.ids
            self.survey_id = self.job_id.survey_id.id
            self.website_published = self.job_id.website_published
            self.hr_coordinator_id = self.job_id.user_role_id.id

    @api.onchange('website_published')
    def onchange_publish_date(self):
        for rec in self:
            if rec.website_published:
                rec.publish_date = fields.Date.today()
            else:
                rec.publish_date = ''


    def action_view_requisition_report(self):
        self.ensure_one()
        if not self.job_id:
            raise UserError(_("No Job Position linked to this requisition."))
        self._generate_requisition_pdf()
        return {
            "type": "ir.actions.act_url",
            "url": f'/web/content/{self.attachment_id.id}?download=true',
            "target": "new",
        }


    def action_view_advert_pdf(self):
        """Regenerates and downloads the Job Advert PDF with latest data."""
        self.ensure_one()
        if not self.job_id:
            raise UserError(_("No Job Position linked to this requisition."))
        self.job_id._generate_advert_pdf()
        return {
            "type": "ir.actions.act_url",
            "url": f'/web/content/{self.attachment_id.id}?download=true',
            "target": "new",
        }

    def _generate_requisition_pdf(self):
        pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
            "recruitment_enhancement.action_report_recruitment_requisition_job_advert", [self.id])
        filename = 'Requisition - %s' % (self.name) + '.pdf'
        requisition_report_id = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': 'recruitment.requisition',
            'res_id': self.id,
            'mimetype': 'application/pdf',
            'company_id': self.company_id.id
        })
        self.attachment_id = requisition_report_id.id

    @api.depends('current_approver_id')
    def _compute_is_current_approver(self):
        for rec in self:
            if rec.current_approver_id == self.env.user:
                rec.is_current_approver = True
            else:
                rec.is_current_approver = False

    @api.depends('approval_line_ids.status', 'approval_line_ids.sequence', 'approval_team_id')
    def _compute_current_approver(self):
        for rec in self:
            pending_lines = rec.approval_line_ids.filtered(lambda l: l.status == 'pending').sorted('sequence')
            rec.current_approver_id = pending_lines[0].user_id if pending_lines else False

    @api.onchange('approval_line_ids')
    def _onchange_approval_line_ids(self):
        for index, line in enumerate(self.approval_line_ids, start=1):
            line.sequence = index

    def action_start_approval_process(self):
        if not self.approval_line_ids:
            raise ValidationError(_("Please add at least one approval line before starting the approval process."))

        # Update sequences before validation
        for index, line in enumerate(self.approval_line_ids.sorted('sequence'), start=1):
            line.sequence = index

        missing_info = []
        for line in self.approval_line_ids:
            if not line.user_id and not line.approver_role_id:
                missing_info.append(_("Line %s: Missing both approver role and user") % line.sequence)
            elif not line.user_id:
                missing_info.append(_("Line %s: User is missing for approval role ['%s']") % (line.sequence, line.approver_role_id.name))
        if missing_info:
            raise ValidationError(_("Please complete the following approval lines:\n%s") % "\n".join(missing_info))

        self.state = "approval_in_process"
        self.approval_status = 'partially_approved'
        self._action_send_mail_to_next_approver()

    def _action_send_mail_to_next_approver(self):
        self.ensure_one()

        next_approver_line = self.approval_line_ids.filtered(
            lambda l: l.status == 'pending'
        ).sorted('sequence')

        if next_approver_line:
            next_approver_line = next_approver_line[0]
            template = self.env.ref('recruitment_enhancement.mail_template_requisition_submit_id', raise_if_not_found=False)

            if template:
                template.with_context(
                    recipient_user=next_approver_line.user_id,
                    requisition_name=self.name,
                ).sudo().send_mail(
                    self.id,
                    force_send=True,
                    email_values={
                        'email_to': next_approver_line.user_id.partner_id.email,
                        'recipient_ids': False
                    }
                )

    def _send_final_approval_notification(self):
        """Send notification to all approvers when approval process is complete"""
        self.ensure_one()

        self._generate_requisition_pdf()

        all_approvers = self.approval_line_ids.mapped('user_id')

        if not all_approvers:
            return

        is_approved = self.state == 'approved'
        status_text = _('Approved') if is_approved else _('Rejected')

        template = self.env.ref('recruitment_enhancement.mail_template_requisition_final_notification',
                               raise_if_not_found=False)

        for approver in all_approvers:
            if not approver.partner_id.email:
                continue

            if template:
                template.with_context(
                    recipient_name=approver.name,
                    requisition_name=self.name,
                    final_status=status_text,
                    is_approved=is_approved,
                ).sudo().send_mail(
                    self.id,
                    force_send=True,
                    email_values={
                        'email_to': approver.partner_id.email,
                        'recipient_ids': False,
                        'attachment_ids': [(4, self.attachment_id.id)] if self.attachment_id else []
                    }
                )
            else:
                # Fallback if template doesn't exist
                url = "%s/web#id=%s&model=%s&view_type=form" % (self.get_base_url(), self.id, self._name)
                body = _(
                    "<p>Dear %(name)s,</p>"
                    "<p>The approval process for Requisition <b>%(req)s</b> has been completed.</p>"
                    "<p>Final Status: <b>%(status)s</b></p>"
                    "<p><a href='%(url)s'>View Requisition</a></p>"
                ) % {
                    'name': approver.name,
                    'req': self.name,
                    'status': status_text,
                    'url': url,
                }

                attachment_ids = [(4, self.attachment_id.id)] if self.attachment_id else []

                self.env['mail.mail'].sudo().create({
                    'subject': _("Requisition %s - Final Status: %s") % (self.name, status_text),
                    'body_html': body,
                    'email_to': approver.partner_id.email,
                    'attachment_ids': attachment_ids,
                }).send()

    def action_approve_requisition(self):
        self.ensure_one()
        login_user = self.env.user

        if login_user != self.current_approver_id:
            raise AccessError(_("You are not authorized to approve this requisition. Current approver is %s.") % (
                    self.current_approver_id.name or _("Unknown")))

        approval_line = self.approval_line_ids.filtered(
            lambda line: line.user_id == login_user and line.status == 'pending')[:1]

        if not approval_line:
            raise AccessError(_("No pending approval line found for you or you have already approved it."))

        if approval_line:
            approval_line.approved = True
            approval_line.status = 'approved'
            approval_line.approval_date = fields.Datetime.now()
            self._update_approval_status()

            remaining_pending = self.approval_line_ids.filtered(lambda l: l.status == 'pending')

            if remaining_pending:
                self._action_send_mail_to_next_approver()

        approval_signed_required = False
        rejected_signed_required = False
        if approval_line.approval_signed:
            approval_signed_required = True

        if approval_line.rejected_signed:
            rejected_signed_required = True

        # Open wizard for signature
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sign Approval'),
            'res_model': 'approval.team.line',
            'view_mode': 'form',
            'view_id': self.env.ref('recruitment_enhancement.approval_team_line_approved_view_form').id,
            'res_id': approval_line.id,
            'target': 'new',
            'context': {
                'default_requisition_id': self.id,
                'default_approval_line_id': approval_line.id,
                'default_user_id': login_user.id,
                'default_contract_id': self.id,
                'form_view_initial_mode': 'edit',
                'default_approval_signed': approval_signed_required,
                'default_rejected_signed': rejected_signed_required,
            },
        }

    def action_reject_requisition(self):
        self.ensure_one()
        login_user = self.env.user

        if login_user != self.current_approver_id:
            raise AccessError(_("You are not authorized to reject this requisition. Current approver is %s.") % (
                    self.current_approver_id.name or _("Unknown")))

        line = self.approval_line_ids.filtered(lambda l: l.user_id == login_user and l.status == 'pending')[:1]
        if not line:
            raise AccessError(_("No pending approval line found for you."))

        # Mark the line as rejected; user will enter the reason in the popup form
        line.write({
            'status': 'rejected',
            'approval_date': fields.Datetime.now(),
            'approved': False,
        })

        other_lines = self.approval_line_ids.filtered(lambda l: l.status == 'pending')
        other_lines.write({'status': 'rejected'})

        # Mark requisition as rejected
        self.write({
            'state': 'rejected',
            'approval_status': 'rejected'
        })

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

    def _update_approval_status(self):
        total_lines = len(self.approval_line_ids)
        approved_count = len(self.approval_line_ids.filtered(lambda l: l.status == 'approved'))
        rejected_count = len(self.approval_line_ids.filtered(lambda l: l.status == 'rejected'))
        pending_count = len(self.approval_line_ids.filtered(lambda l: l.status == 'pending'))

        if pending_count > 0:
            self.approval_status = 'partially_approved'
        elif rejected_count > 0:
            self.state = "rejected"
            self.approval_status = 'rejected'
        else:
            self.state = "approved"
            self.approval_status = 'fully_approved'


    def _notify_approval_line_users(self, status, action_user, reason=False):
        self.ensure_one()
        partners = self.approval_line_ids.mapped('user_id.partner_id')
        if not partners:
            return

        template = self.env.ref('recruitment_enhancement.mail_template_requisition_line_update',
                                raise_if_not_found=False)
        url = "%s/web#id=%s&model=%s&view_type=form" % (self.get_base_url(), self.id, self._name)

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

    @api.depends(
        'create_uid',
        'hr_coordinator_id',
        'state',
        'line_manager_ids.user_id', 'line_manager_ids.sign_initials', 'line_manager_ids.sequence',
        'general_manager_ids.user_id', 'general_manager_ids.sign_initials', 'general_manager_ids.sequence',
        'cfo_ids.user_id', 'cfo_ids.sign_initials', 'cfo_ids.sequence',
        'hcm_manager_ids.user_id', 'hcm_manager_ids.sign_initials', 'hcm_manager_ids.sequence',
    )
    def _compute_allowed_user_ids(self):
        state_stage_map = {
            'to_line_manager': 'line_manager',
            'to_gm': 'general_manager',
            'to_cfo': 'cfo',
            'to_hcm': 'gm_hcm',
        }
        all_stages = ('line_manager', 'general_manager', 'cfo', 'gm_hcm')
        for rec in self:
            allowed = set()

            if rec.create_uid:
                allowed.add(rec.create_uid.id)
            if rec.hr_coordinator_id:
                allowed.add(rec.hr_coordinator_id.id)

            # Users who already signed keep access.
            for stage in all_stages:
                signed_users = rec._stage_lines(stage).filtered(lambda l: l.sign_initials).mapped('user_id')
                allowed.update(u.id for u in signed_users)

    # def _has_document(self, document_code):
    #     self.ensure_one()
    #     return bool(
    #         self.document_line_ids.filtered(
    #             lambda line: line.document_type_id.name == document_code and line.document_file
    #         )[:1]
    #     )

    # @api.depends('document_line_ids.document_type_id', 'document_line_ids.document_file')
    # def _compute_document_complete(self):
    #     for rec in self:
    #         rec.document_complete = rec._has_document('organogram')

    @api.depends('create_date', 'hcm_date')
    def _compute_approval_cycle_days(self):
        for rec in self:
            if rec.create_date and rec.hcm_date:
                rec.approval_cycle_days = (rec.hcm_date.date() - rec.create_date.date()).days
            else:
                rec.approval_cycle_days = 0


    def _check_required_documents(self):
        pass
        # for rec in self:
        #     if not rec.document_complete:
        #         raise ValidationError(_('Attach requisition form, job description, and organogram before submission.'))

    def _stage_lines(self, stage):
        self.ensure_one()
        return self[self.STAGE_FIELDS[stage]].sorted(lambda l: (l.sequence, l.id))

    def _pending_stage_lines(self, stage):
        self.ensure_one()
        return self._stage_lines(stage).filtered(lambda l: l.required and not l.sign_initials)

    def _send_line_mail(self, line, stage):
        req = line.requisition_id
        email_to = line.user_id.partner_id.email
        if not email_to:
            return
        url = "%s/web#id=%s&model=%s&view_type=form" % (req.get_base_url(), req.id, req._name)
        template = self.env.ref('recruitment_enhancement.mail_template_requisition_submit', raise_if_not_found=False)
        if template:
            template.with_context(
                approve_user=line.user_id.name,
                request='approval',
                stage=req.STAGE_LABELS[stage],
                url=url,
            ).sudo().send_mail(
                req.id,
                force_send=True,
                email_values={'email_to': email_to}
            )
        else:
            body = _(
                "<p>Dear %(name)s,</p>"
                "<p>Requisition <b>%(req)s</b> requires your action at <b>%(stage)s</b>.</p>"
                "<p><a href='%(url)s'>Open Requisition</a></p>"
            ) % {
                       'name': line.user_id.name,
                       'req': req.name,
                       'stage': req.STAGE_LABELS[stage],
                       'url': url,
                   }
            self.env['mail.mail'].sudo().create({
                'subject': _("Requisition Approval Request: %s") % req.name,
                'body_html': body,
                'email_to': email_to,
            }).send()
        line.sent_date = fields.Date.today()

    def _notify_next_for_stage(self, stage):
        self.ensure_one()
        pending = self._pending_stage_lines(stage)
        if pending:
            self._send_line_mail(pending[0], stage)
            return True
        return False

    def _log_decision(self, level, decision, note=False):
        self.ensure_one()
        self.env['recruitment.requisition.approval'].create({
            'requisition_id': self.id,
            'level': level,
            'approver_id': self.env.user.id,
            'decision': decision,
            'note': note or False,
            'decision_date': fields.Datetime.now(),
        })

    def _notify_initiator_return(self, level, reason):
        self.ensure_one()
        emails = [self.create_uid.partner_id.email]
        if self.hr_coordinator_id and self.hr_coordinator_id.partner_id.email:
            emails.append(self.hr_coordinator_id.partner_id.email)
        emails = [e for e in emails if e]
        if not emails:
            return
        template = self.env.ref('recruitment_enhancement.mail_template_requisition_returned', raise_if_not_found=False)
        if template:
            url = "%s/web#id=%s&model=%s&view_type=form" % (self.get_base_url(), self.id, self._name)
            template.with_context(
                stage=self.STAGE_LABELS[level],
                reason=reason or _('No feedback'),
                url=url,
            ).sudo().send_mail(
                self.id,
                force_send=True,
                email_values={'email_to': ",".join(emails)}
            )
        else:
            self.env['mail.mail'].sudo().create({
                'subject': _("Requisition Returned: %s") % self.name,
                'body_html': _(
                    "<p>Requisition <b>%(req)s</b> was returned/rejected at <b>%(stage)s</b>.</p>"
                    "<p>Feedback: %(reason)s</p>"
                ) % {'req': self.name, 'stage': self.STAGE_LABELS[level], 'reason': reason or _('No feedback')},
                'email_to': ",".join(emails),
            }).send()

    def _validate_hcm_checklist(self):
        self.ensure_one()
        if not self._has_document('job_description'):
            raise ValidationError(_("Job description must be attached."))
        if not self._has_document('organogram'):
            raise ValidationError(_("Organogram must be attached."))

        # real flow validation + checklist tick validation
        if self._pending_stage_lines('general_manager'):
            raise ValidationError(_("General Manager approval is not complete."))
        if self._pending_stage_lines('cfo'):
            raise ValidationError(_("Finance approval is not complete."))

        if not self.hcm_check_job_description:
            raise ValidationError(_("Tick 'Job description received' checklist item."))
        if not self.hcm_check_organogram:
            raise ValidationError(_("Tick 'Organogram attached' checklist item."))
        if not self.hcm_check_finance_approved:
            raise ValidationError(_("Tick 'Finance approval confirmed' checklist item."))
        if not self.hcm_check_gm_approved:
            raise ValidationError(_("Tick 'General Manager approval confirmed' checklist item."))
        if not self.hcm_check_all_signatories:
            raise ValidationError(_("Tick 'All signatories have signed' checklist item."))
        if not self.hcm_completed_by_id:
            raise ValidationError(_("Set 'Checklist Completed By' (HR Coordinator)."))

    def _advance_after_signed(self, stage):
        self.ensure_one()
        if self._notify_next_for_stage(stage):
            return

        now = fields.Datetime.now()
        if stage == 'line_manager':
            self.line_manager_date = now
            self.state = 'to_gm'
            self.hcm_check_gm_approved = False
            self._notify_next_for_stage('general_manager')
        elif stage == 'general_manager':
            self.gm_date = now
            self.hcm_check_gm_approved = True
            self.state = 'to_cfo'
            self._notify_next_for_stage('cfo')
        elif stage == 'cfo':
            self.cfo_date = now
            self.hcm_check_finance_approved = True
            self.state = 'to_hcm'
            self._notify_next_for_stage('gm_hcm')
        elif stage == 'gm_hcm':
            self._validate_hcm_checklist()
            self.hcm_date = now
            self.hcm_check_date = fields.Datetime.now()
            self.state = 'approved'
            self._create_job_position_if_needed()

    def _on_line_signed(self, stage, line):
        self.ensure_one()
        if line.status in ('rejected', 'incomplete'):
            self.state = 'rejected'
            self.rejection_reason = line.comment
            self._log_decision(stage, 'rejected', line.comment)
            self._notify_initiator_return(stage, line.comment)
            return

        self._log_decision(stage, 'approved', line.comment)
        self._advance_after_signed(stage)

    def _check_has_approvers(self):
        for rec in self:
            if not rec.line_manager_ids:
                raise ValidationError(_("Please add at least one Line Manager approver."))
            if not rec.general_manager_ids:
                raise ValidationError(_("Please add at least one General Manager approver."))
            if not rec.cfo_ids:
                raise ValidationError(_("Please add at least one CFO approver."))
            if not rec.hcm_manager_ids:
                raise ValidationError(_("Please add at least one HCM approver."))

    def action_submit(self):
        for rec in self:
            rec._check_required_documents()
            rec.state = 'in_process'

    def _populate_approval_lines(self):
        pass

    def action_reject(self):
        for rec in self:
            rec.state = 'rejected'
            rec._log_decision('line_manager', 'rejected', rec.rejection_reason)

    def action_reset_to_draft(self):
        for rec in self:
            # current_approver_id unlink this many2one field
            rec.write({'state': 'draft', 'rejection_reason': False, 'current_approver_id': False})
            all_lines = rec.approval_line_ids
            if all_lines:
                all_lines.unlink()

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_recruitment_in_process(self):
        if not self.job_id.website_published:
            raise ValidationError(_("Please publish the job position before starting the recruitment process."))
        else:
            self.state = 'recruitment_in_process'

    def action_done(self):
        self.write({'state': 'done',})

    def action_open_shortlisting(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Shortlisting'),
            'res_model': 'recruitment.shortlisting',
            'view_mode': 'tree,form',
            'domain': [('requisition_id', '=', self.id)],
            'context': {'default_requisition_id': self.id},
        }

    def _create_job_position_if_needed(self):
        self.ensure_one()
        if self.job_id:
            # Keep existing job linked to this requisition.
            if not self.job_id.requisition_id:
                self.job_id.requisition_id = self.id
            return self.job_id

        job_name = self.name and _("Job Position - %s") % self.name or _("Job Position")
        job_vals = {
            'name': job_name,
            'department_id': self.department_id.id if self.department_id else False,
            'company_id': self.company_id.id,
            'requisition_id': self.id,
            'description': self.job_desc or False,
            'ee_target_youth': self.ee_target_youth,
            'ee_target_women': self.ee_target_women,
            'ee_target_pwd': self.ee_target_pwd,
            'job_summary':self.job_summary,
            'interviewer_ids':[(6,0,self.interviewer_ids.ids)],
            'skill_ids':[(6,0,self.skill_ids.ids)],
            'minimum_qualifications':self.minimum_qualifications,
            'required_experience':self.required_experience,
            'survey_id':self.survey_id,
        }
        job = self.env['hr.job'].create(job_vals)
        self.job_id = job.id
        return job

    def action_create_job_position(self):
        self.ensure_one()
        if self.state != 'approved':
            raise ValidationError(_("Job position can only be created when requisition is Approved."))
        job = self._create_job_position_if_needed()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Job Position'),
            'res_model': 'hr.job',
            'view_mode': 'form',
            'res_id': job.id,
            'target': 'current',
        }


class RecruitmentRequisitionApprovalLineBase(models.AbstractModel):
    _name = 'recruitment.requisition.approval.line.base'
    _description = 'Requisition Approval Line Base'
    _order = 'sequence, id'

    _stage_code = False
    _stage_state = False

    requisition_id = fields.Many2one('recruitment.requisition', required=True, ondelete='cascade')
    sequence = fields.Integer(default=1)
    user_id = fields.Many2one('res.users', string='Approver', required=True)
    required = fields.Boolean(default=True)

    status = fields.Selection([
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('incomplete', 'Incomplete Documentation'),
    ], string='Status')
    comment = fields.Text('Comment')
    sign_initials = fields.Binary(string='Signature', copy=False)
    date = fields.Datetime(string='Date', readonly=True)
    sent_date = fields.Date(string='Sent Date', readonly=True)
    is_editable = fields.Boolean(compute='_compute_is_editable', string="Can Edit")

    @api.depends(
        'user_id',
        'requisition_id.state',
        'requisition_id.line_manager_ids.sign_initials',
        'requisition_id.general_manager_ids.sign_initials',
        'requisition_id.cfo_ids.sign_initials',
        'requisition_id.hcm_manager_ids.sign_initials',
    )
    def _compute_is_editable(self):
        for rec in self:
            rec.is_editable = False
            if rec.user_id.id != self.env.user.id:
                continue
            if rec.requisition_id.state != rec._stage_state:
                continue
            pending = rec.requisition_id._pending_stage_lines(rec._stage_code)
            rec.is_editable = bool(pending and pending[0].id == rec.id)

    def _validate_sign_sequence(self):
        self.ensure_one()
        req = self.requisition_id
        if req.state != self._stage_state:
            raise ValidationError(_("You can sign only when requisition is in your stage."))
        stage_lines = req._stage_lines(self._stage_code)
        pending = stage_lines.filtered(lambda l: l.required and not l.sign_initials)
        if not pending or pending[0].id != self.id:
            raise ValidationError(_("You cannot sign before previous approver has signed."))
        if self.user_id.id != self.env.user.id:
            raise AccessError(_("You cannot sign on behalf of another user."))

    def action_sign_line(self):
        self.ensure_one()
        if self.user_id.id != self.env.user.id:
            raise AccessError(_("You cannot sign on behalf of another user."))
        if not self.status:
            raise ValidationError(_("Please set status before signing."))
        if not self.comment or not self.comment.strip():
            raise ValidationError(_("Please add comment before signing."))
        self._validate_sign_sequence()
        return {
            'name': _('Sign'),
            'type': 'ir.actions.act_window',
            'res_model': 'recruitment.requisition.signature.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_requisition_id': self.requisition_id.id,
                'default_line_model': self._name,
                'default_line_id': self.id,
                'default_user_id': self.user_id.id,
            },
        }

    def action_send_mail(self):
        self.ensure_one()
        self.requisition_id._send_line_mail(self, self._stage_code)

    def write(self, vals):
        trigger_records = self.browse()
        for rec in self:
            if vals.get('sign_initials'):
                rec._validate_sign_sequence()
                status = vals.get('status') or rec.status
                comment = vals.get('comment') if 'comment' in vals else rec.comment
                if not status:
                    raise ValidationError(_("Please set status before signing."))
                if not comment or not comment.strip():
                    raise ValidationError(_("Please add comment before signing."))
                vals = dict(vals, date=fields.Datetime.now())
                trigger_records |= rec

        res = super().write(vals)

        for rec in trigger_records:
            rec.requisition_id._on_line_signed(rec._stage_code, rec)
        return res


class RecruitmentRequisitionLineManager(models.Model):
    _name = 'recruitment.requisition.line.manager'
    _inherit = 'recruitment.requisition.approval.line.base'
    _description = 'Requisition Line Manager Approval Line'

    _stage_code = 'line_manager'
    _stage_state = 'to_line_manager'


class RecruitmentRequisitionGeneralManager(models.Model):
    _name = 'recruitment.requisition.general.manager'
    _inherit = 'recruitment.requisition.approval.line.base'
    _description = 'Requisition General Manager Approval Line'

    _stage_code = 'general_manager'
    _stage_state = 'to_gm'


class RecruitmentRequisitionCFO(models.Model):
    _name = 'recruitment.requisition.cfo'
    _inherit = 'recruitment.requisition.approval.line.base'
    _description = 'Requisition CFO Approval Line'

    _stage_code = 'cfo'
    _stage_state = 'to_cfo'


class RecruitmentRequisitionHCM(models.Model):
    _name = 'recruitment.requisition.hcm'
    _inherit = 'recruitment.requisition.approval.line.base'
    _description = 'Requisition HCM Approval Line'

    _stage_code = 'gm_hcm'
    _stage_state = 'to_hcm'


class RecruitmentRequisitionApproval(models.Model):
    _name = 'recruitment.requisition.approval'
    _description = 'Requisition Approval Log'
    _order = 'decision_date desc, id desc'

    requisition_id = fields.Many2one('recruitment.requisition', required=True, ondelete='cascade')
    level = fields.Selection([
        ('line_manager', 'Line Manager'),
        ('general_manager', 'General Manager'),
        ('cfo', 'CFO'),
        ('gm_hcm', 'GM HCM'),
    ], required=True)
    approver_id = fields.Many2one('res.users', required=True)
    decision = fields.Selection([
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], required=True)
    decision_date = fields.Datetime(required=True)
    note = fields.Text()
