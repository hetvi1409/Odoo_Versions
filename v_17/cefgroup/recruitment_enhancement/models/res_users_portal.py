from odoo import api, fields, models, _


class ResUser(models.Model):
    _name = 'applicant.profile'
    _description = "Applicant Profiles"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, copy=False)
    email_from = fields.Char(string='Email', required=True, copy=False)
    phone = fields.Char(string='Phone', required=True, copy=False)
    title_id = fields.Many2one('res.partner.title', string="Title")
    initial = fields.Char(string="Initial", copy=False)
    surname = fields.Char(string="Surname", copy=False)
    country_id = fields.Many2one('res.country', string="Nationality",
                                 ondelete='restrict', copy=False)
    date_of_birth = fields.Date(string="Date of Birth", copy=False)
    gender = fields.Selection(
        [('female', 'Female'), ('male', 'Male'), ('other', 'Other')],
        string="Gender", copy=False)
    race = fields.Selection([('african', 'African'), ('white', 'White'),
                             ('coloured', 'Coloured'), ('indian', 'Indian'),
                             ('other', 'Other')], string="Race", copy=False)
    disability = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                  string='Disability', copy=False)
    desc_disability = fields.Text(string="Disability Description", copy=False)
    relocate = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                string="Willing to Relocate?", copy=False)
    employee_status = fields.Selection(
        [('internal', 'Internal'), ('external', 'External')],
        string='Employee Status')
    notice_period = fields.Selection(
        [('days', '30 Days'), ('month', '1 Calender Month'),
         ('immediate', 'Immediately'),
         ('other', 'Other')], string="Notice Period", copy=False)
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
        string="Higher Qualification", copy=False)
    current_salary = fields.Char(
        string="Current Salary (Total cost to company)")
    passport = fields.Char(string="ID / Passport / Visa Number", copy=False)
    language_id = fields.Many2one('res.lang', 'Home Language', copy=False)
    cv = fields.Binary(string="CV")
    cv_name = fields.Text(string="CV Name")
    picture = fields.Binary(string="Picture")
    terms_conditions = fields.Boolean(
        string='Do you agree to Terms and Conditions?')
    user_id = fields.Many2one('res.users', string="Related User", copy=False)

    applicant_skill_ids = fields.One2many('hr.applicant.skill', 'profile_id',
                                          string="Skills")
    skill_ids = fields.Many2many('hr.skill', compute='_compute_skill_ids',
                                 store=True)
    matching_skill_ids = fields.Many2many(comodel_name='hr.skill',
                                          string="Matching Skills",
                                          compute="_compute_skill_details")
    missing_skill_ids = fields.Many2many(comodel_name='hr.skill',
                                         string="Missing Skills",
                                         compute="_compute_skill_details")
    manager_id = fields.Many2one('res.users', string="Manager")
    application_count = fields.Integer(string="Application Count",
                                       compute='_compute_application_count')
    application_ids = fields.One2many('hr.applicant', 'applicant_id',
                                      "Job Applications")
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
        string="Number of years of experience in different roles/fields if any - Please specify")
    have_honours = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                    string='Do you have honours?')
    have_master = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                   string='Do you have Masters?')
    professional_body = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                         string='Are registered with any professional body?')
    source_id = fields.Many2one('utm.source', string='Source')

    @api.depends_context('active_id')
    @api.depends('skill_ids')
    def _compute_skill_details(self):
        job_id = self.env.context.get('active_id')
        if not job_id:
            self.matching_skill_ids = False
            self.missing_skill_ids = False
        else:
            for candidate in self:
                skill = self.env['hr.job'].browse(job_id).skill_ids
                candidate.matching_skill_ids = skill & candidate.skill_ids
                candidate.missing_skill_ids = skill - candidate.skill_ids

    @api.depends('applicant_skill_ids.skill_id')
    def _compute_skill_ids(self):
        for applicant in self:
            applicant.skill_ids = applicant.applicant_skill_ids.skill_id

    @api.depends()
    def _compute_application_count(self):
        """Compute Application Count"""
        for rec in self:
            application = self.env['hr.applicant'].search_count(
                [('applicant_id', '=', self.id)])
            rec.application_count = application

    def action_open_applications(self):
        """Open The Application"""
        return {
            'name': _('Application'),
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'res_model': 'hr.applicant',
            'domain': [('applicant_id', '=', self.id)],
        }

    @api.model
    def create(self, vals):
        """Supering the create function inorder to set the auction_seq number
        """
        res = super(ResUser, self).create(vals)
        # if res.user_id:
        #     res.user_id.sudo().action_reset_password()
        return res
