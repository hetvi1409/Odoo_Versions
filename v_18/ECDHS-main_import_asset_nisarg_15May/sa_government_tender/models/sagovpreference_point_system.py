# -*- coding: utf-8 -*-
"""Preference Point System Model - Configurable preference point systems per PPPFA"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SagovPreferencePointSystem(models.Model):
    """
    Preference Point System Model

    Defines preference point systems per PPPFA regulations.

    Supports:
    - 80/20 preference system (price 80%, preference points 20%)
    - 90/10 preference system (price 90%, preference points 10%)
    - Custom preference systems

    Each system defines which criteria attract preference points and scoring rules.
    """
    _name = 'sagovpreference.point.system'
    _description = 'Preference Point System Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Preference point system name must be unique!')
    ]

    # Basic Information
    name = fields.Char(
        string='System Name',
        required=True,
        help='E.g., 80/20 System, 90/10 System, Custom System, etc.'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of appearance in selection lists'
    )
    code = fields.Char(
        string='Code',
        required=True,
        help='Unique identifier: system_80_20, system_90_10, etc.'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Inactive systems are not available for selection'
    )
    description = fields.Html(
        string='Description',
        help='Full description of the preference point system'
    )

    # System Configuration
    system_type = fields.Selection([
        ('80_20', '80/20 System (R30,000 - R500,000)'),
        ('90_10', '90/10 System (Above R500,000)'),
        ('custom', 'Custom System')
    ], string='System Type', required=True, default='80_20')

    # Price vs Preference Points Weighting
    price_weight_percentage = fields.Float(
        string='Price Weight (%)',
        default=80.0,
        help='Percentage weight for price evaluation (typically 80 or 90)'
    )
    preference_weight_percentage = fields.Float(
        string='Preference Points Weight (%)',
        default=20.0,
        help='Percentage weight for preference points (typically 20 or 10)'
    )

    # Preference Points Configuration
    total_preference_points = fields.Float(
        string='Total Preference Points Available',
        default=20.0,
        help='Maximum preference points available for suppliers'
    )

    # B-BBEE & Social Policy Points
    bbbee_points = fields.Float(
        string='B-BBEE Points',
        default=0.0,
        help='Preference points available for B-BBEE compliance'
    )
    bbbee_weight = fields.Float(
        string='B-BBEE Weight',
        default=0.0,
        help='Weight/multiplier for B-BBEE points'
    )
    women_empowerment_points = fields.Float(
        string='Women Empowerment Points',
        default=0.0,
        help='Preference points for women-owned or women-managed businesses'
    )
    youth_points = fields.Float(
        string='Youth Entrepreneur Points',
        default=0.0,
        help='Preference points for youth-owned businesses (18-35 years)'
    )
    local_content_points = fields.Float(
        string='Local Content Points',
        default=0.0,
        help='Preference points for local manufacturing/sourcing'
    )
    sme_points = fields.Float(
        string='SME Points',
        default=0.0,
        help='Preference points for small and medium enterprises'
    )
    pwd_points = fields.Float(
        string='PWD (Persons with Disability) Points',
        default=0.0,
        help='Preference points for businesses led by persons with disabilities'
    )

    # Validation Rules
    price_formula = fields.Selection([
        ('lowest_wins', 'Lowest Price Wins'),
        ('lowest_scored', 'Lowest Price Highest Scored'),
        ('custom_formula', 'Custom Formula')
    ], string='Price Scoring Formula', default='lowest_scored')

    custom_price_formula = fields.Text(
        string='Custom Price Formula',
        help='Formula for custom price calculation (e.g., (BID_PRICE / MIN_BID) * 80)'
    )

    preference_criteria_ids = fields.One2many(
        'sagovpreference.point.criteria',
        'system_id',
        string='Preference Criteria',
        help='Detailed preference point criteria for this system'
    )

    # Regulatory Compliance
    pppfa_compliant = fields.Boolean(
        string='PPPFA Compliant',
        default=True,
        help='Compliant with Preferential Procurement Policy Framework Act'
    )
    legal_reference = fields.Text(
        string='Legal Reference',
        help='Reference to PPPFA and other relevant regulations'
    )

    # Applicability
    applicable_value_range_ids = fields.Many2many(
        'sagovprocurement.method',
        'preference_method_rel',
        'preference_id',
        'method_id',
        string='Applicable Procurement Methods',
        help='Procurement methods where this preference system applies'
    )

    minimum_applicable_value = fields.Monetary(
        string='Minimum Applicable Value',
        currency_field='currency_id',
        help='Minimum tender value for this preference system to apply'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True
    )

    # Notes
    policy_notes = fields.Html(
        string='Policy Notes',
        help='Additional policy notes'
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
        """Create record with audit tracking"""
        for vals in vals_list:
            vals['created_by_user_id'] = self.env.user.id
            vals['last_modified_by_user_id'] = self.env.user.id
        return super().create(vals_list)

    def write(self, vals):
        """Write record with audit tracking"""
        vals['last_modified_by_user_id'] = self.env.user.id
        return super().write(vals)

    @api.constrains('price_weight_percentage', 'preference_weight_percentage')
    def _check_weights(self):
        """Ensure weights add up to 100%"""
        for record in self:
            total = record.price_weight_percentage + record.preference_weight_percentage
            if abs(total - 100.0) > 0.01:  # Allow small rounding differences
                raise ValidationError(
                    f'Price weight ({record.price_weight_percentage}%) + '
                    f'Preference weight ({record.preference_weight_percentage}%) '
                    f'must equal 100%'
                )

    @api.constrains('bbbee_points', 'women_empowerment_points', 'youth_points',
                   'local_content_points', 'sme_points', 'pwd_points')
    def _check_total_points(self):
        """Ensure total points don't exceed available preference points"""
        for record in self:
            total_allocated = (
                record.bbbee_points + record.women_empowerment_points +
                record.youth_points + record.local_content_points +
                record.sme_points + record.pwd_points
            )
            if total_allocated > record.total_preference_points:
                raise ValidationError(
                    f'Total allocated preference points ({total_allocated}) '
                    f'exceeds total available ({record.total_preference_points})'
                )

    def get_preference_criteria(self):
        """Get all preference criteria for this system"""
        return self.preference_criteria_ids.sorted('sequence')

    def calculate_preference_score(self, supplier_attrs):
        """
        Calculate preference score for a supplier

        Args:
            supplier_attrs: Dictionary of supplier attributes
                {
                    'bbbee_level': 1-8,
                    'is_women_owned': True/False,
                    'is_youth_owned': True/False,
                    'local_content_percentage': 0-100,
                    'is_sme': True/False,
                    'is_pwd_owner': True/False,
                    ...other criteria
                }

        Returns:
            Float: Calculated preference score
        """
        score = 0.0

        # B-BBEE Scoring
        if 'bbbee_level' in supplier_attrs and self.bbbee_points > 0:
            bbbee_level = supplier_attrs.get('bbbee_level', 0)
            if 1 <= bbbee_level <= 4:  # First-time BEE or Generic BEE
                score += self.bbbee_points
            elif 5 <= bbbee_level <= 8:  # Other BEE levels
                score += self.bbbee_points * 0.5

        # Women Empowerment
        if supplier_attrs.get('is_women_owned', False) and self.women_empowerment_points > 0:
            score += self.women_empowerment_points

        # Youth Entrepreneur
        if supplier_attrs.get('is_youth_owned', False) and self.youth_points > 0:
            score += self.youth_points

        # Local Content
        if self.local_content_points > 0:
            local_content = supplier_attrs.get('local_content_percentage', 0)
            if local_content >= 100:
                score += self.local_content_points
            elif local_content >= 50:
                score += self.local_content_points * 0.75
            elif local_content >= 25:
                score += self.local_content_points * 0.5

        # SME
        if supplier_attrs.get('is_sme', False) and self.sme_points > 0:
            score += self.sme_points

        # PWD (Persons with Disability)
        if supplier_attrs.get('is_pwd_owner', False) and self.pwd_points > 0:
            score += self.pwd_points

        # Custom criteria scoring
        for criteria in self.preference_criteria_ids:
            if criteria.criteria_key in supplier_attrs:
                score += criteria.calculate_score(supplier_attrs.get(criteria.criteria_key))

        return min(score, self.total_preference_points)

    def calculate_final_score(self, price_score, preference_score):
        """
        Calculate final bid score combining price and preference

        Args:
            price_score: Float - price component score
            preference_score: Float - preference points score

        Returns:
            Float: Final weighted score
        """
        price_component = (price_score / 100.0) * self.price_weight_percentage
        preference_component = (preference_score / self.total_preference_points) * self.preference_weight_percentage
        return price_component + preference_component

    def validate_system(self):
        """Validate the preference point system configuration"""
        errors = []

        if self.system_type in ['80_20', '90_10']:
            expected_price = 80.0 if self.system_type == '80_20' else 90.0
            expected_preference = 100.0 - expected_price
            if abs(self.price_weight_percentage - expected_price) > 0.01:
                errors.append(
                    f'{self.system_type} system requires {expected_price}% price weight'
                )

        if self.price_weight_percentage < 0 or self.price_weight_percentage > 100:
            errors.append('Price weight must be between 0% and 100%')

        if not self.preference_criteria_ids and self.preference_weight_percentage > 0:
            errors.append('Define preference criteria for this system')

        if errors:
            raise ValidationError(
                'System validation failed:\n' + '\n'.join(errors)
            )

        return True


