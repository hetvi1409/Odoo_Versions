from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from werkzeug import urls

class HousingSubsidy(models.Model):
    _name = "housing.subsidy"
    _description = "Housing Subsidy"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'individual_reg_number'

    individual_reg_number = fields.Char(string='Individual Registration Number',copy=False, readonly=True,)
    ind_phdb_res_num = fields.Char(string='Individual PHDB Resolution Number')
    credit_linked = fields.Boolean(string='Credit Linked')
    non_credit_linked = fields.Boolean(string='Non-Credit Linked')
    emergency_contact_name = fields.Char(string='Name')
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one("res.country.state",
                                             string='State')
    country_id = fields.Many2one('res.country', string='Country')
    telephone_number = fields.Char()
    mrg_certificate = fields.Many2one('ir.attachment', string="Certified copy of Marriage Certificate")
    identity_doc_self = fields.Many2one('ir.attachment', string="Certified copy of R.S.A. Bar Coded Identity Document")
    identity_doc_spouse = fields.Many2one('ir.attachment', string="Certified copy of R.S.A. Bar Coded Identity Document")
    divorce_certificate = fields.Many2one('ir.attachment', string="Certified copy of Divorce Settlement")
    spouse_death_certificate = fields.Many2one('ir.attachment', string="Certified copy of Spouse’s Death Certificate")
    proof_of_disability = fields.Many2one('ir.attachment', string="Proof of Disability")
    proof_of_loan = fields.Many2one('ir.attachment', string="Proof of loan granted by lender, where applicable")
    agreement_of_sale = fields.Many2one('ir.attachment', string="Certified copy of Agreement of Sale")
    compact_agreement = fields.Many2one('ir.attachment', string="Social compact agreement")
    agreement_with_conveyancer = fields.Many2one('ir.attachment', string="Certified copy of Agreement with Conveyancer (in the case of individual non credit linked subsidies)")
    building_contract_certificate = fields.Many2one('ir.attachment', string="Certified copy of Building Contract and Approved Building Plan")
    proof_of_income_certificate = fields.Many2one('ir.attachment', string="Certified copy of Proof of Monthly Income")
    residence_certificate = fields.Many2one('ir.attachment', string="Certified copy of Permanent Residence Permit (Bar Coded Permit)")

    state = fields.Selection([('draft','Draft'),('submitted','Submitted'),('pending_verify','Pending Verify'),('verified','Verified'),('pending_approval','Pending Approval'),('approve','Approve'),('rejected','Rejected')],default='draft')

    married = fields.Char(string='Married')
    divorced_with_dept = fields.Char(string='Divorced with Dependants')
    hab_long_partner = fields.Char(string='Habitually Co-habiting with long term partner')
    single_depend = fields.Char(string='Single with dependants')
    widow_depend = fields.Char(string='Widow/Widower with dependants')
    applicant_surname = fields.Char(string='Applicant Surname')
    spouse_surname = fields.Char(string='Spouse Surname')
    applicant_maiden_surname = fields.Char(string='Maiden or Former Surname')
    spouse_maiden_surname = fields.Char(string='Maiden or Former Surname')
    applicant_full_name = fields.Char(string='Applicant Full Names')
    spouse_full_name = fields.Char(string='Spouse Full Names')
    identity_number = fields.Char(string='Identity Number')
    identity_number_spouse = fields.Char(string='Identity Number')
    applicant_gender = fields.Selection([('male','Male'),('female','Female')])
    spouse_gender = fields.Selection([('male','Male'),('female','Female')])
    race_applicant = fields.Many2one('res.race',string='Race')
    race_spouse = fields.Many2one('res.race',string='Race')
    residential_address = fields.Char(string='Residential Address')
    disabled = fields.Boolean(string='Disabled')

    dependant_details_id = fields.One2many('dependant.details','dependant_id',string='Dependant Details')

    applicant_emp_details = fields.Selection([('unemployed','Unemployed'),('employed','Employed'),('self_employed','Self Employed'),('pensioner','Pensioner')])
    applicant_basic_income = fields.Float(string='Basic Monthly Income')
    applicant_regular_period = fields.Float(string='Regular Period Allowances')
    applicant_housing_allowance = fields.Float(string='Housing Allowance Payable(Loan Interest Subsidy)')
    applicant_regular_financial = fields.Float(string='Regular financial obligations met by employer on behalf of applicant')
    applicant_commission_received = fields.Float(string='Commission Received(12 months Average)')
    applicant_pension_disability = fields.Float(string='Pension or Disability Grant')
    applicant_total = fields.Float(string='Total')
    joint_total = fields.Float(string='Joint Total')
    subsidy_amt = fields.Float(string='Amount of Subsidy Applied for')
    spouse_total = fields.Float(string='Total')
    spouse_pension_disability = fields.Float(string='Pension or Disability Grant')
    spouse_commission_received = fields.Float(string='Commission Received(12 months Average)')
    spouse_regular_financial = fields.Float(string='Regular financial obligations met by employer on behalf of spouse')
    spouse_housing_allowance = fields.Float(string='Housing Allowance Payable(Loan Interest Subsidy)')
    spouse_regular_period = fields.Float(string='Regular Period Allowances')
    spouse_basic_income = fields.Float(string='Basic Monthly Income')
    spouse_emp_details = fields.Selection([('unemployed','Unemployed'),('employed','Employed'),('self_employed','Self Employed'),('pensioner','Pensioner')])

    citizen = fields.Boolean(string='Are you a South African Citizen?')
    citizen_country_id = fields.Many2one('res.country',string='Country of your Citizen')
    south_african_permit = fields.Char(string='South African Permanent Residence Permit Number')
    date_permit = fields.Date(string='Date Permit was issued')

    name_of_seller = fields.Char('Name of Seller')
    district = fields.Char('District')
    district_id = fields.Many2one('res.region', string='District')
    municipality_id = fields.Many2one('res.municipality', string='Municipality')
    municipality = fields.Char('Municipality')
    township = fields.Char('Township')
    township_extension = fields.Char('Township Extension')
    lot_number = fields.Char('Erf(Stand)/ Lot Number')
    unit_number = fields.Char('Unit Number')
    flat_name = fields.Char('Flat(Name of Building)')
    house = fields.Char('House(Street Address)')
    type_tenure = fields.Selection(([('ownership','Ownership'),('leasehold','Leasehold'),('deed_of_grant','Deed of Grant'),('other','Other')]),string='Type of Tenure')
    other_tenure = fields.Char(string='If other Specify')

    total_product_price = fields.Float(string='Total Product Price')
    subsidy = fields.Float(string='Subsidy')
    amt_home_loan = fields.Float(string='Amount of Home Loan, If applicable')
    emp_contribution = fields.Float(string="Employer's contribution, if any")
    own_contribution = fields.Float(string="Own Cash Contribution")
    own_building = fields.Float(string="Own Building Material Contribution")
    funding_total = fields.Float(string="Total")

    sub_amount = fields.Float(string="Subsidy Amount Qualified for")
    disability_subsidy = fields.Float(string="Disability Subsidy(Plus)")
    geotech_assist = fields.Float(string="Geotechnical Assistance(Plus)")
    sub_total_provincial = fields.Float(string="Sub Total",compute="_compute_subsidy_totals")
    grants_received = fields.Float(string="Grants Received from State Resources(Minus)")
    total_subsidy_qualified = fields. Float(string='Total Subsidy Amount Qualified for',compute="_compute_subsidy_totals",)

    convey_name = fields.Many2one('res.partner',string='Name')
    convey_street = fields.Char(string='Street')
    convey_street2 = fields.Char(string='Street 2')
    convey_zip = fields.Char(string='Zip')
    convey_city = fields.Char(string='City')
    convey_state_id = fields.Many2one("res.country.state",
                                             string='State')
    convey_country_id = fields.Many2one('res.country', string='Country')
    conveyance_fee = fields.Float(string='Conveyance Fee')
    convey_approval_code = fields.Char(string='Approval Code of PHD')
    convey_telephone = fields.Char(string='Telephone Number')
    convey_facsmile = fields.Char(string='FacSmile Number')

    lender_name = fields.Many2one('res.partner', string='Name')
    lender_street = fields.Char(string='Street')
    lender_street2 = fields.Char(string='Street 2')
    lender_zip = fields.Char(string='Zip')
    lender_city = fields.Char(string='City')
    lender_state_id = fields.Many2one("res.country.state",
                                      string='State')
    lender_country_id = fields.Many2one('res.country', string='Country')
    lender_approval_code = fields.Char(string='Approval Code of PHD')
    lender_telephone = fields.Char(string='Telephone Number')
    lender_facsmile = fields.Char(string='FacSmile Number')

    builder_name = fields.Many2one('res.partner', string='Name')
    builder_street = fields.Char(string='Street')
    builder_street2 = fields.Char(string='Street 2')
    builder_zip = fields.Char(string='Zip')
    builder_city = fields.Char(string='City')
    builder_state_id = fields.Many2one("res.country.state",
                                      string='State')
    builder_country_id = fields.Many2one('res.country', string='Country')
    council_reg_number = fields.Char(string="National Home Builders Registration Council's Registration Number")
    builder_telephone = fields.Char(string='Telephone Number')
    builder_facsmile = fields.Char(string='FacSmile Number')

    @api.model_create_multi
    def create(self, vals_list):
        """Generate individual registration numbers for new records"""
        for vals in vals_list:
            if vals.get('individual_reg_number', 'New') == 'New':
                vals['individual_reg_number'] = self.env['ir.sequence'].next_by_code('housing.subsidy') or '/'
        return super().create(vals_list)

    @api.depends('sub_amount', 'disability_subsidy', 'geotech_assist',
                 'grants_received')
    def _compute_subsidy_totals(self):
        for rec in self:
            rec.sub_total_provincial = (
                    rec.sub_amount + rec.disability_subsidy + rec.geotech_assist
            )
            rec.total_subsidy_qualified = (
                    rec.sub_total_provincial - rec.grants_received
            )

    def action_submit(self):
        self.state = 'submitted'

    def action_submit_for_verify(self):
        if self.convey_name:
            mail_template = self.env.ref(
                'website_housing_subsidy.email_template_subsidy_verify')
            mail_template.send_mail(self.id, force_send=True)
            self.state = 'pending_verify'
        else:
            raise ValidationError(
                _('Please choose the Conveyancer'))

    def action_verify_conveyancer(self):
        self.state = 'verified'

    def action_submit_for_approve(self):
        if self.lender_name:
            mail_template = self.env.ref(
                'website_housing_subsidy.email_template_subsidy_approve')
            mail_template.send_mail(self.id, force_send=True)
            self.state = 'pending_approval'
        else:
            raise ValidationError(
                _('Please choose the Lender'))

    def action_rejected(self):
        self.state = 'rejected'

    def action_verify_approve(self):
        self.state = 'approve'

    def get_form_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=housing.subsidy&view_type=form' % self.id)
        return Urls


class DependantsDetails(models.Model):
    _name = "dependant.details"
    _description = "Dependant Details"

    dependant_id = fields.Many2one('housing.subsidy')
    dependant_surname = fields.Char(string='Surname')
    dependant_initials = fields.Char(string='Initials')
    dependant_relation = fields.Char(string='Relationship to Applicant')
    dependant_age = fields.Char(string='Age')
    dependant_gender = fields.Selection([('male','Male'),('female','Female')],string='Gender')
