from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil import relativedelta
import base64
import io
import pandas as pd


class PropertyEnquiry(models.Model):
    """Property Enquiry"""
    _name = "property.enquiry"
    _description = "Property Enquiry"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    active = fields.Boolean(string="Archive", default=True)
    name = fields.Char(string="Enquiry Reference", required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    district_id = fields.Many2one('res.district', string="District", required=True)
    city_id = fields.Many2one('res.district.city', domain="[('district_id', '=?', district_id)]", string="City/Town", required=True)
    date = fields.Date(string="Date", default=fields.Date.context_today)
    property_id = fields.Many2one('building', string="Property")
    building_id = fields.Many2one('product.template',
                                  domain="[('is_property','=',True), ('building_id', '=', property_id)]", string="Building Unit")
    property_state = fields.Selection(related="building_id.state")
    property_type = fields.Selection([
        ('industrial_smme', 'Industrial SMME'),
        ('industrial_light', 'Industrial - Light'),
        ('industrial_large', 'Industrial - Large'),
        ('retail', 'Retail'),
        ('mooring', 'Mooring'),
        ('commercial_office', 'Commercial / Office'),
        ('residential', 'Residential'),
    ], string="Property Type", required=True, tracking=True)

    # 4.4 Mooring dropdowns
    mooring_length = fields.Selection([
        ('5m', '5 m'),
        ('10m', '10 m'),
        ('15m', '15 m'),
        ('20m', '20 m'),
        ('25m', '25 m'),
    ], string="Mooring Length", help="Select the mooring length (in meters)")

    mooring_width = fields.Selection([
        ('2m', '2 m'),
        ('3m', '3 m'),
        ('4m', '4 m'),
        ('5m', '5 m'),
    ], string="Mooring Width", help="Select the mooring width (in meters)")

    # 4.5 For other property types
    min_area = fields.Float(string="Minimum Area (m²)")
    max_area = fields.Float(string="Maximum Area (m²)")
    # 6. Capacity & Contact Details
    capacity = fields.Selection([
        ('tenant', 'Tenant'),
        ('owner', 'Owner'),
        ('agent', 'Agent'),
        ('broker', 'Broker'),
        ('developer', 'Developer'),
        ('other', 'Other'),
    ], string="Capacity", required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string="Enquirer")
    title_id = fields.Many2one('res.partner.title', string="Title")

    contact_name = fields.Char(string="Name", required=True)
    contact_surname = fields.Char(string="Surname", required=True)
    email = fields.Char(string="Email Address")
    phone = fields.Char(string="Contact Number")

    callback_date = fields.Datetime(string="Convenient Call Back Date")

    business_type = fields.Selection([
        ('manufacturing', 'Manufacturing'),
        ('retail', 'Retail'),
        ('services', 'Services'),
        ('logistics', 'Logistics'),
        ('construction', 'Construction'),
        ('agriculture', 'Agriculture'),
        ('other', 'Other'),
    ], string="Business Type")

    business_status = fields.Selection([
        ('new', 'New'),
        ('existing', 'Existing'),
    ], string="New or Existing")

    operations_began_date = fields.Date(string="Date Operations Began")
    nature_of_business = fields.Text(string="Nature of Business")

    # =========================
    # MARKETING INTELLIGENCE (Step 8)
    # =========================
    heard_about_us = fields.Selection([
        ('social_media', 'Social Media'),
        ('website', 'Ithala Website'),
        ('radio', 'Radio'),
        ('newspaper', 'Newspaper'),
        ('referral', 'Referral'),
        ('event', 'Event'),
        ('other', 'Other'),
    ], string="How Did You Hear About Us")

    medium_name = fields.Char(string="Name of Selected Medium")
    communication_method = fields.Selection([
        ('sms', 'SMS'),
        ('email', 'E-mail'),
    ], string="Preferred Communication Method")
    state = fields.Selection([('draft', 'Draft'),
                              ('submitted', 'Submitted'),
                              ('pending', 'Pending'),
                              ('proceed', 'Proceed To Facilities Check'),
                              ('confirm_suitability', 'Confirm Suitability'),
                              ('to_approve', 'To Approve'),
                              ('approve', 'Approve For Site Visit'),
                              ('site_visit', 'Site Visit'),
                              ('approved', 'Approved'),
                              ('declined', 'Declined'),
                              ('closed', 'Closed')
                              ],
                             default="draft")
    ptype = fields.Many2one(related="building_id.ptype")
    status = fields.Many2one(related="building_id.status")
    building_area = fields.Integer(related="building_id.building_area")
    building_area_net = fields.Integer(related="building_id.building_area_net")
    land_area = fields.Integer(related="building_id.land_area")
    occupation_status = fields.Selection([('occupied', 'Occupied'), ('vacant', 'Vacant')])
    comments = fields.Text(string="Availability/Tenant Mix Criteria Comments",
                           readonly=True, copy=False )
    facility = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                string="Facility Required", copy=False)
    facilities_ids = fields.One2many('facilities.investigation', 'enquiry_id',
                                     string="Facilities Required")
    facility_comments = fields.Text(string="Facilities To Investigate Suitability",
                                    readonly=True, copy=False)
    booking_id = fields.Many2one('unit.reservation', string="Booking")
    rental_contract_id = fields.Many2one('rental.contract', string="Booking")

    total_assets = fields.Float("Total Assets")
    total_liabilities = fields.Float("Total Liabilities")
    net_worth = fields.Float("Net Worth")

    compliance_score = fields.Float('Compliance Score(100)')
    max_monthly_rental_approved = fields.Float('Max Monthly Rental Approved')
    deposit_conditions = fields.Char('Deposit Conditions')
    special_conditions = fields.Float('Special Conditions Score(100)')
    term_conditions = fields.Float('Term Conditions')

    # BANK
    bank_name = fields.Char('Bank Name')
    account_holder = fields.Char('Account Holder')
    account_type = fields.Char('Account Type')
    account_number = fields.Char('Account Number')
    bank_statement_start_date = fields.Date('Bank Statement Start Date')
    bank_statement_end_date = fields.Date('Bank Statement End Date')
    average_monthly_salary = fields.Float('Average Monthly Salary')
    avs_processed = fields.Boolean('AVS Processed')

    # Bitventure
    account_status = fields.Char('Account Status')
    account_name_valid = fields.Char('Account Name Valid')
    account_initials_valid = fields.Char('Account Initials Valid')
    account_email_valid = fields.Char('Account Email Valid')
    account_type_valid = fields.Char('Account Type Valid')
    account_phone_number_valid = fields.Char('Account Phone Number Valid')
    account_number_valid = fields.Char('Account Number Valid')
    account_open_for = fields.Char('Account Open for at least 3 Months')
    account_accepts_debits = fields.Char('Account Accepts Debits')
    account_accepts_credits = fields.Char('Account Accepts Credits')


    #
    import_transaction = fields.Binary(string='Import Transaction',filename="import_transaction_filename")
    import_transaction_filename = fields.Char()

    total_amount_of_atm_withdrawals = fields.Float('Total amount of ATM Withdrawals')
    alcohol_transaction_ids = fields.One2many(
        'bank.transactions',
        'enquiry_id',
        string="Alcohol Transactions",
        domain=[('transaction_type', '=', 'alcohol')]
    )
    fuel_transaction_ids = fields.One2many(
        'bank.transactions',
        'enquiry_id',
        string="Fuel Transactions",
        domain=[('transaction_type', '=', 'fuel')]
    )
    toll_transaction_ids = fields.One2many(
        'bank.transactions',
        'enquiry_id',
        string="Toll Transactions",
        domain=[('transaction_type', '=', 'toll')]
    )
    pharmacy_transaction_ids = fields.One2many(
        'bank.transactions',
        'enquiry_id',
        string="Pharmacy Transactions",
        domain=[('transaction_type', '=', 'pharmacy')]
    )
    booking_in_transaction_ids = fields.One2many(
        'bank.transactions',
        'enquiry_id',
        string="Booking Money In",
        domain=[('transaction_type', '=', 'booking_in')]
    )
    booking_out_transaction_ids = fields.One2many(
        'bank.transactions',
        'enquiry_id',
        string="Booking Money Out",
        domain=[('transaction_type', '=', 'booking_out')]
    )
    debit_reversal_transaction_ids = fields.One2many(
        'bank.transactions',
        'enquiry_id',
        string="Debit Other Reversals",
        domain=[('transaction_type', '=', 'debit_reversal')]
    )
    gambling_transaction_ids = fields.One2many(
        'bank.transactions',
        'enquiry_id',
        string="Gambling / Betting Transactions",
        domain=[('transaction_type', '=', 'gambling')]
    )

    #
    employer = fields.Char('Employer')
    occupation = fields.Char('Occupation')
    work_address = fields.Char('Work Address (lead)')
    work_number = fields.Char('Work Number (lead)')
    work_email = fields.Char('Work Email (lead)')
    employment_info_ids = fields.One2many('tu.employment.info.wizard','enquiry_id','Employment Info')
    work_number_ids = fields.One2many('tu.employment.info.wizard','enquiry_id','Work Number')

    confirmed_on_linkedin = fields.Boolean('Confirmed on Linkedin')
    confirmed_on_facebook = fields.Boolean('Confirmed on Facebook')


    #
    id_type = fields.Selection([('rsa_id','RSA ID'),('passport','Passport')])
    passport_number = fields.Char('Passport Number (lead)')
    date_of_birth = fields.Date('Date of Birth (passport)')
    id_number = fields.Char('ID number (lead)')
    cell_number = fields.Char('Cell number (lead)')
    bitventure_id_number_valid = fields.Char('Bitventure ID Number Valid')
    tu_full_name = fields.Char('TU Full Name')
    tu_marital_status = fields.Char('TU Marital Status')
    cell_number_ids = fields.One2many('tu.employment.cell.wizard','enquiry_id','Tu Cell Number')
    cell_number_verified = fields.Boolean('Cell Number Verified')
    nok_name = fields.Char('NOK Name (lead)')
    nok_number = fields.Char('NOK Number (lead)')
    nok_relation = fields.Char('NOK Relation (lead)')
    nok_confirmed = fields.Boolean('NOK Confirmed (lead)')

    # 
    tu_judgement_ids = fields.One2many('tu.judgment.cell.wizard','enquiry_id','Tu Judgements')

    #
    home_address = fields.Char('Home Address (lead)')
    home_address_bank = fields.Char('Home Address (Bank Statement)')
    tu_address_ids = fields.One2many('tu.address.wizard','enquiry_id','TU Address')

    def import_transaction_file(self):
        self.ensure_one()

        if not self.import_transaction:
            raise UserError("Please upload an Excel (.xlsx) file.")

        # if not self.import_transaction_filename or not self.import_transaction_filename.endswith('.xlsx'):
        #     raise UserError("Only .xlsx files are supported.")

        # Decode file
        file_data = base64.b64decode(self.import_transaction)
        file_buffer = io.BytesIO(file_data)

        try:
            df = pd.read_excel(file_buffer, engine='openpyxl')
        except ImportError:
            raise UserError("openpyxl is not installed on the server.")
        except Exception as e:
            raise UserError("Invalid Excel file: %s") % e

        REQUIRED_COLUMNS = [
            'name', 'company_id', 'date',
            'description', 'ind_or_comp',
            'transaction_type', 'amount'
        ]

        for col in REQUIRED_COLUMNS:
            if col not in df.columns:
                raise UserError("Missing required column: %s") % col

        TransactionMap = {
            'Alcohol': 'alcohol',
            'Fuel': 'fuel',
            'Toll': 'toll',
            'Pharmacy': 'pharmacy',
            'Booking/Money In': 'booking_in',
            'Booking/Money Out': 'booking_out',
            'Debit Other Reversals': 'debit_reversal',
            'Gambling/Betting': 'gambling',
        }

        Transaction = self.env['bank.transactions']

        for _, row in df.iterrows():
            transaction_type = TransactionMap.get(
                str(row['transaction_type']).strip()
            )

            if not transaction_type:
                raise UserError("Invalid transaction type: %s" % row['transaction_type'])

            company = self.env['res.company'].search(
                [('name', '=', row['company_id'])], limit=1
            )
            if str(row['date']) == 'NaT':
                row['date'] = ''

            Transaction.create({
                'enquiry_id': self.id,
                'name': row['name'],
                'company_id': company.id if company else False,
                'date': row['date'],
                'description': row['description'],
                'ind_or_comp': row['ind_or_comp'].lower(),
                'transaction_type': transaction_type,
                'amount': float(row['amount']),
            })

    def account_verify_credit_score(self):
        self.write({
            'account_status':'yes',
            'account_name_valid':'yes',
            'account_initials_valid':'yes',
            'account_email_valid':'yes',
            'account_type_valid':'yes',
            'account_phone_number_valid':'yes',
            'account_number_valid':'yes',
            'account_open_for':'yes',
            'account_accepts_debits':'yes',
            'account_accepts_credits':'yes',
            'avs_processed':True,
        })

    # Auto sequence for name
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('property.enquiry') or _('New')

        """Auto-generate enquiry number and send notification."""
        record = super(PropertyEnquiry, self).create(vals)
        return record

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Onchange Partner"""
        for rec in self:
            rec.contact_name = rec.partner_id.name
            rec.title_id = rec.partner_id.title.id
            rec.email = rec.partner_id.email
            rec.phone = rec.partner_id.phone

    @api.onchange('property_type')
    def _onchange_property_type(self):
        if self.property_type == 'mooring':
            self.min_area = False
            self.max_area = False
        else:
            self.mooring_length = False
            self.mooring_width = False

    def action_send_enquiry_acknowledgement(self):
        """Send confirmation email and/or SMS to enquirer."""

        for record in self:
            template = self.env.ref('property_management_system.mail_template_enquiry_ack', raise_if_not_found=False)
            if template:
                template.send_mail(record.id, force_send=True)

            email_template = self.env.ref('property_management_system.mail_template_enquiry_created',
                                    raise_if_not_found=False)
            if email_template:
                recipient_ids = self.env.ref(
                    'itsys_real_estate.group_units_structure').users
                partner = recipient_ids.mapped('partner_id')
                email_values = {
                    'recipient_ids': [(6, 0, partner.ids)]
                }
                email_template.send_mail(record.id, force_send=True, email_values=email_values)
            record.state = "submitted"
        return True

    def action_proceed_availability(self):
        """Check availability/tenant Mix criteria"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Proceed Tenant Mix Criteria',
            'res_model': 'tenant.mix.criteria',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_enquiry_id': self.id,
                'default_type': "approve",
            }
        }

    def action_decline_availability(self):
        """Check availability/tenant Mix criteria"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Decline Tenant Mix Criteria',
            'res_model': 'tenant.mix.criteria',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_enquiry_id': self.id,
                'default_type': "decline",
            }
        }

    def action_reject_facility_suitable(self):
        """Reject Facilities"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Suitable For Nature of Business',
            'res_model': 'facility.comments',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_enquiry_id': self.id,
            }
        }

    def action_approve(self):
        """Approve"""
        self.state = "approve"

        template = self.env.ref(
            'property_management_system.mail_template_enquiry_approved',
            raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)

    def action_revert_back(self):
        """Revert Back with condition"""
        self.state = "to_approve"
        template = self.env.ref(
            'property_management_system.mail_template_enquiry_to_approve',
            raise_if_not_found=False)
        recipient_ids = self.env.ref(
            'itsys_real_estate.group_real_estate_admin').users
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        if template:
            template.send_mail(self.id, force_send=True, email_values=email_values)

    def action_approves(self):
        """Approve"""
        self.state = "approve"

    def action_decline(self):
        self.state = "declined"
        template = self.env.ref(
            'property_management_system.mail_template_enquiry_declined',
            raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)

    def unlink(self):
        """Delete the current record."""
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Can't delete an enquiry in this state. "
                              "We can only delete draft state record."))
        return super().unlink()

    def action_approve_for_site_visit(self):
        """For Site visit"""
        template = self.env.ref(
            'property_management_system.mail_template_enquiry_approve_site_visit',
            raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)

        self.state ="site_visit"

    def action_approve_site_visit(self):
        """Approve Site Visit"""
        self.state = "approved"
        if self.partner_id:
            partner = self.partner_id
            self.partner_id.is_tenant = True
        else:
            partner = self.env['res.partner'].create({
                'name': self.contact_name,
                'contact_surname': self.contact_surname,
                'email': self.email,
                'phone': self.phone,
                'title': self.title_id.id,
                'is_tenant': True
            })
            self.partner_id = partner.id
        self.building_id.tenant_id = partner.id
        contract = self.env['unit.reservation'].create({
            'building_unit': self.building_id.id,
            'partner_id': partner.id
        })
        contract.onchange_unit()
        contract.action_confirm()
        self.booking_id = contract.id
        rental = self.env['rental.contract'].create({
            'reservation_id': contract.id,
            'partner_id': partner.id,
            'building_unit': self.building_id.id,
            'insurance_fee':  0,
            'rental_fee':  0,
            'date_from': fields.Date.today(),
            'date_to': fields.Date.today() + relativedelta.relativedelta(years=+1, days=-1)

        })
        rental.onchange_unit()
        # rental.action_confirm()
        self.rental_contract_id = rental.id

    def action_reject_site_visit(self):
        """Approve Site Visit"""
        self.state = "closed"

    def action_view_booking(self):
        """View booking"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Booking',
            'view_mode': 'form',
            'res_model': self.booking_id._name,
            'res_id': self.booking_id.id,
            'context': "{'create': False}"
        }

    def action_view_rental_contract(self):
        """View booking"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Rental Contract',
            'view_mode': 'form',
            'res_model': self.rental_contract_id._name,
            'res_id': self.rental_contract_id.id,
            'context': "{'create': False}"
        }

    def action_vetting_process(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Client Balance Sheet',
            'view_mode': 'form',
            'res_model': "vetting.process.wizard",
            'context':{
                'default_enquiry_id': self.id
            },
            'target': 'new'
        }
