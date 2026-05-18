
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PurchaseRequisition(models.Model):
    """Purchase Requisition - Step 1 of Tender Process

    GL ACCOUNT USAGE IN REQUISITIONS:
    =================================
    - Each commodity line assigned to a GL Account
    - GL Account represents the budget vote/expense type
    - Examples: 60101 (Office Equipment), 60201 (IT Hardware), 60301 (Consultants)
    - Must align with National Treasury SCOA (Standard Chart of Accounts)
    - Enables proper budget tracking and financial reporting
    - Links to APP budget allocation for the financial year
    """
    _name = 'sagovtender.purchase.requisition'
    _description = 'Purchase Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, name'
    _rec_name = 'description'

    name = fields.Char(
        string='Requisition Number',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('sagovtender.requisition')
    )
    app_id = fields.Many2one(
        'sagovtender.annual.procurement.plan',
        string='Annual Procurement Plan',
        tracking=True,
        help='Link to approved Annual Procurement Plan budget item'
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    procurement_method_config_id = fields.Many2one(
        'sagovprocurement.method',
        string='Procurement Method Configuration',
        compute='_compute_procurement_configs',
        store=True,
        readonly=True
    )
    preference_point_system_config_id = fields.Many2one(
        'sagovpreference.point.system',
        string='Preference Point System Configuration',
        compute='_compute_procurement_configs',
        store=True,
        readonly=True
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Requesting Department',
        required=True,
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    user_id = fields.Many2one(
        'res.users',
        string='Requested By',
        default=lambda self: self.env.user,
        required=True,
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    date_request = fields.Date(
        string='Request Date',
        default=fields.Date.today,
        required=True,
        tracking=True
    )
    date_required = fields.Date(
        string='Date Required',
        required=True,
        tracking=True
    )
    description = fields.Text(
        string='Item Description',
        required=True,
        help='Detailed description of goods or services required'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    motivation = fields.Text(
        string='Motivation',
        help='Motivation if item not on APP or additional justification (for items not on APP)'
    )
    is_on_app = fields.Boolean(
        string='APP Required',
        compute='_compute_is_on_app',
        store=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('budget_review', 'Budget Review'),
        ('budget_confirmed', 'Budget Confirmed'),
        ('specification', 'Specification Development'),
        ('scm_processing', 'SCM Processing'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)

    # Budget Confirmation fields
    sagovbudget_confirmation_id = fields.Many2one(
        'sagovtender.budget.confirm',
        string='Budget Confirmation',
        readonly=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    budget_confirmed_amount = fields.Monetary(
        string='Confirmed Budget Amount',
        currency_field='currency_id',
        readonly=True
    )
    budget_memo_id = fields.Many2one(
        'memo.memo',
        string='Budget Memo',
        help='Attached budget memo if required',
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )

    # Specification fields
    specification_id = fields.Many2one(
        'sagovtender.specification',
        string='Specification',
        readonly=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    has_specification = fields.Boolean(
        string='Has Specification',
        compute='_compute_has_specification'
    )

    # Tender link
    tender_id = fields.Many2one(
        'sagovtender.tender',
        string='Tender',
        readonly=True,
        help='Link to created tender'
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    notes = fields.Text(string='Notes')

    # Commodity Lines
    commodity_line_ids = fields.One2many(
        'sagovtender.purchase.requisition.line',
        'requisition_id',
        string='Commodities',
        help='Commodities/Items being procured'
    )

    # Document Attachments
    document_ids = fields.Many2many(
        'ir.attachment',
        'purchase_requisition_attachment_rel',
        'requisition_id',
        'attachment_id',
        string='Attached Documents',
        help='Supporting documents for this requisition'
    )
    document_count = fields.Integer(
        string='Document Count',
        compute='_compute_document_count'
    )

    # Optional Memo Link
    link_to_memo = fields.Boolean(
        string='Memo Required',
        default=False,
        help='Enable to link this requisition to a memo from e_system'
    )
    memo_id = fields.Many2one(
        'memo.memo',
        string='Memo',
        help='Link to related memo from e_system',
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )

    # GL Account Summary
    gl_account_summary = fields.Text(
        string='GL Account Allocation',
        compute='_compute_gl_account_summary',
        help='Summary of amounts allocated to each GL Account (for National Treasury reporting)'
    )

    @api.depends('app_id')
    def _compute_is_on_app(self):
        """Check if requisition is linked to APP"""
        for record in self:
            record.is_on_app = bool(record.app_id)

    def name_get(self):
        result = []
        for record in self:
            display = record.display_name
            result.append((record.id, display))
        return result

    def _compute_display_name(self):
        for record in self:
            if record.description and record.name:
                record.display_name = f"{record.description} - {record.name}"
            else:
                record.display_name = record.description or record.name or ''

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            domain = ['|', ('description', operator, name), ('name', operator, name)]
            records = self.search(domain + args, limit=limit)
        else:
            records = self.search(args, limit=limit)
        return records.name_get()

    @api.depends('commodity_line_ids.subtotal', 'app_id')
    def _compute_procurement_configs(self):
        """Set procurement method and preference system based on commodity totals"""
        method_model = self.env['sagovprocurement.method']
        for record in self:
            total_value = sum(record.commodity_line_ids.mapped('subtotal'))
            if not total_value:
                if record.app_id:
                    record.procurement_method_config_id = record.app_id.procurement_method_config_id
                    record.preference_point_system_config_id = record.app_id.preference_point_system_config_id
                else:
                    record.procurement_method_config_id = False
                    record.preference_point_system_config_id = False
                continue

            method = method_model.get_applicable_method(total_value)
            record.procurement_method_config_id = method
            record.preference_point_system_config_id = (
                method.preference_point_system_ids[:1] if method else False
            )

    @api.depends('document_ids')
    def _compute_document_count(self):
        """Count attached documents"""
        for record in self:
            record.document_count = len(record.document_ids)

    @api.depends('commodity_line_ids.account_id', 'commodity_line_ids.subtotal')
    def _compute_gl_account_summary(self):
        """Calculate GL Account allocation summary for National Treasury reporting"""
        for record in self:
            if not record.commodity_line_ids:
                record.gl_account_summary = _('No commodity lines added yet.')
                continue

            # Group by GL Account
            account_totals = {}
            unallocated = 0.0

            for line in record.commodity_line_ids:
                if line.account_id:
                    key = f"{line.account_id.code} - {line.account_id.name}"
                    account_totals[key] = account_totals.get(key, 0.0) + line.subtotal
                else:
                    unallocated += line.subtotal

            # Format summary
            summary_lines = []
            summary_lines.append('═' * 60)
            summary_lines.append('GL ACCOUNT ALLOCATION (PFMA/MFMA Compliance)')
            summary_lines.append('═' * 60)

            if account_totals:
                for account, total in sorted(account_totals.items()):
                    summary_lines.append(f"{account:<45} {record.currency_id.symbol}{total:>12,.2f}")

            if unallocated > 0:
                summary_lines.append(f"{'⚠ UNALLOCATED (Assign GL Accounts)':<45} {record.currency_id.symbol}{unallocated:>12,.2f}")

            summary_lines.append('─' * 60)
            total = sum(account_totals.values()) + unallocated
            summary_lines.append(f"{'TOTAL REQUISITION VALUE':<45} {record.currency_id.symbol}{total:>12,.2f}")
            summary_lines.append('═' * 60)

            if unallocated > 0:
                summary_lines.append('')
                summary_lines.append('⚠ WARNING: All commodities must have GL Accounts assigned')
                summary_lines.append('  This is required for budget encumbrance and Treasury reporting.')

            record.gl_account_summary = '\\n'.join(summary_lines)

    @api.depends('specification_id')
    def _compute_has_specification(self):
        """Check if specification exists"""
        for record in self:
            record.has_specification = bool(record.specification_id)

    @api.onchange('app_id')
    def _onchange_app_id(self):
        """Auto-fill fields from APP and trigger dependent field refresh"""
        if self.app_id:
            self.department_id = self.app_id.department_id
            if not self.description:
                self.description = self.app_id.item_description

    @api.onchange('commodity_line_ids', 'commodity_line_ids.subtotal')
    def _onchange_commodity_line_totals(self):
        """Refresh procurement configurations on commodity changes"""
        self._compute_procurement_configs()

    @api.onchange('procurement_method_config_id', 'preference_point_system_config_id')
    def _onchange_procurement_configuration(self):
        """Trigger when configuration fields change - framework recognizes field dependencies"""
        # This onchange is triggered by the form when these fields change
        # It allows dependent fields to be properly recomputed on the form view
        pass

    @api.constrains('date_required', 'date_request')
    def _check_dates(self):
        """Validate dates"""
        for record in self:
            if record.date_required < record.date_request:
                raise ValidationError(
                    'Required date cannot be earlier than request date.'
                )

    @api.constrains('quantity')
    def _check_quantity(self):
        """Validate quantity"""
        for record in self:
            if record.quantity <= 0:
                raise ValidationError('Quantity must be greater than zero.')

    def action_submit(self):
        """Submit requisition for budget review"""
        for record in self:
            if not record.is_on_app and not record.motivation:
                raise UserError(
                    'Please provide motivation for items not on APP.'
                )
            record.write({'state': 'budget_review'})
            record.message_post(body='Requisition submitted for budget review.')
            # Create budget confirmation record
            record._create_sagovbudget_confirmation()

    def action_send_to_specification(self):
        """Send back to department for specification development"""
        self.write({'state': 'specification'})
        self.message_post(body='Sent back for specification development.')

    def action_send_to_scm(self):
        """Send to SCM for processing"""
        for record in self:
            if not record.has_specification:
                raise UserError('Specification must be completed before sending to SCM.')
            record.write({'state': 'scm_processing'})
            record.message_post(body='Sent to SCM for processing.')

    def action_approve(self):
        """Approve requisition"""
        self.write({'state': 'approved'})
        self.message_post(body='Requisition approved.')

    def action_reject(self):
        """Reject requisition"""
        self.write({'state': 'rejected'})
        self.message_post(body='Requisition rejected.')

    def action_cancel(self):
        """Cancel requisition"""
        self.write({'state': 'cancelled'})
        self.message_post(body='Requisition cancelled.')

    def _create_sagovbudget_confirmation(self):
        """Create budget confirmation record"""
        self.ensure_one()
        if not self.sagovbudget_confirmation_id:
            budget_conf = self.env['sagovtender.budget.confirm'].create({
                'requisition_id': self.id,
                'department_id': self.department_id.id,
            })
            budget_conf._sync_lines_from_requisition()
            self.sagovbudget_confirmation_id = budget_conf.id

    def action_create_specification(self):
        """Create specification"""
        self.ensure_one()
        if not self.specification_id:
            spec = self.env['sagovtender.specification'].create({
                'requisition_id': self.id,
                'name': f'Specification for {self.name}',
                'description': self.description,
            })
            self.specification_id = spec.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Specification',
            'res_model': 'sagovtender.specification.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_requisition_id': self.id},
        }

    def action_view_tender(self):
        """View related tender"""
        self.ensure_one()
        if not self.tender_id:
            raise UserError('No tender created for this requisition.')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.tender',
            'res_id': self.tender_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_open_sagovbudget_confirmation(self):
        self.ensure_one()
        if not self.sagovbudget_confirmation_id:
            raise UserError('No budget confirmation created for this requisition.')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Budget Confirmation',
            'res_model': 'sagovtender.budget.confirmation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_requisition_id': self.id},
        }

    def action_view_documents(self):
        """View attached documents"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Documents',
            'res_model': 'ir.attachment',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.document_ids.ids)],
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
            },
        }


class PurchaseRequisitionLine(models.Model):
    """Purchase Requisition Line - Commodities/Items"""
    _name = 'sagovtender.purchase.requisition.line'
    _description = 'Purchase Requisition Line'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    requisition_id = fields.Many2one(
        'sagovtender.purchase.requisition',
        string='Requisition',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product/Commodity',
        required=True,
        help='Select the commodity or product to be procured',
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )
    name = fields.Text(
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
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='requisition_id.currency_id',
        store=True
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

    notes = fields.Text(string='Notes')

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        """Calculate subtotal"""
        for line in self:
            line.subtotal = line.quantity * line.unit_price

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

        self.name = self.product_id.name
        self.uom_id = self.product_id.uom_id
        self.unit_price = self.product_id.standard_price

        budget_item_model = self.env['account.report.budget.item']
        matching_items = budget_item_model.search([
            ('product_id', '=', self.product_id.id)
        ])

        if not matching_items:
            self.budget_id = False
            self.account_id = False
            return {
                'warning': {
                    'title': _('No Matching Budget Item'),
                    'message': _(
                        'No budget items were found for the selected product. '
                        'Create a budget item or select the budget manually.'
                    ),
                }
            }

        matching_budgets = matching_items.mapped('budget_id')
        if len(matching_budgets) > 1:
            narrowed_budgets = matching_budgets
            if 'department_id' in self.env['account.report.budget']._fields:
                narrowed_budgets = narrowed_budgets.filtered(
                    lambda budget: budget.department_id == self.requisition_id.department_id
                ) or narrowed_budgets

            if 'company_id' in self.env['account.report.budget']._fields:
                narrowed_budgets = narrowed_budgets.filtered(
                    lambda budget: budget.company_id == self.requisition_id.company_id
                ) or narrowed_budgets

            if len(narrowed_budgets) > 1:
                self.budget_id = False
                self.account_id = False
                return {
                    'warning': {
                        'title': _('Multiple Matching Budgets'),
                        'message': _(
                            'Multiple budgets contain this product, even after applying '
                            'company/department matching. Please select the correct budget manually.'
                        ),
                    }
                }

            matching_budgets = narrowed_budgets

        self.budget_id = matching_budgets
        budget_items = matching_items.filtered(lambda item: item.budget_id == self.budget_id)
        account_ids = budget_items.mapped('account_id')
        if len(account_ids) == 1:
            self.account_id = account_ids
        elif len(account_ids) > 1:
            self.account_id = False
            return {
                'warning': {
                    'title': _('Multiple GL Accounts'),
                    'message': _(
                        'The selected budget has multiple GL accounts for this product. '
                        'Please choose the correct GL account manually.'
                    ),
                }
            }

    @api.onchange('budget_id')
    def _onchange_budget_id(self):
        """Auto-fill GL account from selected budget item"""
        if not self.budget_id or not self.product_id:
            return

        budget_items = self.budget_id.item_ids.filtered(
            lambda item: item.product_id == self.product_id
        )
        account_ids = budget_items.mapped('account_id')
        if len(account_ids) == 1:
            self.account_id = account_ids
        elif len(account_ids) > 1:
            self.account_id = False
            return {
                'warning': {
                    'title': _('Multiple GL Accounts'),
                    'message': _(
                        'The selected budget has multiple GL accounts for this product. '
                        'Please choose the correct GL account manually.'
                    ),
                }
            }

    @api.constrains('quantity')
    def _check_quantity(self):
        """Validate quantity"""
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(
                    'Quantity must be greater than zero.'
                )