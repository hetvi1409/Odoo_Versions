# -*- coding: utf-8 -*-
from odoo import api, fields, models

class CrmLead(models.Model):
    _inherit = "crm.lead"


    tenant = fields.Char('Tenant')
    total_score = fields.Integer('Total Score')
    alcohol = fields.Integer('Alcohol')
    fuel = fields.Integer('Fuel')
    uber = fields.Integer('Uber')
    gambling = fields.Integer('Gambling')
    credit = fields.Integer('Credit')
    age_score = fields.Integer('Age score')
    employeement = fields.Integer('Employeement')
    address = fields.Integer('Address')


    district_id = fields.Many2one('res.district', string="District",
                                  required=True)
    city_id = fields.Many2one('res.district.city',
                              domain="[('district_id', '=?', district_id)]",
                              string="City/Town", required=True)
    date = fields.Date(string="Date", default=fields.Date.context_today)
    property_id = fields.Many2one('building', string="Property")
    building_id = fields.Many2one('product.template',
                                  domain="[('is_property','=',True), ('building_id', '=', property_id)]",
                                  string="Building Unit")
    contact_surname = fields.Char(string="Surname", required=False)
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
    enquiry_type = fields.Selection([
        ('rent', 'Rent'),
        ('buy', 'Buy'),
    ], string="Enquiry Type")

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
        ('event', 'Evenenquiry_typet'),
        ('other', 'Other'),
    ], string="How Did You Hear About Us")

    medium_name = fields.Char(string="Name of Selected Medium")
    communication_method = fields.Selection([
        ('sms', 'SMS'),
        ('email', 'E-mail'),
    ], string="Preferred Communication Method")

    enquiry_comments = fields.Text(string="Enquiry Comments")
    contract_id = fields.Many2one('rental.contract')
    ownership_contract_id = fields.Many2one('ownership.contract')

    reg_number = fields.Char(string="Registration Number")
    id_number = fields.Char(string="ID Number")
    vat = fields.Char(string="ID Number")
    passport_number = fields.Char(string="Passport Number")
    trust_number = fields.Char(string="Trust Number")
    is_trust = fields.Boolean()
    company_type = fields.Selection(
        [('person', 'Individual'), ('company', 'Company'), ('trust', 'Trust')],
        ondelete={'trust': 'set company'})

    cipc_certificate = fields.Binary(string="CIPC Certificate")
    notice_cipc_certificate = fields.Binary(
        string="Notice of Registered Office Certificate")
    moi_founding_statement = fields.Binary(string="MOI / Founding Statement")
    id_proof_address = fields.Binary(string="ID + Proof of Address")
    utility_bill_lease = fields.Binary(string="Utility Bill / Lease")
    sars_certificate = fields.Binary(string="SARS Certificate")
    bank_letter = fields.Binary(string="Bank Letter")

    id_passport_copy = fields.Binary(string="ID / Passport Copy")
    home_affairs_immigration = fields.Binary(
        string="Home Affairs / Immigration Document")
    utility_bill_lease_bank_statement = fields.Binary(
        string="Utility Bill / Lease/ Bank Statement")
    sars_document = fields.Binary(string="SARS Document")
    certified_trust_deed = fields.Binary(string="Certified Trust Deed")
    master_letter_authority = fields.Binary(
        string="Master’s Letter of Authority")
    trustee_id_proof_address = fields.Binary(
        string="Trustee IDs and Proof of Address")

