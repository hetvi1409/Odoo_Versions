# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ComplianceCheckWizard(models.TransientModel):
    _name = 'sagovtender.compliance.check.wizard'
    _description = 'Create Compliance Check Wizard'

    tender_id = fields.Many2one(
        'sagovtender.tender',
        string='Tender',
        required=True,
        readonly=True,
        default=lambda self: self.env.context.get('default_tender_id'),
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )

    bid_id = fields.Many2one(
        'sagovtender.bid',
        string='Bid',
        required=True,
        domain='[("tender_id", "=", tender_id)]',
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Bidder',
        related='bid_id.partner_id',
        readonly=True,
        store=False
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    def action_confirm(self):
        self.ensure_one()
        if not self.tender_id or not self.bid_id:
            raise UserError(_('Please select a bid.'))

        # Prevent duplicate compliance check for the same bid
        existing = self.env['sagovtender.compliance.check'].search([
            ('tender_id', '=', self.tender_id.id),
            ('bid_id', '=', self.bid_id.id),
        ], limit=1)
        if existing:
            compliance = existing
        else:
            compliance = self.env['sagovtender.compliance.check'].create({
                'tender_id': self.tender_id.id,
                'bid_id': self.bid_id.id,
            })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Compliance Check'),
            'res_model': 'sagovtender.compliance.check',
            'view_mode': 'form',
            'res_id': compliance.id,
            'target': 'new',
            'flags': {
                'mode': 'readonly',  # Start in readonly, buttons switch to edit automatically
            },
            'context': {
                'form_view_initial_mode': 'readonly',  # No Save/Discard shown initially
            }
        }
