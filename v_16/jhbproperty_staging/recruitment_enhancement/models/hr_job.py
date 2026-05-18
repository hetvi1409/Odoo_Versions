from odoo import api, fields, models, _
from markupsafe import Markup
from werkzeug import urls
import base64
from odoo.exceptions import ValidationError
from datetime import date
from ast import literal_eval


class HrJob(models.Model):
    _inherit = 'hr.job'

    requisition_id = fields.Many2one('recruitment.requisition', copy=False)
    requisition_count = fields.Integer(compute='_compute_requisition_count')

    ee_target_youth = fields.Boolean(string='EE Target: Youth')
    ee_target_women = fields.Boolean(string='EE Target: Women')
    ee_target_pwd = fields.Boolean(string='EE Target: PWD')

    attachment_id = fields.Many2one('ir.attachment', tracking=True, copy=False)
    create_job_advert_pdf = fields.Boolean(string="Create Job Advert PDF", default=False, copy=False,
                                           compute='_compute_job_advert_pdf')
    is_re_advertised = fields.Boolean(string='Is Re-Advertised?', default=False)
    re_advertised_job_id = fields.Many2one('hr.job', string="Re-Advertised Job")
    job_summary = fields.Html(
        related='requisition_id.job_summary',
        string='Job Summary',
        readonly=False,
        store=True,
    )
    skill_ids = fields.Many2many(comodel_name='hr.skill',
                                 string="Expected Skills")
    kpi_ids = fields.Many2many(
        comodel_name='hr.job.kpi',
        relation='hr_job_kpi_rel',
        column1='job_id',
        column2='kpi_id',
        string='KPIs'
    )
    kpi_names = fields.Char(string='KPI Names', compute='_compute_kpi_names', store=True)
    required_experience = fields.Char("Required Experience")
    minimum_qualifications = fields.Char(string="Minimum Qualifications")
    work_level = fields.Selection(
        [('executive', 'Executive Management'), ('senior', 'Senior Management'),
         ('middle', 'Middle Management'), ('junior', 'Junior Management'),
         ('skilled', 'Skilled Technical'), ('semi', 'Semi-Skilled'),
         ('unskilled', 'Unskilled')], string='Work Level', copy=False)
    salary = fields.Selection(
        [('market_related', 'Market Related'), ('negotiable', 'Negotiable')],
        string='Salary', copy=False)
    ee_position = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                   string='EE Position', copy=False)
    staging_application_count = fields.Integer(string="Failed Applications Count",
                                               compute="_compute_staging_application_count")
    user_role_id = fields.Many2one('hr.employee', "Role Reporting To",
                                   tracking=True,
                                   help="The Recruiter will be the default value for all Applicants Recruiter's field in this job position. The Recruiter is automatically added to all meetings with the Applicant.")
    new_application_count = fields.Integer()
    qualification_application_count = fields.Integer(compute='_compute_qualification_application_count', string="Qualification Application Count")
    closing_date = fields.Date(string="Application Closing Date")
    job_purpose = fields.Char(string="Job Purpose")
    company_overview = fields.Char(string="Company Overview")
    notes = fields.Text(string="Notes")

    # fields not in v16
    job_skill_ids = fields.One2many(
        comodel_name="hr.job.skill",
        inverse_name="job_id",
        string="Skills",
    )
    expected_degree = fields.Many2one("hr.recruitment.degree")
    current_job_skill_ids = fields.One2many(
        comodel_name="hr.job.skill",
        compute="_compute_current_job_skill_ids",
        search="_search_current_job_skill_ids",
        readonly=False,
    )
    skill_ids = fields.Many2many(
        comodel_name="hr.skill",
        compute="_compute_skill_ids",
        store=True,
    )
    stage_application_count = fields.Integer(
        compute='_compute_stage_application_count'
    )
    employee_skill_ids = fields.One2many('hr.employee.skill', 'employee_id', string="Skills")

    @api.depends('kpi_ids')
    def _compute_kpi_names(self):
        for job in self:
            if job.kpi_ids:
                job.kpi_names = ', '.join(job.kpi_ids.mapped('name'))
            else:
                job.kpi_names = ''

    @api.depends("job_skill_ids")
    def _compute_current_job_skill_ids(self):
        for job in self:
            job.current_job_skill_ids = job.job_skill_ids.filtered(
                lambda skill: not skill.valid_to or skill.valid_to >= fields.Date.today()
            )

    def _search_current_job_skill_ids(self, operator, value):
        if operator not in ('in', 'not in', 'any'):
            raise NotImplementedError()

        domain = ['|', ('valid_to', '=', False), ('valid_to', '>=', fields.Date.today())]

        if operator == 'any' and isinstance(value, list):
            domain = domain + value
        elif operator in ('in', 'not in'):
            domain = domain + [('id', 'in', value)]

        job_skill_ids = self.env['hr.job.skill'].search(domain).ids
        return [('job_skill_ids', 'in', job_skill_ids)]

    @api.depends("job_skill_ids.skill_id")
    def _compute_skill_ids(self):
        for job in self:
            job.skill_ids = job.job_skill_ids.mapped('skill_id')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals_job_skill = vals.pop("current_job_skill_ids", []) + vals.get("job_skill_ids", [])
            vals["job_skill_ids"] = vals_job_skill
        return super().create(vals_list)

    def write(self, vals):
        if "current_job_skill_ids" in vals or "job_skill_ids" in vals:
            vals_job_skill = vals.pop("current_job_skill_ids", []) + vals.get("job_skill_ids", [])
            vals["job_skill_ids"] = vals_job_skill
        return super().write(vals)

    @api.onchange('company_id')
    def onchange_company(self):
        if self.company_id:
            address_parts = []
            if self.company_id.street:
                address_parts.append(self.company_id.street)
            if self.company_id.street2:
                address_parts.append(self.company_id.street2)
            if self.company_id.city:
                address_parts.append(self.company_id.city)
            if self.company_id.state_id:
                address_parts.append(self.company_id.state_id.name)
            if self.company_id.zip:
                address_parts.append(self.company_id.zip)
            if self.company_id.country_id:
                address_parts.append(self.company_id.country_id.name)

            self.company_overview = ', '.join(address_parts)


    def _compute_qualification_application_count(self):
        qualification_stage = self.env['hr.recruitment.stage'].search([
            ('name', 'ilike', 'Initial Qualification')
        ], limit=1)

        if not qualification_stage:
            for job in self:
                job.qualification_application_count = 0
            return

        grouped = self.env['hr.applicant']._read_group(
            [
                ('job_id', 'in', self.ids),
                ('stage_id', '=', qualification_stage.id),
            ],
            ['job_id'],
            ['job_id'],
        )
        count_map = {data['job_id'][0]: data['job_id_count'] for data in grouped}
        for job in self:
            job.qualification_application_count = count_map.get(job.id, 0)

    def action_view_qualification_applications(self):
        self.ensure_one()
        qualification_stage = self.env['hr.recruitment.stage'].search([
            ('name', 'ilike', 'Initial Qualification')
        ], limit=1)

        if not qualification_stage:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Qualification Applications',
                'res_model': 'hr.applicant',
                'view_mode': 'kanban,list,form',
                'domain': [('job_id', '=', self.id)],
                'context': {
                    'default_job_id': self.id,
                    'search_default_job_id': self.id,
                },
            }

        # Fold all stages
        self.env['hr.recruitment.stage'].sudo().search([
            ('id', '!=', qualification_stage.id)
        ]).write({'fold': True})

        # Unfold the qualification stage
        qualification_stage.sudo().write({'fold': False})

        return {
            'type': 'ir.actions.act_window',
            'name': 'Qualification Applications',
            'res_model': 'hr.applicant',
            'view_mode': 'kanban,list,form',
            'domain': [('job_id', '=', self.id), ('stage_id', '=', qualification_stage.id)],
            'context': {
                'default_job_id': self.id,
                'default_stage_id': qualification_stage.id,
                'search_default_job_id': self.id,
            },
        }

    def _compute_stage_application_count(self):
        for job in self:
            stage = self.env.ref('recruitment_enhancement.stage_job7')
            job.stage_application_count = self.env['hr.applicant'].search_count([
                ('job_id', '=', job.id),
                ('stage_id', '=', stage.id),
            ])

    def action_view_stage_applications(self):
        self.ensure_one()
        stage = self.env.ref('recruitment_enhancement.stage_job7')

        # Fold ALL stages except our target
        self.env['hr.recruitment.stage'].sudo().search([
            ('id', '!=', stage.id)
        ]).write({'fold': True})

        stage.sudo().write({'fold': False})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stage Applications',
            'res_model': 'hr.applicant',
            'view_mode': 'kanban,list,form',
            'domain': [('job_id', '=', self.id)],
            'context': {
                'default_job_id': self.id,
                'default_stage_id': stage.id,
                'search_default_job_id': self.id,
            },
        }

    def action_view_new_applications(self):
        self.ensure_one()

        # Find "New" stage — it's the one with sequence=1 or named "New"
        stage = self.env['hr.recruitment.stage'].search([
            ('name', 'ilike', 'New')
        ], order='sequence asc', limit=1)

        if not stage:
            # fallback: just open all applications without folding
            return {
                'type': 'ir.actions.act_window',
                'name': 'New Applications',
                'res_model': 'hr.applicant',
                'view_mode': 'kanban,list,form',
                'domain': [('job_id', '=', self.id)],
                'context': {
                    'default_job_id': self.id,
                    'search_default_job_id': self.id,
                },
            }

        # Fold all stages except "New"
        self.env['hr.recruitment.stage'].sudo().search([
            ('id', '!=', stage.id)
        ]).write({'fold': True})

        stage.sudo().write({'fold': False})

        return {
            'type': 'ir.actions.act_window',
            'name': 'New Applications',
            'res_model': 'hr.applicant',
            'view_mode': 'kanban,list,form',
            'domain': [('job_id', '=', self.id)],
            'context': {
                'default_job_id': self.id,
                'default_stage_id': stage.id,
                'search_default_job_id': self.id,
            },
        }

    @api.depends('application_count')
    def _compute_staging_application_count(self):
        for job in self:
            job.staging_application_count = self.env[
                'hr.applicant'].search_count([
                ('stage_id.name', 'ilike', 'Staging'),
                ('job_id', '=', job.id)])

    def search_new_applications(self):
        self.ensure_one()
        first_stage = self._get_first_stage()
        domain = [('job_id', '=', self.id)]
        if first_stage:
            domain.append(('stage_id', '=', first_stage.id))
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Applications',
            'res_model': 'hr.applicant',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {
                'search_default_job_id': self.id,
                'default_job_id': self.id,
            },
        }

    def action_search_matching_candidates(self):
        self.ensure_one()
        help_message_1 = _("No Matching Profiles")
        action = self.env['ir.actions.actions']._for_xml_id('hr_recruitment.crm_case_categ0_act_job')
        context = literal_eval(action['context'])
        context['active_id'] = self.id
        matching_candidates = self.env['hr.applicant'].sudo().search(
            [('job_id', '=', self.id), ('skill_ids', 'in', self.skill_ids.ids)])
        action.update({
            'name': _("Matching Profiles"),
            'context': context,
            'domain': [('id', 'in', matching_candidates.ids)],
            'views': [
                (self.env.ref(
                    'hr_recruitment.crm_case_tree_view_job').id,
                 'tree'),
                (False, 'kanban'),
                (False, 'form'),
            ],
            'help': Markup(
                "<p class='o_view_nocontent_empty_folder'>%s</p>") % (
                        help_message_1),
        })
        return action

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
        self.ensure_one()
        hr_officer_group = self.env.ref("hr_recruitment.group_hr_recruitment_manager", raise_if_not_found=False)
        if not hr_officer_group:
            return

        hr_officers = hr_officer_group.users.filtered(lambda u: u.partner_id)
        partner_ids = hr_officers.mapped("partner_id").ids
        if not partner_ids:
            return

        self.message_notify(
            subject=_('Job Advert PDF generated'),
            body=_('Job Advert PDF generated for %s.') % self.name,
            partner_ids=partner_ids,
            email_layout_xmlid='mail.mail_notification_light',
        )

    def _compute_job_advert_pdf(self):
        for job in self:
            job.create_job_advert_pdf = bool(job.attachment_id)
            # job._generate_advert_pdf()
            # job.create_job_advert_pdf = True

    # @api.model_create_multi
    # def create(self, vals_list):
    #     jobs = super(HrJob, self).create(vals_list)
    #     for job in jobs:
    #         job._generate_advert_pdf()
    #     return jobs

    def action_view_advert_pdf(self):
        """Redirects to PDF attachment when the smart button is clicked."""
        self.ensure_one()
        self._generate_advert_pdf()
        return {
            "type": "ir.actions.act_url",
            "url": f'/web/content/{self.attachment_id.id}?download=true',
            "target": "new",
        }

    def _compute_requisition_count(self):
        grouped = self.env['recruitment.requisition']._read_group(
            [('job_id', 'in', self.ids)],
            ['job_id'],
            ['job_id'],
        )
        count_map = {data['job_id'][0]: data['job_id_count'] for data in grouped}
        for job in self:
            job.requisition_count = count_map.get(job.id, 0)

    def action_view_requisitions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Requisitions',
            'res_model': 'recruitment.requisition',
            'view_mode': 'tree,form',
            'domain': [('job_id', '=', self.id)],
            'context': {'default_job_id': self.id},
        }
