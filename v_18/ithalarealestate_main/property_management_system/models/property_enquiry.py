from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil import relativedelta


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
            record.state = "pending"
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
