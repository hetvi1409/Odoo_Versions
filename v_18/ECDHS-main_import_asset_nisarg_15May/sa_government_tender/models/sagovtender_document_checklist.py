# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class SagovTenderDocumentChecklist(models.Model):
    """Document checklist generated from procurement method requirements"""
    _name = 'sagovtender.document.checklist'
    _description = 'Tender Document Checklist'
    _order = 'sequence, id'

    tender_id = fields.Many2one(
        'sagovtender.tender',
        string='Tender',
        required=True,
        ondelete='cascade',
        index=True
    )
    document_requirement_id = fields.Many2one(
        'sagovprocurement.document.requirement',
        string='Document Requirement',
        required=False,
        ondelete='restrict',
        help='Link to the procurement method document requirement (auto-filled when created from workflow)'
    )
    sequence = fields.Integer(
        related='document_requirement_id.sequence',
        string='Sequence',
        store=True
    )
    name = fields.Char(
        string='Document Name',
        compute='_compute_name',
        store=True,
        help='Document requirement name or custom document name'
    )
    document_type = fields.Selection(
        related='document_requirement_id.document_type',
        string='Document Type',
        store=True
    )
    mandatory = fields.Boolean(
        string='Mandatory',
        compute='_compute_mandatory',
        store=True,
        help='Whether this document is mandatory'
    )
    description = fields.Text(
        related='document_requirement_id.description',
        string='Description'
    )
    tender_document_id = fields.Many2one(
        'sagovtender.document',
        string='Uploaded Document',
        help='Link to the actual uploaded document'
    )
    uploaded = fields.Boolean(
        string='Uploaded',
        compute='_compute_uploaded',
        store=True
    )
    uploaded_by_id = fields.Many2one(
        related='tender_document_id.uploaded_by_id',
        string='Uploaded By'
    )
    upload_date = fields.Datetime(
        related='tender_document_id.upload_date',
        string='Upload Date'
    )
    state = fields.Selection([
        ('pending', 'Pending'),
        ('uploaded', 'Uploaded'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ], string='Status', default='pending', required=True)
    verification_notes = fields.Text(string='Verification Notes')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    @api.depends('tender_document_id')
    def _compute_uploaded(self):
        """Check if document has been uploaded"""
        for record in self:
            record.uploaded = bool(record.tender_document_id)
            if record.uploaded and record.state == 'pending':
                record.state = 'uploaded'

    @api.depends('document_requirement_id')
    def _compute_name(self):
        """Set document name from requirement"""
        for record in self:
            record.name = record.document_requirement_id.name if record.document_requirement_id else ''

    @api.depends('document_requirement_id')
    def _compute_mandatory(self):
        """Set mandatory flag from requirement"""
        for record in self:
            record.mandatory = bool(record.document_requirement_id and record.document_requirement_id.mandatory)

    def action_upload_document(self):
        """Open upload form for a tender document and link it to this checklist item."""
        self.ensure_one()
        if not self.tender_id:
            raise UserError('Please select a tender before uploading a document.')

        default_document_type = self.document_type or 'sagovtender_document'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Upload Document',
            'res_model': 'sagovtender.document',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_tender_id': self.tender_id.id,
                'default_name': self.name or 'Tender Document',
                'default_document_type': default_document_type,
                'checklist_item_id': self.id,
            },
        }

    def action_verify_document(self):
        """Mark checklist item as verified."""
        self.ensure_one()
        if not self.tender_document_id:
            raise UserError('Please upload a document before verifying.')
        self.write({'state': 'verified'})
        return True

    def action_reject_document(self):
        """Reject the uploaded document."""
        self.ensure_one()
        if not self.tender_document_id:
            raise UserError('Please upload a document before rejecting.')
        self.write({'state': 'rejected'})
        return True
