from odoo import api, models, fields, _


class SupplierVerificationChecklist(models.Model):
    _name = 'supplier.verification.checklist'
    _description = 'Supplier Verification Checklist'

    verification_id = fields.Many2one('supplier.verification', string='Verification')
    checklist_doc = fields.Char(string='Checklist Docs')
    document_file = fields.Binary(string='Document File')
    checklist_checkbox = fields.Boolean(string='Checklist Checkbox')
    compliant_selection = fields.Selection([
        ('comply', 'Comply'),
        ('non_comply', 'Non-Comply')
    ], string='Compliant Selection')
    comment = fields.Text(string='Comment')
