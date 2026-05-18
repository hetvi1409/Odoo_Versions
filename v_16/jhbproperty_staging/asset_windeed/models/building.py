from odoo import models, fields

class Building(models.Model):
    _inherit = 'building'

    # Property Details
    property_type = fields.Char(string='Property Type')
    diagram_deed_number = fields.Char(string='Diagram Deed Number')
    township = fields.Char(string='Township')
    local_authority = fields.Char(string='Local Authority')
    erf_number = fields.Char(string='Erf Number')
    province = fields.Char(string='Province')
    portion_number = fields.Char(string='Portion Number')
    extent = fields.Float(string='Extent')
    registration_division = fields.Char(string='Registration Division')
    lpi_code = fields.Char(string='LPI Code')

    # Ownership
    person_type = fields.Selection([('individual', 'Individual'), ('company', 'Company')], string='Person Type')
    id_number = fields.Char(string='ID Number')
    owner_name = fields.Char(string='Name')
    multiple_owners = fields.Boolean(string='Multiple Owners')
    multiple_properties = fields.Boolean(string='Multiple Properties')
    share_percentage = fields.Float(string='Share (%)')
    ownership_document = fields.Binary(string='Ownership Document')
    microfilm_scanned_date = fields.Date(string='Ownership Microfilm / Scanned Date')
    purchase_price = fields.Float(string='Purchase Price (R)')
    purchase_date_ownership = fields.Date(string='Ownership Purchase Date')
    registration_date_ownership = fields.Date(string='Ownership Registration Date')

    # Endorsements
    endorsement_document = fields.Binary(string='Endorsements Document')
    institution = fields.Char(string='Institution')
    endorsement_amount = fields.Float(string='Endorsements Amount (R)')
    endorsement_microfilm_date = fields.Date(string='Endorsement Microfilm / Scanned Date')

    # History of Documents
    history_document = fields.Binary(string='History Document')
    history_institution = fields.Char(string='History Institution')
    history_amount = fields.Float(string='History Amount (R)')
    history_microfilm_date = fields.Date(string='History Microfilm / Scanned Date')
