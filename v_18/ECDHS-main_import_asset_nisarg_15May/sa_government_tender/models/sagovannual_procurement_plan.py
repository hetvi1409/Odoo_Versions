
# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AnnualProcurementPlan(models.Model):
    """Annual Procurement Plan (APP) - Budget planning for procurement"""
    _name = 'sagovtender.annual.procurement.plan'
    _description = 'Annual Procurement Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fiscal_year desc, name'
    _rec_name = 'item_description'

    name = fields.Char(
        string='Plan Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('sagovtender.app')
    )
    fiscal_year = fields.Char(
        string='Fiscal Year',
        required=True,
        tracking=True,
        help='Financial year for this procurement plan (e.g., 2024/2025)'
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        required=True,
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    budget_line = fields.Char(
        string='Budget Line',
        help='Budget line item reference'
    )
    item_description = fields.Text(
        string='Item Description',
        required=True,
        help='Description of goods or services to be procured'
    )
    estimated_value = fields.Monetary(
        string='Estimated Value',
        required=True,
        currency_field='currency_id',
        tracking=True
    )
    available_budget = fields.Monetary(
        string='Available Budget',
        required=True,
        currency_field='currency_id',
        tracking=True
    )
    allocated_amount = fields.Monetary(
        string='Allocated Amount',
        compute='_compute_allocated_amount',
        store=True,
        currency_field='currency_id'
    )
    remaining_budget = fields.Monetary(
        string='Remaining Budget',
        compute='_compute_remaining_budget',
        store=True,
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    planned_date = fields.Date(
        string='Planned Procurement Date',
        required=True
    )

    # DEPRECATED: Legacy field - kept for backward compatibility, computed from procurement_method_config_id
    procurement_method = fields.Selection([
        ('petty_cash', 'Petty Cash (< R2,000)'),
        ('quotation', 'Written Quotations (R2,001 - R200,000)'),
        ('rfq', 'Formal RFQ (R200,001 - R500,000)'),
        ('tender', 'Competitive Tender (> R500,000)'),
        ('single_source', 'Single Source'),
        ('other', 'Other'),
    ], string='Procurement Method (Legacy)', compute='_compute_legacy_fields', store=True, readonly=True,
       help='DEPRECATED: Use procurement_method_config_id instead. This field is auto-computed for compatibility.')
    procurement_method_config_id = fields.Many2one(
        'sagovprocurement.method',
        string='Procurement Method Configuration',
        help='Recommended procurement method based on estimated value'
    )
    preference_point_system_config_id = fields.Many2one(
        'sagovpreference.point.system',
        string='Preference Point System Configuration',
        help='Recommended preference point system based on estimated value'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)
    requisition_ids = fields.One2many(
        'sagovtender.purchase.requisition',
        'app_id',
        string='Purchase Requisitions'
    )
    requisition_count = fields.Integer(
        string='Requisition Count',
        compute='_compute_requisition_count'
    )
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    tender_ids = fields.One2many(
        'sagovtender.tender',
        'requisition_app_id',
        string='Tenders'
    )

    # Backlinks to source annual procurement plan
    source_app_line_id = fields.Many2one(
        'annual.procurement.plan.line',
        string='Source APP Line',
        required=False,
        help='Link to the original annual procurement plan line that created this record'
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    source_app_id = fields.Many2one(
        'annual.procurement.plan',
        string='Source APP',
        required=False,
        help='Link to the original annual procurement plan'
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    @api.depends('requisition_ids.budget_confirmed_amount')
    def _compute_allocated_amount(self):
        """Calculate total allocated amount from requisitions"""
        for record in self:
            record.allocated_amount = sum(
                record.requisition_ids.filtered(
                    lambda r: r.state not in ['cancelled', 'rejected']
                ).mapped('budget_confirmed_amount')
            )

    @api.depends('available_budget', 'allocated_amount')
    def _compute_remaining_budget(self):
        """Calculate remaining budget"""
        for record in self:
            record.remaining_budget = record.available_budget - record.allocated_amount

    @api.depends('requisition_ids')
    def _compute_requisition_count(self):
        """Count related requisitions"""
        for record in self:
            record.requisition_count = len(record.requisition_ids)

    @api.constrains('available_budget', 'estimated_value')
    def _check_budget_values(self):
        """Ensure budget values are positive"""
        for record in self:
            if record.available_budget < 0:
                raise ValidationError('Available budget cannot be negative.')
            if record.estimated_value < 0:
                raise ValidationError('Estimated value cannot be negative.')
            if record.estimated_value > record.available_budget:
                raise ValidationError(
                    'Estimated value cannot exceed available budget.'
                )

    @api.depends('procurement_method_config_id')
    def _compute_legacy_fields(self):
        """Compute legacy field from configuration field for backward compatibility"""
        for record in self:
            if record.procurement_method_config_id:
                # Map config method to selection value
                method_name = record.procurement_method_config_id.name
                if 'Quotation' in method_name and '30' in method_name:
                    record.procurement_method = 'quotation'
                elif 'RFQ' in method_name:
                    record.procurement_method = 'rfq'
                elif 'Competitive' in method_name or 'Tender' in method_name:
                    record.procurement_method = 'tender'
                elif 'Single' in method_name or 'Sole' in method_name:
                    record.procurement_method = 'single_source'
                else:
                    record.procurement_method = 'other'
            else:
                record.procurement_method = False

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.display_name))
        return result

    def _compute_display_name(self):
        for record in self:
            if record.item_description and record.name:
                record.display_name = f"{record.item_description} - {record.name}"
            else:
                record.display_name = record.item_description or record.name or ''

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            domain = ['|', ('item_description', operator, name), ('name', operator, name)]
            records = self.search(domain + args, limit=limit)
        else:
            records = self.search(args, limit=limit)
        return records.name_get()

    def action_submit(self):
        """Submit APP for approval"""
        self.write({'state': 'submitted'})
        self.message_post(body='APP submitted for approval.')

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._set_procurement_config_defaults()
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'estimated_value' in vals or not vals.get('procurement_method_config_id'):
            self._set_procurement_config_defaults()
        return res

    def _set_procurement_config_defaults(self):
        for record in self:
            if not record.estimated_value:
                continue
            if record.procurement_method_config_id:
                continue
            method = record.env['sagovprocurement.method'].get_applicable_method(
                record.estimated_value
            )
            if method:
                record.procurement_method_config_id = method
                if method.preference_point_system_ids:
                    record.preference_point_system_config_id = method.preference_point_system_ids[0]

    @api.onchange('estimated_value')
    def _onchange_estimated_value(self):
        """Suggest procurement method based on value"""
        if self.estimated_value:
            method = self.env['sagovprocurement.method'].get_applicable_method(
                self.estimated_value
            )
            if method:
                self.procurement_method_config_id = method
                if method.preference_point_system_ids:
                    self.preference_point_system_config_id = method.preference_point_system_ids[0]

    @api.onchange('procurement_method_config_id')
    def _onchange_procurement_method_config(self):
        """When procurement method changes, update related fields and trigger dependent calculations"""
        if self.procurement_method_config_id:
            if self.procurement_method_config_id.preference_point_system_ids:
                self.preference_point_system_config_id = (
                    self.procurement_method_config_id.preference_point_system_ids[0]
                )

    @api.onchange('preference_point_system_config_id')
    def _onchange_preference_point_system_config(self):
        """When preference point system changes, trigger dependent calculations"""
        # Ensure dependent fields are properly recalculated on form change
        pass

    def action_approve(self):
        """Approve APP"""
        self.write({'state': 'approved'})
        self.message_post(body='APP approved.')

    def action_cancel(self):
        """Cancel APP"""
        self.write({'state': 'cancelled'})
        self.message_post(body='APP cancelled.')

    def action_view_requisitions(self):
        """View related purchase requisitions"""
        self.ensure_one()
        return {
            'name': 'Purchase Requisitions',
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.purchase.requisition',
            'view_mode': 'list,form',
            'domain': [('app_id', '=', self.id)],
            'context': {'default_app_id': self.id}
        }

    has_approved_requisition_line = fields.Boolean(
        compute="_compute_has_approved_requisition_line",
        store=False
    )

    def _compute_has_approved_requisition_line(self):
        for rec in self:
            rec.has_approved_requisition_line = any(
                line.state == 'approved' for line in rec.requisition_ids
            )

    def action_create_requisition(self):
        """Create related purchase requisitions"""
        self.ensure_one()
        return {
            'name': 'Purchase Requisitions',
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.purchase.requisition',
            # 'view_mode': 'list,form',
            'view_mode': 'form',
            'domain': [('app_id', '=', self.id)],
            'context': {'default_app_id': self.id}
        }

    def action_create_tender(self):
        """Create a tender from the APP"""
        self.ensure_one()
        tender = self.env['sagovtender.tender'].create({
            'requisition_app_id': self.id,
            'procurement_method_config_id': self.procurement_method_config_id.id,
            'preference_point_system_config_id': self.preference_point_system_config_id.id,
        })
        return {
            'name': 'Purchase Requisitions',
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.tender',
            # 'view_mode': 'list,form',
            'view_mode': 'form',
            'res_id': tender.id,
            'target': 'current',
            'domain': [('requisition_app_id', '=', self.id)],
            'context': {
                'default_requisition_app_id': self.id,
                'default_procurement_method_config_id': self.procurement_method_config_id.id,
                'default_preference_point_system_config_id': self.preference_point_system_config_id.id,
            }
        }
