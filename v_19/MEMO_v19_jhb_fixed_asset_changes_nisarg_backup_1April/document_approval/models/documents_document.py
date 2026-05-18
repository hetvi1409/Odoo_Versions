from odoo import fields, models


class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

    approval_request_id = fields.Many2one('documents.approval', string="Approval Request")
    # state = fields.Selection(selection=[
    #     ('draft', 'Draft'),
    #     ('send', 'Send for Approval'),
    #     ('approved', 'Approved'),
    #     ('reject', 'Rejected')], string='Status', required=True, readonly=True,
    #     copy=False, tracking=True, default='draft')
