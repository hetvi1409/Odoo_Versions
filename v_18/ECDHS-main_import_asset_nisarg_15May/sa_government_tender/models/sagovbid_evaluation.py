# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class BidEvaluation(models.Model):
    """Bid Evaluation - Step 9 of Tender Process (BEC)"""
    _name = 'sagovtender.bid.evaluation'
    _description = 'Bid Evaluation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('sagovtender.evaluation')
    )
    bid_id = fields.Many2one(
        'sagovtender.bid',
        string='Bid',
        required=True,
        ondelete='cascade',
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    tender_id = fields.Many2one(
        'sagovtender.tender',
        related='bid_id.tender_id',
        string='Tender',
        required=True,
        ondelete='cascade',
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    partner_id = fields.Many2one(
        'res.partner',
        related='bid_id.partner_id',
        string='Bidder',
        store=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    # Functionality Evaluation
    functionality_line_ids = fields.One2many(
        'sagovtender.eval.funct.line',
        'evaluation_id',
        string='Functionality Criteria'
    )
    functionality_score = fields.Float(
        string='Functionality Score (%)',
        compute='_compute_functionality_score',
        store=True
    )
    functionality_passed = fields.Boolean(
        string='Passed Functionality',
        compute='_compute_functionality_passed',
        store=True
    )
    functionality_threshold = fields.Float(
        related='tender_id.functionality_threshold',
        string='Threshold'
    )

    # Price Evaluation
    bid_amount = fields.Monetary(
        related='bid_id.bid_amount',
        string='Bid Amount',
        store=True
    )
    price_score = fields.Float(
        string='Price Score',
        compute='_compute_price_score',
        store=True
    )

    # B-BBEE Evaluation
    # Related field - inherits Selection type from res.partner.bbbee_level
    bbbee_level = fields.Selection(
        related='partner_id.bbbee_level',
        string='B-BBEE Level',
        store=True
    )
    bbbee_score = fields.Float(
        string='B-BBEE Score',
        compute='_compute_bbbee_score',
        store=True
    )

    # Total Score
    total_score = fields.Float(
        string='Total Score',
        compute='_compute_total_score',
        store=True
    )
    ranking = fields.Integer(
        string='Ranking',
        compute='_compute_ranking',
        store=True
    )

    # Recommendation
    recommended = fields.Boolean(
        string='Recommended for Award',
        tracking=True
    )
    recommendation_notes = fields.Text(string='Recommendation Notes')

    # Evaluation Team
    evaluator_ids = fields.Many2many(
        'res.users',
        string='Evaluators',
        help='BEC members who evaluated this bid'
    )
    evaluation_date = fields.Date(
        string='Evaluation Date',
        tracking=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('approved', 'Approved'),
    ], string='Status', default='draft', required=True, tracking=True)

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    notes = fields.Text(string='Evaluation Notes')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    @api.depends('functionality_line_ids.weighted_score')
    def _compute_functionality_score(self):
        """Calculate total functionality score"""
        for record in self:
            if record.functionality_line_ids:
                record.functionality_score = sum(
                    record.functionality_line_ids.mapped('weighted_score')
                )
            else:
                record.functionality_score = 0.0

    @api.depends('functionality_score', 'functionality_threshold')
    def _compute_functionality_passed(self):
        """Check if functionality threshold is met"""
        for record in self:
            if record.tender_id.has_functionality:
                record.functionality_passed = record.functionality_score >= record.functionality_threshold
            else:
                record.functionality_passed = True

    @api.depends('bid_amount', 'tender_id.bid_ids')
    def _compute_price_score(self):
        """Calculate price score"""
        for record in self:
            if not record.tender_id or not record.bid_amount:
                record.price_score = 0.0
                continue

            # Get lowest compliant bid
            compliant_bids = record.tender_id.bid_ids.filtered(
                lambda b: b.is_compliant and b.bid_amount > 0
            )

            if not compliant_bids:
                record.price_score = 0.0
                continue

            lowest_bid = min(compliant_bids.mapped('bid_amount'))

            # Determine max price points
            if record.tender_id.preference_system == '80_20':
                max_points = 80
            elif record.tender_id.preference_system == '90_10':
                max_points = 90
            else:
                max_points = 100

            # Price score formula: Ps = max_points × (1 - (P - Pmin) / Pmin)
            if lowest_bid > 0:
                record.price_score = max_points * (1 - (record.bid_amount - lowest_bid) / lowest_bid)
            else:
                record.price_score = 0.0

    @api.depends('bbbee_level', 'tender_id.preference_system')
    def _compute_bbbee_score(self):
        """Calculate B-BBEE preference points"""
        for record in self:
            if not record.tender_id:
                record.bbbee_score = 0.0
                continue

            level = record.bbbee_level or 0

            # B-BBEE points allocation
            if record.tender_id.preference_system == '80_20':
                points_map = {1: 20, 2: 18, 3: 14, 4: 12, 5: 8, 6: 6, 7: 4, 8: 2}
            elif record.tender_id.preference_system == '90_10':
                points_map = {1: 10, 2: 9, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1}
            else:
                points_map = {}

            record.bbbee_score = points_map.get(level, 0)

    @api.depends('functionality_passed', 'price_score', 'bbbee_score')
    def _compute_total_score(self):
        """Calculate total score"""
        for record in self:
            if record.tender_id.has_functionality and not record.functionality_passed:
                record.total_score = 0.0  # Disqualified
            else:
                record.total_score = record.price_score + record.bbbee_score

    @api.depends('total_score', 'tender_id.evaluation_ids')
    def _compute_ranking(self):
        """Calculate ranking among evaluated bids"""
        for record in self:
            if record.tender_id:
                # Get all evaluations with scores
                evaluations = record.tender_id.evaluation_ids.filtered(
                    lambda e: e.functionality_passed or not e.tender_id.has_functionality
                ).sorted(key=lambda e: e.total_score, reverse=True)

                record.ranking = list(evaluations.ids).index(record.id) + 1 if record.id in evaluations.ids else 0
            else:
                record.ranking = 0

    def action_start_evaluation(self):
        """Start evaluation"""
        self.ensure_one()
        if not self.bid_id.is_compliant:
            raise UserError('Only compliant bids can be evaluated.')

        # Load functionality criteria from tender
        self._load_functionality_criteria()

        self.write({
            'state': 'in_progress',
            'evaluation_date': fields.Date.today()
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bid Evaluation'),
            'res_model': 'sagovtender.bid.evaluation',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'edit',
            },
        }

    def action_complete_evaluation(self):
        """Complete evaluation"""
        self.ensure_one()
        if self.tender_id.has_functionality:
            if not self.functionality_line_ids:
                raise UserError('Please complete functionality evaluation.')
            if not all(line.score > 0 for line in self.functionality_line_ids):
                raise UserError('Please score all functionality criteria.')

        self.write({'state': 'completed'})
        self.message_post(
            body=f'Evaluation completed.\nTotal Score: {self.total_score}\nRanking: {self.ranking}'
        )
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bid Evaluation'),
            'res_model': 'sagovtender.bid.evaluation',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'readonly',
            },
        }

    def action_approve(self):
        """Approve evaluation"""
        self.write({'state': 'approved'})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bid Evaluation'),
            'res_model': 'sagovtender.bid.evaluation',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'readonly',
            },
        }

    def _load_functionality_criteria(self):
        """Load functionality evaluation criteria from tender configuration"""
        self.ensure_one()
        # Clear existing lines
        self.functionality_line_ids.unlink()

        # NEW: Load from procurement method configuration
        if self.tender_id.procurement_method_config_id and self.tender_id.evaluation_criteria_ids:
            config_criteria = self.tender_id.evaluation_criteria_ids.filtered(
                lambda c: c.criteria_type == 'functionality'
            )

            if config_criteria:
                # Load criteria from configuration
                for criteria in config_criteria.sorted('sequence'):
                    self.env['sagovtender.eval.funct.line'].create({
                        'evaluation_id': self.id,
                        'criteria': criteria.name,
                        'weight': criteria.weight,
                        'max_score': 100,
                        'description': criteria.description,
                        'sequence': criteria.sequence,
                    })
                self.message_post(
                    body=f'Loaded {len(config_criteria)} evaluation criteria from '
                         f'{self.tender_id.procurement_method_config_id.name}'
                )
                return

        # Fallback to default criteria if none configured
        criteria_data = [
            {'name': 'Technical Capability', 'weight': 30, 'max_score': 100, 'sequence': 10},
            {'name': 'Experience and Track Record', 'weight': 25, 'max_score': 100, 'sequence': 20},
            {'name': 'Proposed Methodology', 'weight': 25, 'max_score': 100, 'sequence': 30},
            {'name': 'Key Personnel Qualifications', 'weight': 20, 'max_score': 100, 'sequence': 40},
        ]

        for criteria in criteria_data:
            self.env['sagovtender.eval.funct.line'].create({
                'evaluation_id': self.id,
                'criteria': criteria['name'],
                'weight': criteria['weight'],
                'max_score': criteria['max_score'],
                'sequence': criteria.get('sequence', 10),
            })


