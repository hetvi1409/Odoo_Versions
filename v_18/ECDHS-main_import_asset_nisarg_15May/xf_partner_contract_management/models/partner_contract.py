# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PartnerContract(models.Model):
    """Partner Contract — ECDHS SOP-aligned workflow extension"""
    _inherit = 'xf.partner.contract'

    supplier_ids = fields.Many2many('res.partner', string="Supplier")
    memo_id = fields.Many2one('contract.memo', string="Memo")
    verified = fields.Selection([
        ('verified', 'Verified'),
        ('not_verified', 'Not Verified')], string='Verified',
        copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Verify Drafted Contract'),
        ('send_service', 'Sent to Service Provider'),
        ('provider_signed', 'Provider Signed'),
        ('review_amend', 'Review / Amend Contract'),
        ('verify_contract', 'Verify Contract'),
        ('send_for_betting', 'Send for Vetting'),
        ('recommend_by_deputy', 'Recommend By Deputy Director'),
        ('recommend_by_legal', 'Recommend By Legal Services Department'),
        ('approval', 'Approval'),
        ('sign', 'Signed the Contract'),
        ('onsite_meeting', 'Onsite Meeting'),
        ('running', 'Running'),
        ('to_renew', 'To Renew'),
        ('expired', 'Expired'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft',
        required=True, readonly=False, copy=False, tracking=True)
    amendments = fields.Char(string='Required Amendments')
    recommend_by_deputy = fields.Char(string='Recommend By Deputy Director')
    recommend_by_legal = fields.Char(
        string='Recommend By Legal Services Department')
    meeting_id = fields.Many2one('calendar.event', string='Meeting')

    monitoring_frequency = fields.Selection([
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly')],
        string='Monitoring Frequency',
        default='quarterly')

    last_monitoring_date = fields.Date('Last Monitoring Date')
    next_monitoring_date = fields.Date('Next Monitoring Date')

    monitoring_checklist_ids = fields.One2many(
        'contract.monitoring.checklist',
        'contract_id',
        string='Monitoring Checklist'
    )

    monitoring_report_ids = fields.One2many(
        'contract.monitoring.report',
        'contract_id',
        string='Monitoring Reports'
    )
    procurement_required = fields.Boolean(string="Procurement Required")
    provincial_treasury_approval = fields.Boolean(
        string='Provincial Treasury Approval Obtained',
        help='Required when variation exceeds SOP threshold.',
        copy=False,
    )

    # Amendment / version tracking (defined here to avoid cross-module One2many issue)
    amendment_ids = fields.One2many(
        'contract.amendment',
        'contract_id',
        string='Amendments',
        readonly=True,
    )
    amendment_count = fields.Integer(
        compute='_compute_amendment_count',
        string='Amendments',
    )
    current_version = fields.Integer(
        string='Version',
        default=1,
        readonly=True,
        copy=False,
    )

    # Signing fields (Odoo Sign integration — optional, guarded at runtime)
    sign_request_provider_id = fields.Many2one(
        'sign.request',
        string='Provider Sign Request',
        readonly=True,
        copy=False,
    )
    sign_request_internal_id = fields.Many2one(
        'sign.request',
        string='Internal Sign Request',
        readonly=True,
        copy=False,
    )
    provider_signed = fields.Boolean(
        string='Provider Signed',
        compute='_compute_sign_status',
        store=True,
    )
    internal_signed = fields.Boolean(
        string='Internally Signed',
        compute='_compute_sign_status',
        store=True,
    )

    @api.depends('amendment_ids')
    def _compute_amendment_count(self):
        for record in self:
            record.amendment_count = len(record.amendment_ids)

    @api.depends('sign_request_provider_id', 'sign_request_internal_id')
    def _compute_sign_status(self):
        for rec in self:
            try:
                rec.provider_signed = bool(
                    rec.sign_request_provider_id
                    and rec.sign_request_provider_id.state == 'signed'
                )
                rec.internal_signed = bool(
                    rec.sign_request_internal_id
                    and rec.sign_request_internal_id.state == 'signed'
                )
            except Exception:
                rec.provider_signed = False
                rec.internal_signed = False

    @api.constrains('variation_order_percentage', 'classification', 'provincial_treasury_approval')
    def _check_variation_threshold(self):
        """
        SOP rule:
        - up to 20% for construction-related goods/works,
        - up to 15% for other contracts,
        - above threshold requires Provincial Treasury approval.
        We map capital commitments to the 20% threshold.
        """
        for rec in self:
            if not rec.variation_order_percentage:
                continue
            threshold = 20.0 if rec.classification == 'capital_commitments' else 15.0
            if rec.variation_order_percentage > threshold and not rec.provincial_treasury_approval:
                raise UserError(_(
                    'Variation order percentage %(pct)s%% exceeds the SOP threshold of %(thr)s%%. '
                    'Capture Provincial Treasury approval before proceeding.'
                ) % {
                    'pct': rec.variation_order_percentage,
                    'thr': threshold,
                })

    def action_view_amendments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Amendments'),
            'res_model': 'contract.amendment',
            'view_mode': 'list,form',
            'domain': [('contract_id', '=', self.id)],
            'context': {'default_contract_id': self.id},
        }

    def action_view_tender(self):
        self.ensure_one()
        if not self.tender_id:
            return
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tender'),
            'res_model': 'sagovtender.tender',
            'view_mode': 'form',
            'res_id': self.tender_id.id,
            'target': 'current',
        }

    def action_view_sign_request(self):
        self.ensure_one()
        if not self.sign_request_provider_id:
            return
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sign Request'),
            'res_model': 'sign.request',
            'view_mode': 'form',
            'res_id': self.sign_request_provider_id.id,
            'target': 'current',
        }


    @api.model
    def _cron_generate_monitoring_reports(self):
        """Automatically generate monitoring reports based on frequency"""
        today = fields.Date.today()
        contracts = self.search([
            ('next_monitoring_date', '<=', today),
            ('state', '=', 'running'),
        ])
        for contract in contracts:
            contract._create_monitoring_report()

    def _create_monitoring_report(self):
        """Create a new monitoring report for the contract"""
        self.ensure_one()
        report = self.env['contract.monitoring.report'].create({
            'contract_id': self.id,
            'date': fields.Date.today(),
            'user_id': self.user_id.id or self.env.user.id,
        })

        # Set next monitoring date based on frequency
        if self.monitoring_frequency == 'weekly':
            next_date = fields.Date.add(fields.Date.today(), days=7)
        elif self.monitoring_frequency == 'monthly':
            next_date = fields.Date.add(fields.Date.today(), months=1)
        else:  # quarterly
            next_date = fields.Date.add(fields.Date.today(), months=3)

        self.write({
            'last_monitoring_date': fields.Date.today(),
            'next_monitoring_date': next_date
        })

    def view_memo_details(self):
        self.ensure_one()
        return {
            'name': _('Contract Memo'),
            'type': 'ir.actions.act_window',
            'res_model': 'contract.memo',
            'view_mode': 'form',
            'res_id': self.memo_id.id,
            'context': {'create': False},
        }

    def action_view_monitoring(self):
        self.ensure_one()
        reports = self.env['contract.monitoring.report'].search(
            [('contract_id', '=', self.id)])
        return {
            'name': _('Contract Monitoring'),
            'type': 'ir.actions.act_window',
            'res_model': 'contract.monitoring.report',
            'view_mode': 'list,form',
            'domain': [('id', 'in', reports.ids)],
            'context': {'default_contract_id': self.id},
        }

    def action_view_procurement(self):
        self.ensure_one()
        requests = self.env['contract.procurement.request'].search(
            [('contract_id', '=', self.id)])
        return {
            'name': _('Procurement Requests'),
            'type': 'ir.actions.act_window',
            'res_model': 'contract.procurement.request',
            'view_mode': 'list,form',
            'domain': [('id', 'in', requests.ids)],
            'context': {'default_contract_id': self.id},
        }

    # --- URL helper (Odoo v18 — werkzeug.urls removed) ---

    def get_list_url(self):
        """Direct URL to this contract for email templates."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        path = '/web#id=%s&model=xf.partner.contract&view_type=form' % self.id
        return urljoin(base_url, path)

    # --- SOP Workflow actions ---

    def action_verify(self):
        """Internal staff verify the drafted contract."""
        self.ensure_one()
        self.verified = 'verified'
        self.state = 'verify'
        template = self.env.ref(
            'xf_partner_contract_management.email_template_send_contract',
            raise_if_not_found=False)
        if template:
            template.send_mail(
                self.id, force_send=True,
                email_values={'recipient_ids': [(6, 0, self.partner_id.ids)]})
        self.message_post(body=_("Contract verified: %s") % self.name)

    def action_not_verify(self):
        """Mark contract not verified and notify partner."""
        self.ensure_one()
        self.verified = 'not_verified'
        template = self.env.ref(
            'xf_partner_contract_management.email_template_send_contract_not_verified',
            raise_if_not_found=False)
        if template:
            template.send_mail(
                self.id, force_send=True,
                email_values={'recipient_ids': [(6, 0, self.partner_id.ids)]})
        self.message_post(body=_("Contract not verified: %s") % self.name)

    def action_send_verified_mail(self):
        """Send verified contract to supplier(s) and advance state."""
        self.ensure_one()
        template = self.env.ref(
            'xf_partner_contract_management.email_template_send_contract',
            raise_if_not_found=False)
        if template and self.supplier_ids:
            template.send_mail(
                self.id, force_send=True,
                email_values={'recipient_ids': [(6, 0, self.supplier_ids.ids)]})
        self.state = 'send_service'

    def action_send_for_provider_signing(self):
        """
        Generate a sign.request for the service provider (Phase D).
        Gracefully degrades to manual tracking if Odoo Sign is unavailable.
        SOP requirement: provider must sign before any internal signing.
        """
        self.ensure_one()
        SignRequest = self.env.get('sign.request')
        SignTemplate = self.env.get('sign.request.template')
        if SignRequest is not None and SignTemplate is not None:
            sign_template = SignTemplate.search(
                [('name', 'ilike', 'contract')], limit=1)
            if sign_template:
                req = SignRequest.create({
                    'template_id': sign_template.id,
                    'reference': self.ref or self.name,
                    'request_item_ids': [(0, 0, {
                        'partner_id': self.partner_id.id,
                        'role_id': (
                            sign_template.sign_item_ids[:1].responsible_id.id
                            if sign_template.sign_item_ids else False
                        ),
                    })],
                })
                self.sign_request_provider_id = req.id
                req.action_sent(
                    subject=_('Please sign: %s') % self.name,
                    message=_('Dear %s, please review and sign the attached contract.')
                    % self.partner_id.name,
                )
        self.state = 'send_service'
        self.message_post(
            body=_("Contract sent to service provider for signing."))

    def action_provider_signed(self):
        """Manual trigger: service provider has signed."""
        self.ensure_one()
        self.state = 'provider_signed'
        self.message_post(
            body=_("Service provider has signed the contract."))

    def action_send_for_internal_signing(self):
        """
        Forward to internal signing chain.
        Blocked unless provider has signed (SOP constraint).
        """
        self.ensure_one()
        if not self.provider_signed:
            raise UserError(
                _('The service provider must sign the contract before internal '
                  'signing can proceed. Use "Send for Provider Signing" first.'))
        self.state = 'sign'
        self.message_post(
            body=_("Contract forwarded for internal signing."))

    def action_review(self):
        """Initiate review/amend loop after provider feedback."""
        self.ensure_one()
        if not self.amendments:
            raise UserError(
                _('Please capture the required amendments before proceeding.'))
        template = self.env.ref(
            'xf_partner_contract_management.email_template_send_contract_amend_created',
            raise_if_not_found=False)
        if template and self.supplier_ids:
            template.send_mail(
                self.id, force_send=True,
                email_values={'recipient_ids': [(6, 0, self.supplier_ids.ids)]})
        self.state = 'review_amend'

    def action_verify_amend(self):
        """Accept amendments — move to Verify Contract."""
        self.ensure_one()
        self.state = 'verify_contract'

    def action_send_betting(self):
        """Send contract for legal vetting."""
        self.ensure_one()
        self.state = 'send_for_betting'
        template = self.env.ref(
            'xf_partner_contract_management.email_template_send_contract_send_for_betting',
            raise_if_not_found=False)
        if template:
            deputy_group = self.env.ref(
                'xf_partner_contract_management.group_xf_partner_contract_deputy',
                raise_if_not_found=False)
            if deputy_group:
                partners = deputy_group.users.mapped('partner_id').ids
                template.send_mail(
                    self.id, force_send=True,
                    email_values={'recipient_ids': [(6, 0, partners)]})

    def action_recommend_by_deputy(self):
        """Deputy Director recommendation."""
        self.ensure_one()
        if not self.recommend_by_deputy:
            raise UserError(
                _('Please capture the Deputy Director recommendation.'))
        self.state = 'recommend_by_deputy'

    def action_recommend_by_legal(self):
        """Legal Services Department recommendation."""
        self.ensure_one()
        if not self.recommend_by_legal:
            raise UserError(
                _('Please capture the Legal Services Department recommendation.'))
        self.state = 'recommend_by_legal'

    def action_approve(self):
        """
        Move to Approval stage.
        Contracts >= R500 000 require a legal recommendation per SOP.
        """
        self.ensure_one()
        if self.amount >= 500000 and not self.recommend_by_legal:
            raise UserError(
                _('Contracts of R500 000 or more require a Legal Services '
                  'Department recommendation before approval.'))
        self.state = 'approval'

    def action_sign_contract(self):
        """All internal parties have signed — record signature."""
        self.ensure_one()
        self.state = 'sign'

    def action_create_meeting(self):
        """Create on-site meeting and activate the contract."""
        self.ensure_one()
        meeting = self.env['calendar.event'].create({
            'name': _('Onsite Meeting — %s') % self.name,
            'start': fields.Datetime.now(),
            'stop': fields.Datetime.now(),
        })
        self.meeting_id = meeting.id
        self.state = 'running'
        self.message_post(
            body=_("Onsite meeting created: %s") % self.name)

    @api.model
    def _cron_notify_expiring_contracts(self):
        """SOP step 23: issue monthly notice for contracts expiring in next 6 months."""
        today = fields.Date.today()
        limit_date = fields.Date.add(today, months=6)
        contracts = self.search([
            ('state', 'in', ['running', 'to_renew']),
            ('date_end', '>=', today),
            ('date_end', '<=', limit_date),
        ])
        template = self.env.ref(
            'xf_partner_contract_management.email_template_contract_expiry_notice',
            raise_if_not_found=False,
        )
        for contract in contracts:
            if template:
                template.send_mail(contract.id, force_send=True)
            if contract.user_id:
                contract.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=_('Contract expiring within 6 months'),
                    note=_('Please complete the SOP expiry checklist and initiate procurement if required.'),
                    user_id=contract.user_id.id,
                )
            contract.message_post(
                body=_('Expiry notice generated: contract ends on %s.') % contract.date_end
            )

    def action_initiate_procurement(self):
        """Open procurement request form."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Procurement Request'),
            'res_model': 'contract.procurement.request',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_contract_id': self.id},
        }