class SagovPreferencePointCriteria(models.Model):
    """Detailed preference criteria for scoring"""
    _name = 'sagovpreference.point.criteria'
    _description = 'Preference Point Criteria'
    _order = 'sequence'

    system_id = fields.Many2one(
        'sagovpreference.point.system',
        string='Preference System',
        required=True,
        ondelete='cascade'
    )
    name = fields.Char(
        string='Criteria Name',
        required=True,
        help='E.g., B-BBEE Level, Women Empowerment, etc.'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    criteria_key = fields.Char(
        string='Criteria Key',
        required=True,
        help='Key used to retrieve this criterion from supplier data'
    )
    description = fields.Html(
        string='Description'
    )
    criteria_type = fields.Selection([
        ('binary', 'Binary (Yes/No)'),
        ('level', 'Level-based'),
        ('percentage', 'Percentage'),
        ('points', 'Direct Points'),
        ('custom', 'Custom Calculation')
    ], string='Criteria Type', required=True)
    points = fields.Float(
        string='Points Available',
        help='Maximum points for this criterion'
    )
    scoring_rule = fields.Selection([
        ('all_or_nothing', 'All or Nothing'),
        ('proportional', 'Proportional'),
        ('tiered', 'Tiered/Bracketed')
    ], string='Scoring Rule', default='all_or_nothing')
    tiered_scoring = fields.Text(
        string='Tiered Scoring Definition',
        help='JSON format: {"0-25": 5, "26-50": 10, "51-75": 15, "76-100": 20}'
    )

    def calculate_score(self, value):
        """Calculate score based on the criterion value"""
        if self.criteria_type == 'binary':
            return self.points if value else 0.0

        if self.criteria_type == 'percentage' and self.scoring_rule == 'proportional':
            return (value / 100.0) * self.points if value else 0.0

        if self.criteria_type == 'points':
            return value if value <= self.points else self.points

        return 0.0
