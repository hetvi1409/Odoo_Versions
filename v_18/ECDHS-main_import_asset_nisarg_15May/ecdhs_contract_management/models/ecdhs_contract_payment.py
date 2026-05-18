# -*- coding: utf-8 -*-
# Eastern Cape DSD – Contract Payment Verification Model
# SOP Steps 22 (payment verification before processing)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EcdhsContractPayment(models.Model):
    _name = 'ecdhs.contract.payment'
    _description = 'Contract Payment Verification'
    _inherit = ['mail.thread']
    _order = 'invoice_date desc'

    contract_id = fields.Many2one(
        'ecdhs.contract', string='Contract',
        required=True, ondelete='cascade', tracking=True,
    )
    name = fields.Char(
        'Invoice / Payment Reference',
        copy=False, tracking=True, readonly=True,
        help='Auto-populated from the linked Vendor Bill reference (Odoo invoicing sequence).',
    )
    invoice_date = fields.Date(
        'Invoice Date', required=True, default=fields.Date.today, tracking=True,
    )
    service_period = fields.Char(
        'Service Period',
        help='Period covered by this invoice, e.g. "Q1 2026" or "January 2026".',
    )
    currency_id = fields.Many2one(
        'res.currency', related='contract_id.currency_id', readonly=True,
    )
    original_contract_value = fields.Monetary(
        string='Original Contract Value',
        tracking=True,
        help='Defaults from the selected contract but can be adjusted manually for this payment verification.',
    )
    contracted_amount = fields.Monetary(
        'Contracted Amount for Period',
        help='Amount the SLA specifies for this particular service period.',
    )
    invoice_amount = fields.Monetary(
        'Invoiced Amount', required=True, tracking=True,
    )
    amount_variance = fields.Monetary(
        'Variance (Invoice − Contracted)',
        compute='_compute_variance', store=True,
    )
    remaining_contract_balance = fields.Monetary(
        'Remaining Contract Balance',
        related='contract_id.contract_value',
        readonly=True,
        help='Original contract value less all payment verifications already marked as paid.',
    )

    # -------------------------------------------------------------------------
    # Verification Checklist  –  SOP Step 22
    # -------------------------------------------------------------------------
    monitoring_report_received = fields.Boolean(
        'Contract Review Received from Service Provider', tracking=True,
    )
    services_delivery_confirmed = fields.Boolean(
        'End-User Confirms Services Were Delivered', tracking=True,
    )
    invoice_matches_sla = fields.Boolean(
        'Invoice Amount Does Not Exceed Contracted Amount', tracking=True,
    )
    tax_clearance_valid = fields.Boolean(
        'Tax Clearance Certificate Valid at Time of Payment', tracking=True,
    )
    grv_stamped = fields.Boolean(
        'GRV Stamped by End-User and Sent to Payment Section', tracking=True,
        help='Goods/Services Received Voucher must be stamped before payment can be processed.',
    )

    # -------------------------------------------------------------------------
    # Approval
    # -------------------------------------------------------------------------
    verified_by_id = fields.Many2one(
        'res.users', 'Verified By (Senior Admin CM)', tracking=True, copy=False,
    )
    approved_by_id = fields.Many2one(
        'res.users', 'Approved By (Assistant Director CM)', tracking=True, copy=False,
    )
    vendor_bill_id = fields.Many2one(
        'account.move',
        string='Vendor Bill',
        domain="[('move_type', '=', 'in_invoice')]",
        tracking=True,
        copy=False,
        help='Accounting vendor bill submitted by the service provider for this contract period.',
    )
    state = fields.Selection([
        ('pending', 'Pending Verification'),
        ('verified', 'Verified – Ready for Payment'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
    ], string='Status', default='pending', tracking=True, copy=False)

    notes = fields.Text('Remarks / Exceptions')

    # -------------------------------------------------------------------------
    # Document Filing System
    # -------------------------------------------------------------------------
    folder_id = fields.Many2one(
        'documents.document',
        string='Document Folder',
        readonly=True,
        domain="[('type', '=', 'folder')]",
        help='Folder for storing payment verification documents, linked to parent contract.'
    )

    # =========================================================================
    # Computed
    # =========================================================================

    @api.depends('invoice_amount', 'contracted_amount')
    def _compute_variance(self):
        for payment in self:
            payment.amount_variance = (
                (payment.invoice_amount or 0.0) - (payment.contracted_amount or 0.0)
            )

    @api.onchange('contract_id')
    def _onchange_contract_id(self):
        if self.contract_id:
            self.original_contract_value = (
                self.contract_id.original_contract_value or self.contract_id.contract_value
            )
        else:
            self.original_contract_value = 0.0

    @api.onchange('vendor_bill_id')
    def _onchange_vendor_bill_id(self):
        if self.vendor_bill_id and self.vendor_bill_id.name:
            self.name = self.vendor_bill_id.name

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('original_contract_value') and vals.get('contract_id'):
                contract = self.env['ecdhs.contract'].browse(vals['contract_id'])
                vals['original_contract_value'] = (
                    contract.original_contract_value or contract.contract_value
                )
            if not vals.get('name') and vals.get('vendor_bill_id'):
                bill = self.env['account.move'].browse(vals['vendor_bill_id'])
                if bill.name and bill.name != '/':
                    vals['name'] = bill.name
        records = super().create(vals_list)
        # Assign payment to Monthly Reports subfolder of parent contract
        for payment in records:
            if payment.contract_id and payment.contract_id.folder_id:
                monthly_reports_folder = payment.contract_id._get_contract_subfolder('Monthly Reports')
                if monthly_reports_folder:
                    payment.sudo().write({'folder_id': monthly_reports_folder.id})
        records.mapped('contract_id')._sync_remaining_contract_value()
        return records

    def write(self, vals):
        # Sync name from vendor bill if bill is being changed
        if 'vendor_bill_id' in vals and vals['vendor_bill_id'] and not vals.get('name'):
            bill = self.env['account.move'].browse(vals['vendor_bill_id'])
            if bill.name and bill.name != '/':
                vals['name'] = bill.name
        if 'contract_id' in vals and vals['contract_id'] and 'original_contract_value' not in vals:
            contract = self.env['ecdhs.contract'].browse(vals['contract_id'])
            vals['original_contract_value'] = (
                contract.original_contract_value or contract.contract_value
            )
        previous_contracts = self.mapped('contract_id')
        res = super().write(vals)
        # Re-assign folder if contract changes
        if 'contract_id' in vals:
            for payment in self:
                if payment.contract_id and payment.contract_id.folder_id:
                    monthly_reports_folder = payment.contract_id._get_contract_subfolder('Monthly Reports')
                    if monthly_reports_folder:
                        payment.sudo().write({'folder_id': monthly_reports_folder.id})
        (previous_contracts | self.mapped('contract_id'))._sync_remaining_contract_value()
        return res

    def unlink(self):
        contracts = self.mapped('contract_id')
        res = super().unlink()
        contracts._sync_remaining_contract_value()
        return res


    # =========================================================================
    # State transitions
    # =========================================================================

    def action_verify(self):
        """All five checklist items must be confirmed before verification."""
        for payment in self:
            failed = []
            if not payment.monitoring_report_received:
                failed.append('• Contract Review not yet received')
            if not payment.services_delivery_confirmed:
                failed.append('• End-user delivery confirmation outstanding')
            if not payment.invoice_matches_sla:
                failed.append('• Invoice amount exceeds contracted amount')
            if not payment.tax_clearance_valid:
                failed.append('• Tax clearance certificate not valid')
            if not payment.grv_stamped:
                failed.append('• GRV not yet stamped')
            if failed:
                raise UserError(_(
                    'Payment verification for "%s" cannot proceed. '
                    'The following checklist items are outstanding:\n%s',
                    payment.name, '\n'.join(failed),
                ))
            payment.write({
                'state': 'verified',
                'verified_by_id': self.env.uid,
            })

    def action_mark_paid(self):
        for payment in self.filtered(lambda p: p.state == 'verified'):
            if payment.vendor_bill_id and payment.vendor_bill_id.state != 'posted':
                raise UserError(_(
                    'Vendor Bill %(bill)s must be posted before marking payment %(payment)s as paid.',
                    bill=payment.vendor_bill_id.display_name,
                    payment=payment.name,
                ))
            payment.write({'state': 'paid'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_open_vendor_bill(self):
        self.ensure_one()
        if not self.vendor_bill_id:
            raise UserError(_('No Vendor Bill is linked to this payment verification yet.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Vendor Bill'),
            'res_model': 'account.move',
            'res_id': self.vendor_bill_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
