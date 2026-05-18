# -*- coding: utf-8 -*-
"""Procurement Method Model - Configurable procurement methods per SA Government regulations"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SagovProcurementMethod(models.Model):
    """
    Procurement Method Model

    Defines configurable procurement methods per PFMA, MFMA, PPPFA,
    and National Treasury regulations.

    Each method specifies:
    - Method type and description
    - Value ranges for applicability
    - Requirements (quotations, evaluation criteria, etc.)
    - Workflow configuration
    - Compliance rules
    """
    _name = 'sagovprocurement.method'
    _description = 'Procurement Method Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Procurement method name must be unique!')
    ]

    # Basic Information
    name = fields.Char(
        string='Method Name',
        required=True,
        help='E.g., Quotation < R30,000, Open RFQ, Competitive Bid, Sole Source, etc.'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of appearance in selection lists'
    )
    code = fields.Char(
        string='Code',
        required=True,
        help='Unique identifier: quotation_r30k, open_rfq, competitive_bid_r50m, etc.'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Inactive methods are not available for selection'
    )
    description = fields.Html(
        string='Description',
        help='Full description of the procurement method'
    )

    # Value Thresholds
    min_value = fields.Monetary(
        string='Minimum Value',
        currency_field='currency_id',
        help='Minimum procurement value for this method'
    )
    max_value = fields.Monetary(
        string='Maximum Value',
        currency_field='currency_id',
        help='Maximum procurement value for this method (0 = no limit)'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True
    )

    # Quotation Requirements
    quotations_required = fields.Integer(
        string='Number of Quotations Required',
        default=1,
        help='Minimum number of quotations/bids required'
    )
    quotation_period_days = fields.Integer(
        string='Quotation Period (Days)',
        default=10,
        help='Number of days allowed for quotation submission'
    )
    written_quotation_only = fields.Boolean(
        string='Written Quotation Only',
        default=True,
        help='If checked, only written quotations (email/letterhead/PDF) are accepted'
    )

    # Approval Requirements
    requires_bsc_approval = fields.Boolean(
        string='Requires BSC Approval',
        default=False,
        help='Whether Bid Specification Committee approval is required'
    )
    requires_bec_evaluation = fields.Boolean(
        string='Requires BEC Evaluation',
        default=False,
        help='Whether Bid Evaluation Committee evaluation is required'
    )
    requires_bac_review = fields.Boolean(
        string='Requires BAC Review',
        default=False,
        help='Whether Bid Adjudication Committee review is required'
    )
    requires_briefing_session = fields.Boolean(
        string='Briefing Session',
        default=False,
        help='Whether a briefing session is compulsory or optional'
    )
    briefing_mandatory = fields.Boolean(
        string='Briefing Mandatory',
        default=False,
        help='If true, briefing session is compulsory; if false, optional'
    )

    # Advertising & Compliance
    advertising_days_minimum = fields.Integer(
        string='Minimum Advertising Period (Days)',
        default=7,
        help='Minimum number of days to advertise the procurement'
    )
    late_bids_rejected = fields.Boolean(
        string='Late Bids/Quotations Rejected',
        default=True,
        help='If true, submissions after closing are automatically rejected'
    )
    requires_compliance_check = fields.Boolean(
        string='Requires Compliance Check',
        default=False,
        help='Whether CSD, Tax, COID, B-BBEE compliance verification is required'
    )
    requires_declaration_interest = fields.Boolean(
        string='Requires Declaration of Interest',
        default=False,
        help='Whether suppliers must declare conflicts of interest'
    )

    # Preference Point System Configuration
    preference_point_system_ids = fields.Many2many(
        'sagovpreference.point.system',
        'method_preference_rel',
        'method_id',
        'preference_id',
        string='Applicable Preference Point Systems',
        help='Preference point systems that apply to this procurement method'
    )

    # Workflow Configuration
    workflow_stage_ids = fields.One2many(
        'sagovprocurement.workflow.stage',
        'method_id',
        string='Workflow Stages',
        help='Stages/steps in the workflow for this procurement method'
    )

    # Regulatory Compliance
    pppfa_compliant = fields.Boolean(
        string='PPPFA Compliant',
        default=True,
        help='Compliant with Preferential Procurement Policy Framework Act'
    )
    pfma_compliant = fields.Boolean(
        string='PFMA Compliant',
        default=True,
        help='Compliant with Public Finance Management Act'
    )
    mfma_compliant = fields.Boolean(
        string='MFMA Compliant',
        default=False,
        help='Compliant with Municipal Finance Management Act (for municipalities)'
    )
    treasury_regulation_compliant = fields.Boolean(
        string='National Treasury Regulation Compliant',
        default=True,
        help='Compliant with National Treasury regulations'
    )
    legal_framework = fields.Text(
        string='Legal Framework',
        help='Reference to relevant laws and regulations (Constitution S217, PFMA, MFMA, etc.)'
    )

    # Documentation Requirements
    document_requirement_ids = fields.One2many(
        'sagovprocurement.document.requirement',
        'method_id',
        string='Document Requirements',
        help='Required documents for this procurement method'
    )

    # Evaluation Criteria
    evaluation_criteria_ids = fields.One2many(
        'sagovprocurement.evaluation.criteria',
        'method_id',
        string='Evaluation Criteria',
        help='Criteria used to evaluate bids/quotations'
    )

    # Additional Settings
    allows_negotiation = fields.Boolean(
        string='Allows Negotiation',
        default=False,
        help='Whether supplier negotiation is permitted after evaluation'
    )
    allows_framework_agreement = fields.Boolean(
        string='Allows Framework Agreement',
        default=False,
        help='Whether framework agreements can be used with this method'
    )
    allows_panel_procurement = fields.Boolean(
        string='Allows Panel Procurement',
        default=False,
        help='Whether panel of pre-approved suppliers can be used'
    )

    # Notes and Policies
    policy_notes = fields.Html(
        string='Policy Notes',
        help='Additional notes on organizational procurement policy for this method'
    )
    internal_notes = fields.Text(
        string='Internal Notes',
        help='Internal notes for SCM team'
    )

    # Audit Fields
    created_by_user_id = fields.Many2one(
        'res.users',
        string='Created By',
        readonly=True,
        default=lambda self: self.env.user
    )
    last_modified_by_user_id = fields.Many2one(
        'res.users',
        string='Last Modified By',
        readonly=True,
        default=lambda self: self.env.user
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Create method with audit tracking"""
        for vals in vals_list:
            vals['created_by_user_id'] = self.env.user.id
            vals['last_modified_by_user_id'] = self.env.user.id
        return super().create(vals_list)

    def write(self, vals):
        """Write method with audit tracking"""
        vals['last_modified_by_user_id'] = self.env.user.id
        return super().write(vals)

    @api.constrains('min_value', 'max_value')
    def _check_value_range(self):
        """Ensure min_value <= max_value"""
        for record in self:
            if record.max_value > 0 and record.min_value > record.max_value:
                raise ValidationError(
                    f'Minimum value ({record.min_value}) cannot be greater than '
                    f'maximum value ({record.max_value})'
                )

    @api.constrains('quotations_required')
    def _check_quotations_required(self):
        """Ensure quotations_required is at least 1"""
        for record in self:
            if record.quotations_required < 1:
                raise ValidationError('At least 1 quotation/bid is required')

    def get_applicable_method(self, estimated_value):
        """
        Get applicable procurement method for a given value

        Args:
            estimated_value: The estimated value of the procurement

        Returns:
            Procurement method record or None
        """
        return self.search([
            ('active', '=', True),
            ('min_value', '<=', estimated_value),
            ('|'),
            ('max_value', '=', 0),
            ('max_value', '>=', estimated_value)
        ], limit=1)

    def get_workflow_sequence(self):
        """Get the complete workflow sequence for this method"""
        return self.workflow_stage_ids.sorted('sequence')

    def get_document_requirements(self):
        """Get all document requirements for this method"""
        return self.document_requirement_ids

    def get_evaluation_criteria(self):
        """Get all evaluation criteria for this method"""
        return self.evaluation_criteria_ids.sorted('sequence')

    def validate_compliance(self):
        """Validate that all compliance requirements are met"""
        missing_compliance = []

        if self.pfma_compliant and not self.legal_framework:
            missing_compliance.append('Legal framework reference missing for PFMA compliance')

        if (self.requires_bsc_approval or self.requires_bec_evaluation) and not self.evaluation_criteria_ids:
            missing_compliance.append('Evaluation criteria must be defined for this method')

        if missing_compliance:
            raise ValidationError(
                'Compliance validation failed:\n' + '\n'.join(missing_compliance)
            )

        return True
