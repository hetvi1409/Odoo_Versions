# -*- coding: utf-8 -*-

from odoo import models, fields


class SagovProcurementDocumentRequirement(models.Model):
    """Document required for a specific procurement method"""
    _name = 'sagovprocurement.document.requirement'
    _description = 'Procurement Method Document Requirement'
    _order = 'sequence'

    method_id = fields.Many2one(
        'sagovprocurement.method',
        string='Procurement Method',
        required=True,
        ondelete='cascade'
    )
    name = fields.Char(
        string='Document Name',
        required=True,
        help='E.g., Tax Clearance, CSD Certificate, B-BBEE Certificate, etc.'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    description = fields.Text(
        string='Description',
        help='Details about this document requirement'
    )
    mandatory = fields.Boolean(
        string='Mandatory',
        default=True,
        help='Is this document mandatory or optional?'
    )
    document_type = fields.Selection([
        ('compliance', 'Compliance Document'),
        ('technical', 'Technical Document'),
        ('financial', 'Financial Document'),
        ('legal', 'Legal Document'),
        ('other', 'Other')
    ], string='Document Type', default='compliance')
