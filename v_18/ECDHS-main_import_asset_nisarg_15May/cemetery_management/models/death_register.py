from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date


class DeathRegister(models.Model):
    _name = 'death.register'
    _description = 'Death Register'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'surname'
    """
        This model is used to record and manage information related to death registrations,
        including details of the deceased, certification by medical practitioners, and other 
        relevant information. It is structured into sections for easy data entry and retrieval.
    """
    # Section A: PARTICULARS OF THE DECEASED
    is_death = fields.Selection(
        [('death', 'Death'), ('still_birth', 'Still Birth')],
        string='Was this a death or a still birth?',
        help='Specify whether the case is a death or still birth')
    identification = fields.Selection([
        ('id_document',
         'The deceased was identified with an ID document/passport produced by the family'),
        ('still_born', 'Still born child'),
        ('features_mismatch',
         'The features of the deceased do not seem to match the features on the ID document or passport of deceased'),
        ('no_id',
         'ID document or passport of the deceased was not presented. The deceased was identified through word of mouth'),
        ('already_buried',
         'The deceased was already buried prior to the completion of this form'),
        ('unidentifiable', 'The deceased was unidentifiable')
    ], string='Identification of the deceased',
        help='Specify how the deceased was identified')
    unidentifiable_reason = fields.Selection([
        ('burnt', 'Burnt'),
        ('decomposed', 'Decomposed'),
        ('other', 'Other (specify)'),
        ('dna_samples', 'DNA samples retrieved for identification purposes'),
        ('dental_records', 'Dental records taken for identification purposes')
    ], string='If unidentifiable, specify reason',
        help='Specify the reason if the deceased was unidentifiable')
    date_of_death = fields.Date(
        string='Date of Death / Still Birth', required=True,
        help='Date when the death or still birth occurred')
    place_of_death = fields.Char(
        string='Place of Death / Still Birth (City/Town/Village)',
        required=True, help='Location where the death or still birth occurred')
    province_of_death_id = fields.Many2one(
        'province.province',
        string='Province of Death / Still Birth',
        help='Province where the death or still birth occurred')
    place_of_registration = fields.Char(
        string='Place of Registration of Death / Still Birth',
        help='Location where the death or still birth was registered')
    hours_alive = fields.Integer(
        string='If death occurred within 24 hours after birth, number of hours alive',
        help='Number of hours the deceased lived if death occurred within 24 hours after birth')
    home_phone = fields.Char(
        string='Home Telephone No.',
        help='Home telephone number of the deceased')
    identity_no = fields.Char(
        string='Identity No',
        help='Identity number of the deceased')
    is_foreigner = fields.Boolean(
        string='Is Foreigner',
        help='Indicate if the deceased was a foreigner')
    id_number_passport = fields.Char(
        string='Passport No',
        help='Passport number of the deceased')
    date_of_birth = fields.Date(
        string='Date of Birth',
        help='Date of birth of the deceased')
    gender = fields.Selection([
        ('male', 'Male'), ('female', 'Female'),
        ('indeterminable', 'Indeterminable')
    ], string='Gender', required=True,
        help='Gender of the deceased')
    surname = fields.Char(
        string='Surname',
        help='Surname of the deceased')
    previous_surname = fields.Char(
        string='Previous / Maiden Surname',
        help='Previous or maiden surname of the deceased')
    forenames = fields.Char(
        string='Forenames',
        help='Forenames of the deceased')
    residential_street = fields.Char(
        string='Residential Street',
        help='Residential street of the deceased')
    residential_town = fields.Char(
        string='Residential Town',
        help='Residential town of the deceased')
    residential_province = fields.Many2one(
        'province.province',
        string='Residential Province',
        help='Residential province of the deceased')
    residential_postal_code = fields.Char(
        string='Residential Postal Code',
        help='Residential postal code of the deceased')
    citizenship_id = fields.Many2one(
        'res.country',
        string='Citizenship', required=True,
        help='Citizenship of the deceased')
    is_abroad = fields.Boolean(
        string='Is Abroad',
        help='Indicate if the deceased was abroad')
    place_of_birth = fields.Char(
        string='Place of Birth (City/Town/Village or Country of Birth)',
        help='Place of birth of the deceased')
    province_of_birth = fields.Char(
        string='Province of Birth',
        help='Province of birth of the deceased')
    right_thumbprint = fields.Binary(
        string='Right Thumbprint of Deceased',
        help='Right thumbprint of the deceased')
    left_thumbprint = fields.Binary(
        string='Left Thumbprint of Deceased',
        help='Left thumbprint of the deceased')
    marital_status = fields.Selection([
        ('single', 'Single'), ('married', 'Married'), ('widowed', 'Widowed'),
        ('divorced', 'Divorced')
    ], string='Marital Status of the Deceased',
        help='Marital status of the deceased')
    education_level = fields.Selection([
        ('non_gr', 'Non Gr'), ('gr1', 'Gr 1'), ('gr2', 'Gr 2'), ('gr3', 'Gr 3'),
        ('gr4', 'Gr 4'), ('gr5', 'Gr 5'), ('gr6', 'Gr 6'), ('gr7', 'Gr 7'),
        ('gr8', 'Gr 8 Form 1'), ('gr9', 'Gr 9 Form 2'), ('gr10', 'Gr 10'),
        ('gr11', 'Gr 11 Form 3'), ('gr12', 'Gr 12 Form 4'), ('form5', 'Form 5'),
        ('ntc1', 'NTC 1'), ('ntc2', 'NTC 2'), ('ntc3', 'NTC 3'),
        ('univ', 'University'), ('tech', 'Technical'), ('unknown', 'Unknown')
    ], string='Education Level of Deceased',
        help='Highest education level achieved by the deceased')
    occupation = fields.Char(
        string='Usual Occupation of Deceased',
        help='Usual occupation of the deceased')
    business_industry = fields.Selection([
        ('agriculture', 'Agriculture, hunting, forestry and fishing'),
        ('mining', 'Mining and quarrying'),
        ('manufacturing', 'Manufacturing'),
        ('utilities', 'Electricity, gas and water supply'),
        ('construction', 'Construction'),
        ('wholesale',
         'Wholesale and retail trade; repair of motor vehicles, motorcycles and personal and household goods; hotels and restaurants'),
        ('transport', 'Transport, storage and communication'),
        ('financial',
         'Financial intermediation, insurance, real estate and business services'),
        ('services', 'Community, social and personal services'),
        ('private',
         'Private households, exterritorial organisations, representatives of foreign governments & other activities not adequately defined')
    ], string='Type of Business/Industry',
        help='Type of business or industry the deceased was involved in')
    regular_smoker = fields.Selection([
        ('yes', 'Yes'), ('no', 'No'), ('unknown', 'Do not know'),
        ('not_applicable', 'Not applicable (minor)')
    ], string='Was the deceased a regular smoker five years ago?',
        help='Indicate if the deceased was a regular smoker five years ago')
    # Fields for Section B: CERTIFICATE BY ATTENDING MEDICAL PRACTITIONER / PROFESSIONAL NURSE
    certificate_by_attend_mp = fields.Boolean(
        string='Certificate by Attending Medical Practitioner',
        help='Certify that the deceased died solely and exclusively due to Natural Causes')
    not_certified_by_mp = fields.Boolean(
        string='Not in a position to certify',
        help='Not in a position to certify that the deceased died exclusively due to Natural Causes')
    attending_mp_surname = fields.Char(
        string='Surname',
        help='Surname of the attending medical practitioner')
    attending_mp_forenames = fields.Char(
        string='Forename',
        help='Forenames of the attending medical practitioner')
    health_facility_practice_name = fields.Char(
        string='Name of Health Facility / Practice',
        help='Name of the health facility or practice')
    hpcsa_registration_no = fields.Char(
        string='HPCSA Registration No.',
        help='HPCSA registration number of the attending medical practitioner')
    facility_practice_no = fields.Char(
        string='Facility/Practice No.',
        help='Facility or practice number')
    office_telephone_no = fields.Char(
        string='Telephone No. (Office)',
        help='Office telephone number of the health facility or practice')
    business_postal_code = fields.Char(
        string='Postal Code',
        help='Postal code of the health facility or practice')
    declaration_date_signed = fields.Date(
        string='Declaration Date Signed',
        help='Date when the declaration was signed')
    signature = fields.Binary(
        string='Signature',
        help='Signature of the attending medical practitioner')
    business_street = fields.Char(
        string='Street',
        help='Street address of the health facility or practice')
    business_town = fields.Char(
        string='Town',
        help='Town of the health facility or practice')
    business_province = fields.Many2one(
        'province.province', string='Province',
        help='Province of the health facility or practice')
    office_stamp = fields.Binary(
        string='Office stamp of health facility or practice',
        help='Office stamp of the health facility or practice')
    # Fields for Section C: CERTIFICATE BY MEDICAL PRACTITIONER/ FORENSIC PATHOLOGIST
    certificate_by_medical_practitioner = fields.Selection([
        ('natural', 'Natural'), ('unnatural', 'Unnatural'),
        ('under_investigation', 'Under Investigation')
    ], string='Certificate by Medical Practitioner / Forensic Pathologist',
        help='Certification by medical practitioner or forensic pathologist on the cause of death')
    date_of_postmortem = fields.Date(
        string='Date of Post-mortem',
        help='Date when the post-mortem was conducted')
    medico_legal_mortuary_name = fields.Char(
        string='Name of Medico-legal Mortuary / Mortuary',
        help='Name of the medico-legal mortuary or mortuary')
    mortuary_reference_no = fields.Char(
        string='Mortuary Reference Number of Deceased',
        help='Reference number of the deceased at the mortuary')
    saps_case_no = fields.Char(
        string='SAPS Case No.',
        help='SAPS case number associated with the deceased')
    medical_practitioner_surname = fields.Char(
        string='Surname(practitioner)',
        help='Surname of the medical practitioner')
    medical_practitioner_forenames = fields.Char(
        string='Forenames(practitioner)',
        help='Forenames of the medical practitioner')
    business_street_practitioner = fields.Char(
        string='Street(practitioner',
        help='Street address of the medical practitioner')
    business_town_practitioner = fields.Char(
        string='Town(practitioner)',
        help='Town of the medical practitioner')
    business_province_practitioner = fields.Many2one(
        'province.province', string='Province(practitioner)',
        help='Province of the medical practitioner')
    business_postal_code_practitioner = fields.Char(
        string='Postal Code(Practitioner)',
        help='Postal code of the medical practitioner')
    name_of_police_station = fields.Char(
        string='Name of Police Station',
        help='Name of the police station handling the case')
    medical_practitioner_hpcsa_no = fields.Char(
        string='HPCSA Register No',
        help='HPCSA registration number of the medical practitioner')
    medical_practitioner_office_telephone_no = fields.Char(
        string='Telephone No',
        help='Office telephone number of the medical practitioner')
    signature_date_signed = fields.Date(
        string='Date Signed',
        help='Date when the signature was done')
    medical_practitioner_signature = fields.Binary(
        string='Medical Practitioner Signature',
        help='Signature of the medical practitioner')
    mortuary_no = fields.Char(
        string='Mortuary No.',
        help='Mortuary number')
    office_stamp_of_mortuary = fields.Binary(
        string='Office stamp of mortuary',
        help='Office stamp of the mortuary')
    # Fields for Section Cause of Death
    cause_death_id = fields.Many2one(
        'cause.death', string='Cause of Death',
         help='Cause of Death')
    image = fields.Image()
    # Section D: PARTICULARS OF INFORMANT
    is_informant_foreigner = fields.Boolean(
        string='Is Informant Foreigner',
        help='Indicate if the Informant was a foreigner')
    passport_informant_no = fields.Char(
        string='Passport No:',
        help='Passport number of the Informant')
    informant_identity_no = fields.Char(string='Informant Identity No.',
                                        help='Identity No')
    informant_citizenship_id = fields.Many2one(
        'res.country', string='Informant Citizenship',
        help='Citizenship of the informant')
    informant_surname = fields.Char(string='Informant Surname',
                                    help='Surname of the informant')
    informant_forenames = fields.Char(string='Informant Forenames',
                                      help='Forenames of the informant')
    informant_residential_street = fields.Char(
        string='Informant Residential Street',
        help='Residential Street of the informant')
    informant_residential_town = fields.Char(
        string='Informant Residential Town',
        help='Residential Town of the informant')
    informant_residential_province = fields.Many2one(
        'province.province',
        string='Informant Residential Province',
        help='Residential Province of the informant')
    informant_residential_postal_code = fields.Char(
        string='Informant Residential Postal Code',
        help='Postal Code of the informant')
    informant_home_phone = fields.Char(string='Informant Telephone No. (Home)',
                                       help='Home Telephone No. of the informant')
    informant_cellphone_no = fields.Char(string='Informant Cellphone No.',
                                         help='Cellphone No. of the informant')
    informant_date_of_birth = fields.Date(string='Informant Date of Birth',
                                          help='Date of Birth of the informant')
    informant_relationship = fields.Selection([
        ('parent', 'Parent'),
        ('spouse', 'Spouse'),
        ('child', 'Child'),
        ('other', 'Other, Specify')
    ], string='The Deceased is my',
        help='Relationship of the informant to the deceased')
    informant_relationship_other = fields.Char(string='Other Relationship',
                                               help='Specify other relationship if selected')
    informant_signature = fields.Binary(string='Informant Signature',
                                        help='Signature of the informant')
    informant_left_thumbprint = fields.Binary(
        string='Informant Left Thumbprint',
        help='Left thumb print of the informant')
    informant_date_signed = fields.Date(string='Date Signed',
                                        help='Date when the form was signed by the informant')
    informant_place_signed = fields.Char(string='Place Signed',
                                         help='Place where the form was signed by the informant')
    personal_no = fields.Char(string="Personal No")

    def _get_parlour_domain(self):
        parlour_ids = self.env['funeral.parlour'].search([
            ('undertaker_ids', 'in', self.env.user.id)
        ]).ids
        return [('id', 'in', parlour_ids)]

    # Section E: PARTICULARS OF FUNERAL UNDERTAKER
    funeral_parlour_id = fields.Many2one('funeral.parlour',
                                         string='Name of Funeral Parlour',
                                         domain=_get_parlour_domain)

    dha_designation_no = fields.Char(string='DHA Designation No.')
    sars_reg_no = fields.Char(string='SARS Reg. No. (Income tax reference no.)')
    is_undertaker_foreigner = fields.Boolean(
        string='Is Undertaker Foreigner',
        help='Indicate if the Undertaker was a foreigner')
    passport_undertaker = fields.Char(
        string='Passport No',
        help='Passport number of the Undertaker')
    undertaker_identity_no = fields.Char(
        string='Undertaker Identity No')
    undertaker_surname = fields.Char(string='Undertaker Surname')
    undertaker_forenames = fields.Char(string='Undertaker Forenames')
    company_reg_no = fields.Char(string='Company Reg. No.')
    undertaker_street = fields.Char(string='Street:')
    undertaker_town = fields.Char(string='Town:')
    undertaker_province = fields.Many2one(
        'province.province', string='Province:')
    undertaker_postal_code = fields.Char(
        string='Postal Code:')
    office_phone_no = fields.Char(string='Office Telephone No.')
    undertaker_cellphone_no = fields.Char(string='Undertaker Cellphone No.')
    date_of_collection_of_corpse = fields.Date(
        string='Date of Collection of Corpse')
    interment_type = fields.Selection([
        ('burial', 'Burial'),
        ('cremation', 'Cremation')
    ], string='Interment Type', required=True)
    date_of_cremation = fields.Date(string='Date of Cremation')
    place_of_burial = fields.Char(string='Place of Burial (City/Town/Village)')
    date_of_burial = fields.Date(string='Date of Burial')
    is_grave_available = fields.Boolean(
        string='Grave Available',
        help='Indicate Grave Available')
    grave_no = fields.Char(string='Grave No')
    collector_name = fields.Char(
        string='Name of Person who Collected the Deceased')
    is_collector_foreigner = fields.Boolean(
        string='Is Collector Foreigner',
        help='Indicate if the Collector was a foreigner')
    collector_identity_no = fields.Char(
        string='Collector Identity No')
    collector_passport_number = fields.Char(
        string='Collector Passport No')
    collector_surname = fields.Char(string='Collector Surname')
    collector_forenames = fields.Char(string='Collector Forenames')
    undertaker_place_signed = fields.Char(string='Place Signed')
    undertaker_date_signed = fields.Date(string='Date Signed')
    undertaker_signature = fields.Binary(string='Undertaker Signature')
    undertaker_left_thumbprint = fields.Binary(
        string='Left thumbprint of funeral undertaker')
    office_stamp = fields.Binary(string='Office Stamp of Funeral Undertaker')

    age = fields.Integer(string='Age', compute="_compute_age")

    cemetery_id = fields.Many2one('cemetery.cemetery', string='Cemetery',
                                  domain="[('municipality_id', '=', municipality_id)]")
    section_id = fields.Many2one('cemetery.section', string='Section')

    def _get_municipality(self):
        """Returns municipality data"""
        municipality = self.env['municipality.municipality'].search(
            [('company_id', '=', self.env.company.id)], limit=1)
        return municipality.id

    municipality_id = fields.Many2one('municipality.municipality',
                                      default=_get_municipality,
                                      string="Municipality", required=True)

    grave_id = fields.Many2one('grave.grave', string="Grave",
                               domain="[('section_id', '=', section_id)]")

    @api.depends('date_of_birth', 'date_of_death')
    def _compute_age(self):
        for rec in self:
            age = 0
            if rec.date_of_birth and rec.date_of_death:
                age = rec.date_of_death.year - rec.date_of_birth.year
            rec.age = age

    @api.onchange('date_of_death')
    def _onchange_date_of_death(self):
        """
        Check if the date_of_death is in the future and raise an error if it is.
        This method is triggered whenever the date_of_death field is changed. If the
        new date is greater than today's date, it resets the field and raises a UserError.
        """
        if self.date_of_death and self.date_of_death > date.today():
            self.date_of_death = False
            raise UserError(
                "The Date of Death / Still Birth cannot be in the future.")