class EvaluationFunctionalityLine(models.Model):
    """Functionality Evaluation Lines"""
    _name = 'sagovtender.eval.funct.line'
    _description = 'Functionality Evaluation Line'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    evaluation_id = fields.Many2one(
        'sagovtender.bid.evaluation',
        string='Evaluation',
        required=True,
        ondelete='cascade'
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    criteria = fields.Char(string='Evaluation Criteria', required=True)
    description = fields.Text(string='Description')
    weight = fields.Float(
        string='Weight (%)',
        required=True,
        help='Weight of this criterion (total should be 100%)'
    )
    max_score = fields.Float(
        string='Maximum Score',
        default=100.0,
        required=True
    )
    score = fields.Float(
        string='Score',
        help='Score awarded (0 to max_score)'
    )
    weighted_score = fields.Float(
        string='Weighted Score',
        compute='_compute_weighted_score',
        store=True
    )
    comments = fields.Text(string='Comments')

    @api.depends('score', 'weight', 'max_score')
    def _compute_weighted_score(self):
        """Calculate weighted score"""
        for record in self:
            if record.max_score > 0:
                normalized = (record.score / record.max_score) * 100
                record.weighted_score = (normalized * record.weight) / 100
            else:
                record.weighted_score = 0.0

    @api.constrains('score', 'max_score')
    def _check_score(self):
        """Validate score"""
        for record in self:
            if record.score < 0:
                raise ValidationError('Score cannot be negative.')
            if record.score > record.max_score:
                raise ValidationError(f'Score cannot exceed maximum score of {record.max_score}.')

    @api.constrains('weight')
    def _check_weight(self):
        """Validate weight"""
        for record in self:
            if record.weight < 0 or record.weight > 100:
                raise ValidationError('Weight must be between 0 and 100.')
