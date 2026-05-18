# -*- coding: utf-8 -*-

from odoo import models, fields


class SagovProcurementEvaluationCriteria(models.Model):
    """Evaluation criteria for a procurement method"""
    _name = 'sagovprocurement.evaluation.criteria'
    _description = 'Procurement Method Evaluation Criteria'
    _order = 'sequence'

    method_id = fields.Many2one(
        'sagovprocurement.method',
        string='Procurement Method',
        required=True,
        ondelete='cascade'
    )
    name = fields.Char(
        string='Criteria Name',
        required=True,
        help='E.g., Price, Quality, B-BBEE Status, Delivery Time, etc.'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    description = fields.Text(
        string='Description'
    )
    weight = fields.Float(
        string='Weight (%)',
        help='Weight/importance of this criteria in evaluation (0-100)'
    )
    criteria_type = fields.Selection([
        ('price', 'Price'),
        ('quality', 'Quality'),
        ('bbbee', 'B-BBEE'),
        ('technical', 'Technical'),
        ('delivery', 'Delivery'),
        ('experience', 'Experience'),
        ('other', 'Other')
    ], string='Criteria Type', default='price')
