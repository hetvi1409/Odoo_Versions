# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TenderAwardWizard(models.TransientModel):
    """Wizard for awarding tender"""
    _name = 'sagovtender.award.wizard'
    _description = 'Tender Award Wizard'

    tender_id = fields.Many2one(
        'sagovtender.tender',
        string='Tender',
        required=True,
        default=lambda self: self.env.context.get('active_id'),
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )
    awarded_bid_id = fields.Many2one(
        'sagovtender.bid',
        string='Awarded Bid',
        required=True,
        domain="[('tender_id', '=', tender_id), ('is_compliant', '=', True), ('state', '=', 'evaluated')]",
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )
    awarded_partner_id = fields.Many2one(
        'res.partner',
        related='awarded_bid_id.partner_id',
        string='Awarded To',
        readonly=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    award_value = fields.Monetary(
        string='Award Value',
        required=True,
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    award_date = fields.Date(
        string='Award Date',
        default=fields.Date.today,
        required=True
    )
    contract_start_date = fields.Date(
        string='Contract Start Date'
    )
    contract_end_date = fields.Date(
        string='Contract End Date'
    )
    award_justification = fields.Html(
        string='Award Justification',
        required=True
    )
    create_purchase_order = fields.Boolean(
        string='Create Purchase Order',
        default=True
    )
    publish_award = fields.Boolean(
        string='Publish Award Online',
        default=True
    )

    @api.onchange('awarded_bid_id')
    def _onchange_awarded_bid(self):
        """Load bid details"""
        if self.awarded_bid_id:
            self.award_value = self.awarded_bid_id.bid_amount
            self._generate_justification()

    def _generate_justification(self):
        """Generate award justification"""
        if self.awarded_bid_id:
            self.award_justification = f"""
            <h4>Award Justification</h4>
            <p><strong>Bidder:</strong> {self.awarded_partner_id.name}</p>
            <p><strong>Total Score:</strong> {self.awarded_bid_id.total_score}</p>
            <p><strong>Price Score:</strong> {self.awarded_bid_id.price_score}</p>
            <p><strong>B-BBEE Score:</strong> {self.awarded_bid_id.bbbee_score}</p>
            <p><strong>Functionality Score:</strong> {self.awarded_bid_id.functionality_score}%</p>
            <p><strong>Bid Amount:</strong> {self.awarded_bid_id.bid_amount}</p>
            <p>This bidder achieved the highest total score in the evaluation process
            and is recommended for award by the BEC and approved by the BAC.</p>
            """

    def action_award(self):
        """Award tender"""
        self.ensure_one()

        # Create award record
        award = self.env['sagovtender.award'].create({
            'tender_id': self.tender_id.id,
            'awarded_bid_id': self.awarded_bid_id.id,
            'award_date': self.award_date,
            'award_value': self.award_value,
            'contract_start_date': self.contract_start_date,
            'contract_end_date': self.contract_end_date,
            'award_justification': self.award_justification,
        })

        # Confirm award
        award.action_confirm_award()

        # Publish if requested
        if self.publish_award:
            award.action_publish_award()

        # Create PO if requested
        if self.create_purchase_order:
            award.action_create_purchase_order()

        # Return action to view award
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tender Award',
            'res_model': 'sagovtender.award',
            'res_id': award.id,
            'view_mode': 'form',
            'target': 'current',
        }
