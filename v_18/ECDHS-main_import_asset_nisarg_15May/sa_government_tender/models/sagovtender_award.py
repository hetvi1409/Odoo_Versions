# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TenderAward(models.Model):
    """Tender Award - Step 11 of Tender Process"""
    _name = 'sagovtender.award'
    _description = 'Tender Award'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Award Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('sagovtender.award')
    )
    tender_id = fields.Many2one(
        'sagovtender.tender',
        string='Tender',
        required=True,
        ondelete='cascade',
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    awarded_bid_id = fields.Many2one(
        'sagovtender.bid',
        string='Awarded Bid',
        required=True,
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    awarded_partner_id = fields.Many2one(
        'res.partner',
        related='awarded_bid_id.partner_id',
        string='Awarded To',
        store=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    award_date = fields.Date(
        string='Award Date',
        default=fields.Date.today,
        required=True,
        tracking=True
    )
    award_value = fields.Monetary(
        string='Award Value',
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

    # Contract Details
    contract_start_date = fields.Date(
        string='Contract Start Date',
        tracking=True
    )
    contract_end_date = fields.Date(
        string='Contract End Date',
        tracking=True
    )
    contract_duration = fields.Integer(
        string='Contract Duration (Days)',
        compute='_compute_contract_duration'
    )
    contract_number = fields.Char(
        string='Contract Number',
        tracking=True
    )

    # Award Justification
    award_justification = fields.Html(
        string='Award Justification',
        help='Justification for awarding to this bidder'
    )
    bec_score = fields.Float(
        related='awarded_bid_id.total_score',
        string='Total Score',
        store=True
    )

    # Approval
    approved_by_id = fields.Many2one(
        'res.users',
        string='Approved By',
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    approval_date = fields.Date(
        string='Approval Date',
        tracking=True
    )

    # Documents
    award_letter_id = fields.Many2one(
        'ir.attachment',
        string='Award Letter',
        storage='binary',
        store=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    signed_contract_id = fields.Many2one(
        'ir.attachment',
        string='Signed Contract',
        storage='binary',
        store=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    # Purchase Order
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        readonly=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    po_created = fields.Boolean(
        string='PO Created',
        compute='_compute_po_created'
    )

    # Publication
    published = fields.Boolean(
        string='Award Published',
        default=False,
        tracking=True,
        help='Award published online as per transparency requirements'
    )
    publication_date = fields.Date(string='Publication Date')
    publication_url = fields.Char(string='Publication URL')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('awarded', 'Awarded'),
        ('published', 'Published'),
        ('contract_signed', 'Contract Signed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)

    notes = fields.Text(string='Notes')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    @api.depends('contract_start_date', 'contract_end_date')
    def _compute_contract_duration(self):
        """Calculate contract duration"""
        for record in self:
            if record.contract_start_date and record.contract_end_date:
                delta = record.contract_end_date - record.contract_start_date
                record.contract_duration = delta.days
            else:
                record.contract_duration = 0

    @api.depends('purchase_order_id')
    def _compute_po_created(self):
        """Check if PO is created"""
        for record in self:
            record.po_created = bool(record.purchase_order_id)

    def action_confirm_award(self):
        """Confirm tender award with full compliance validation"""
        for record in self:
            # NEW: Validate all compliance requirements before award
            record.tender_id.validate_committee_requirements()
            record.tender_id.validate_quotation_requirements()

            record.write({
                'state': 'awarded',
                'approved_by_id': self.env.user.id,
                'approval_date': fields.Date.today()
            })

            # Update tender
            record.tender_id.write({
                'state': 'awarded',
                'award_id': record.id,
                'awarded_partner_id': record.awarded_partner_id.id,
                'award_value': record.award_value
            })

            # Update bid
            record.awarded_bid_id.action_award()

            # Reject other bids
            other_bids = record.tender_id.bid_ids.filtered(
                lambda b: b.id != record.awarded_bid_id.id and b.state not in ['cancelled', 'rejected']
            )
            other_bids.action_reject()

            record.message_post(
                body='Tender award confirmed - All compliance requirements validated (PFMA, MFMA, PPPFA, National Treasury).'
            )

        return {
            'type': 'ir.actions.act_window',
            'name': _('Tender Award'),
            'res_model': 'sagovtender.award',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'edit',
            },
        }

    def action_publish_award(self):
        """Publish award online"""
        self.write({
            'published': True,
            'publication_date': fields.Date.today(),
            'state': 'published'
        })
        self.message_post(body='Award published online.')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tender Award'),
            'res_model': 'sagovtender.award',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'edit',
            },
        }

    def action_create_purchase_order(self):
        """Create purchase order from award"""
        self.ensure_one()
        if self.purchase_order_id:
            raise UserError('Purchase Order already created.')

        # Create PO
        spec = self.tender_id.specification_id
        notes = f'Purchase Order for Tender: {self.tender_id.title or self.tender_id.name}'
        if spec:
            detail_parts = []
            if spec.description:
                detail_parts.append(f'General Description:\n{spec.description}')
            if detail_parts:
                notes = f'{notes}\n\n' + '\n\n'.join(detail_parts)

        po_vals = {
            'partner_id': self.awarded_partner_id.id,
            'date_order': fields.Datetime.now(),
            'origin': self.tender_id.name,
            'notes': notes,
        }

        # Specification commodities are removed; create a single summary line for the award.
        po_vals['order_line'] = [(0, 0, {
            'name': self.tender_id.title or self.tender_id.name or _('Tender Award'),
            'product_qty': 1,
            'product_uom': False,
            'price_unit': self.award_value,
            'date_planned': fields.Datetime.now(),
        })]

        po = self.env['purchase.order'].create(po_vals)
        self.purchase_order_id = po.id

        self.message_post(body=f'Purchase Order {po.name} created.')

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': po.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_purchase_order(self):
        """View created purchase order"""
        self.ensure_one()
        if not self.purchase_order_id:
            raise UserError('No Purchase Order created yet.')

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': self.purchase_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_mark_contract_signed(self):
        """Mark contract as signed"""
        if not self.signed_contract_id:
            raise UserError('Please attach the signed contract document.')

        self.write({'state': 'contract_signed'})
        self.message_post(body='Contract marked as signed.')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tender Award'),
            'res_model': 'sagovtender.award',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'edit',
            },
        }

    def action_complete(self):
        """Complete award process"""
        self.write({'state': 'completed'})
        self.message_post(body='Award process completed.')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tender Award'),
            'res_model': 'sagovtender.award',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'readonly',
            },
        }

    def action_cancel(self):
        """Cancel award"""
        self.write({'state': 'cancelled'})
        self.message_post(body='Award cancelled.')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tender Award'),
            'res_model': 'sagovtender.award',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'readonly',
            },
        }

    def action_print_award_letter(self):
        """Print award letter"""
        return self.env.ref('sa_government_tender.action_report_award_letter').report_action(self)
