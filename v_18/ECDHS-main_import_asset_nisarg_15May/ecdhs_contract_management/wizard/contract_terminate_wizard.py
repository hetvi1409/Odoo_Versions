# -*- coding: utf-8 -*-
# Eastern Cape DSD – Contract Termination Wizard
# SOP Steps 19-20: request approval, draft termination memo, notify provider

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EcdhsContractTerminateWizard(models.TransientModel):
    _name = 'ecdhs.contract.terminate.wizard'
    _description = 'Contract Termination Wizard'

    contract_id = fields.Many2one(
        'ecdhs.contract', string='Contract',
        required=True,
        default=lambda self: self.env.context.get('active_id'),
        readonly=True,
    )
    contract_value = fields.Monetary(
        related='contract_id.contract_value', readonly=True,
    )
    currency_id = fields.Many2one(
        related='contract_id.currency_id', readonly=True,
    )
    service_provider_id = fields.Many2one(
        related='contract_id.service_provider_id', readonly=True,
    )

    termination_date = fields.Date(
        'Effective Termination Date',
        required=True, default=fields.Date.today,
        help='Date on which the contract will formally be terminated.',
    )
    termination_reason = fields.Selection([
        ('non_performance', 'Non-Performance / Persistent SLA Breach'),
        ('mutual_agreement', 'Mutual Agreement with Service Provider'),
        ('expiry', 'Natural Contract Expiry'),
        ('budget', 'Budget Reduction / Departmental Restructure'),
        ('penalty_close', 'Penalty Close (Contract / SLA Invoked)'),
        ('other', 'Other'),
    ], string='Primary Reason for Termination', required=True,
    )
    termination_notes = fields.Text(
        'Detailed Motivation',
        help='Full context as required for the termination memo (SOP Step 19).',
    )
    notify_provider = fields.Boolean(
        'Post Termination Notice to Contract Chatter', default=True,
        help='Logs a formal notice message on the contract record.',
    )

    # =========================================================================
    # Actions
    # =========================================================================

    def action_terminate(self):
        self.ensure_one()
        contract = self.contract_id
        if contract.state in ('terminated', 'cancelled'):
            raise UserError(_('This contract is already terminated or cancelled.'))

        reason_label = dict(
            self._fields['termination_reason'].selection
        ).get(self.termination_reason, self.termination_reason)

        full_reason = reason_label
        if self.termination_notes:
            full_reason = '%s\n\n%s' % (reason_label, self.termination_notes)

        contract.write({
            'state': 'terminated',
            'termination_date': self.termination_date,
            'termination_reason': full_reason,
        })

        if self.notify_provider:
            contract.message_post(
                body=_(
                    'Contract terminated effective %(date)s.\n'
                    'Reason: %(reason)s',
                    date=self.termination_date,
                    reason=full_reason,
                )
            )

        return {'type': 'ir.actions.act_window_close'}
