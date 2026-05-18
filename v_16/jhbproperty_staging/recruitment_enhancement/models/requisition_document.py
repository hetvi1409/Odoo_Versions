from odoo import api, fields, models, _


class DocumentType(models.Model):
    _name = 'document.type'
    _description = 'Document Type'
    _order = 'sequence, name'
    _rec_name = 'name'

    name = fields.Char(required=True)
    # code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)


class RequisitionDocument(models.Model):
    _name = 'requisition.document'
    _description = 'Requisition Document'
    _order = 'id'
    _rec_name = 'requisition_id'

    requisition_id = fields.Many2one('recruitment.requisition', ondelete='cascade')
    document_type_id = fields.Many2one(
        'document.type',
        string='Document Type',
        required=True,
        ondelete='restrict',
    )
    document_file = fields.Binary(string='Document', attachment=True, required=True)
    document_filename = fields.Char(string='Filename')
