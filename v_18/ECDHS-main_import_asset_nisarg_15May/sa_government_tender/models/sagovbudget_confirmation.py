
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

"""
SA Government Budget Management - PFMA/MFMA Compliance

REAL-WORLD SCENARIO & GL ACCOUNT FLOW:
======================================

1. REQUISITION STAGE (Step 1):
   - Department creates requisition with commodity lines
   - Each commodity assigned to GL Account (e.g., 60101 - Office Equipment)
   - Links to APP (Annual Procurement Plan) budget line
   - GL Account determines which budget vote the expense comes from

2. BUDGET CONFIRMATION STAGE (Step 2) - THIS MODULE:
   - Finance Officer verifies funds available in GL Account
   - System checks:
     a) APP has remaining budget
     b) GL Account has unspent allocation
     c) Current financial year (Apr-Mar for National, Jul-Jun for Provincial)
   - On confirmation:
     a) Creates ENCUMBRANCE entry (commits the funds)
     b) Reduces available budget in GL Account
     c) Prevents other departments from using same funds
     d) Creates audit trail for AG (Auditor-General)

3. SPECIFICATION STAGE (Step 3):
   - GL Accounts auto-populate from requisition commodities
   - Technical specs developed per commodity
   - Each spec line tracks back to GL Account for reporting

4. TENDER AWARD STAGE (Step 11):
   - System creates COMMITMENT entry
   - Converts encumbrance to firm commitment
   - Updates procurement register
   - Prepares for payment processing

5. INVOICE PAYMENT (Post-Tender):
   - Actual journal entry posted to GL Account
   - Reduces commitment, creates expense
   - Updates SCOA (Standard Chart of Accounts) balances
   - Feeds into National Treasury BAS system

PFMA/MFMA REQUIREMENTS:
=======================
- Section 38/62: No expenditure without approved budget
- Section 45/70: Prevent unauthorized, irregular, fruitless expenditure
- National Treasury Instruction 8: Budget control and reporting
- SCOA Compliance: GL accounts must align with prescribed chart
- Monthly reporting: All commitments and expenditure tracked

MULTI-YEAR BUDGET (MTEF):
=========================
- Procurement can span financial years
- GL Account tracks across FY boundaries
- Commitments roll forward with budget adjustments
- Provincial vs National: Different fiscal calendars

THRESHOLD MANAGEMENT:
====================
- R10,000 - R30,000: Obtain 3 written quotes
- R30,000 - R500,000: Formal quotation process
- Above R500,000: Competitive bidding (tenders)
- Above R10 million: May require Treasury approval
- GL Account helps enforce threshold rules

AUDIT TRAIL:
===========
- Every budget action logged with GL Account reference
- Links requisition → budget → specification → award → payment
- AG can trace any expense back to original approval
- Supports irregular expenditure investigations
"""


