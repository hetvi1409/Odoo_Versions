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
    # staging_application_count = fields.Integer(compute="_compute_new_application_count")


    def _compute_qualification_application_count(self):
        for job in self:
            job.qualification_application_count = self.env['hr.applicant'].search_count([
                ('stage_id.name', 'ilike', 'Qualification'),
                ('job_id', '=', job.id)
            ])

    # def _compute_open_application_count(self):
    #     hired_stages = self.env['hr.recruitment.stage'].search([('hired_stage', '=', True)])
    #     result = dict(self.env['hr.applicant']._read_group([
    #         ('job_id', 'in', self.ids),
    #         ('stage_id', 'not in', hired_stages.ids),
    #     ], ['job_id'], ['__count']))
    #     for job in self:
    #         job.open_application_count = result.get(job, 0)



    @api.depends('application_count')
    def _compute_staging_application_count(self):
        for job in self:
            job.staging_application_count = self.env[
                'hr.applicant'].search_count([
                ('stage_id.name', 'ilike', 'Staging'),
                ('job_id', '=', job.id)])

    def search_new_applications(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Applications',
            'res_model': 'hr.applicant',
            'view_mode': 'list,form',
            'domain': [
                ('job_id', '=', self.id),
                ('stage_id.name', 'ilike', 'New'),
            ],
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
        application = self.env['hr.applicant'].sudo().search(
            [('job_id', '=', self.id)])
        print('\n\n\n APPLICATION------------>',application.mapped('id'))
        matching_candidates = self.env['hr.applicant'].sudo().search(
            [('job_id', '=', self.id), ('skill_ids', 'in', self.job_skill_ids.skill_id.ids)])
        print('\n\n\n MATCHING_CANDIDATES------------>',matching_candidates)
        action.update({
            'name': _("Matching Profiles"),
            'context': context,
            'domain': [('id', 'in', matching_candidates.ids)],
            'views': [
                (self.env.ref(
                    'hr_recruitment.crm_case_tree_view_job').id,
                 'list'),
                (False, 'kanban'),
                (False, 'form'),
            ],
            'help': Markup(
                "<p class='o_view_nocontent_empty_folder'>%s</p>") % (
                        help_message_1),
        })
        return action



    # def action_search_matching_candidates(self):
    #     self.ensure_one()
    #     help_message_1 = _("No Matching Profiles")
    #     action = self.env['ir.actions.actions']._for_xml_id('recruitment_enhancement.action_applicant_profile')
    #     context = literal_eval(action['context'])
    #     context['active_id'] = self.id
    #     application = self.env['hr.applicant'].sudo().search(
    #         [('job_id', '=', self.id)]).mapped('applicant_id')
    #     matching_candidates = application.search(
    #         [('skill_ids', 'in', self.skill_ids.ids)])
    #     action.update({
    #         'name': _("Matching Profiles"),
    #         'context': context,
    #         'domain': [('id', 'in', matching_candidates.ids)],
    #         'views': [
    #             (self.env.ref(
    #                 'recruitment_enhancement.view_applicant_profile_list_skill').id,
    #              'list'),
    #             (False, 'kanban'),
    #             (False, 'form'),
    #         ],
    #         'help': Markup(
    #             "<p class='o_view_nocontent_empty_folder'>%s</p>") % (
    #                     help_message_1),
    #     })
    #     return action

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

        hr_officers = hr_officer_group.user_ids.filtered(lambda u: u.partner_id)
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

    @api.model_create_multi
    def create(self, vals_list):
        jobs = super(HrJob, self).create(vals_list)
        for job in jobs:
            job._generate_advert_pdf()
        return jobs

    def action_view_advert_pdf(self):
        """Redirects to PDF attachment when the smart button is clicked."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": f'/web/content/{self.attachment_id.id}?download=true',
            "target": "new",
        }

    def _compute_requisition_count(self):
        grouped = self.env['recruitment.requisition']._read_group(
            [('job_id', 'in', self.ids)],
            ['job_id'],
            ['__count'],
        )
        count_map = {job.id: count for job, count in grouped}
        for job in self:
            job.requisition_count = count_map.get(job.id, 0)

    def action_view_requisitions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Requisitions',
            'res_model': 'recruitment.requisition',
            'view_mode': 'list,form',
            'domain': [('job_id', '=', self.id)],
            'context': {'default_job_id': self.id},
        }
