# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BudgetConfirmationWizard(models.TransientModel):
    """Wizard for opening budget confirmation from requisition"""
    _name = 'sagovtender.budget.confirmation.wizard'
    _description = 'Budget Confirmation Wizard'

    requisition_id = fields.Many2one(
        'sagovtender.purchase.requisition',
        string='Purchase Requisition',
        required=True,
        readonly=True,
        default=lambda self: self.env.context.get('default_requisition_id'),
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )
    budget_confirmation_id = fields.Many2one(
        'sagovtender.budget.confirm',
        string='Budget Confirmation',
        readonly=True,
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )

    def action_open_budget_confirmation(self):
        """Open budget confirmation form"""
        self.ensure_one()

        if not self.requisition_id.sagovbudget_confirmation_id:
            raise UserError(_('No budget confirmation created for this requisition.'))

        self.budget_confirmation_id = self.requisition_id.sagovbudget_confirmation_id

        return {
            'type': 'ir.actions.act_window',
            'name': _('Budget Confirmation'),
            'res_model': 'sagovtender.budget.confirm',
            'res_id': self.budget_confirmation_id.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'form_view_initial_mode': 'edit',
            }
        }
