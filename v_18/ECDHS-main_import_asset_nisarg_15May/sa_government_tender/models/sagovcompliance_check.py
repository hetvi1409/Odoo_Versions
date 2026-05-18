# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ComplianceCheck(models.Model):
    """Compliance Check - Step 7 of Tender Process"""
    _name = 'sagovtender.compliance.check'
    _description = 'Tender Compliance Check'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('sagovtender.compliance.check')
    )
    tender_id = fields.Many2one(
        'sagovtender.tender',
        string='Tender',
        required=True,
        ondelete='cascade',
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    bid_id = fields.Many2one(
        'sagovtender.bid',
        string='Bid',
        required=True,
        ondelete='cascade',
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    partner_id = fields.Many2one(
        'res.partner',
        string='Bidder',
        required=True,
        tracking=True,
        related='bid_id.partner_id',
        store=False
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    checked_by_id = fields.Many2one(
        'res.users',
        string='Checked By',
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    check_date = fields.Date(
        string='Check Date',
        tracking=True
    )

    # CSD Registration
    csd_registered = fields.Boolean(
        string='CSD Registered',
        tracking=True,
        help='Registered on Central Supplier Database'
    )
    csd_number = fields.Char(
        string='CSD Number',
        related='partner_id.csd_number',
        readonly=True
    )
    csd_verified = fields.Boolean(
        string='CSD Verified',
        default=False
    )
    csd_notes = fields.Text(string='CSD Notes')

    # Tax Compliance
    tax_compliant = fields.Boolean(
        string='Tax Compliant',
        tracking=True,
        help='Valid SARS tax clearance'
    )
    tax_clearance_number = fields.Char(string='Tax Clearance Number')
    tax_clearance_expiry = fields.Date(string='Tax Clearance Expiry')
    tax_verified = fields.Boolean(string='Tax Verified', default=False)
    tax_notes = fields.Text(string='Tax Notes')

    # COID (Compensation for Occupational Injuries and Diseases)
    coid_compliant = fields.Boolean(
        string='COID Compliant',
        tracking=True,
        help='COID Letter of Good Standing'
    )
    coid_number = fields.Char(string='COID Number')
    coid_verified = fields.Boolean(string='COID Verified', default=False)
    coid_notes = fields.Text(string='COID Notes')

    # B-BBEE
    bbbee_compliant = fields.Boolean(
        string='B-BBEE Certificate Submitted',
        tracking=True,
        help='B-BBEE Certificate or Affidavit'
    )
    # Related field - inherits Selection type from res.partner.bbbee_level
    bbbee_level = fields.Selection(
        related='partner_id.bbbee_level',
        readonly=True,
        store=True  # Store for performance and reporting
    )
    bbbee_certificate_type = fields.Selection([
        ('certificate', 'B-BBEE Certificate'),
        ('affidavit', 'Sworn Affidavit'),
    ], string='B-BBEE Document Type')
    bbbee_verified = fields.Boolean(string='B-BBEE Verified', default=False)
    bbbee_notes = fields.Text(string='B-BBEE Notes')

    # Company Registration
    cipc_registered = fields.Boolean(
        string='CIPC Registered',
        default=True,
        help='Registered with Companies and Intellectual Property Commission'
    )
    cipc_number = fields.Char(
        string='Company Registration Number',
        related='partner_id.company_registry',
        readonly=True
    )
    cipc_verified = fields.Boolean(string='CIPC Verified', default=False)

    # Mandatory Documents
    sbd_forms_complete = fields.Boolean(
        string='SBD Forms Complete',
        compute='_compute_sbd_complete',
        store=True
    )

    # Overall Compliance
    is_compliant = fields.Boolean(
        string='Compliant',
        compute='_compute_is_compliant',
        store=True,
        tracking=True
    )
    non_compliance_reasons = fields.Text(
        string='Non-Compliance Reasons',
        compute='_compute_non_compliance_reasons'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('checking', 'Checking'),
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('closed', 'Closed'),
    ], string='Status', default='draft', required=True, tracking=True)

    remarks = fields.Text(string='Remarks')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    @api.depends('bid_id.sbd1_complete', 'bid_id.sbd2_complete',
                 'bid_id.sbd3_complete', 'bid_id.sbd4_complete')
    def _compute_sbd_complete(self):
        """Check if mandatory SBD forms are complete"""
        for record in self:
            if record.bid_id:
                record.sbd_forms_complete = all([
                    record.bid_id.sbd1_complete,
                    record.bid_id.sbd2_complete,
                    record.bid_id.sbd3_complete,
                    record.bid_id.sbd4_complete,
                ])
            else:
                record.sbd_forms_complete = False

    @api.depends('csd_verified', 'tax_verified', 'coid_verified',
                 'bbbee_verified', 'cipc_verified', 'sbd_forms_complete')
    def _compute_is_compliant(self):
        """Determine overall compliance"""
        for record in self:
            record.is_compliant = all([
                record.csd_verified,
                record.tax_verified,
                record.coid_verified,
                record.bbbee_verified,
                record.cipc_verified,
                record.sbd_forms_complete,
            ])

    @api.depends('is_compliant', 'csd_verified', 'tax_verified',
                 'coid_verified', 'bbbee_verified', 'cipc_verified', 'sbd_forms_complete')
    def _compute_non_compliance_reasons(self):
        """List non-compliance reasons"""
        for record in self:
            reasons = []
            if not record.csd_verified:
                reasons.append('CSD registration not verified')
            if not record.tax_verified:
                reasons.append('Tax compliance not verified')
            if not record.coid_verified:
                reasons.append('COID compliance not verified')
            if not record.bbbee_verified:
                reasons.append('B-BBEE certificate not verified')
            if not record.cipc_verified:
                reasons.append('CIPC registration not verified')
            if not record.sbd_forms_complete:
                reasons.append('Mandatory SBD forms incomplete')

            record.non_compliance_reasons = '\n'.join(reasons) if reasons else ''

    def action_start_checking(self):
        """Start compliance checking"""
        self.write({
            'state': 'checking',
            'checked_by_id': self.env.user.id,
            'check_date': fields.Date.today()
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Compliance Check'),
            'res_model': 'sagovtender.compliance.check',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'edit',  # Allow editing verification fields
            },
        }

    def action_verify_all(self):
        """Auto-verify all checks (for demo purposes)"""
        self.write({
            'csd_verified': self.csd_registered,
            'tax_verified': self.tax_compliant,
            'coid_verified': self.coid_compliant,
            'bbbee_verified': self.bbbee_compliant,
            'cipc_verified': self.cipc_registered,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Compliance Check'),
            'res_model': 'sagovtender.compliance.check',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'edit',
            },
        }

    def action_mark_compliant(self):
        """Mark as compliant"""
        self.ensure_one()
        if not self.is_compliant:
            raise UserError(
                f'Cannot mark as compliant. Reasons:\n{self.non_compliance_reasons}'
            )

        self.write({'state': 'compliant'})
        self.bid_id.action_mark_compliant()
        self.message_post(body='Bid marked as compliant.')
        self.bid_id.sagovcompliance_check_id = self.id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Compliance Check'),
            'res_model': 'sagovtender.compliance.check',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'readonly',  # Compliant - show in readonly
            },
        }

    def action_mark_non_compliant(self):
        """Mark as non-compliant"""
        self.write({'state': 'non_compliant'})
        self.bid_id.action_mark_non_compliant()
        self.message_post(
            body=f'Bid marked as non-compliant.\nReasons:\n{self.non_compliance_reasons}'
        )
        return {
            'type': 'ir.actions.act_window',
            'name': _('Compliance Check'),
            'res_model': 'sagovtender.compliance.check',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'readonly',  # Non-compliant - show in readonly
            },
        }

    def action_close(self):
        """Close compliance check"""
        self.write({'state': 'closed'})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Compliance Check'),
            'res_model': 'sagovtender.compliance.check',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'readonly',  # Closed - show in readonly
            },
        }
