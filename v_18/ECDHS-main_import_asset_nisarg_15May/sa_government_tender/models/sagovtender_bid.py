# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class TenderBid(models.Model):
    """Tender Bid - Vendor Submissions"""
    _name = 'sagovtender.bid'
    _description = 'Tender Bid'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Bid Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('sagovtender.bid')
    )
    tender_id = fields.Many2one(
        'sagovtender.tender',
        string='Tender',
        required=True,
        ondelete='cascade',
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    partner_id = fields.Many2one(
        'res.partner',
        string='Bidder',
        required=True,
        domain=[('is_company', '=', True)],
        tracking=True,
        store=True,
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )
    submission_date = fields.Datetime(
        string='Submission Date',
        default=fields.Datetime.now,
        required=True,
        tracking=True
    )
    bid_amount = fields.Monetary(
        string='Bid Amount',
        required=True,
        currency_field='currency_id',
        tracking=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    validity_period = fields.Integer(
        string='Validity Period (Days)',
        default=90,
        help='Number of days this bid remains valid'
    )

    # SBD Documents
    sbd1_complete = fields.Boolean(string='SBD 1 - Invitation to Bid')
    sbd2_complete = fields.Boolean(string='SBD 2 - Tax Clearance')
    sbd3_complete = fields.Boolean(string='SBD 3 - Pricing Schedule')
    sbd4_complete = fields.Boolean(string='SBD 4 - Declaration of Interest')
    sbd6_complete = fields.Boolean(string='SBD 6.1 - Preference Points')
    sbd7_complete = fields.Boolean(string='SBD 7 - Contract Form')
    sbd8_complete = fields.Boolean(string='SBD 8 - Past SCM Practices')
    sbd9_complete = fields.Boolean(string='SBD 9 - Independent Bid Determination')

    # Compliance
    sagovcompliance_check_id = fields.Many2one(
        'sagovtender.compliance.check',
        string='Compliance Check',
        readonly=False
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    is_compliant = fields.Boolean(
        string='Compliant',
        compute='_compute_is_compliant',
        store=True,
        help='Whether bid passed compliance checks'
    )

    # Evaluation
    evaluation_ids = fields.One2many(
        'sagovtender.bid.evaluation',
        'bid_id',
        string='Evaluations'
    )
    functionality_score = fields.Float(
        string='Functionality Score',
        compute='_compute_functionality_score',
        store=True
    )
    price_score = fields.Float(
        string='Price Score',
        compute='_compute_price_score',
        store=True
    )
    bbbee_score = fields.Float(
        string='B-BBEE Score',
        compute='_compute_bbbee_score',
        store=True
    )
    total_score = fields.Float(
        string='Total Score',
        compute='_compute_total_score',
        store=True
    )

    # Documents
    document_ids = fields.Many2many(
        'ir.attachment',
        string='Bid Documents',
        help='All documents submitted with bid'
    )

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('opened', 'Opened'),
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('evaluated', 'Evaluated'),
        ('awarded', 'Awarded'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)

    notes = fields.Text(string='Notes')
    rejection_reason = fields.Text(string='Rejection Reason')

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    @api.depends('sagovcompliance_check_id', 'sagovcompliance_check_id.state')
    def _compute_is_compliant(self):
        """Check if bid is compliant"""
        for record in self:
            if record.sagovcompliance_check_id:
                record.is_compliant = record.sagovcompliance_check_id.state == 'compliant'
            else:
                record.is_compliant = False

    @api.constrains('bid_amount')
    def _check_bid_amount(self):
        """Validate bid amount to prevent invalid values"""
        for record in self:
            if record.bid_amount <= 0:
                raise ValidationError(_("Bid amount must be greater than zero"))
            if record.bid_amount > 999999999999.99:
                raise ValidationError(_("Bid amount exceeds maximum allowed amount"))

    @api.constrains('validity_period')
    def _check_validity_period(self):
        """Validate validity period is within reasonable bounds"""
        for record in self:
            if record.validity_period < 1:
                raise ValidationError(_("Validity period must be at least 1 day"))
            if record.validity_period > 365:
                raise ValidationError(_("Validity period cannot exceed 365 days"))

    @api.constrains('partner_id', 'tender_id')
    def _check_unique_bid(self):
        """Ensure one bid per supplier per tender"""
        for record in self:
            existing = self.search([
                ('partner_id', '=', record.partner_id.id),
                ('tender_id', '=', record.tender_id.id),
                ('id', '!=', record.id),
                ('state', '!=', 'cancelled')
            ])
            if existing:
                raise ValidationError(_(
                    "A bid from %s already exists for this tender. "
                    "Only one bid per supplier is allowed."
                ) % record.partner_id.name)

    @api.depends('evaluation_ids.functionality_score')
    def _compute_functionality_score(self):
        """Calculate average functionality score"""
        for record in self:
            evals = record.evaluation_ids.filtered(lambda e: e.state == 'completed')
            if evals:
                record.functionality_score = sum(evals.mapped('functionality_score')) / len(evals)
            else:
                record.functionality_score = 0.0

    @api.depends('bid_amount', 'tender_id.bid_ids')
    def _compute_price_score(self):
        """Calculate price score based on preference system"""
        for record in self:
            if not record.tender_id or not record.bid_amount:
                record.price_score = 0.0
                continue

            # Get lowest bid amount
            lowest_bid = min(record.tender_id.bid_ids.filtered(
                lambda b: b.is_compliant and b.bid_amount > 0
            ).mapped('bid_amount'), default=0)

            if lowest_bid == 0:
                record.price_score = 0.0
                continue

            # Calculate price score based on preference system
            if record.tender_id.preference_system == '80_20':
                max_points = 80
            elif record.tender_id.preference_system == '90_10':
                max_points = 90
            else:
                max_points = 100

            # Formula: Ps = 80/90 × (Pt − P min) / P min
            record.price_score = max_points * (1 - (record.bid_amount - lowest_bid) / lowest_bid)

    @api.depends('partner_id.bbbee_level')
    def _compute_bbbee_score(self):
        """Calculate B-BBEE preference points"""
        for record in self:
            if not record.tender_id:
                record.bbbee_score = 0.0
                continue

            bbbee_level = record.partner_id.bbbee_level or 0

            # B-BBEE points table
            if record.tender_id.preference_system == '80_20':
                # 20 points for B-BBEE
                points_map = {1: 20, 2: 18, 3: 14, 4: 12, 5: 8, 6: 6, 7: 4, 8: 2}
            elif record.tender_id.preference_system == '90_10':
                # 10 points for B-BBEE
                points_map = {1: 10, 2: 9, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1}
            else:
                points_map = {}

            record.bbbee_score = points_map.get(bbbee_level, 0)

    @api.depends('price_score', 'bbbee_score', 'functionality_score')
    def _compute_total_score(self):
        """Calculate total evaluation score"""
        for record in self:
            if record.tender_id.has_functionality:
                # Check if meets functionality threshold
                threshold = record.tender_id.functionality_threshold
                if record.functionality_score < threshold:
                    record.total_score = 0.0  # Disqualified
                else:
                    record.total_score = record.price_score + record.bbbee_score
            else:
                record.total_score = record.price_score + record.bbbee_score

    @api.constrains('submission_date', 'tender_id')
    def _check_submission_date(self):
        """Validate submission date"""
        for record in self:
            if record.tender_id.closing_date:
                if record.submission_date > record.tender_id.closing_date:
                    raise ValidationError('Bid submitted after closing date.')

    def action_submit(self):
        """Submit bid"""
        for record in self:
            # Validate required documents
            if not all([
                record.sbd1_complete, record.sbd2_complete,
                record.sbd3_complete, record.sbd4_complete
            ]):
                raise UserError('Please complete all mandatory SBD forms.')
            if record.bid_amount < 1.00:
                raise UserError('Bid amount must be greater than zero.')

            record.write({
                'state': 'submitted',
                'submission_date': fields.Datetime.now()
            })
            record.message_post(body='Bid submitted.')

    def action_open(self):
        """Open bid (during bid opening)"""
        self.write({'state': 'opened'})

    def action_mark_compliant(self):
        """Mark as compliant"""
        self.write({'state': 'compliant'})

    def action_mark_non_compliant(self):
        """Mark as non-compliant"""
        self.write({'state': 'non_compliant'})

    def action_mark_evaluated(self):
        """Mark as evaluated"""
        self.write({'state': 'evaluated'})

    def action_award(self):
        """Award bid"""
        self.write({'state': 'awarded'})

    def action_reject(self):
        """Reject bid"""
        self.write({'state': 'rejected'})

    def action_cancel(self):
        """Cancel bid"""
        self.write({'state': 'cancelled'})
