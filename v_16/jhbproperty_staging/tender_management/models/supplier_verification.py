from odoo import api, models, fields, _


class SupplierVerification(models.Model):
    _name = 'supplier.verification'
    _description = 'Supplier Verification'
    _rec_name = 'supplier_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    supplier_id = fields.Many2one('res.partner', string='Supplier',
                                  domain=[('supplier_rank', '>', 0)],
                                  help="Select the supplier for which verification is being performed.")

    csd_id = fields.Char(string='CSD ID',
                         help="Unique identifier from CSD for supplier verification.")

    csd_verification_status = fields.Selection([
        ('verified', 'Verified'),
        ('unverified', 'Unverified')
    ], string='CSD Verification Status',
        help="Status of CSD verification for the supplier.")

    cidb_id = fields.Char(string='CIDB ID',
                          help="Unique identifier from CIDB for supplier verification.")

    cidb_verification_status = fields.Selection([
        ('verified', 'Verified'),
        ('unverified', 'Unverified')
    ], string='CIDB Verification Status',
        help="Status of CIDB verification for the supplier.")

    checklist_docs = fields.One2many('supplier.verification.checklist', 'verification_id', string='Checklist Documents')
