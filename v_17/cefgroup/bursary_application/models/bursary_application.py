from odoo import api, models, fields

class BursaryApplication(models.Model):
    _name = "bursary.application"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Bursary Application"

    # Personal Information
    #
    subject = fields.Char("Subject / Application", required=False, tracking=True)

    name = fields.Char()
    date_of_birth = fields.Date(required=True)
    id_number = fields.Char()
    nationality = fields.Selection([
        ('sa', 'South African'),
        ('non_sa', 'Non-South African')
    ], required=True)
    race = fields.Selection([
        ('african', 'African'),
        ('coloured', 'Coloured'),
        ('indian', 'Indian'),
        ('white', 'White')
    ], required=True)
    gender = fields.Selection([
        ('female', 'Female'),
        ('male', 'Male')
    ], required=True)
    disability = fields.Selection([('yes', 'Yes'), ('no', 'No')],)
    disability_type = fields.Char()
    student_number = fields.Char(string='Student Contact Number')
    student_email = fields.Char(string='Student Email')
    province_id = fields.Many2one('res.province', required=True)

    # Parent/Guardian Details
    contact_number = fields.Char(required=True)
    alt_number = fields.Char()
    email = fields.Char(required=True)
    address = fields.Char(required=True)
    # income_below_600k = fields.Selection([('yes', 'Yes'), ('no', 'No')],
    #                                      string="Income Below (600K)", help='Does the combined household income fall below threshold', required=True)
    mother_name = fields.Char(required=True)
    father_name = fields.Char()
    guardian_name = fields.Char()
    annual_income = fields.Float()
    payslips = fields.Binary(attachment=True)
    parent_deceased = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Whether one or both parents are deceased")
    death_certificate = fields.Binary(attachment=True)

    # Academic Information
    highest_grade = fields.Char(required=True)
    grade12_avg = fields.Float(required=True)
    currently_studying = fields.Boolean()
    academic_records = fields.Binary(attachment=True)
    current_qualification = fields.Char()
    institution = fields.Char()
    year_of_completion = fields.Char()
    funding_source = fields.Selection([
        ('parents', 'Parents'),
        ('loan', 'Loan'),
        ('bursary', 'Bursary'),
        ('nsfas', 'NSFAS'),
        ('other', 'Other')
    ])
    # age_16_26 = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Age Group 16–26", help="Are you between the age of 16 and 26?", required=True)
    # is_citizen = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Citizenship", help="Are you a South African citizen?", required=True)
    age = fields.Integer("Applicant's age")
    # Study Plans
    applied_next_year = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Applied for Next Year", help="Have you applied for university studies next year")
    institution_type = fields.Selection([
        ('public', 'Public'),
        ('private', 'Private'),
        ('international', 'International')
    ])
    proposed_institution = fields.Char()
    qualification_type = fields.Selection([
        ('degree', 'Degree'),
        ('diploma', 'Diploma'),
        ('certificate', 'Higher Certificate'),
        ('postgrad', 'Postgraduate Diploma'),
        ('other', 'Other')
    ])

    # Funding Status
    applied_bursaries = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Funding Status", help="Have you applied for any bursaries or funding (including NSFAS)")
    received_bursary = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Received Bursary Before", help='Have you received any bursary or funding to date?')
    # has_previous_qualifications = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Previous Qualifications", help='Do you already hold any academic or professional qualifications?')
    # further_study_post_undergrad = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Studying Beyond Undergraduate", help='Are you undertaking studies beyond your undergraduate qualification?')
    bursary_details = fields.Char()

    # Document Uploads
    mother_id = fields.Binary(attachment=True)
    father_id = fields.Binary(attachment=True)
    mother_payslip = fields.Binary(attachment=True)
    father_payslip = fields.Binary(attachment=True)
    student_id = fields.Binary(attachment=True)
    matric_results = fields.Binary(attachment=True)
    tertiary_results = fields.Binary(attachment=True)
    proof_of_registration = fields.Binary(attachment=True)
    guardian_death_certificate = fields.Binary(attachment=True)

    # Declaration
    declaration = fields.Boolean(required=True)
    bursary_id = fields.Many2one('bursary.bursary', string="Bursary")

    # Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft', tracking=True)

    surname = fields.Char(string="Surname")
    place_of_birth = fields.Char(string="Place of Birth")
    current_activity = fields.Selection([('gap', 'Gap Year'),
                                         ('matric', 'Matric'),
                                         ('college', 'Tertiary/College')])

    def _get_default_stage(self):
        stage_ids = []
        stage_ids = self.env['bursary.application.stage'].search([
            ('fold', '=', False)
        ], order='sequence asc', limit=1)
        return stage_ids.id if stage_ids else False

    stage_id = fields.Many2one('bursary.application.stage', copy=False, default=_get_default_stage)

    @api.onchange('bursary_id')
    def _onchange_bursary(self):
        for rec in self:
            if rec.bursary_id.name:
                rec.subject = rec.name + ' - ' + rec.bursary_id.name

    @api.model
    def create(self, vals):
        """Supering the create function inorder to set the auction_seq number
        """
        res = super(BursaryApplication, self).create(vals)
        res._onchange_bursary()
        return res

    def action_elimination(self):
        survey = self.env['survey.user_input'].search([('bursary_application_id', '=', self.id)], limit="1")
        if survey.scoring_success:
            stage = self.env.ref('bursary_application.bursary_stage0')
        else:
            stage = self.env.ref('bursary_application.bursary_stage7')
        # if (self.age_16_26 == 'yes' and self.has_previous_qualifications == 'yes'
        #         and self.is_citizen == 'yes' and self.further_study_post_undergrad == 'yes'
        # and self.income_below_600k == 'yes'):
        #     stage = self.env.ref('bursary_application.bursary_stage0')
        # else:
        #     stage = self.env.ref('bursary_application.bursary_stage7')
        self.stage_id = stage.id

    def action_submit(self):
        for rec in self:
            rec.state = 'submitted'

    def action_review(self):
        for rec in self:
            rec.state = 'review'

    def action_approve(self):
        for rec in self:
            rec.state = 'approved'

    def action_rejected(self):
        for rec in self:
            rec.state = 'rejected'

    def action_eliminated_questions(self):
        """View Application"""
        return {
            'name': 'Bursary Application',
            'view_mode': 'tree,form',
            'res_model': 'survey.user_input',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'create': False},
            'domain': [('bursary_application_id', '=', self.id)]
        }

    # def calculate_screening_point(self):
    #     """Compute screening point"""
    #     for record in self:
    #         grade12_avg, age = False, False
    #         if record.grade12_avg >= 70:
    #             grade12_avg = True
    #         birth_age = fields.Date.today().year - record.date_of_birth.year
    #         if 12 <= birth_age >= 26:
    #             age = True
    #         if age and grade12_avg:
    #             record.stage_id = self.env.ref('bursary_application.bursary_stage0').id
    #         else:
    #             record.stage_id = self.env.ref('bursary_application.stage_job7').id
