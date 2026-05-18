# -*- coding: utf-8 -*-
# Eastern Cape DSD – Contract Monitoring / Performance Report Model
# SOP Steps 16-19 (on-site review, checklist, non-compliance, penalties)

from odoo import api, fields, models, _


class EcdhsContractMonitoring(models.Model):
    _name = 'ecdhs.contract.monitoring'
    _description = 'Contract Review'
    _inherit = ['mail.thread']
    _order = 'monitoring_date desc'

    contract_id = fields.Many2one(
        'ecdhs.contract', string='Contract',
        required=True, ondelete='cascade',
    )
    monitoring_date = fields.Date(
        'Monitoring Date', required=True, default=fields.Date.today, tracking=True,
    )
    monitoring_type = fields.Selection([
        ('quarterly', 'Quarterly On-Site Review'),
        ('monthly', 'Monthly Desk Review'),
        ('ad_hoc', 'Ad-Hoc / Special Inspection'),
    ], string='Review Type', required=True, default='quarterly', tracking=True)

    conducted_by_id = fields.Many2one(
        'res.users', 'Conducted By',
        default=lambda self: self.env.user, tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency', related='contract_id.currency_id', readonly=True,
    )

    # -------------------------------------------------------------------------
    # SOP Step 18 – SLA Compliance Checklist (Monthly Review)
    # 7 standard checklist questions from the SOP (page 10)
    # -------------------------------------------------------------------------
    sla_compliant = fields.Boolean(
        '1. Contract complies with SLA requirements', tracking=True,
    )
    noncompliance_steps = fields.Text(
        '2. Steps taken to rectify non-compliance',
        help='Describe corrective actions taken or proposed.',
    )
    pm_monitoring_regular = fields.Boolean(
        '3. Project Manager monitors contract regularly', tracking=True,
    )
    monitoring_reports_available = fields.Boolean(
        '4. Contract Reviews are available', tracking=True,
    )
    service_needed_after_expiry = fields.Boolean(
        '5. Service will be needed beyond contract expiry', tracking=True,
    )
    procurement_start_date = fields.Date(
        '6. Planned procurement start date (if renewal needed)',
        help='When will a new procurement process start to avoid irregular extension?',
    )
    provider_performance_comments = fields.Text(
        '7. Overall performance of service provider',
    )

    # -------------------------------------------------------------------------
    # Findings and Penalties  –  SOP Step 18-19
    # -------------------------------------------------------------------------
    findings = fields.Text('Summary of Findings / Observations')
    non_compliance_found = fields.Boolean(
        'Non-Compliance Found', tracking=True,
    )
    penalty_applicable = fields.Boolean(
        'Penalty Applicable per SLA', tracking=True,
    )
    penalty_amount = fields.Monetary(
        'Penalty Amount Imposed', tracking=True,
    )
    penalty_letter_sent = fields.Boolean(
        'Non-Compliance / Penalty Letter Sent to Provider', tracking=True,
    )
    meeting_minutes_ref = fields.Char(
        'On-Site Meeting Minutes Reference',
        help='File reference for the minutes of the quarterly on-site meeting.',
    )

    # -------------------------------------------------------------------------
    # Escalation
    # -------------------------------------------------------------------------
    termination_recommended = fields.Boolean(
        'Termination Recommended (persistent non-performance)', tracking=True,
        help='If non-compliance persists after the 7-day remedy letter, this flag triggers '
             'the termination approval process per SOP Step 19.',
    )

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted to Deputy Director'),
        ('acknowledged', 'Acknowledged'),
    ], default='draft', tracking=True, string='Status')

    notes = fields.Text('Additional Notes')

    # -------------------------------------------------------------------------
    # Letters/Reports Document Attachments
    # -------------------------------------------------------------------------
    letter_report_document_upload_ids = fields.One2many(
        'ecdhs.contract.document.upload',
        'monitoring_id',
        string='Letters/Reports Documents',
        domain=[('document_type', '=', 'monitoring_letter_report')],
    )

    # =========================================================================
    # Computed
    # =========================================================================

    @api.depends('contract_id.name', 'monitoring_date')
    def _compute_display_name(self):
        for rec in self:
            if rec.contract_id and rec.monitoring_date:
                rec.display_name = '%s – %s' % (
                    rec.contract_id.name,
                    fields.Date.to_string(rec.monitoring_date),
                )
            elif rec.contract_id:
                rec.display_name = rec.contract_id.name
            else:
                rec.display_name = _('New')

    # =========================================================================
    # State transitions
    # =========================================================================

    def action_submit(self):
        """Submit report to Deputy Director; flag contract kanban if issues found."""
        self.write({'state': 'submitted'})
        for rec in self:
            if rec.non_compliance_found:
                rec.contract_id.kanban_state = 'blocked'
            if rec.termination_recommended:
                rec.contract_id.message_post(
                    body=_(
                        'Contract Review dated %s recommends termination of this contract '
                        'due to persistent non-performance.',
                        rec.monitoring_date,
                    )
                )

    def action_acknowledge(self):
        """Deputy Director acknowledges the report."""
        self.write({'state': 'acknowledged'})
