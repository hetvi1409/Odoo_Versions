# -*- coding: utf-8 -*-

import json

from odoo import fields, models


class EcdhsContractDashboard(models.Model):
    _name = 'ecdhs.contract.dashboard'
    _description = 'Contracts Management Dashboard'

    name = fields.Char(
        string='Dashboard Name',
        default='Contract Management Dashboard',
        readonly=True,
    )

    company_currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        compute='_compute_dashboard_metrics',
    )

    active_contracts = fields.Integer(compute='_compute_dashboard_metrics')
    expiring_contracts = fields.Integer(compute='_compute_dashboard_metrics')
    delayed_milestones = fields.Integer(compute='_compute_dashboard_metrics')
    compliance_alerts = fields.Integer(compute='_compute_dashboard_metrics')
    total_contracts = fields.Integer(compute='_compute_dashboard_metrics')
    on_track_contracts = fields.Integer(compute='_compute_dashboard_metrics')

    my_open_contracts = fields.Integer(compute='_compute_dashboard_metrics')
    my_expiring_contracts = fields.Integer(compute='_compute_dashboard_metrics')
    my_blocked_contracts = fields.Integer(compute='_compute_dashboard_metrics')

    monitoring_total = fields.Integer(compute='_compute_dashboard_metrics')
    monitoring_compliant = fields.Integer(compute='_compute_dashboard_metrics')
    monitoring_compliance_rate = fields.Float(compute='_compute_dashboard_metrics')

    payments_verified = fields.Integer(compute='_compute_dashboard_metrics')
    payments_paid = fields.Integer(compute='_compute_dashboard_metrics')
    payments_rejected = fields.Integer(compute='_compute_dashboard_metrics')

    type_sla_count = fields.Integer(compute='_compute_dashboard_metrics')
    type_funding_count = fields.Integer(compute='_compute_dashboard_metrics')
    type_lease_count = fields.Integer(compute='_compute_dashboard_metrics')
    type_cession_count = fields.Integer(compute='_compute_dashboard_metrics')

    budget_amount = fields.Monetary(
        currency_field='company_currency_id',
        compute='_compute_dashboard_metrics',
    )
    spend_amount = fields.Monetary(
        currency_field='company_currency_id',
        compute='_compute_dashboard_metrics',
    )
    budget_vs_spend_delta = fields.Monetary(
        currency_field='company_currency_id',
        compute='_compute_dashboard_metrics',
    )

    # Chart data fields (JSON strings consumed by the OWL chart widget)
    chart_type_distribution = fields.Char(compute='_compute_chart_data', string='Chart: Portfolio by Type')
    chart_state_distribution = fields.Char(compute='_compute_chart_data', string='Chart: Lifecycle States')
    chart_health_distribution = fields.Char(compute='_compute_chart_data', string='Chart: Contract Health')
    chart_payment_summary = fields.Char(compute='_compute_chart_data', string='Chart: Payment Summary')

    def _compute_chart_data(self):
        Contract = self.env['ecdhs.contract'].sudo()
        Payment = self.env['ecdhs.contract.payment'].sudo()
        live_states = ['terminated', 'cancelled']

        # --- Doughnut: Portfolio by Type ---
        type_specs = [
            ('sla', 'SLA'),
            ('funding_agreement', 'Funding'),
            ('lease', 'Lease'),
            ('cession', 'Cession'),
        ]
        type_counts = [
            Contract.search_count([('contract_type', '=', t), ('state', 'not in', live_states)])
            for t, _ in type_specs
        ]
        chart_type = json.dumps({
            'type': 'doughnut',
            'data': {
                'labels': [l for _, l in type_specs],
                'datasets': [{
                    'data': type_counts,
                    'backgroundColor': ['#6366f1', '#f59e0b', '#1e3a5f', '#d97706'],
                    'borderWidth': 2,
                    'borderColor': '#ffffff',
                }],
            },
        })

        # --- Bar: Contract Lifecycle States ---
        state_specs = [
            ('draft', 'New Draft'),
            ('verified', 'Verified'),
            ('contract_drafted', 'Drafted'),
            ('legal_review', 'Legal Review'),
            ('approved', 'Approved'),
            ('signing', 'Awaiting Signature'),
            ('fully_signed', 'Fully Signed'),
            ('active', 'Active'),
            ('expiring', 'Due for Renewal'),
            ('terminated', 'Terminated'),
        ]
        state_counts = [Contract.search_count([('state', '=', s)]) for s, _ in state_specs]
        chart_state = json.dumps({
            'type': 'bar',
            'data': {
                'labels': [l for _, l in state_specs],
                'datasets': [{
                    'label': 'Contracts',
                    'data': state_counts,
                    'backgroundColor': [
                        '#94a3b8', '#0ea5e9', '#3b82f6', '#8b5cf6',
                        '#10b981', '#f59e0b', '#22c55e', '#14b8a6',
                        '#f97316', '#ef4444',
                    ],
                    'borderRadius': 6,
                    'borderSkipped': False,
                }],
            },
            'options': {
                'plugins': {'legend': {'display': False}},
                'scales': {
                    'y': {'beginAtZero': True, 'ticks': {'stepSize': 1}},
                    'x': {'ticks': {'font': {'size': 10}}},
                },
            },
        })

        # --- Pie: Contract Health (kanban_state) ---
        health_counts = [
            Contract.search_count([('kanban_state', '=', 'normal'), ('state', 'not in', live_states)]),
            Contract.search_count([('kanban_state', '=', 'blocked'), ('state', 'not in', live_states)]),
            Contract.search_count([('kanban_state', '=', 'done'), ('state', 'not in', live_states)]),
        ]
        chart_health = json.dumps({
            'type': 'pie',
            'data': {
                'labels': ['On Track', 'Action Required', 'Ready for Next Stage'],
                'datasets': [{
                    'data': health_counts,
                    'backgroundColor': ['#10b981', '#ef4444', '#3b82f6'],
                    'borderWidth': 2,
                    'borderColor': '#ffffff',
                }],
            },
        })

        # --- Polar Area: Payment Summary ---
        payment_counts = [
            Payment.search_count([('state', '=', 'verified')]),
            Payment.search_count([('state', '=', 'paid')]),
            Payment.search_count([('state', '=', 'rejected')]),
            Payment.search_count([('state', '=', 'draft')]),
        ]
        chart_payment = json.dumps({
            'type': 'polarArea',
            'data': {
                'labels': ['Verified', 'Paid', 'Rejected', 'Pending'],
                'datasets': [{
                    'data': payment_counts,
                    'backgroundColor': [
                        'rgba(59,130,246,0.75)',
                        'rgba(34,197,94,0.75)',
                        'rgba(239,68,68,0.75)',
                        'rgba(107,114,128,0.75)',
                    ],
                    'borderColor': ['#3b82f6', '#22c55e', '#ef4444', '#6b7280'],
                    'borderWidth': 2,
                }],
            },
        })

        for rec in self:
            rec.chart_type_distribution = chart_type
            rec.chart_state_distribution = chart_state
            rec.chart_health_distribution = chart_health
            rec.chart_payment_summary = chart_payment

    def _compute_dashboard_metrics(self):
        Contract = self.env['ecdhs.contract'].sudo()
        Monitoring = self.env['ecdhs.contract.monitoring'].sudo()
        Payment = self.env['ecdhs.contract.payment'].sudo()
        active_states = ['active', 'expiring']

        active_count = Contract.search_count([('state', '=', 'active')])
        expiring_count = Contract.search_count([('state', '=', 'expiring')])
        delayed_count = Contract.search_count([
            ('kanban_state', '=', 'blocked'),
            ('state', 'not in', ['terminated', 'cancelled']),
        ])
        compliance_count = Monitoring.search_count([('non_compliance_found', '=', True)])
        total_count = Contract.search_count([('state', 'not in', ['terminated', 'cancelled'])])
        on_track_count = Contract.search_count([
            ('kanban_state', '=', 'normal'),
            ('state', 'not in', ['terminated', 'cancelled']),
        ])

        my_open_count = Contract.search_count([
            ('admin_officer_id', '=', self.env.user.id),
            ('state', 'in', active_states),
        ])
        my_expiring_count = Contract.search_count([
            ('admin_officer_id', '=', self.env.user.id),
            ('state', '=', 'expiring'),
        ])
        my_blocked_count = Contract.search_count([
            ('admin_officer_id', '=', self.env.user.id),
            ('kanban_state', '=', 'blocked'),
            ('state', 'not in', ['terminated', 'cancelled']),
        ])

        monitoring_total = Monitoring.search_count([])
        monitoring_non_compliant = Monitoring.search_count([('non_compliance_found', '=', True)])
        monitoring_compliant = max(monitoring_total - monitoring_non_compliant, 0)
        monitoring_rate = (monitoring_compliant / monitoring_total * 100.0) if monitoring_total else 0.0

        payments_verified = Payment.search_count([('state', '=', 'verified')])
        payments_paid = Payment.search_count([('state', '=', 'paid')])
        payments_rejected = Payment.search_count([('state', '=', 'rejected')])

        type_sla_count = Contract.search_count([
            ('contract_type', '=', 'sla'),
            ('state', 'not in', ['terminated', 'cancelled']),
        ])
        type_funding_count = Contract.search_count([
            ('contract_type', '=', 'funding_agreement'),
            ('state', 'not in', ['terminated', 'cancelled']),
        ])
        type_lease_count = Contract.search_count([
            ('contract_type', '=', 'lease'),
            ('state', 'not in', ['terminated', 'cancelled']),
        ])
        type_cession_count = Contract.search_count([
            ('contract_type', '=', 'cession'),
            ('state', 'not in', ['terminated', 'cancelled']),
        ])

        budget_group = Contract.read_group(
            [('state', 'not in', ['terminated', 'cancelled'])],
            ['original_contract_value:sum'],
            [],
        )
        spend_group = Payment.read_group(
            [('state', 'in', ['verified', 'paid'])],
            ['invoice_amount:sum'],
            [],
        )
        budget_sum = budget_group[0].get('original_contract_value_sum', 0.0) if budget_group else 0.0
        spend_sum = spend_group[0].get('invoice_amount_sum', 0.0) if spend_group else 0.0

        for rec in self:
            rec.company_currency_id = self.env.company.currency_id
            rec.active_contracts = active_count
            rec.expiring_contracts = expiring_count
            rec.delayed_milestones = delayed_count
            rec.compliance_alerts = compliance_count
            rec.total_contracts = total_count
            rec.on_track_contracts = on_track_count

            rec.my_open_contracts = my_open_count
            rec.my_expiring_contracts = my_expiring_count
            rec.my_blocked_contracts = my_blocked_count

            rec.monitoring_total = monitoring_total
            rec.monitoring_compliant = monitoring_compliant
            rec.monitoring_compliance_rate = monitoring_rate

            rec.payments_verified = payments_verified
            rec.payments_paid = payments_paid
            rec.payments_rejected = payments_rejected

            rec.type_sla_count = type_sla_count
            rec.type_funding_count = type_funding_count
            rec.type_lease_count = type_lease_count
            rec.type_cession_count = type_cession_count

            rec.budget_amount = budget_sum
            rec.spend_amount = spend_sum
            rec.budget_vs_spend_delta = budget_sum - spend_sum

    def _open_action(self, xmlid):
        return self.env.ref(xmlid).read()[0]

    def _open_contracts(self, domain, name):
        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'res_model': 'ecdhs.contract',
            'view_mode': 'list,kanban,form',
            'domain': domain,
            'target': 'current',
        }

    def _open_monitoring(self, domain, name):
        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'res_model': 'ecdhs.contract.monitoring',
            'view_mode': 'list,form',
            'domain': domain,
            'target': 'current',
        }

    def _open_payments(self, domain, name):
        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'res_model': 'ecdhs.contract.payment',
            'view_mode': 'list,form',
            'domain': domain,
            'target': 'current',
        }

    def action_open_active_contracts(self):
        return self._open_action('ecdhs_contract_management.action_ecdhs_contract_active')

    def action_open_expiring_contracts(self):
        return self._open_action('ecdhs_contract_management.action_ecdhs_contract_expiring')

    def action_open_delayed_milestones(self):
        return self._open_action('ecdhs_contract_management.action_ecdhs_contract_delayed_milestones')

    def action_open_budget_vs_spend(self):
        return self._open_action('ecdhs_contract_management.action_ecdhs_contract_budget_vs_spend')

    def action_open_compliance_alerts(self):
        return self._open_action('ecdhs_contract_management.action_ecdhs_contract_compliance_alerts')

    def action_open_my_open_contracts(self):
        return self._open_contracts(
            [('admin_officer_id', '=', self.env.user.id), ('state', 'in', ['active', 'expiring'])],
            'My Open Contracts',
        )

    def action_open_my_expiring_contracts(self):
        return self._open_contracts(
            [('admin_officer_id', '=', self.env.user.id), ('state', '=', 'expiring')],
            'My Expiring Contracts',
        )

    def action_open_my_blocked_contracts(self):
        return self._open_contracts(
            [
                ('admin_officer_id', '=', self.env.user.id),
                ('kanban_state', '=', 'blocked'),
                ('state', 'not in', ['terminated', 'cancelled']),
            ],
            'My Blocked Contracts',
        )

    def action_open_on_track_contracts(self):
        return self._open_contracts(
            [('kanban_state', '=', 'normal'), ('state', 'not in', ['terminated', 'cancelled'])],
            'On-Track Contracts',
        )

    def action_open_all_live_contracts(self):
        return self._open_contracts(
            [('state', 'not in', ['terminated', 'cancelled'])],
            'All Live Contracts',
        )

    def action_open_monitoring_reports(self):
        return self._open_monitoring([], 'Contract Reviews')

    def action_open_compliant_monitoring_reports(self):
        return self._open_monitoring([('non_compliance_found', '=', False)], 'Compliant Reports')

    def action_open_verified_payments(self):
        return self._open_payments([('state', '=', 'verified')], 'Verified Payments')

    def action_open_paid_payments(self):
        return self._open_payments([('state', '=', 'paid')], 'Paid Payments')

    def action_open_rejected_payments(self):
        return self._open_payments([('state', '=', 'rejected')], 'Rejected Payments')

    def action_open_sla_contracts(self):
        return self._open_contracts(
            [('contract_type', '=', 'sla'), ('state', 'not in', ['terminated', 'cancelled'])],
            'SLA Contracts',
        )

    def action_open_funding_contracts(self):
        return self._open_contracts(
            [('contract_type', '=', 'funding_agreement'), ('state', 'not in', ['terminated', 'cancelled'])],
            'Funding Agreement Contracts',
        )

    def action_open_lease_contracts(self):
        return self._open_contracts(
            [('contract_type', '=', 'lease'), ('state', 'not in', ['terminated', 'cancelled'])],
            'Lease Contracts',
        )

    def action_open_cession_contracts(self):
        return self._open_contracts(
            [('contract_type', '=', 'cession'), ('state', 'not in', ['terminated', 'cancelled'])],
            'Cession Contracts',
        )
