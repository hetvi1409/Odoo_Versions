
# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TenderSpecification(models.Model):
    """Tender Specification - Step 3 of Tender Process"""
    _name = 'sagovtender.specification'
    _description = 'Tender Specification'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Specification Title',
        required=True,
        tracking=True
    )
    requisition_id = fields.Many2one(
        'sagovtender.purchase.requisition',
        string='Purchase Requisition',
        required=True,
        ondelete='cascade',
        tracking=True
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
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='requisition_id.department_id',
        store=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    description = fields.Html(
        string='General Description',
        required=True,
        help='General description of goods or services'
    )
    document_ids = fields.Many2many(
        'ir.attachment',
        string='Supporting Documents',
        help='Technical drawings, samples, or reference documents'
    )

    # Optional Memo Link
    link_to_memo = fields.Boolean(
        string='Link to Memo',
        default=False,
        help='Enable to link this specification to a memo from e_system'
    )
    memo_id = fields.Many2one(
        'memo.memo',
        string='Memo',
        help='Link to related memo from e_system',
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', required=True, tracking=True)
    prepared_by_id = fields.Many2one(
        'res.users',
        string='Prepared By',
        default=lambda self: self.env.user,
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    approved_by_id = fields.Many2one(
        'res.users',
        string='Approved By',
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    approval_date = fields.Date(
        string='Approval Date',
        tracking=True
    )
    notes = fields.Text(string='Additional Notes')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        """When requisition changes, refresh configuration fields"""
        if self.requisition_id:
            # Force refresh of related configuration fields
            self.procurement_method_config_id = self.requisition_id.procurement_method_config_id
            self.preference_point_system_config_id = self.requisition_id.preference_point_system_config_id
            # Update department as well
            self.department_id = self.requisition_id.department_id

    @api.onchange('procurement_method_config_id', 'preference_point_system_config_id')
    def _onchange_procurement_configuration(self):
        """Trigger when configuration fields change - framework recognizes field dependencies"""
        # This onchange is triggered by the form when these fields change
        # It allows dependent fields to be properly recomputed on the form view
        pass

    def action_submit_for_review(self):
        """Submit specification for review"""
        for record in self:
            record.write({'state': 'review'})
            record.message_post(body='Specification submitted for review.')

        # Return action to reload form and keep dialog open
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.specification',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }

    def action_approve(self):
        """Approve specification"""
        self.write({
            'state': 'approved',
            'approved_by_id': self.env.user.id,
            'approval_date': fields.Date.today(),
        })
        # Update requisition state
        self.requisition_id.write({'state': 'specification'})
        self.message_post(body='Specification approved.')

        # Return action to reload form and keep dialog open
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.specification',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }

    def action_reject(self):
        """Reject specification"""
        self.write({'state': 'rejected'})
        self.message_post(body='Specification rejected.')

        # Return action to reload form and keep dialog open
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.specification',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }

    def action_reset_to_draft(self):
        """Reset to draft"""
        self.write({'state': 'draft'})

