# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BursaryBursary(models.Model):
    _name = "bursary.bursary"
    _description = "Bursary"
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
        'website.published.mixin',
        'website.seo.metadata',
        # 'website.cover_properties.mixin',
        'website.searchable.mixin',
    ]

    def _compute_website_url(self):
        super(BursaryBursary, self)._compute_website_url()
        for rec in self:
            rec.website_url = "/bursary/%s" % (rec.id)

    website_id = fields.Many2one('website', readonly=False, store=True)
    name = fields.Char(string="Bursary Name", required=True, tracking=True)
    description = fields.Html(string="Description", required=True)
    application_start_date = fields.Date(string="Start Date", tracking=True)
    application_end_date = fields.Date(string="End Date", tracking=True)
    # funding_amount = fields.Monetary(string="Total Bursary Value", copy=False, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.
                                  currency_id)
    programme_ids = fields.Many2many('bursary.programme', string="Programme", copy=False, tracking=True)
    academic_year_id = fields.Many2one('academic.year', string="Academic Year")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Approval'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed')
    ], default='draft', tracking=True)
    eligibility = fields.Html(required=True)
    required_documents = fields.Html(string="Required Documents")
    website_published = fields.Boolean('Published on Website', default=False, copy=False, tracking=True)
    survey_id = fields.Many2one('survey.survey', string="Survey")
    question_and_page_ids = fields.One2many('survey.question',
                                            related="survey_id.question_and_page_ids",
                                            string='Sections and Questions',
                                            readonly=False, copy=False)
    bursary_count = fields.Integer(compute="_compute_bursary_count")
    active = fields.Boolean('Active', default=True)
    new_application_count = fields.Integer(compute="_compute_new_application_count")
    staging_application_count = fields.Integer(compute="_compute_new_application_count")

    @api.model
    def _compute_bursary_count(self):
        for rec in self:
            rec.bursary_count = self.env['bursary.application'].search_count([('bursary_id', '=', rec.id)])

    def write(self, vals):
        for rec in self:
            new_website_published = vals.get('website_published',
                                             rec.website_published)

            if rec.state == 'published' and not new_website_published:
                vals['state'] = 'approved'

            elif rec.state == 'approved' and new_website_published:
                vals['state'] = 'published'

            elif rec.state not in ['approved',
                                   'published'] and new_website_published:
                vals['website_published'] = False

        return super().write(vals)

    def action_open_website(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for rec in self:
            return {
                'type': 'ir.actions.act_url',
                'url': f"{base_url}/bursary/{rec.id}",
                'target': 'new',
            }

    def action_submit(self):
        for rec in self:
            rec.state = 'submitted'
            rec.message_post(
                body=_('The Bursary was submitted by %s') % (
                     rec.env.user.name))

    def action_approve(self):
        for rec in self:
            rec.state = 'approved'
            rec.message_post(
                body=_('The Bursary was approved by %s') % (
                     rec.env.user.name))

    def action_reject(self):
        for rec in self:
            rec.state = 'rejected'
            rec.message_post(
                body=_('The Bursary was rejected by %s') % (
                     rec.env.user.name))

    def action_publish(self):
        for rec in self:
            if rec.state == 'approved':
                rec.is_published = True
                rec.state = 'published'
                rec.message_post(
                    body=_('The Bursary was published by %s') % (
                         rec.env.user.name))
            else:
                raise UserError('Only approved bursaries can be published.')

    def action_unpublish(self):
        for rec in self:
            rec.is_published = False
            rec.state = 'approved'
            rec.message_post(
                body=_('The Bursary was unpublished by %s') % (
                     rec.env.user.name))

    def action_draft(self):
        for rec in self:
            rec.is_published = False
            rec.state = 'draft'
            rec.message_post(
                body=_('The Bursary was move back to draft by %s') % (
                     rec.env.user.name))

    def action_close_bursary(self):
        """"""
        bursary = self.env['bursary.bursary'].search([('state', '=', 'published')])
        today = fields.Date.today()
        for rec in bursary:
            if today >= rec.application_end_date:
                rec.action_close()

    def action_close(self):
        self.state = 'closed'
        self.is_published = False
        self.message_post(
            body=_('The Bursary was move closed by %s') % (
                 self.env.user.name))

    def action_create_elimination_survey(self):
        self.ensure_one()
        # Check if a survey already exists for this job
        existing_survey = self.env['survey.survey'].search(
            [('bursary_id', '=', self.id)], limit=1)
        if existing_survey:
            # If an existing survey is found, open it
            self.survey_id = existing_survey.id

        else:
            # If no survey exists, create a new one and set job_id
            new_survey = self.env['survey.survey'].create({
                'title': f"Additional Questions for {self.name}",
                'bursary_id': self.id,
                'survey_type': 'custom',
                'questions_layout': 'one_page',
                'access_mode': 'public',
                'scoring_type': 'scoring_with_answers'
            })

            [a_01, a_02] = self.env[
                'survey.question.answer'].create([{
                'value': 'Yes',
                'answer_score': 10.0,
                'is_correct': True
            }, {
                'value': 'No',
                'answer_score': 2.0,
                'is_correct': False
            }])
            [b_01, b_02] = self.env[
                'survey.question.answer'].create([{
                'value': 'Yes',
                'answer_score': 10.0,
                'is_correct': True
            }, {
                'value': 'No',
                'answer_score': 2.0,
                'is_correct': False
            }])
            [c_01, c_02] = self.env[
                'survey.question.answer'].create([{
                'value': 'Yes',
                'answer_score': 10.0,
                'is_correct': True
            }, {
                'value': 'No',
                'answer_score': 2.0,
                'is_correct': False
            }])
            [d_01, d_02] = self.env[
                'survey.question.answer'].create([{
                'value': 'Yes',
                'answer_score': 10.0,
                'is_correct': True
            }, {
                'value': 'No',
                'answer_score': 2.0,
                'is_correct': False
            }])
            [e_01, e_02] = self.env[
                'survey.question.answer'].create([{
                'value': 'Yes',
                'answer_score': 10.0,
                'is_correct': True
            }, {
                'value': 'No',
                'answer_score': 2.0,
                'is_correct': False
            }])
            self.env['survey.question'].create({
                'title': 'Are you between the age of 16 & 26 Age 16-26',
                'survey_id': new_survey.id,
                'sequence': 2,
                'constr_mandatory': True,
                'question_type': 'simple_choice',
                'suggested_answer_ids': [(6, 0, (a_01 | a_02).ids)]
            })
            self.env['survey.question'].create({
                'title': 'Do you already hold any previous academic or professional qualifications?',
                'survey_id': new_survey.id,
                'sequence': 2,
                'constr_mandatory': True,
                'question_type': 'simple_choice',
                'suggested_answer_ids': [(6, 0, (b_01 | b_02).ids)]
            })
            self.env['survey.question'].create({
                'title': 'Are you a citizen of South Africa?',
                'survey_id': new_survey.id,
                'sequence': 2,
                'constr_mandatory': True,
                'question_type': 'simple_choice',
                'suggested_answer_ids': [(6, 0, (c_01 | c_02).ids)]
            })
            self.env['survey.question'].create({
                'title': 'Are you undertaking further studies beyond your undergraduate qualification?',
                'survey_id': new_survey.id,
                'sequence': 2,
                'constr_mandatory': True,
                'question_type': 'simple_choice',
                'suggested_answer_ids': [(6, 0, (d_01 | d_02).ids)]
            })
            self.env['survey.question'].create({
                'title': "Is your parents' or guardian's total combined household income less than R600,000 per year?",
                'survey_id': new_survey.id,
                'sequence': 2,
                'constr_mandatory': True,
                'question_type': 'simple_choice',
                'suggested_answer_ids': [(6, 0, (e_01 | e_02).ids)]
            })
            self.survey_id = new_survey.id

    def action_view_application(self):
        """View Application"""
        return {
            'name': 'Bursary Application',
            'view_mode': 'tree,form',
            'res_model': 'bursary.application',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'create': False},
            'domain': [('bursary_id', '=', self.id)]
        }

    def action_view_elimination_survey(self):
        """View Application"""
        return {
            'name': 'Elimination Questions',
            'view_mode': 'form',
            'res_model': 'survey.survey',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.survey_id.id,
            'context': {'create': False},
        }

    def action_open_bursary_bursary_applications(self):
        """View Application"""
        return {
            'name': 'Application',
            'view_mode': 'tree,form',
            'res_model': 'bursary.application',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('bursary_id', '=', self.id)],
            'context': {'default_bursary_id': self.id},
        }

    @api.model
    def _compute_new_application_count(self):
        """Compute"""
        for rec in self:
            stage_new = self.env.ref('bursary_application.bursary_stage0')
            rec.new_application_count = self.env['bursary.application'].search_count([('stage_id', '=', stage_new.id), ('bursary_id', '=', rec.id)])
            stage_staging = self.env.ref('bursary_application.bursary_stage7')
            rec.staging_application_count = self.env['bursary.application'].search_count([('stage_id', '=', stage_staging.id), ('bursary_id', '=', rec.id)])

    def action_new_bursary_applications(self):
        """View Application"""
        stage = self.env.ref('bursary_application.bursary_stage0')
        application = self.env['bursary.application'].search(
            [('stage_id', '=', stage.id), ('bursary_id', '=', self.id)])
        return {
            'name': 'Application',
            'view_mode': 'tree,form',
            'res_model': 'bursary.application',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', application.ids)],
            'context': {'default_bursary_id': self.id},
        }

    def action_staging_bursary_applications(self):
        """View Application"""
        stage_staging = self.env.ref('bursary_application.bursary_stage7')
        staging_application_count = self.env['bursary.application'].search([('stage_id', '=', stage_staging.id), ('bursary_id', '=', self.id)])

        return {
            'name': 'Application',
            'view_mode': 'tree,form',
            'res_model': 'bursary.application',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', staging_application_count.ids)],
            'context': {'default_bursary_id': self.id},
        }
