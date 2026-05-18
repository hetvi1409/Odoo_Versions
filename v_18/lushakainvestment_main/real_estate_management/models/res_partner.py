from odoo import fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    contact_surname = fields.Char(string="Surname", required=False)
    reg_number = fields.Char(string="Registration Number")
    id_number = fields.Char(string="ID Number")
    passport_number = fields.Char(string="Passport Number")
    trust_number = fields.Char(string="Trust Number")
    is_trust = fields.Boolean()
    company_type = fields.Selection([('person', 'Individual'), ('company', 'Company'), ('trust', 'Trust')], ondelete={'trust': 'set company'})
    cipc_certificate = fields.Binary(string="CIPC Certificate")
    notice_cipc_certificate = fields.Binary(string="Notice of Registered Office Certificate")
    moi_founding_statement = fields.Binary(string="MOI / Founding Statement")
    id_proof_address = fields.Binary(string="ID + Proof of Address")
    utility_bill_lease = fields.Binary(string="Utility Bill / Lease")
    sars_certificate = fields.Binary(string="SARS Certificate")
    bank_letter = fields.Binary(string="Bank Letter")

    id_passport_copy = fields.Binary(string="ID / Passport Copy")
    home_affairs_immigration = fields.Binary(string="Home Affairs / Immigration Document")
    utility_bill_lease_bank_statement = fields.Binary(string="Utility Bill / Lease/ Bank Statement")
    sars_document = fields.Binary(string="SARS Document")
    certified_trust_deed = fields.Binary(string="Certified Trust Deed")
    master_letter_authority = fields.Binary(string="Master’s Letter of Authority")
    trustee_id_proof_address = fields.Binary(string="Trustee IDs and Proof of Address")