class BudgetConfirmation(models.Model):
    """Budget Confirmation - Step 2 of Tender Process"""
    _name = 'sagovtender.budget.confirm'
    _description = 'Budget Confirmation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('sagovtender.budget.confirm')
    )
    requisition_id = fields.Many2one(
        'sagovtender.purchase.requisition',
        string='Purchase Requisition',
        required=True,
        ondelete='cascade',
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='requisition_id.department_id',
        store=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    app_id = fields.Many2one(
        'sagovtender.annual.procurement.plan',
        string='APP Budget Line',
        related='requisition_id.app_id',
        store=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    procurement_method_config_id = fields.Many2one(
        'sagovprocurement.method',
        string='Procurement Method Configuration',
        related='requisition_id.procurement_method_config_id',
        store=True,
        readonly=True
    )
    preference_point_system_config_id = fields.Many2one(
        'sagovpreference.point.system',
        string='Preference Point System Configuration',
        related='requisition_id.preference_point_system_config_id',
        store=True,
        readonly=True
    )
    requested_amount = fields.Monetary(
        string='Requested Amount',
        compute='_compute_requested_amount',
        store=True,
        currency_field='currency_id',
        tracking=True
    )
    confirmed_amount = fields.Monetary(
        string='Confirmed Amount',
        currency_field='currency_id',
        tracking=True
    )
    available_budget = fields.Monetary(
        string='Available Budget',
        compute='_compute_available_budget',
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    budget_verified = fields.Boolean(
        string='Budget Verified',
        default=False,
        tracking=True
    )
    memo_required = fields.Boolean(
        string='Memo Required',
        default=False
    )
    memo_attachment_id = fields.Many2one(
        'memo.memo',
        string='Budget Memo',
        help='Attached budget memo document',
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )
    finance_user_id = fields.Many2one(
        'res.users',
        string='Finance Officer',
        tracking=True,
        help='Finance officer responsible for budget confirmation'
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    confirmation_date = fields.Date(
        string='Confirmation Date',
        tracking=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('confirmed', 'Budget Confirmed'),
        ('insufficient', 'Insufficient Budget'),
        ('rejected', 'Rejected'),
    ], string='Status', default='pending', required=True, tracking=True)
    remarks = fields.Text(
        string='Remarks',
        help='Additional comments or notes from finance'
    )

    line_ids = fields.One2many(
        'sagovtender.budget.confirm.line',
        'budget_confirm_id',
        string='Commodity Budget Lines',
        help='Commodity lines copied from the requisition for budget confirmation'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    def write(self, vals):
        locked_records = self.filtered(lambda record: record.state not in ('draft', 'pending'))
        if locked_records:
            raise UserError(
                _('Budget confirmations can only be edited in Draft or Pending status.')
            )
        return super().write(vals)

    @api.depends('app_id', 'app_id.remaining_budget')
    def _compute_available_budget(self):
        """Get available budget from APP"""
        for record in self:
            if record.app_id:
                record.available_budget = record.app_id.remaining_budget
            else:
                record.available_budget = 0.0

    @api.depends('line_ids.subtotal')
    def _compute_requested_amount(self):
        """Calculate total requested amount from budget lines"""
        for record in self:
            record.requested_amount = sum(record.line_ids.mapped('subtotal'))

    def _get_requisition_account_totals(self):
        """Aggregate requisition line subtotals by GL account."""
        self.ensure_one()
        totals = {}
        if not self.requisition_id:
            return totals

        for line in self.requisition_id.commodity_line_ids:
            account = line.account_id
            if not account:
                continue
            totals[account] = totals.get(account, 0.0) + line.subtotal

        return totals

    def _create_budget_encumbrance(self):
        """Create budget encumbrance entries per requisition GL account."""
        self.ensure_one()
        account_totals = self._get_requisition_account_totals()
        if not account_totals:
            self.message_post(
                body=_('Budget encumbrance not created because requisition lines have no GL accounts.')
            )
            return

        app = self.requisition_id.app_id if self.requisition_id else False
        analytic_account = getattr(app, 'analytic_account_id', False) if app else False
        if not analytic_account:
            self.message_post(
                body=_('Budget encumbrance not created because the APP record has no analytic account.')
            )
            return

        for account, total in account_totals.items():
            self.env['account.analytic.line'].create({
                'name': _('Budget Encumbrance: %s') % self.requisition_id.name,
                'account_id': analytic_account.id,
                'general_account_id': account.id,
                'amount': -total,
                'unit_amount': 1,
                'ref': self.name,
                'date': fields.Date.today(),
            })

        currency = self.currency_id or self.env.company.currency_id
        symbol = currency.symbol or ''
        summary_lines = []
        for account, amount in sorted(account_totals.items(), key=lambda item: item[0].name or ''):
            summary_lines.append(
                '%s - %s: %s%0.2f' % (account.code, account.name, symbol, amount)
            )
        summary = '\n'.join(summary_lines)
        self.message_post(
            body=_('Budget encumbrance created per GL account.\n%s') % summary
        )

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        """When requisition changes, refresh configuration fields"""
        if self.requisition_id:
            # Force refresh of related configuration fields
            self.procurement_method_config_id = self.requisition_id.procurement_method_config_id
            self.preference_point_system_config_id = self.requisition_id.preference_point_system_config_id
            # Also update the app link
            self.app_id = self.requisition_id.app_id
            self._sync_lines_from_requisition()

    @api.onchange('procurement_method_config_id', 'preference_point_system_config_id')
    def _onchange_procurement_configuration(self):
        """Trigger when configuration fields change - framework recognizes field dependencies"""
        # This onchange is triggered by the form when these fields change
        # It allows dependent fields to be properly recomputed on the form view
        pass

    @api.onchange('budget_verified', 'requested_amount')
    def _onchange_budget_verified(self):
        """Auto-set confirmed amount when verified"""
        if self.budget_verified:
            self.confirmed_amount = self.requested_amount

    def action_refresh_lines(self):
        """Refresh commodity budget lines from the requisition."""
        self.ensure_one()
        self._sync_lines_from_requisition()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.budget.confirm',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }

    @api.constrains('confirmed_amount', 'requested_amount')
    def _check_amounts(self):
        """Validate amounts"""
        for record in self:
            if record.confirmed_amount < 0:
                raise ValidationError('Confirmed amount cannot be negative.')
            if record.state == 'confirmed' and record.confirmed_amount > record.requested_amount:
                raise ValidationError(
                    'Confirmed amount cannot exceed requested amount.'
                )

    def action_confirm_budget(self):
        """Confirm budget availability (PFMA/MFMA Compliance)

        Per SA Government regulations:
        1. Verify budget availability against GL account
        2. Create budget encumbrance (commitment)
        3. Link to APP for multi-year budget tracking
        4. Ensure proper authorization and documentation
        """
        for record in self:
            if not record.budget_verified:
                raise UserError(_('Please verify budget before confirming.'))
            if record.memo_required and not record.memo_attachment_id:
                raise UserError(_('Budget memo is required per National Treasury regulations.'))
            if record.app_id and record.confirmed_amount > record.available_budget:
                raise UserError(
                    _('Insufficient budget in APP. Available: %s, Requested: %s\n\n'
                      'Per PFMA/MFMA Section 38/62, expenditure cannot exceed approved budget.') % (
                        record.available_budget,
                        record.confirmed_amount
                    )
                )

            record._sync_lines_from_requisition()

            if not record.line_ids:
                raise UserError(_('No commodity budget lines found for this confirmation.'))

            # Validate each commodity line budget
            for line in record.line_ids:
                if not line.budget_id:
                    raise UserError(
                        _('Each commodity line must be linked to a budget before confirmation.')
                    )
                if not line.product_id:
                    raise UserError(_('Each commodity line must have a product before confirmation.'))

                budget_items = line.budget_id.item_ids.filtered(
                    lambda item: item.product_id == line.product_id
                )
                if not budget_items:
                    raise UserError(
                        _('No budget items found for product %s in budget %s.') % (
                            line.product_id.display_name,
                            line.budget_id.display_name
                        )
                    )

                available_amount = sum(budget_items.mapped('amount'))
                if available_amount < line.amount:
                    raise UserError(
                        _('Insufficient budget for %s. Available: %s, Required: %s') % (
                            line.product_id.display_name,
                            available_amount,
                            line.amount
                        )
                    )

            record.write({
                'state': 'confirmed',
                'confirmation_date': fields.Date.today(),
                'finance_user_id': self.env.user.id,
            })

            # Deduct budgets once confirmed
            for line in record.line_ids:
                if not line.deducted:
                    budget_items = line.budget_id.item_ids.filtered(
                        lambda item: item.product_id == line.product_id
                    )
                    remaining_to_deduct = line.amount
                    for item in budget_items.sorted(key=lambda i: i.date or fields.Date.today()):
                        if remaining_to_deduct <= 0:
                            break
                        deduction = min(item.amount, remaining_to_deduct)
                        item.write({'amount': item.amount - deduction})
                        remaining_to_deduct -= deduction
                    line.deducted = True

            # Create budget encumbrance entries per GL account
            record._create_budget_encumbrance()

            # Update requisition
            record.requisition_id.write({
                'state': 'budget_confirmed',
                'budget_confirmed_amount': record.confirmed_amount,
            })

            record.message_post(
                body=_('Budget confirmed per PFMA/MFMA requirements.\n'
                      'Amount: %s') % record.confirmed_amount
            )

        # Return action to reload form and keep dialog open
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.budget.confirm',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }

    def _sync_lines_from_requisition(self):
        """Sync commodity lines from the requisition into budget confirmation."""
        self.ensure_one()
        if not self.requisition_id:
            return

        existing = {line.requisition_line_id.id: line for line in self.line_ids if line.requisition_line_id}
        requisition_lines = self.requisition_id.commodity_line_ids

        for req_line in requisition_lines:
            if req_line.id in existing:
                # Update existing line with latest values from requisition
                existing_line = existing[req_line.id]
                existing_line.write({
                    'product_id': req_line.product_id.id,
                    'description': req_line.name,
                    'quantity': req_line.quantity,
                    'uom_id': req_line.uom_id.id,
                    'unit_price': req_line.unit_price,
                    'budget_id': req_line.budget_id.id if req_line.budget_id else False,
                    'account_id': req_line.account_id.id if req_line.account_id else False,
                })
            else:
                # Create new line from requisition line
                self.env['sagovtender.budget.confirm.line'].create({
                    'budget_confirm_id': self.id,
                    'requisition_line_id': req_line.id,
                    'product_id': req_line.product_id.id,
                    'description': req_line.name,
                    'quantity': req_line.quantity,
                    'uom_id': req_line.uom_id.id,
                    'unit_price': req_line.unit_price,
                    'budget_id': req_line.budget_id.id if req_line.budget_id else False,
                    'account_id': req_line.account_id.id if req_line.account_id else False,
                })

        missing = self.line_ids.filtered(lambda l: l.requisition_line_id and l.requisition_line_id not in requisition_lines)
        if missing:
            missing.unlink()

    def action_mark_insufficient(self):
        """Mark budget as insufficient"""
        self.write({'state': 'insufficient'})
        self.requisition_id.write({'state': 'rejected'})
        self.message_post(body='Budget marked as insufficient.')

        # Return action to reload form and keep dialog open
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.budget.confirm',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }

    def action_reject(self):
        """Reject budget request"""
        self.write({'state': 'rejected'})
        self.requisition_id.write({'state': 'rejected'})
        self.message_post(body='Budget request rejected.')

        # Return action to reload form and keep dialog open
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.budget.confirm',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }


class SagovBudgetConfirmationLine(models.Model):
    _name = 'sagovtender.budget.confirm.line'
    _description = 'Budget Confirmation Line'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    budget_confirm_id = fields.Many2one(
        'sagovtender.budget.confirm',
        string='Budget Confirmation',
        required=True,
        ondelete='cascade'
    )
    requisition_line_id = fields.Many2one(
        'sagovtender.purchase.requisition.line',
        string='Requisition Line',
        ondelete='restrict'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product/Commodity',
        required=True,
        help='Select the commodity or product to be procured',
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )
    description = fields.Text(
        string='Description',
        required=True,
        help='Detailed description of the commodity'
    )
    quantity = fields.Float(
        string='Quantity',
        default=1.0,
        required=True,
        digits='Product Unit of Measure'
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True,
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )
    unit_price = fields.Monetary(
        string='Estimated Unit Price',
        currency_field='currency_id'
    )
    subtotal = fields.Monetary(
        string='Subtotal',
        currency_field='currency_id',
        compute='_compute_subtotal',
        store=True
    )
    amount = fields.Monetary(
        string='Amount',
        compute='_compute_amount',
        store=True,
        currency_field='currency_id'
    )

    # GL Account for Commodity
    account_id = fields.Many2one(
        'account.account',
        string='GL Account',
        domain="[('deprecated', '=', False)]",
        help='General Ledger account for this commodity',
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )

    # Budget Link (per commodity line)
    budget_id = fields.Many2one(
        'account.report.budget',
        string='Budget',
        domain="[('item_ids.product_id', '=', product_id)]",
        help='Odoo budget linked to this commodity line',
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )
    remaining_budget = fields.Monetary(
        string='Remaining Budget',
        compute='_compute_remaining_budget',
        currency_field='currency_id',
        help='Remaining budget available in the linked budget'
    )

    deducted = fields.Boolean(
        string='Deducted',
        default=False,
        help='Indicates whether the budget amount has been deducted'
    )
    currency_id = fields.Many2one(
        related='budget_confirm_id.currency_id',
        string='Currency',
        store=True,
        readonly=True
    )

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        """Calculate subtotal"""
        for line in self:
            line.subtotal = line.quantity * line.unit_price

    @api.depends('subtotal')
    def _compute_amount(self):
        for line in self:
            line.amount = line.subtotal

    @api.depends('budget_id', 'product_id', 'budget_id.item_ids.amount', 'budget_id.item_ids.product_id')
    def _compute_remaining_budget(self):
        """Calculate remaining budget from linked budget"""
        for line in self:
            if not line.budget_id or not line.product_id:
                line.remaining_budget = 0.0
                continue

            matching_items = line.budget_id.item_ids.filtered(
                lambda item: item.product_id == line.product_id
            )
            line.remaining_budget = sum(matching_items.mapped('amount'))

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Auto-fill fields from product"""
        if not self.product_id:
            self.budget_id = False
            self.account_id = False
            return

        self.description = self.product_id.name
        self.uom_id = self.product_id.uom_id
        self.unit_price = self.product_id.standard_price

        # Find budget items for this product
        budget_item_model = self.env['account.report.budget.item']
        matching_items = budget_item_model.search([
            ('product_id', '=', self.product_id.id)
        ])

        if not matching_items:
            self.budget_id = False
            self.account_id = False
            return {
                'warning': {
                    'title': 'No Budget Found',
                    'message': 'No budget items found for product: %s' % self.product_id.name
                }
            }

        # Auto-select first budget with available balance
        budgets = matching_items.mapped('budget_id')
        if budgets:
            # Filter budgets with available balance
            available_budgets = budgets.filtered(
                lambda b: b.item_ids.filtered(
                    lambda item: item.product_id == self.product_id and item.amount > 0
                )
            )
            if available_budgets:
                self.budget_id = available_budgets[0]
            else:
                self.budget_id = budgets[0]
                return {
                    'warning': {
                        'title': 'Insufficient Budget',
                        'message': 'Selected budget has insufficient funds for product: %s' % self.product_id.name
                    }
                }

        # Auto-fill account from budget or product
        if self.budget_id and self.budget_id.account_id:
            self.account_id = self.budget_id.account_id
        elif hasattr(self.product_id, 'property_account_expense_id'):
            self.account_id = self.product_id.property_account_expense_id

    @api.onchange('budget_id')
    def _onchange_budget_id(self):
        """Update account when budget changes"""
        if self.budget_id and self.budget_id.account_id:
            self.account_id = self.budget_id.account_id

