from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class CemeteryApplication(models.Model):
    _name = 'cemetery.application'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Cemetery Application'

    def _get_country_id(self):
        """Returns Country"""
        return self.env.ref('base.za').id

    def _get_province_data(self):
        """Returns province data"""
        return self.env.ref('cemetery_management.province_province_kwaZulu_natal').id

    def _get_municipality(self):
        """Returns municipality data"""
        municipality = self.env['municipality.municipality'].search(
            [('company_id', '=', self.env.company.id)], limit=1)
        return municipality.id

    name = fields.Char(string='Application ID', required=True, copy=False,
                       readonly=True, default='New')
    type = fields.Selection(
        [('undertaker', 'Undertaker'), ('public', 'Public')],
        default='undertaker', string="User Type")
    interment_type = fields.Selection([
        ('burial', 'Burial'),
        ('cremation', 'Cremation')
    ], string='Interment Type', required=True, default='burial')
    religion = fields.Selection([('christian', 'Christian'), ('muslim', 'Muslim'), ('hindu', 'Hindu'),
                                 ('african', 'Traditional African Religions'), ('other', 'Other')],
                                string='Religion')

    crematorium_id = fields.Many2one('crematorium.crematorium',
                                     string="Crematorium")
    user_type = fields.Selection(
        [('undertaker', 'Undertaker'), ('general_user', 'General User')],
        string='User Type', default='undertaker')
    # Undertaker details
    undertaker_id = fields.Many2one('undertaker.undertaker',
                                    string='Undertaker', required=True)
    surname = fields.Char(string="Undertaker's Surname", related='undertaker_id.surname')
    forenames = fields.Char(string="Forenames", related='undertaker_id.forename')
    undertaker_street = fields.Char(string="Street",
                                    help="Name of the street")
    undertaker_street2 = fields.Char(string="Street 2",
                                     help="Name of the street")
    undertaker_zip = fields.Char(string="Postal Code", help="Postal Code")
    undertaker_city = fields.Char(string="City", help="Name of the city")
    undertaker_country_id = fields.Many2one('res.country', string='Country',
                                            default=_get_country_id,
                                            ondelete='restrict',
                                            help="Name of the country")
    undertaker_ward_id = fields.Many2one('ward.ward', string="Ward",
                              help="Name of the Ward")
    undertaker_province_id = fields.Many2one('province.province',
                                             string="Province",
                                             required=False,
                                             default=_get_province_data,
                                             domain="[('country_id', '=?', arranger_country_id)]")
    undertaker_municipality_id = fields.Many2one('municipality.municipality',
                                                 string="Municipality",
                                                 default=_get_municipality,
                                                 domain="[('province_id', '=?', arranger_province_id)]")

    persal_no = fields.Char(string="Personal No")
    undertaker_id_number = fields.Char(string="ID Number of Recipient")
    designation_number = fields.Char(string="Designation Number")
    # Arranger (General User) details
    # Section D: Authorisation by Person Booking
    arranger_name = fields.Char(string='Applicant Name')
    arranger_email = fields.Char(string='Applicant Email')
    arranger_address = fields.Char(string='Applicant Address')
    arranger_phone = fields.Char(string='Applicant Phone Number')
    arranger_signature = fields.Binary(string='Signature')
    arranger_street = fields.Char(string="Street",
                                  help="Name of the street")
    arranger_street2 = fields.Char(string="Street 2",
                                   help="Name of the street")
    arranger_zip = fields.Char(string="Postal Code", help="Postal code")
    arranger_city = fields.Char(string="City", help="Name of the city")
    arranger_country_id = fields.Many2one('res.country', string='Country',
                                          default=_get_country_id,
                                          ondelete='restrict',
                                          help="Name of the country")
    arranger_province_id = fields.Many2one('province.province',
                                           string="Province",
                                           default=_get_province_data,
                                           required=False,
                                           domain="[('country_id', '=?', arranger_country_id)]")
    arranger_municipality_id = fields.Many2one('municipality.municipality',
                                               string="Municipality",
                                               default=_get_municipality,
                                               domain="[('province_id', '=?', arranger_province_id)]")

    date = fields.Date(string="Date Of Apply", default=fields.Date.today())
    date_issue = fields.Date(string="Date Of Received",
                             default=fields.Date.today())
    serial_number = fields.Char(string="Serial Number of DHA", )
    barcode_number = fields.Char(string="Barcode Number of DHA", )

    is_deceased = fields.Boolean(string="Is Deceased", required=True)
    date_of_death = fields.Date(string="Date Of Dead")
    foreigner = fields.Boolean(string="Is Foreigner")
    passport_number = fields.Char(string="Passport Number")
    id_number = fields.Char(string="ID Number")
    citizenship_id = fields.Many2one('res.country', string="CitizenShip", default=_get_country_id)

    # Section Deceased
    deceased_surname = fields.Char(string='Surname')
    deceased_firstname = fields.Char(string='First Name')
    deceased_preferred_name = fields.Char(string='Preferred Name')
    street = fields.Char(string="Street",
                         help="Name of the street")
    street2 = fields.Char(string="Street 2",
                          help="Name of the street")
    zip = fields.Char(string="Postal Code", help="Postal Code")
    ward_id = fields.Many2one('ward.ward', string="Ward",)
    arranger_ward_id = fields.Many2one('ward.ward', string="Ward",)
    city = fields.Char(string="City", help="Name of the city")
    country_id = fields.Many2one('res.country', string='Country',
                                 ondelete='restrict', default=_get_country_id,
                                 help="Name of the country")
    province_id = fields.Many2one('province.province', string="Province",
                                  required=False, default=_get_province_data,
                                  domain="[('country_id', '=?', country_id)]")
    municipality_id = fields.Many2one('municipality.municipality',
                                      string="Municipality",
                                      default=_get_municipality,
                                      domain="[('province_id', '=?', province_id)]")
    date_of_birth = fields.Date(string="Date Of Birth")
    cause_of_death_id = fields.Many2one('cause.death', string="Cause Of Death")
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        string='Gender')
    grave_number_memorial = fields.Char(string='Grave Number for Memorial')
    burial_order = fields.Binary(string='Burial Order')
    deceased_id = fields.Binary(string='Certified Copy of Deceased ID')
    next_of_kin_id = fields.Binary(string='Certified Copy of Next of Kin ID')
    death_certificate = fields.Binary(
        string='Certified Copy of Death Certificate')

    # old deceased
    # previous_maiden_surname = fields.Char(string='Previous or Maiden Surname')
    # deceased_forenames = fields.Char(string='Deceased Person Forenames')
    place_of_death = fields.Char(string='Place of death (City/Town)')
    place_of_burial = fields.Char(string='Place of burial (City/Town)')
    death_province_id = fields.Many2one('province.province',
                                        default=_get_province_data,
                                        string="Province for place of death")
    burial_province_id = fields.Many2one('province.province',
                                         default=_get_province_data,
                                         string="Province for place of burial")
    cemetery_id = fields.Many2one('cemetery.cemetery', string='Cemetery')
    section_id = fields.Many2one('cemetery.section', string='Section',
                                 domain="[('cemetery_id', '=', cemetery_id)]")
    grave_id = fields.Many2one('grave.grave', string='Grave',
                               domain="[('section_id', '=', section_id), ('state', 'in', ('active','purchase', 'lease'))]")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('verified', 'Verified'),
        ('quotation_generated', 'Quotation Generated'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True)

    is_deceased_id_passport = fields.Boolean(string="Deceased's ID/Passport "
                                                    "Number", default=False)
    document_ids = fields.Many2many('ir.attachment',
                                    string="Copy Deceased's ID/Passport "
                                           "Number")
    is_informant_id_passport = fields.Boolean(string="Informant's ID/Passport "
                                                     "Number", default=False)
    informant_document_ids = fields.Many2many('ir.attachment',
                                              'informant_document_rel',
                                              string="Copy Informant's ID/ "
                                                     "Passport Number")

    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 help="Company Name",
                                 default=lambda self: self.env.company)

    # Section C: Burial/Memorial/Cremation Instructions
    interment_date = fields.Date(string='Date of Burial/Cremation')
    interment_time = fields.Float(string='Time of Burial/Cremation')
    grave_preparation = fields.Selection(
        [('basic', 'Basic'), ('luxury', 'Luxury')], string='Grave Preparation')
    memorial_epitaph = fields.Text(string='Memorial Epitaph / Message')
    other_instructions = fields.Text(string='Other Instructions')

    # Section B: Plot Requirements
    plot_cemetery_id = fields.Many2one('cemetery.cemetery', string='Cemetery')
    category = fields.Selection([('general', 'General'), ('vip', 'VIP')],
                                string='Category')
    plot_municipality_id = fields.Many2one('municipality.municipality',
                                           string='Municipality of the plot',
                                           default=_get_municipality)
    first_grave_lease = fields.Boolean(string='First Grave Lease')
    subsequent_lease = fields.Boolean(string='Second/Subsequent Lease')
    pre_purchased_grave_plot = fields.Boolean(string='Pre-Purchased Grave Plot')
    attended_by_family = fields.Boolean(string='Attended by Family')
    number_of_attendants = fields.Integer(string='Number of Attendants')
    # Section E: Processing of Booking
    grave_allocation_method = fields.Selection(
        [('system', 'System'), ('manual', 'Manual')],
        string='Allocation Method')
    grave_number = fields.Char(string='Grave Number')
    grave_field = fields.Char(string='Field')
    grave_row = fields.Char(string='Row')
    grave_section_id = fields.Many2one('cemetery.section', string='Section')
    grave_type = fields.Selection([('single', 'Single'), ('double', 'Double')],
                                  string='Type')
    confirmed_by = fields.Char(string='Confirmed By')
    confirmation_signature = fields.Binary(string='Confirmation Signature')
    confirmation_date = fields.Date(string='Confirmation Date')
    invoice_id = fields.Many2one('account.move', string='Invoice')

    # Section F: Superintendent Burial Confirmation and Booking Closure
    burial_confirmation_number = fields.Char(string='Confirmation Number')
    burial_confirmation_field = fields.Char(string='Field')
    burial_confirmation_row = fields.Char(string='Row')
    burial_confirmation_section_id = fields.Many2one('cemetery.section',
                                                     string='Section')
    burial_confirmation_type = fields.Selection(
        [('single', 'Single'), ('double', 'Double')], string='Type')
    burial_confirmed_by = fields.Char(string='Confirmed By')
    burial_confirmation_date = fields.Date(string='Confirmation Date')
    burial_confirmation_signature = fields.Binary(
        string='Confirmation Signature')
    notes = fields.Text(string='Notes')
    quotation_id = fields.Many2one('sale.order', string='Quotation', copy=False)

    has_quotation = fields.Boolean(string='Has Quotation',
                                   compute='_compute_has_quotation', store=True)

    invoice_id = fields.Many2one('account.move', string='Invoice')
    has_invoice = fields.Boolean(string='Has Invoice',
                                 compute='_compute_has_invoice', store=True)
    burial_invoice_paid = fields.Boolean(string='Burial Invoice Paid',
                                         compute='_compute_burial_invoice_paid',
                                         store=True)
    death_register_id = fields.Many2one('death.register', string="Death Register", copy=False, readonly=True)
    # Grave
    grave_purchase_id = fields.Many2one("grave.booking", string="Grave Purchase",
                                        domain="[('type', '=', 'purchase')]")
    grave_lease_id = fields.Many2one("grave.booking", string="Grave Lease",
                                        domain="[('type', '=', 'lease')]")
    burial_status = fields.Selection([('complete', 'Complete'),
                                      ('incomplete', 'Incomplete')],
                                     string="Burial Status", default="incomplete")
    cremation_street = fields.Char(string="Street",
                                    help="Name of the street")
    cremation_street2 = fields.Char(string="Street 2",
                                     help="Name of the street")
    cremation_zip = fields.Char(string="Postal Code", help="Postal Code")
    cremation_city = fields.Char(string="City", help="Name of the city")
    cremation_country_id = fields.Many2one('res.country', string='Country',
                                            default=_get_country_id,
                                            ondelete='restrict',
                                            help="Name of the country")
    cremation_ward_id = fields.Many2one('ward.ward', string="Ward",
                                         help="Name of the Ward")
    cremation_province_id = fields.Many2one('province.province',
                                             string="Province",
                                             required=False,
                                             default=_get_province_data,
                                             domain="[('country_id', '=?', arranger_country_id)]")
    cremation_municipality_id = fields.Many2one('municipality.municipality',
                                                 string="Municipality",
                                                 default=_get_municipality,
                                                 domain="[('province_id', '=?', arranger_province_id)]")
    ash_collected_id = fields.Many2one('res.partner', string="Person who collected ashes")

    @api.depends('quotation_id')
    def _compute_has_quotation(self):
        for record in self:
            record.has_quotation = bool(record.quotation_id)

    @api.constrains('id_number', 'undertaker_id_number')
    def constrains_id_number(self):
        """Constrains functionality used to indicate or raise an
        UserError when we adding id number """
        if self.id_number:
            if len(self.id_number) != 13:
                raise UserError(_(
                    "The id number must be 13 digits"))
        if self.undertaker_id_number:
            if len(self.undertaker_id_number) != 13:
                raise UserError(_(
                    "The id number must be 13 digits"))

    @api.onchange('cemetery_id')
    def _onchange_cemetery_id(self):
        self.plot_cemetery_id = self.cemetery_id

    @api.onchange('grave_id')
    def _onchange_grave_id(self):
        self.grave_number = self.grave_id.name
        self.grave_section_id = self.section_id
        self.burial_confirmation_section_id = self.section_id
        self.grave_number_memorial = self.grave_id.name

    @api.onchange('undertaker_id')
    def _onchange_user_id(self):
        """Adding values to surname, forenames based on the user"""
        # self.surname = self.undertaker_id.partner_id.surname
        # self.forenames = self.undertaker_id.partner_id.forenames
        self.undertaker_street = self.undertaker_id.undertaker_street
        self.undertaker_street2 = self.undertaker_id.undertaker_street2
        self.undertaker_zip = self.undertaker_id.undertaker_zip
        self.undertaker_city = self.undertaker_id.undertaker_city
        self.undertaker_province_id = self.undertaker_id.undertaker_province_id
        self.undertaker_municipality_id = self.undertaker_id.undertaker_municipality_id
        # self.undertaker_state_id = self.undertaker_id.undertaker_state_id
        self.undertaker_country_id = self.undertaker_id.undertaker_country_id

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].sudo().next_by_code(
                'cemetery.application') or 'New'
        return super(CemeteryApplication, self).create(vals)

    def action_submit(self):
        """"Submit the Application form"""
        if self.interment_type in ['burial', 'cremation', 'memorial']:
            if self.is_deceased:
                if not self.deceased_surname:
                    raise ValidationError(_("Please Add the Deceased Surname"))
                if not self.deceased_firstname:
                    raise ValidationError(
                        _("Please Add the Deceased First Name"))
                if not self.id_number:
                    raise ValidationError(_("Please Add the ID Number"))
                if not self.date_of_birth:
                    raise ValidationError(_("Please Add the Date Of Birth"))
                if not self.date_of_death:
                    raise ValidationError(_("Please Add the Date Of Death"))
                if self.foreigner:
                    if not self.passport_number:
                        raise ValidationError(
                            _("Please Add the Passport Number"))
                if not self.place_of_death:
                    raise ValidationError(_("Please Add the Place Of Death"))
                if not self.death_province_id:
                    raise ValidationError(
                        _("Please Add the province for place of death"))
                if not self.place_of_burial:
                    raise ValidationError(_("Please Add the Place Of Burial"))
                if not self.burial_province_id:
                    raise ValidationError(
                        _("Please Add the province for place of burial"))
        if self.interment_type in ['burial']:
            if not self.cemetery_id:
                raise ValidationError(_("Please enter the Cemetery Details"))
            if not self.section_id:
                raise ValidationError(
                    _("Please enter the Cemetery Section Details"))
            if not self.grave_id:
                raise ValidationError(_("Please enter the Grave Details"))
            if self.is_deceased_id_passport:
                if not self.document_ids:
                    raise ValidationError(_("Please Add Copy Deceased's"
                                            " ID/Passport Number"))
            if self.is_informant_id_passport:
                if not self.informant_document_ids:
                    raise ValidationError(_("Please Add Copy Informant's"
                                            " ID/Passport Number"))
        if self.interment_type in ['burial', 'cremation']:
            if not self.interment_date:
                raise UserError(_("Please Add the Date of Burial/Cremation"))
            if not self.interment_time:
                raise UserError(_("Please Add the time of Burial/Cremation"))
            # create the calendar events
            hour, minute = divmod(self.interment_time, 1)
            minute *= 60
            event = self.env["calendar.event"].create(
                {"name": "Burial/ Cremation: " + self.name,
                 "start": datetime(self.interment_date.year,
                                   self.interment_date.month,
                                   self.interment_date.day, int(hour),
                                   int(minute)),
                 "stop": datetime(self.interment_date.year,
                                  self.interment_date.month,
                                  self.interment_date.day, int(hour) + 2,
                                  int(minute)),
                 'res_id': self.id,
                 'res_model_id': self.env['ir.model']._get_id(self._name)
                 }
            )
        self.write({'state': 'submitted'})

    def action_view_calender(self):
        """View The calendar events"""
        return {
            'name': _('Calender'),
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'view_mode': 'calendar,tree,form',
            'target': 'current',
            'domain': [('res_id', '=', self.id), ('res_model', '=', self._name)]
        }

    def action_view_grave_purchase(self):
        """View The calendar events"""
        return {
            'name': _('Grave Purchase'),
            'type': 'ir.actions.act_window',
            'res_model': self.grave_purchase_id._name,
            'res_id': self.grave_purchase_id.id,
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('res_id', '=', self.id), ('res_model', '=', self._name)]
        }

    def action_view_grave_lease(self):
        """View The calendar events"""
        return {
            'name': _('Grave Lease'),
            'type': 'ir.actions.act_window',
            'res_model': self.grave_lease_id._name,
            'res_id': self.grave_lease_id.id,
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('res_id', '=', self.id), ('res_model', '=', self._name)]
        }

    def action_approve(self):
        """Approve the application form and create a death register record"""
        self.grave_id.in_use = True
        death_register = self.env['death.register'].sudo().create({
            'surname': self.deceased_surname,
            'date_of_death': self.date_of_death,
            'date_of_birth': self.date_of_birth,
            'place_of_death': self.place_of_death,
            'municipality_id': self.municipality_id.id if self.municipality_id else False,
            'gender': self.gender,
            'citizenship_id': self.citizenship_id.id if self.citizenship_id else False,
            'cause_death_id': self.cause_of_death_id.id if self.cause_of_death_id else False,
            'interment_type': self.interment_type,
            'identity_no': self.id_number,
            'cemetery_id': self.cemetery_id.id if self.cemetery_id else False,
            'section_id': self.section_id.id if self.section_id else False,
            'grave_id': self.grave_id.id if self.grave_id else False,

        })
        self.death_register_id = death_register.id
        self.state = 'approved'

    def action_complete(self):
        """Action complete Burial Order"""
        self.burial_status = 'complete'

    def action_verify(self):
        """Verify the application form"""
    # return {
    #     'name': _('Verify'),
    #     'type': 'ir.actions.act_window',
    #     'res_model': 'application.verify',
    #     'view_mode': 'form',
    #     'target': 'new',
    #     'context': {
    #         'default_application_id': self.id,
    #     }
    # }
        self.write({'state': 'verified'})

    def create_quotation(self):
        # Create the new product template record
        grave_product_vals = {
            'name': self.grave_id.name or 'Default Name',
            'detailed_type': 'service',
            'list_price': self.grave_id.grave_purchase_value or 0.0,
        }
        grave_product = self.env['product.template'].create(grave_product_vals)

        # Extract details from undertaker_id to create a new partner
        # Check the user type and create partner values accordingly
        if self.user_type == 'undertaker':
            partner_vals = {
                'name': self.undertaker_id.full_name,
                'phone': self.undertaker_id.phone_number,
                'email': self.undertaker_id.email_address,
                'street': self.undertaker_id.undertaker_street,
                'street2': self.undertaker_id.undertaker_street2,
                'zip': self.undertaker_id.undertaker_zip,
                'city': self.undertaker_id.undertaker_city,
                'country_id': self.undertaker_id.undertaker_country_id.id,
                'state_id': self.undertaker_id.undertaker_province_id.id,
            }
        else:  # Assume user_type is 'general_user'
            partner_vals = {
                'name': self.arranger_name,
                'phone': self.arranger_phone,
                'email': self.arranger_email,
                'street': self.arranger_street,
                'street2': self.arranger_street2,
                'zip': self.arranger_zip,
                'city': self.arranger_city,
                'country_id': self.arranger_country_id.id,
                # 'state_id': self.arranger_province_id.id,
            }
        partner = self.env['res.partner'].create(partner_vals)

        # Create the draft customer invoice
        quotation_vals = {
            'partner_id': partner.id,
            'order_line': [(0, 0, {
                'product_id': grave_product.product_variant_id.id,
                'product_uom_qty': 1,  # Correct field name for quantity
                'price_unit': grave_product.list_price,
                'name': grave_product.name,
            })],
            'burial_booking_id': self.id,
        }
        quotation = self.env['sale.order'].create(quotation_vals)
        self.write({'state': 'quotation_generated'})

        # Set the quotation ID in the burial booking
        self.quotation_id = quotation.id

        action = {
            'name': _('Quotation'),
            'view_mode': 'form',
            'view_id': self.env.ref('sale.view_order_form').id,
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'res_id': quotation.id,
        }
        return action


    def action_view_quotation(self):
        if self.quotation_id:
            return {
                'name': _('Quotation'),
                'view_mode': 'form',
                'view_id': self.env.ref('sale.view_order_form').id,
                'res_model': 'sale.order',
                'type': 'ir.actions.act_window',
                'res_id': self.quotation_id.id,
            }
        else:
            # Handle case when no invoice is linked
            # For example, display a warning message
            return {
                'warning': {
                    'title': _('Warning'),
                    'message': _('No Quotation linked to this booking.'),
                }
            }


    @api.depends('invoice_id')
    def _compute_has_invoice(self):
        for record in self:
            record.has_invoice = bool(record.invoice_id)


    @api.depends('invoice_id')
    def _compute_burial_invoice_paid(self):
        for record in self:
            record.burial_invoice_paid = False
            if record.invoice_id and record.invoice_id.payment_state == 'paid':
                record.burial_invoice_paid = True


    def action_view_invoice(self):
        self.ensure_one()
        if not self.invoice_id:
            raise UserError(
                _('There is no invoice linked to this burial booking.'))
        action = {
            'name': _('Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'res_id': self.invoice_id.id,
        }
        return action


    def action_reject(self):
        self.write({'state': 'rejected'})


# def action_approve(self):
#     self.write({'state': 'approved'})
