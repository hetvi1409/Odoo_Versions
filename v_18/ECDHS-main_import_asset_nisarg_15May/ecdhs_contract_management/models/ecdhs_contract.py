# -*- coding: utf-8 -*-
# Eastern Cape Department of Human Settlements
# Contract Management – Main Contract Model

import base64
import io
import logging
import uuid

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

_CHATTER_GREEN_BOX_STYLE = (
    'background-color:#dcefe0;'
    'border:1px solid #b8d8bf;'
    'border-radius:8px;'
    'padding:18px 20px;'
    'color:#2f3b4a;'
)


def _get_pdf_tools():
    try:
        from pypdf import PdfReader, PdfWriter
        return PdfReader, PdfWriter
    except ImportError:
        pass
    try:
        from PyPDF2 import PdfReader, PdfWriter
        return PdfReader, PdfWriter
    except ImportError:
        return None, None


class EcdhsContract(models.Model):
    _name = 'ecdhs.contract'
    _description = 'Procurement Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'contract_date desc, name desc'
    _mail_post_access = 'read'

    # -------------------------------------------------------------------------
    # Identity & Classification
    # -------------------------------------------------------------------------
    name = fields.Char(
        'Contract Reference',
        required=True, copy=False, readonly=True,
        default=lambda self: _('New'),
        tracking=True,
    )
    subject = fields.Char(
        'Contract Subject / Service Description',
        required=True, tracking=True,
    )
    memo_id = fields.Many2one(
        'memo.memo',
        string='Memo Link',
        tracking=True,
        ondelete='set null',
        help='Links this contract to a memo record.',
    )
    contract_type = fields.Selection([
        ('funding_agreement', 'Funding Agreement (Municipalities)'),
        ('funding_agreement_service_provider', 'Funding Agreement (Service Provider)'),
        ('sla', 'Service Level Agreement (SLA)'),
        ('mou', 'Memorandum of Understanding (MOU)'),
        ('cession', 'Cession'),
    ], string='Contract Type', required=True, default='funding_agreement', tracking=True)
    bid_reference = fields.Char(
        'Bid Reference No.',
        help='Reference number of the bid or tender that resulted in this contract.',
    )
    scmu_number = fields.Char(
        'SCMU No.',
        help='Supply Chain Management Unit reference number.',
    )
    contract_date = fields.Date(
        'Creation Date',
        default=fields.Date.today, tracking=True,
    )
    active = fields.Boolean(default=True)

    # -------------------------------------------------------------------------
    # Parties
    # -------------------------------------------------------------------------
    service_provider_id = fields.Many2one(
        'res.partner', string='Service Provider',
        required=True, tracking=True,
        help='The supplier or company awarded this contract.',
    )
    service_provider_contact = fields.Char(
        'Service Provider Contact Details',
        help='Physical address and key contact for this service provider.',
    )
    end_user_department_id = fields.Many2one(
        'hr.department', string='End-User Department', tracking=True,
    )
    end_user_id = fields.Many2one(
        'res.users', string='End-User Representative', tracking=True,
    )

    # -------------------------------------------------------------------------
    # Contract Period
    # -------------------------------------------------------------------------
    CONTRACT_PERIOD_SELECTION = [
        ('6', '6 Months'),
        ('12', '12 Months (1 Year)'),
        ('18', '18 Months'),
        ('24', '24 Months (2 Years)'),
        ('30', '30 Months'),
        ('36', '36 Months (3 Years)'),
        ('42', '42 Months'),
        ('48', '48 Months (4 Years)'),
        ('54', '54 Months'),
        ('60', '60 Months (5 Years)'),
        ('66', '66 Months'),
        ('72', '72 Months (6 Years)'),
    ]

    date_start = fields.Date('Contract Start Date', required=True, tracking=True)
    date_end = fields.Date('Contract End Date', tracking=True)
    contract_period_months = fields.Selection(
        selection=CONTRACT_PERIOD_SELECTION,
        string='Contract Period',
        default='12',
        tracking=True,
    )
    is_indefinite = fields.Boolean(
        'No Fixed End Date',
        help='Tick if this contract has no fixed expiry date (e.g. ongoing lease).',
    )
    days_to_expiry = fields.Integer(
        'Days to Expiry',
        compute='_compute_days_to_expiry', store=False,
    )

    # -------------------------------------------------------------------------
    # Financial
    # -------------------------------------------------------------------------
    company_id = fields.Many2one(
        'res.company', string='Region',
        default=lambda self: self.env.company, required=True,
    )
    municipality_id = fields.Many2one(
        'res.municipality', string='Municipality',
    )
    region_id = fields.Many2one(
        'res.region', string='Region', compute='_compute_region_id', store=True, readonly=True,
    )
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', readonly=True,
    )
    contract_value = fields.Monetary(
        'Total Contract Value', tracking=True,
        help='Total rand value of the contract as awarded.',
    )
    original_contract_value = fields.Monetary(
        'Original Contract Value', tracking=True, copy=False,
        help='Baseline awarded contract value before deductions from paid payment verifications.',
    )
    annual_value = fields.Monetary(
        'Annual Value', tracking=True,
        help='Annualised cost to the department.',
    )
    budget_account = fields.Char(
        'Budget Vote / Vote Number',
        help='Budget vote or accounting classification for contract expenditure.',
    )
    requires_delegated_approval = fields.Boolean(
        'Requires Delegated Official Approval (> R500 000)',
        compute='_compute_requires_delegated_approval', store=True,
        help='Contracts above R500,000 require a Delegated Official to approve per PFMA.',
    )

    # -------------------------------------------------------------------------
    # Bid Documentation Checklist  –  SOP Steps 1-2
    # -------------------------------------------------------------------------
    bid_spec_attached = fields.Boolean(
        'Bid Specification Attached', tracking=True,
    )
    ecbd4_attached = fields.Boolean(
        'Approved Budget (ECBD4 Form) Attached', tracking=True,
    )
    tax_clearance_valid = fields.Boolean(
        'Tax Clearance Certificate Valid', tracking=True,
    )
    company_documents_obtained = fields.Boolean(
        'Company / CSD Registration Documents Obtained', tracking=True,
    )
    all_documents_verified = fields.Boolean(
        'All Supporting Documents Verified',
        tracking=True, readonly=True, copy=False,
    )

    # -------------------------------------------------------------------------
    # Responsible Officials
    # -------------------------------------------------------------------------
    admin_officer_id = fields.Many2one(
        'res.users', string='Admin Officer (CM)', tracking=True,
        default=lambda self: self.env.user,
    )
    assistant_director_id = fields.Many2one(
        'res.users', string='Assistant Director (CM)', tracking=True,
    )
    deputy_director_id = fields.Many2one(
        'res.users', string='Deputy Director (CM)', tracking=True,
    )
    legal_reviewer_id = fields.Many2one(
        'res.users', string='Reviewer/Quality Assurer', tracking=True,
    )
    cfo_id = fields.Many2one(
        'res.users', string='CFO', tracking=True,
    )
    delegated_official_id = fields.Many2one(
        'res.users', string='Delegated Official', tracking=True,
        help='Required for contracts above R500,000 per PFMA delegation framework.',
    )

    # -------------------------------------------------------------------------
    # Contract Document Governance (Drafting, Compliance, Signature)
    # -------------------------------------------------------------------------
    procurement_method = fields.Selection([
        ('open_tender', 'Open Tender'),
        ('rfq', 'Request for Quotation (RFQ)'),
        ('transversal', 'Transversal Contract'),
        ('deviation', 'Approved Deviation / Sole Source'),
        ('other', 'Other'),
    ], string='Procurement Method', tracking=True)
    preference_point_system = fields.Selection([
        ('80_20', '80/20'),
        ('90_10', '90/10'),
        ('na', 'Not Applicable'),
    ], string='Preference Point System', tracking=True)
    bbbee_level = fields.Char(
        'BBBEE Contributor Level',
        tracking=True,
        help='Record bidder BBBEE level used during evaluation and award verification.',
    )
    delegated_authority_ref = fields.Char(
        'Delegated Authority Reference',
        tracking=True,
        help='Reference to delegated authority instrument used for approval.',
    )
    treasury_instruction_ref = fields.Char(
        'Treasury Instruction / Circular Reference',
        tracking=True,
        help='Applicable National/Provincial instruction notes, circulars, or practice notes.',
    )
    contract_terms_summary = fields.Html(
        'Draft Contract Terms and Working Arrangements',
        help='Core obligations, service levels, deliverables, penalties, and responsibilities.',
    )
    contract_template_id = fields.Many2one(
        'ecdhs.contract.template',
        string='Contract Template',
        domain=[('is_addendum', '=', False)],
        tracking=True,
        help='Selecting a template overwrites Draft Contract Terms with the template body.',
    )
    provider_access_token = fields.Char(
        'Provider Access Token', copy=False, readonly=True,
        help='Unique token embedded in the portal URL sent to the service provider.',
    )

    constitution_s217_checked = fields.Boolean(
        'Constitution Section 217 Considered',
        tracking=True,
        help='Fair, equitable, transparent, competitive and cost-effective procurement confirmed.',
    )
    pfma_checked = fields.Boolean('PFMA Compliance Confirmed', tracking=True)
    pppfa_checked = fields.Boolean('PPPFA / PPPFA Regulations Compliance Confirmed', tracking=True)
    bbbee_checked = fields.Boolean('BBBEE Compliance Confirmed', tracking=True)
    public_admin_act_checked = fields.Boolean('Public Administration Act Compliance Confirmed', tracking=True)
    paia_checked = fields.Boolean('PAIA Record-Keeping and Access Controls Confirmed', tracking=True)
    treasury_regulations_checked = fields.Boolean('Treasury Regulations Compliance Confirmed', tracking=True)
    practice_notes_checked = fields.Boolean('Applicable Practice/Instruction Notes Confirmed', tracking=True)

    compiled_by_id = fields.Many2one('res.users', string='Compiled By', tracking=True)
    compiled_date = fields.Date('Compiled Date', tracking=True)
    recommended_by_id = fields.Many2one('res.users', string='Recommended By', tracking=True)
    recommended_date = fields.Date('Recommended Date', tracking=True)
    supported_by_id = fields.Many2one('res.users', string='Supported By', tracking=True)
    supported_date = fields.Date('Supported Date', tracking=True)

    signatory_ids = fields.One2many(
        'ecdhs.contract.signatory', 'contract_id', string='Signatories')
    annexure_document_upload_ids = fields.One2many(
        'ecdhs.contract.document.upload',
        'contract_id',
        string='Annexures / Appendices',
        domain=[('document_type', '=', 'annexure')],
        copy=False,
    )
    supporting_document_upload_ids = fields.One2many(
        'ecdhs.contract.document.upload',
        'contract_id',
        string='Supporting Documents',
        domain=[('document_type', '=', 'supporting')],
        copy=False,
    )
    verify_without_annexures_confirmed = fields.Boolean(
        string='Proceed Without Annexures Confirmed',
        copy=False,
        default=False,
    )
    verify_without_supporting_confirmed = fields.Boolean(
        string='Proceed Without Supporting Documents Confirmed',
        copy=False,
        default=False,
    )
    verify_without_jbcc_confirmed = fields.Boolean(
        string='Proceed Without JBCC Confirmed',
        copy=False,
        default=False,
    )
    verify_without_gcc_confirmed = fields.Boolean(
        string='Proceed Without GCC Confirmed',
        copy=False,
        default=False,
    )
    jbcc_required = fields.Boolean('JBCC Required', tracking=True, copy=False)
    gcc_required = fields.Boolean('GCC Required', tracking=True, copy=False)
    jbcc_upload_file = fields.Binary('JBCC Upload', attachment=True, copy=False)
    jbcc_upload_filename = fields.Char('JBCC Upload Filename', copy=False)
    gcc_upload_file = fields.Binary('GCC Upload', attachment=True, copy=False)
    gcc_upload_filename = fields.Char('GCC Upload Filename', copy=False)

    # -------------------------------------------------------------------------
    # Digital Signature (sign module integration)
    # -------------------------------------------------------------------------
    sign_template_id = fields.Many2one(
        'sign.template',
        string='Signing Template',
        copy=False,
        help='The sign.template created for the current signing ceremony.',
    )
    sign_request_id = fields.Many2one(
        'sign.request',
        string='Signed Contract',
        copy=False,
        help='Active or last-completed digital signature request for this contract.',
    )
    signed_document_attachment_id = fields.Many2one(
        'ir.attachment',
        string='Signed Contract Document',
        ondelete='set null',
        readonly=True,
        copy=False,
        help='The counter-signed PDF produced once all parties have signed.',
    )
    provider_signed_document_attachment_id = fields.Many2one(
        'ir.attachment',
        string='Provider Signed Contract Document',
        ondelete='set null',
        readonly=True,
        copy=False,
        help='Snapshot of the signed PDF from the provider signing ceremony (before HOD cover-letter signing).',
    )
    draft_watermarked_attachment_id = fields.Many2one(
        'ir.attachment',
        string='Draft Watermarked Document',
        ondelete='set null',
        readonly=True,
        copy=False,
        help='Watermarked draft PDF used for Draft Versions folder filing.',
    )

    # -------------------------------------------------------------------------
    # Workflow State
    # -------------------------------------------------------------------------
    state = fields.Selection([
        ('draft', 'New Draft'),
        ('contract_drafted', 'Contract Drafted'),
        ('verified', 'Documents Verified'),
        ('legal_review', 'Vetting'),
        ('change_requested', 'Request Changes'),
        ('changes_requested', 'Changes Requested'),
        ('approved', 'Vetting Approved'),
        ('legal_vetting_declined', 'Vetting Declined'),
        ('provider_review_sent', 'Draft Sent to Provider'),
        ('provider_changes_requested', 'Provider Changes Requested'),
        ('provider_rejected', 'Provider Rejected Draft'),
        ('provider_accepted', 'Provider Accepted Draft'),
        ('signing', 'Awaiting Provider Signature'),
        ('fully_signed', 'Provider Fully Signed'),
        ('signature_refused', 'Signature Refused'),
        ('cover_letter_sent', 'Send Contract Cover Letter to HOD'),
        ('cover_letter_signed', 'Contract Cover Letter Signed'),
        ('cover_letter_rejected', 'Contract Cover Letter Rejected'),
        ('active', 'Active'),
        ('expiring', 'Due for Renewal'),
        ('terminated', 'Terminated'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, copy=False,
       group_expand='_expand_states')

    kanban_state = fields.Selection([
        ('normal', 'On Track'),
        ('done', 'Ready for Next Stage'),
        ('blocked', 'Action Required'),
    ], string='Progress', default='normal', tracking=True, copy=False)

    # -------------------------------------------------------------------------
    # Related records
    # -------------------------------------------------------------------------
    addendum_ids = fields.One2many(
        'ecdhs.contract.addendum', 'contract_id', string='Addenda',
    )
    addendum_count = fields.Integer(compute='_compute_counts', string='# Addenda')

    payment_ids = fields.One2many(
        'ecdhs.contract.payment', 'contract_id', string='Payment Verifications',
    )
    payment_count = fields.Integer(compute='_compute_counts', string='# Payments')

    monitoring_ids = fields.One2many(
        'ecdhs.contract.monitoring', 'contract_id', string='Contract Reviews',
    )
    monitoring_count = fields.Integer(compute='_compute_counts', string='# Reviews')

    clause_ids = fields.One2many(
        'ecdhs.contract.clause', 'contract_id', string='Mandatory Clauses',
    )
    mandatory_clause_ok = fields.Boolean(
        string='All Mandatory Clauses Confirmed',
        compute='_compute_mandatory_clause_ok',
    )
    contract_cover_sheet_html = fields.Html(
        string='Contract Cover Sheet',
        compute='_compute_contract_cover_sheet_html',
        sanitize=False,
    )

    provider_review_state = fields.Selection([
        ('not_sent', 'Not Sent to Provider'),
        ('sent_for_review', 'Sent to Provider for Review'),
        ('provider_changes_requested', 'Provider Requested Changes'),
        ('revised_sent', 'Revised Draft Sent'),
        ('provider_accepted', 'Provider Accepted Draft'),
        ('provider_rejected', 'Provider Rejected Draft'),
    ], string='Provider Collaboration Status', default='not_sent', tracking=True, copy=False)
    provider_review_due_date = fields.Date('Provider Review Due Date', tracking=True)
    provider_last_sent_datetime = fields.Datetime('Last Draft Sent To Provider', tracking=True, copy=False)
    provider_last_response_datetime = fields.Datetime('Last Provider Response', tracking=True, copy=False)
    provider_last_reminder_date = fields.Date('Last Provider Reminder Date', copy=False)
    draft_version = fields.Integer('Draft Version', default=1, tracking=True, copy=False)
    draft_revision_count = fields.Integer('Draft Revision Count', default=0, tracking=True, copy=False)
    provider_acceptance_note = fields.Text('Provider Acceptance Note')
    provider_acceptance_datetime = fields.Datetime('Provider Acceptance Datetime', copy=False)
    provider_review_url = fields.Char(
        'Provider Review Link',
        compute='_compute_provider_review_url',
    )
    finance_link = fields.Char(string="Finance System Reference Link",
        help='Link to the finance system or portal for this payment verification.',
    )

    change_request_ids = fields.One2many(
        'ecdhs.contract.change.request', 'contract_id', string='Provider Change Requests',
    )
    change_request_count = fields.Integer(
        string='# Change Requests',
        compute='_compute_counts',
    )
    version_ids = fields.One2many(
        'ecdhs.contract.version', 'contract_id', string='Versions',
    )
    version_count = fields.Integer(
        string='# Versions',
        compute='_compute_counts',
    )

    signature_section_ids = fields.One2many(
        'ecdhs.contract.signature.section', 'contract_id', string='Section Signatures',
    )
    all_required_signatures_done = fields.Boolean(
        string='All Required Section Signatures Completed',
        compute='_compute_all_required_signatures_done',
    )

    # -------------------------------------------------------------------------
    # Termination tracking
    # -------------------------------------------------------------------------
    termination_date = fields.Date('Termination Date', tracking=True, copy=False)
    termination_reason = fields.Text('Termination Reason', copy=False)

    # -------------------------------------------------------------------------
    # Document Filing System
    # -------------------------------------------------------------------------
    folder_id = fields.Many2one(
        'documents.document',
        string='Document Folder',
        readonly=True,
        domain="[('type', '=', 'folder')]",
        help='Hierarchical folder structure for contract documents, automatically created and managed.'
    )
    contract_reference_folder_id = fields.Many2one(
        'documents.document',
        string='Contract Reference Folder',
        readonly=True,
        copy=False,
        domain="[('type', '=', 'folder')]",
        help='Internal folder used to store the contract-specific filing structure.'
    )

    # -------------------------------------------------------------------------
    # Internal notes & cron tracking
    # -------------------------------------------------------------------------
    notes = fields.Html('Internal Notes')
    expiry_notice_sent = fields.Boolean(
        'Expiry Notice Sent', copy=False,
        help='Set automatically by the monthly cron once a 6-month expiry notice has been issued.',
    )

    # =========================================================================
    # Computed methods
    # =========================================================================

    @api.depends('contract_value')
    def _compute_requires_delegated_approval(self):
        for contract in self:
            comparison_value = contract.original_contract_value or contract.contract_value or 0.0
            contract.requires_delegated_approval = comparison_value > 500_000.0

    @api.depends('date_end', 'is_indefinite')
    def _compute_days_to_expiry(self):
        today = fields.Date.today()
        for contract in self:
            if contract.is_indefinite or not contract.date_end:
                contract.days_to_expiry = 0
            else:
                contract.days_to_expiry = (contract.date_end - today).days

    @api.onchange('municipality_id')
    def _onchange_municipality_id(self):
        for rec in self:
            rec.region_id = rec.municipality_id.region_id

    @api.depends('municipality_id', 'municipality_id.region_id')
    def _compute_region_id(self):
        for rec in self:
            rec.region_id = rec.municipality_id.region_id

    @api.onchange('date_start', 'contract_period_months', 'is_indefinite')
    def _onchange_contract_period_months(self):
        for contract in self:
            if contract.is_indefinite:
                contract.date_end = False
                continue
            if contract.date_start and contract.contract_period_months:
                period_months = int(contract.contract_period_months)
                contract.date_end = contract.date_start + relativedelta(months=period_months)

    @api.depends('addendum_ids', 'payment_ids', 'monitoring_ids', 'change_request_ids', 'version_ids')
    def _compute_counts(self):
        for contract in self:
            contract.addendum_count = len(contract.addendum_ids)
            contract.payment_count = len(contract.payment_ids)
            contract.monitoring_count = len(contract.monitoring_ids)
            contract.change_request_count = len(contract.change_request_ids)
            contract.version_count = len(contract.version_ids)

    @api.depends('clause_ids.required', 'clause_ids.confirmed')
    def _compute_mandatory_clause_ok(self):
        for contract in self:
            required_lines = contract.clause_ids.filtered(lambda l: l.required)
            contract.mandatory_clause_ok = bool(required_lines) and all(required_lines.mapped('confirmed'))

    @api.depends(
        'name', 'subject', 'contract_type', 'service_provider_id', 'bid_reference',
        'contract_date', 'date_start', 'date_end', 'is_indefinite', 'contract_value',
        'original_contract_value',
        'procurement_method', 'preference_point_system', 'bbbee_level',
        'admin_officer_id', 'assistant_director_id', 'deputy_director_id',
    )
    def _compute_contract_cover_sheet_html(self):
        for contract in self:
            end_date = 'Indefinite' if contract.is_indefinite else (fields.Date.to_string(contract.date_end) or '-')
            start_date = fields.Date.to_string(contract.date_start) if contract.date_start else '-'
            contract_date = fields.Date.to_string(contract.contract_date) if contract.contract_date else '-'
            contract.contract_cover_sheet_html = """
                <div class="p-2">
                    <h3>Contract Cover Sheet</h3>
                    <table class="table table-sm table-bordered" style="width:100%%; border-collapse: collapse;">
                        <tr><td><strong>Contract Reference</strong></td><td>%s</td></tr>
                        <tr><td><strong>Subject</strong></td><td>%s</td></tr>
                        <tr><td><strong>Contract Type</strong></td><td>%s</td></tr>
                        <tr><td><strong>Service Provider</strong></td><td>%s</td></tr>
                        <tr><td><strong>Bid / Tender Ref</strong></td><td>%s</td></tr>
                        <tr><td><strong>Contract Date</strong></td><td>%s</td></tr>
                        <tr><td><strong>Start Date</strong></td><td>%s</td></tr>
                        <tr><td><strong>End Date</strong></td><td>%s</td></tr>
                        <tr><td><strong>Total Contract Value</strong></td><td>%s %s</td></tr>
                        <tr><td><strong>Remaining Contract Balance</strong></td><td>%s %s</td></tr>
                        <tr><td><strong>Procurement Method</strong></td><td>%s</td></tr>
                        <tr><td><strong>Preference Points</strong></td><td>%s</td></tr>
                        <tr><td><strong>BBBEE Level</strong></td><td>%s</td></tr>
                        <tr><td><strong>Compiled By</strong></td><td>%s</td></tr>
                        <tr><td><strong>Recommended By</strong></td><td>%s</td></tr>
                        <tr><td><strong>Supported By</strong></td><td>%s</td></tr>
                    </table>
                </div>
            """ % (
                contract.name or '-',
                contract.subject or '-',
                dict(contract._fields['contract_type'].selection).get(contract.contract_type, '-') if contract.contract_type else '-',
                contract.service_provider_id.display_name or '-',
                contract.bid_reference or '-',
                contract_date,
                start_date,
                end_date,
                contract.currency_id.symbol or '',
                '{:,.2f}'.format(contract.original_contract_value or contract.contract_value or 0.0),
                contract.currency_id.symbol or '',
                '{:,.2f}'.format(contract.contract_value or 0.0),
                dict(contract._fields['procurement_method'].selection).get(contract.procurement_method, '-') if contract.procurement_method else '-',
                dict(contract._fields['preference_point_system'].selection).get(contract.preference_point_system, '-') if contract.preference_point_system else '-',
                contract.bbbee_level or '-',
                contract.compiled_by_id.display_name or '-',
                contract.recommended_by_id.display_name or '-',
                contract.supported_by_id.display_name or '-',
            )

    def _sync_remaining_contract_value(self):
        for contract in self:
            paid_total = sum(contract.payment_ids.filtered(lambda payment: payment.state == 'paid').mapped('invoice_amount'))
            baseline = contract.original_contract_value
            updates = {}

            if baseline in (False, None):
                baseline = (contract.contract_value or 0.0) + paid_total
                updates['original_contract_value'] = baseline

            remaining_value = baseline - paid_total
            if contract.contract_value != remaining_value:
                updates['contract_value'] = remaining_value

            if updates:
                contract.with_context(
                    skip_original_contract_value_sync=True,
                    skip_remaining_contract_value_sync=True,
                ).write(updates)

    @api.depends('provider_access_token')
    def _compute_provider_review_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='').rstrip('/')
        for contract in self:
            if not contract.id:
                contract.provider_review_url = ''
                continue
            if not contract.provider_access_token:
                # Auto-generate token for contracts that pre-date this feature
                token = uuid.uuid4().hex
                contract.sudo().write({'provider_access_token': token})
            else:
                token = contract.provider_access_token
            contract.provider_review_url = '%s/contract/review/%s/%s' % (base_url, contract.id, token)

    @api.depends(
        'signature_section_ids.provider_signature_required',
        'signature_section_ids.provider_signed',
        'signature_section_ids.internal_signature_required',
        'signature_section_ids.internal_signed',
    )
    def _compute_all_required_signatures_done(self):
        for contract in self:
            required_sections = contract.signature_section_ids.filtered(
                lambda s: s.provider_signature_required or s.internal_signature_required
            )
            if not required_sections:
                contract.all_required_signatures_done = False
                continue
            provider_ok = all(
                s.provider_signed for s in required_sections if s.provider_signature_required
            )
            internal_ok = all(
                s.internal_signed for s in required_sections if s.internal_signature_required
            )
            contract.all_required_signatures_done = provider_ok and internal_ok

    @api.model
    def _default_clause_values(self):
        return [
            {
                'sequence': 10,
                'name': 'Constitution S217 Procurement Principle Clause',
                'legislative_reference': 'Constitution of the Republic of South Africa, 1996, Section 217',
            },
            {
                'sequence': 20,
                'name': 'PFMA Financial Governance and Accountability Clause',
                'legislative_reference': 'Public Finance Management Act, No. 1 of 1999',
            },
            {
                'sequence': 30,
                'name': 'PPPFA Preference Point and Award Criteria Clause',
                'legislative_reference': 'PPPFA and PPPFA Regulations, 2017',
            },
            {
                'sequence': 40,
                'name': 'BBBEE Compliance and Verification Clause',
                'legislative_reference': 'Broad-Based Black Economic Empowerment Act',
            },
            {
                'sequence': 50,
                'name': 'PAIA Records Access and Retention Clause',
                'legislative_reference': 'Promotion of Access to Information Act (PAIA)',
            },
            {
                'sequence': 60,
                'name': 'Treasury Regulations and Practice Notes Clause',
                'legislative_reference': 'National / Provincial Treasury Regulations, Practice Notes and Circulars',
            },
            {
                'sequence': 70,
                'name': 'Monitoring, Audit and Reporting Clause',
                'legislative_reference': 'Contract Management Policy Framework 2025/26; SPF GPG Contract Lifecycle',
            },
            {
                'sequence': 80,
                'name': 'Close-out, Handover and Lessons Learned Clause',
                'legislative_reference': 'SPF Good Practice Guide - Contract Lifecycle Management',
            },
        ]

    @api.model
    def _default_signature_section_values(self):
        return [
            {'sequence': 10, 'name': 'Scope of Work and Deliverables', 'section_reference': 'Section A'},
            {'sequence': 20, 'name': 'Pricing and Payment Terms', 'section_reference': 'Section B'},
            {'sequence': 30, 'name': 'SLA, Monitoring and Penalties', 'section_reference': 'Section C'},
            {'sequence': 40, 'name': 'Confidentiality and PAIA', 'section_reference': 'Section D'},
            {'sequence': 50, 'name': 'Execution / Signature Block', 'section_reference': 'Section E'},
        ]

    def _send_provider_template(self, xml_id):
        self.ensure_one()
        if not self.service_provider_id.email:
            raise UserError(_('Service Provider email address is required before sending outbound provider emails.'))
        template = self.env.ref(xml_id, raise_if_not_found=False)
        if not template:
            raise UserError(_('Email template %s is missing.', xml_id))
        template.send_mail(self.id, force_send=True)

    def _send_internal_template(self, xml_id):
        """Send internal workflow template (no hard stop if recipient email is missing)."""
        self.ensure_one()
        template = self.env.ref(xml_id, raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)

    def _send_email_to_recipients(self, subject, body_html, emails):
        self.ensure_one()
        clean_emails = sorted({(email or '').strip() for email in emails if email})
        if not clean_emails:
            return
        normalized_body = (body_html or '').strip()
        if 'data-ecdhs-green-mail="1"' not in normalized_body:
            normalized_body = (
                '<div data-ecdhs-green-mail="1" style="%s">%s</div>'
                % (_CHATTER_GREEN_BOX_STYLE, normalized_body)
            )
        mail_vals = {
            'subject': subject,
            'body_html': normalized_body,
            'email_to': ','.join(clean_emails),
            'email_from': self.env.user.email_formatted or self.company_id.email_formatted,
            'auto_delete': True,
        }
        self.env['mail.mail'].sudo().create(mail_vals).send()

    def _get_contract_team_emails(self):
        """Resolve contract-team recipients from configured security groups."""
        self.ensure_one()
        group_xml_ids = [
            'ecdhs_contract_management.group_contract_manager',
            'ecdhs_contract_management.group_contract_officer',
            'ecdhs_contract_management.group_contract_user',
        ]
        users = self.env['res.users']
        for xml_id in group_xml_ids:
            group = self.env.ref(xml_id, raise_if_not_found=False)
            if group:
                users |= group.users

        # Prefer partner emails but also include user login emails as fallback.
        email_candidates = list(users.mapped('partner_id.email')) + list(users.mapped('email'))
        return sorted({(email or '').strip() for email in email_candidates if email})

    def _notify_contract_team_memo_required(self):
        self.ensure_one()
        if self.memo_id:
            return

        recipient_emails = self._get_contract_team_emails()
        if recipient_emails:
            template = self.env.ref(
                'ecdhs_contract_management.mail_template_contract_memo_required',
                raise_if_not_found=False,
            )
            if template:
                template.send_mail(
                    self.id,
                    force_send=True,
                    email_values={'email_to': ','.join(recipient_emails)},
                )
            else:
                subject = _('Memo Required for Contract Cover Letter - %s', self.name)
                body_html = _(
                    '<p>Dear Contract Team,</p>'
                    '<p>Contract <strong>%(contract)s</strong> is now fully signed by the provider but has no linked memo.</p>'
                    '<p>Please create and link a memo to this contract so the Contract Cover Letter can be sent to HOD.</p>',
                    contract=self.name,
                )
                self._send_email_to_recipients(subject=subject, body_html=body_html, emails=recipient_emails)
        self.message_post(
            body=_(
                'Memo is required before sending Contract Cover Letter to HOD. '
                'Contract team notification email has been sent to: %(emails)s.',
                emails=', '.join(recipient_emails) if recipient_emails else _('No configured recipients'),
            ),
            subtype_xmlid='mail.mt_note',
        )

    def _prepare_cover_letter_pdf_bytes(self):
        self.ensure_one()
        if not self.memo_id:
            raise UserError(_('Please link a Memo before sending the Contract Cover Letter to HOD.'))
        if not self.signed_document_attachment_id or not self.signed_document_attachment_id.datas:
            raise UserError(_('No signed provider contract document was found to prepare the cover-letter package.'))

        memo_pdf, _memo_mimetype = self.env['ir.actions.report']._render_qweb_pdf(
            'e_system.action_report_memo_management',
            self.memo_id.id,
        )
        contract_pdf = base64.b64decode(self.signed_document_attachment_id.datas)

        PdfReader, PdfWriter = _get_pdf_tools()
        if not PdfReader or not PdfWriter:
            raise UserError(_('PDF merge library is not available (pypdf/PyPDF2).'))

        # Build full cover pages:
        # 1) before memo: "Contract Memo Cover Page"
        # 2) after memo: contract type name
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except ImportError as exc:
            raise UserError(_('PDF cover-page library is not available (reportlab).')) from exc

        # Prepare company logo for all pages in the package.
        logo_img = None
        company_logo_data = self.env.company.logo
        if company_logo_data:
            try:
                from reportlab.lib.utils import ImageReader
                logo_bytes = base64.b64decode(company_logo_data)
                logo_img = ImageReader(io.BytesIO(logo_bytes))
            except Exception:
                logo_img = None

        def _get_logo_size(page_width):
            if not logo_img:
                return (0, 0)
            iw, ih = logo_img.getSize()
            if not iw or not ih:
                return (0, 0)
            # Match the report header constraints: max-height 80, width constrained to header area.
            max_h = 80.0
            max_w = min(150.0, float(page_width) * 0.25)
            scale = min(max_w / float(iw), max_h / float(ih), 1.0)
            return (float(iw) * scale, float(ih) * scale)

        def _apply_logo_overlay(page):
            if not logo_img:
                return
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            if page_width <= 0 or page_height <= 0:
                return
            logo_w, logo_h = _get_logo_size(page_width)
            if not logo_w or not logo_h:
                return

            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=(page_width, page_height))
            can.drawImage(
                logo_img,
                40,
                page_height - 40 - logo_h,
                width=logo_w,
                height=logo_h,
                mask='auto',
                preserveAspectRatio=True,
                anchor='nw',
            )
            can.showPage()
            can.save()
            packet.seek(0)
            overlay_reader = PdfReader(packet)
            if overlay_reader.pages:
                page.merge_page(overlay_reader.pages[0])

        def _build_cover_page_pdf(title):
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            width, height = A4
            can.setFont('Helvetica-Bold', 28)
            can.drawCentredString(width / 2.0, height / 2.0, title or '')
            can.showPage()
            can.save()
            return packet.getvalue()

        contract_type_name = dict(self._fields['contract_type'].selection).get(
            self.contract_type,
            self.contract_type or _('Contract'),
        )
        memo_cover_pdf = _build_cover_page_pdf(_('Contract Memo Cover Page'))
        contract_type_cover_pdf = _build_cover_page_pdf(contract_type_name)

        writer = PdfWriter()

        memo_cover_reader = PdfReader(io.BytesIO(memo_cover_pdf))
        for page in memo_cover_reader.pages:
            _apply_logo_overlay(page)
            writer.add_page(page)

        memo_reader = PdfReader(io.BytesIO(memo_pdf))
        for page in memo_reader.pages:
            # Memo is rendered by Odoo's report engine which already
            # includes the company logo in the header — do NOT overlay again.
            writer.add_page(page)

        contract_type_cover_reader = PdfReader(io.BytesIO(contract_type_cover_pdf))
        for page in contract_type_cover_reader.pages:
            _apply_logo_overlay(page)
            writer.add_page(page)

        contract_reader = PdfReader(io.BytesIO(contract_pdf))
        for page in contract_reader.pages:
            # Signed contract PDF already has the logo from contract_minimal_layout
            # header — do NOT overlay again.
            writer.add_page(page)

        output = io.BytesIO()
        writer.write(output)
        return output.getvalue()

    def _apply_contract_template_terms(self, template):
        """Overwrite contract terms with selected template body."""
        self.ensure_one()
        if not template:
            return
        self.contract_terms_summary = template.body_html or False

    def _ensure_pdf_filename(self, filename, fallback):
        name = (filename or fallback or '').strip()
        if not name:
            name = fallback
        if not name.lower().endswith('.pdf'):
            name = '%s.pdf' % name
        return name

    def _sync_special_annexure_uploads(self):
        upload_model = self.env['ecdhs.contract.document.upload']
        for contract in self:
            for key, required, file_data, file_name, label in [
                ('jbcc', contract.jbcc_required, contract.jbcc_upload_file, contract.jbcc_upload_filename, 'JBCC Upload'),
                ('gcc', contract.gcc_required, contract.gcc_upload_file, contract.gcc_upload_filename, 'GCC Upload'),
            ]:
                line_domain = [
                    ('contract_id', '=', contract.id),
                    ('document_type', '=', 'annexure'),
                    ('source_document', '=', key),
                ]
                existing_lines = upload_model.search(line_domain, order='sequence, id')
                primary_line = existing_lines[:1]
                extra_lines = existing_lines[1:]

                should_have_line = bool(
                    contract.contract_type == 'funding_agreement'
                    and required
                    and file_data
                )

                if should_have_line:
                    safe_file_name = contract._ensure_pdf_filename(file_name, label)
                    vals = {
                        'contract_id': contract.id,
                        'document_type': 'annexure',
                        'file_name': safe_file_name,
                        'datas': file_data,
                        'source_document': key,
                    }
                    if primary_line:
                        primary_line.write(vals)
                    else:
                        upload_model.create(vals)
                elif primary_line:
                    primary_line.unlink()

                if extra_lines:
                    extra_lines.unlink()

    @api.constrains('contract_type', 'jbcc_required', 'jbcc_upload_file', 'gcc_required', 'gcc_upload_file')
    def _check_required_funding_uploads(self):
        for contract in self:
            if contract.contract_type != 'funding_agreement':
                continue
            if contract.jbcc_required and not contract.jbcc_upload_file:
                raise ValidationError(_('Please upload JBCC document when JBCC Required is enabled.'))
            if contract.gcc_required and not contract.gcc_upload_file:
                raise ValidationError(_('Please upload GCC document when GCC Required is enabled.'))

    @api.onchange('contract_template_id')
    def _onchange_contract_template_id(self):
        for contract in self:
            if contract.contract_template_id:
                contract._apply_contract_template_terms(contract.contract_template_id)
            else:
                contract.contract_terms_summary = False

    @api.onchange('jbcc_upload_file', 'jbcc_upload_filename')
    def _onchange_jbcc_upload_filename(self):
        for contract in self:
            if contract.jbcc_upload_file and not contract.jbcc_upload_filename:
                contract.jbcc_upload_filename = 'JBCC Upload.pdf'

    @api.onchange('gcc_upload_file', 'gcc_upload_filename')
    def _onchange_gcc_upload_filename(self):
        for contract in self:
            if contract.gcc_upload_file and not contract.gcc_upload_filename:
                contract.gcc_upload_filename = 'GCC Upload.pdf'

    @api.onchange('contract_type', 'jbcc_required', 'jbcc_upload_file', 'gcc_required', 'gcc_upload_file')
    def _onchange_sync_special_annexures(self):
        # Keep the annexure list immediately aligned in form view.
        self._sync_special_annexure_uploads()

    # -------------------------------------------------------------------------
    # Service Provider signatory sync
    # -------------------------------------------------------------------------

    def _prepare_sp_signatory_vals(self, reset_signature=False):
        self.ensure_one()
        vals = {
            'sequence': 1,
            'is_service_provider': True,
            'partner_id': self.service_provider_id.id,
            'user_id': False,
            'role_designation': 'Service Provider',
            'required': True,
        }
        if reset_signature:
            vals.update({
                'status': 'Pending',
                'comment': False,
                'date': False,
                'sign_initials': False,
            })
        return vals

    def _sync_sp_signatory(self):
        """Keep the Service Provider locked at sequence 1 in the signatories list.

        Called from onchange (in-memory) and write (persisted).  The helper
        works on both transient (onchange) and saved records.
        """
        for contract in self:
            sp_sigs = contract.signatory_ids.filtered(lambda s: s.is_service_provider)
            if contract.service_provider_id:
                vals = contract._prepare_sp_signatory_vals()
                if sp_sigs:
                    primary_sp = sp_sigs[0]
                    primary_sp.update(vals)
                    extras = sp_sigs - primary_sp
                    if extras:
                        contract.signatory_ids -= extras
                else:
                    contract.update({
                        'signatory_ids': [(0, 0, vals)],
                    })
            else:
                if sp_sigs:
                    contract.signatory_ids -= sp_sigs

            # Guard against transient blank rows being introduced by repeated
            # onchange mutations on the x2many list.
            blank_lines = contract.signatory_ids.filtered(
                lambda s: not s.is_service_provider
                and not s.partner_id
                and not s.user_id
                and not s.role_designation
                and not s.comment
                and not s.date
                and not s.sign_initials
                and s.status in (False, 'Pending')
            )
            if blank_lines:
                contract.signatory_ids -= blank_lines

    def _sync_sp_signatory_saved(self):
        """Persist-side sync: called after super().write() when service_provider_id changed."""
        for contract in self:
            sp_sigs = contract.signatory_ids.filtered(lambda s: s.is_service_provider)
            if contract.service_provider_id:
                reset_signature = False
                if sp_sigs:
                    primary_sp = sp_sigs[0]
                    if primary_sp.partner_id != contract.service_provider_id:
                        reset_signature = True
                    vals = contract._prepare_sp_signatory_vals(reset_signature=reset_signature)
                    primary_sp.write(vals)
                    if len(sp_sigs) > 1:
                        sp_sigs[1:].with_context(_bypass_sp_unlink=True).unlink()
                else:
                    vals = contract._prepare_sp_signatory_vals(reset_signature=True)
                    self.env['ecdhs.contract.signatory'].create(dict(
                        vals,
                        contract_id=contract.id,
                    ))
            else:
                if sp_sigs:
                    sp_sigs.with_context(_bypass_sp_unlink=True).unlink()

    @staticmethod
    def _format_service_provider_contact(partner):
        if not partner:
            return False
        parts = [p for p in [partner.phone, partner.mobile] if p]
        return ' / '.join(parts) if parts else False

    @api.onchange('service_provider_id')
    def _onchange_service_provider_id(self):
        for contract in self:
            contract.service_provider_contact = self._format_service_provider_contact(contract.service_provider_id)
        self._sync_sp_signatory()

    # =========================================================================
    # Constraints
    # =========================================================================

    @api.constrains('date_start', 'date_end', 'is_indefinite')
    def _check_dates(self):
        for contract in self:
            if not contract.is_indefinite and contract.date_end and \
                    contract.date_start and contract.date_start > contract.date_end:
                raise ValidationError(_(
                    'Contract %(ref)s: start date %(start)s must be earlier than end date %(end)s.',
                    ref=contract.name,
                    start=contract.date_start,
                    end=contract.date_end,
                ))

    @api.constrains('original_contract_value', 'contract_value')
    def _check_contract_value_positive(self):
        for contract in self:
            baseline_value = contract.original_contract_value
            if baseline_value in (False, None):
                baseline_value = contract.contract_value
            if baseline_value is not None and baseline_value <= 0:
                raise ValidationError(_(
                    'Contract %(ref)s: Contract Value must be greater than 0.',
                    ref=contract.name or _('New'),
                ))

    # =========================================================================
    # Document Filing System
    # =========================================================================

    def _get_or_create_document_folder_tree(self):
        """Ensure the department and contract-specific folders exist for this contract."""
        self.ensure_one()
        if not self.end_user_department_id:
            return False, False

        parent_department = self.end_user_department_id.parent_id
        department_name = parent_department.name or self.end_user_department_id.name

        documents = self.env['documents.document'].sudo()
        root_folder = documents.search([
            ('name', '=', 'Business Unit'),
            ('folder_id', '=', False),
            ('type', '=', 'folder'),
        ], limit=1)
        if not root_folder:
            root_folder = documents.create({
                'name': 'Business Unit',
                'type': 'folder',
            })

        dept_folder = documents.search([
            ('name', '=', department_name),
            ('folder_id', '=', root_folder.id),
            ('type', '=', 'folder'),
        ], limit=1)
        if not dept_folder:
            dept_folder = documents.create({
                'name': department_name,
                'folder_id': root_folder.id,
                'type': 'folder',
            })

        contracts_folder = documents.search([
            ('name', '=', 'Contracts'),
            ('folder_id', '=', dept_folder.id),
            ('type', '=', 'folder'),
        ], limit=1)
        if not contracts_folder:
            contracts_folder = documents.create({
                'name': 'Contracts',
                'folder_id': dept_folder.id,
                'type': 'folder',
            })

        contract_ref_folder = documents.search([
            ('name', '=', self.name),
            ('folder_id', '=', contracts_folder.id),
            ('type', '=', 'folder'),
        ], limit=1)
        if not contract_ref_folder:
            contract_ref_folder = documents.create({
                'name': self.name,
                'folder_id': contracts_folder.id,
                'type': 'folder',
            })

        return dept_folder, contract_ref_folder

    def _assign_document_folder(self):
        """
        Create and assign hierarchical folder structure for contract documents:
        Business Unit → end_user_department.parent_id → Contracts → Contract Reference → Sub-folders

        Sub-folder categories:
        - Annexures: Annexure documents
        - Addendums: Contract addendums and amendments
        - Supporting Documents: Bid specs, budget, company docs, tax clearance, etc.
        - Monthly Reports: Payment verifications, monitoring reports
        - Other Documents: Miscellaneous files
        """
        for contract in self:
            if not contract.end_user_department_id:
                continue

            try:
                dept_folder, contract_ref_folder = contract._get_or_create_document_folder_tree()
                if not dept_folder or not contract_ref_folder:
                    continue

                # Keep the clickable field on the contract-specific folder.
                contract.sudo().write({
                    'folder_id': contract_ref_folder.id,
                    'contract_reference_folder_id': contract_ref_folder.id,
                })

                # Step 5: Create sub-folders for document categories
                contract._create_contract_sub_folders(contract_ref_folder)
                contract._sync_contract_key_documents_to_fileplan()

            except Exception as e:
                _logger.warning(
                    "Error creating document folders for contract %s: %s",
                    contract.name, str(e)
                )

    def _create_contract_sub_folders(self, parent_folder):
        """Create sub-folders for different document categories within a contract."""
        sub_folder_names = [
            'Annexures',
            'Addendums',
            'Supporting Documents',
            'Monthly Reports',
            'Other Documents',
            'Draft Versions',
        ]

        for folder_name in sub_folder_names:
            existing_folder = self.env['documents.document'].sudo().search([
                ('name', '=', folder_name),
                ('folder_id', '=', parent_folder.id),
                ('type', '=', 'folder')
            ], limit=1)

            if not existing_folder:
                self.env['documents.document'].sudo().create({
                    'name': folder_name,
                    'folder_id': parent_folder.id,
                    'type': 'folder'
                })

    def _upsert_documents_entry(self, attachment, folder, name=None):
        """Create/update documents.document so attachments are visible in File Plan."""
        self.ensure_one()
        if not attachment or not folder:
            return False

        owner_id = self.end_user_id.id or self.create_uid.id or self.env.user.id
        vals = {
            'attachment_id': attachment.id,
            'folder_id': folder.id,
            'owner_id': owner_id,
            'res_model': self._name,
            'res_id': self.id,
            'name': name or attachment.name or self.name,
        }
        document = self.env['documents.document'].sudo().search([
            ('attachment_id', '=', attachment.id),
        ], limit=1)
        if document:
            document.sudo().write(vals)
        else:
            document = self.env['documents.document'].sudo().create(vals)
        return document

    def _sync_contract_key_documents_to_fileplan(self):
        """Sync contract draft/provider/final signed artifacts into Documents folders."""
        for contract in self:
            if not contract.end_user_department_id:
                continue
            if not contract.contract_reference_folder_id:
                contract._assign_document_folder()
            if not contract.contract_reference_folder_id:
                continue

            contract._refresh_signed_attachment_links_from_requests()
            contract._ensure_draft_watermarked_attachment()

            if contract.draft_watermarked_attachment_id:
                draft_folder = contract._get_contract_subfolder('Draft Versions')
                contract._upsert_documents_entry(
                    contract.draft_watermarked_attachment_id,
                    draft_folder,
                    name=_('%s - Draft Contract', contract.name),
                )

            if contract.provider_signed_document_attachment_id:
                provider_folder = contract.contract_reference_folder_id
                contract._upsert_documents_entry(
                    contract.provider_signed_document_attachment_id,
                    provider_folder,
                    name=_('%s - Provider Signed Contract', contract.name),
                )

            if contract.signed_document_attachment_id:
                final_folder = contract.contract_reference_folder_id
                contract._upsert_documents_entry(
                    contract.signed_document_attachment_id,
                    final_folder,
                    name=_('%s - Final Signed Contract', contract.name),
                )

            contract._sync_completion_certificates_to_fileplan()

            contract._normalize_contract_fileplan_entries()

    @staticmethod
    def _is_completion_certificate_attachment(attachment):
        name = (attachment.name or '').strip().lower()
        return 'certificate of completion' in name

    def _sync_completion_certificates_to_fileplan(self):
        """Store completion certificates as separate file-plan copies."""
        for contract in self:
            if not contract.contract_reference_folder_id:
                continue

            requests = self.env['sign.request'].sudo().search([
                ('contract_id', '=', contract.id),
                ('state', '=', 'signed'),
            ])
            if not requests:
                continue

            provider_req = requests.filtered(lambda r: not r.is_cover_letter_flow)[:1]
            final_req = requests.filtered(lambda r: r.is_cover_letter_flow)[:1]

            provider_folder = contract.contract_reference_folder_id
            final_folder = contract.contract_reference_folder_id

            if provider_req:
                provider_certs = provider_req.completed_document_attachment_ids.filtered(
                    lambda a: contract._is_completion_certificate_attachment(a)
                )
                for cert in provider_certs:
                    contract._upsert_documents_entry(
                        cert,
                        provider_folder,
                        name=_('%s - Provider Signed Contract - Certificate of Completion', contract.name),
                    )

            if final_req:
                final_certs = final_req.completed_document_attachment_ids.filtered(
                    lambda a: contract._is_completion_certificate_attachment(a)
                )
                for cert in final_certs:
                    contract._upsert_documents_entry(
                        cert,
                        final_folder,
                        name=_('%s - Final Signed Contract - Certificate of Completion', contract.name),
                    )

    def _normalize_contract_fileplan_entries(self):
        """Force canonical folder+attachment mapping for Draft/Provider/Final contract files."""
        for contract in self:
            if not contract.contract_reference_folder_id:
                continue

            draft_folder = contract._get_contract_subfolder('Draft Versions')
            expected = [
                (
                    _('%s - Draft Contract', contract.name),
                    contract.draft_watermarked_attachment_id,
                    draft_folder,
                ),
                (
                    _('%s - Provider Signed Contract', contract.name),
                    contract.provider_signed_document_attachment_id,
                    contract.contract_reference_folder_id,
                ),
                (
                    _('%s - Final Signed Contract', contract.name),
                    contract.signed_document_attachment_id,
                    contract.contract_reference_folder_id,
                ),
            ]

            for label, attachment, folder in expected:
                if not attachment or not folder:
                    continue

                primary_doc = contract._upsert_documents_entry(attachment, folder, name=label)
                if not primary_doc:
                    continue

                duplicate_by_label = self.env['documents.document'].sudo().search([
                    ('res_model', '=', contract._name),
                    ('res_id', '=', contract.id),
                    ('name', '=', label),
                    ('id', '!=', primary_doc.id),
                ])
                if duplicate_by_label:
                    duplicate_by_label.sudo().unlink()

                duplicate_by_attachment = self.env['documents.document'].sudo().search([
                    ('res_model', '=', contract._name),
                    ('res_id', '=', contract.id),
                    ('attachment_id', '=', attachment.id),
                    ('id', '!=', primary_doc.id),
                ])
                if duplicate_by_attachment:
                    duplicate_by_attachment.sudo().unlink()

    def _refresh_signed_attachment_links_from_requests(self):
        """Prefer completed signed files from sign.request over older/plain attachments."""
        for contract in self:
            requests = self.env['sign.request'].sudo().search([
                ('contract_id', '=', contract.id),
                ('state', '=', 'signed'),
            ], order='id desc')
            if not requests:
                continue

            provider_request = requests.filtered(lambda r: not r.is_cover_letter_flow)[:1]
            cover_request = requests.filtered(lambda r: r.is_cover_letter_flow)[:1]

            vals = {}
            if provider_request and provider_request.completed_document_attachment_ids:
                provider_non_cert = provider_request.completed_document_attachment_ids.filtered(
                    lambda a: not contract._is_completion_certificate_attachment(a)
                )
                provider_pick = (provider_non_cert.sorted('id')[-1:] or provider_request.completed_document_attachment_ids.sorted('id')[-1:])
                if provider_pick:
                    vals['provider_signed_document_attachment_id'] = provider_pick.id
            if cover_request and cover_request.completed_document_attachment_ids:
                cover_non_cert = cover_request.completed_document_attachment_ids.filtered(
                    lambda a: not contract._is_completion_certificate_attachment(a)
                )
                cover_pick = (cover_non_cert.sorted('id')[-1:] or cover_request.completed_document_attachment_ids.sorted('id')[-1:])
                if cover_pick:
                    vals['signed_document_attachment_id'] = cover_pick.id
            elif provider_request and provider_request.completed_document_attachment_ids and not contract.signed_document_attachment_id:
                provider_non_cert = provider_request.completed_document_attachment_ids.filtered(
                    lambda a: not contract._is_completion_certificate_attachment(a)
                )
                provider_pick = (provider_non_cert.sorted('id')[-1:] or provider_request.completed_document_attachment_ids.sorted('id')[-1:])
                if provider_pick:
                    vals['signed_document_attachment_id'] = provider_pick.id

            if vals:
                contract.with_context(skip_fileplan_sync=True).sudo().write(vals)

    def _ensure_draft_watermarked_attachment(self):
        """Generate/update the draft watermarked PDF attachment for file-plan sync."""
        self.ensure_one()
        report = self.env.ref('ecdhs_contract_management.action_report_contract_document_draft_preview')
        pdf_content, _mime = report.sudo()._render_qweb_pdf(
            report.report_name,
            res_ids=[self.id],
        )
        pdf_content = self._add_draft_watermark(pdf_content)
        encoded_pdf = base64.b64encode(pdf_content)
        attachment_name = '%s - Draft Contract Preview.pdf' % (self.name or 'Contract')

        if self.draft_watermarked_attachment_id:
            self.draft_watermarked_attachment_id.sudo().write({
                'name': attachment_name,
                'type': 'binary',
                'datas': encoded_pdf,
                'mimetype': 'application/pdf',
                'res_model': self._name,
                'res_id': self.id,
            })
            return self.draft_watermarked_attachment_id

        attachment = self.env['ir.attachment'].sudo().create({
            'name': attachment_name,
            'type': 'binary',
            'datas': encoded_pdf,
            'mimetype': 'application/pdf',
            'res_model': self._name,
            'res_id': self.id,
        })
        self.with_context(skip_fileplan_sync=True).sudo().write({'draft_watermarked_attachment_id': attachment.id})
        return attachment

    def _get_contract_subfolder(self, subfolder_name):
        """
        Get or create a specific sub-folder within this contract's folder.
        Useful for assigning documents to the appropriate category.
        """
        self.ensure_one()
        contract_folder = self.contract_reference_folder_id
        if not contract_folder:
            dept_folder, contract_folder = self._get_or_create_document_folder_tree()
            if dept_folder and contract_folder:
                self.sudo().write({
                    'folder_id': contract_folder.id,
                    'contract_reference_folder_id': contract_folder.id,
                })

        if not contract_folder:
            return False

        subfolder = self.env['documents.document'].sudo().search([
            ('name', '=', subfolder_name),
            ('folder_id', '=', contract_folder.id),
            ('type', '=', 'folder')
        ], limit=1)

        if not subfolder:
            subfolder = self.env['documents.document'].sudo().create({
                'name': subfolder_name,
                'folder_id': contract_folder.id,
                'type': 'folder'
            })

        return subfolder

    # =========================================================================
    # ORM overrides
    # =========================================================================

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('ecdhs.contract') or _('New')
                )
            if 'provider_review_state' in vals and 'state' not in vals:
                vals['state'] = {
                    'sent_for_review': 'provider_review_sent',
                    'revised_sent': 'provider_review_sent',
                    'provider_changes_requested': 'provider_changes_requested',
                    'provider_rejected': 'provider_rejected',
                    'provider_accepted': 'provider_accepted',
                }.get(vals['provider_review_state'], vals.get('state', 'draft'))
            if vals.get('contract_value') is not None and vals.get('original_contract_value') is None:
                vals['original_contract_value'] = vals['contract_value']
            if vals.get('is_indefinite'):
                vals['date_end'] = False
            elif vals.get('date_start') and vals.get('contract_period_months'):
                start_date = fields.Date.to_date(vals['date_start'])
                period_months = int(vals['contract_period_months'])
                vals['date_end'] = fields.Date.to_string(start_date + relativedelta(months=period_months))
        records = super().create(vals_list)
        for vals, contract in zip(vals_list, records):
            # Generate a secure access token for the provider portal link
            if not contract.provider_access_token:
                contract.provider_access_token = uuid.uuid4().hex
            if contract.contract_template_id:
                contract._apply_contract_template_terms(contract.contract_template_id)
            if vals.get('clause_ids'):
                continue
            if contract.clause_ids:
                continue
            clauses = [
                dict(item, contract_id=contract.id)
                for item in contract._default_clause_values()
            ]
            self.env['ecdhs.contract.clause'].create(clauses)
            signatures = [
                dict(item, contract_id=contract.id)
                for item in contract._default_signature_section_values()
            ]
            self.env['ecdhs.contract.signature.section'].create(signatures)
        # Auto-create the SP signatory for every new contract that has a service provider
        # (only when the caller did not already supply signatory_ids).
        for vals, contract in zip(vals_list, records):
            if contract.service_provider_id:
                sp_sigs = contract.signatory_ids.filtered(lambda s: s.is_service_provider)
                has_broken_sp = any(not s.partner_id for s in sp_sigs)
                if not sp_sigs or has_broken_sp:
                    contract._sync_sp_signatory_saved()
        records._sync_special_annexure_uploads()
        # Assign document folders for all created records
        records.sudo()._assign_document_folder()
        records.sudo()._sync_contract_key_documents_to_fileplan()
        return records

    def write(self, vals):
        previous_states = {contract.id: contract.state for contract in self}
        if self.env.context.get('skip_period_end_sync'):
            return super().write(vals)

        if 'provider_review_state' in vals and 'state' not in vals:
            _provider_to_state = {
                'sent_for_review': 'provider_review_sent',
                'revised_sent': 'provider_review_sent',
                'provider_changes_requested': 'provider_changes_requested',
                'provider_rejected': 'provider_rejected',
                'provider_accepted': 'provider_accepted',
            }
            mapped = _provider_to_state.get(vals['provider_review_state'])
            if mapped:
                vals = dict(vals, state=mapped)


        if (
            'contract_value' in vals
            and not self.env.context.get('skip_original_contract_value_sync')
            and 'original_contract_value' not in vals
        ):
            paid_exists = any(contract.payment_ids.filtered(lambda payment: payment.state == 'paid') for contract in self)
            if not paid_exists:
                vals = dict(vals, original_contract_value=vals['contract_value'])

        should_sync_period = any(k in vals for k in ('date_start', 'contract_period_months', 'is_indefinite'))
        res = super().write(vals)

        if should_sync_period:
            for contract in self:
                if contract.is_indefinite:
                    target_date_end = False
                elif contract.date_start and contract.contract_period_months:
                    period_months = int(contract.contract_period_months)
                    target_date_end = contract.date_start + relativedelta(months=period_months)
                else:
                    target_date_end = contract.date_end

                if contract.date_end != target_date_end:
                    contract.with_context(skip_period_end_sync=True).write({'date_end': target_date_end})

        if 'contract_template_id' in vals:
            template_id = vals.get('contract_template_id')
            if template_id:
                template = self.env['ecdhs.contract.template'].browse(template_id)
                for contract in self:
                    contract._apply_contract_template_terms(template)
            else:
                super(EcdhsContract, self).write({'contract_terms_summary': False})
        should_sync_sp = ('service_provider_id' in vals or 'signatory_ids' in vals)
        if not should_sync_sp:
            should_sync_sp = any(
                contract.service_provider_id and contract.signatory_ids.filtered(
                    lambda s: s.is_service_provider and not s.partner_id
                )
                for contract in self
            )

        if should_sync_sp:
            self._sync_sp_signatory_saved()

        if not self.env.context.get('skip_remaining_contract_value_sync') and (
            'original_contract_value' in vals or 'contract_value' in vals
        ):
            self._sync_remaining_contract_value()

        if any(field in vals for field in (
            'contract_type',
            'jbcc_required',
            'jbcc_upload_file',
            'jbcc_upload_filename',
            'gcc_required',
            'gcc_upload_file',
            'gcc_upload_filename',
        )):
            self._sync_special_annexure_uploads()

        for contract in self:
            transitioned_to_fully_signed = (
                previous_states.get(contract.id) != 'fully_signed'
                and contract.state == 'fully_signed'
            )
            memo_removed_while_fully_signed = (
                'memo_id' in vals
                and not vals.get('memo_id')
                and contract.state == 'fully_signed'
            )
            if (transitioned_to_fully_signed or memo_removed_while_fully_signed) and not contract.memo_id:
                contract._notify_contract_team_memo_required()

        # Reassign document folders if department changes
        if 'end_user_department_id' in vals:
            self.sudo()._assign_document_folder()

        if not self.env.context.get('skip_fileplan_sync') and any(field in vals for field in (
            'sign_template_id',
            'provider_signed_document_attachment_id',
            'signed_document_attachment_id',
            'draft_watermarked_attachment_id',
        )):
            self.sudo()._sync_contract_key_documents_to_fileplan()

        return res

    # =========================================================================
    # Kanban / UI helpers
    # =========================================================================

    @api.model
    def _expand_states(self, states, domain, order):
        return [key for key, __ in type(self).state.selection]


    # =========================================================================
    # State-transition actions  (SOP step mapping noted)
    # =========================================================================

    def action_verify_documents(self):
        """SOP Step 2 – Admin Officer CM verifies all supporting documents."""
        self.ensure_one()
        if self.annexure_document_upload_ids and self.verify_without_annexures_confirmed:
            self.write({'verify_without_annexures_confirmed': False})

        if self.supporting_document_upload_ids and self.verify_without_supporting_confirmed:
            self.write({'verify_without_supporting_confirmed': False})

        if self.jbcc_required and self.verify_without_jbcc_confirmed:
            self.write({'verify_without_jbcc_confirmed': False})

        if self.gcc_required and self.verify_without_gcc_confirmed:
            self.write({'verify_without_gcc_confirmed': False})

        if not self.annexure_document_upload_ids and not self.verify_without_annexures_confirmed:
            return self._open_missing_documents_warning(
                warning_type='annexure',
            )

        if not self.supporting_document_upload_ids and not self.verify_without_supporting_confirmed:
            return self._open_missing_documents_warning(
                warning_type='supporting',
            )

        if self.contract_type == 'funding_agreement' and not self.jbcc_required and not self.verify_without_jbcc_confirmed:
            return self._open_missing_documents_warning(
                warning_type='jbcc',
            )

        if self.contract_type == 'funding_agreement' and not self.gcc_required and not self.verify_without_gcc_confirmed:
            return self._open_missing_documents_warning(
                warning_type='gcc',
            )

        for contract in self:
            missing = []
            # if not contract.bid_spec_attached:
            #     missing.append('• Bid Specification')
            # if not contract.ecbd4_attached:
            #     missing.append('• Approved Budget (ECBD4 Form)')
            # if not contract.tax_clearance_valid:
            #     missing.append('• Tax Clearance Certificate')
            # if not contract.company_documents_obtained:
            #     missing.append('• Company / CSD Documents')
            # if missing:
            #     raise UserError(_(
            #         'The following bid documentation must be confirmed before verifying:\n%s',
            #         '\n'.join(missing),
            #     ))
            contract.write({
                'state': 'verified',
                'all_documents_verified': True,
                'verify_without_annexures_confirmed': False,
                'verify_without_supporting_confirmed': False,
                'verify_without_jbcc_confirmed': False,
                'verify_without_gcc_confirmed': False,
            })

    def _open_missing_documents_warning(self, warning_type):
        self.ensure_one()
        return {
            'name': _('Missing Attachments Warning'),
            'type': 'ir.actions.act_window',
            'res_model': 'ecdhs.contract.verify.warning.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_contract_id': self.id,
                'default_warning_type': warning_type,
            },
        }

    def action_draft_contract(self):
        """SOP Step 3 – Assistant Director CM drafts contract per specification."""
        for contract in self.filtered(lambda c: c.state == 'draft'):
            missing = []
            # if not contract.procurement_method:
            #     missing.append('• Procurement Method')
            # if not contract.preference_point_system:
            #     missing.append('• Preference Point System (PPPFA)')
            # if not contract.contract_terms_summary:
            #     missing.append('• Draft Contract Terms and Working Arrangements')
            # if missing:
            #     raise UserError(_(
            #         'Contract drafting cannot proceed for %(ref)s.\nMissing mandatory drafting records:\n%(items)s',
            #         ref=contract.name,
            #         items='\n'.join(missing),
            #     ))
            contract.write({'state': 'contract_drafted'})

    def action_send_to_legal(self):
        """SOP Step 8 – Submit contract for vetting."""
        for contract in self.filtered(lambda c: c.state == 'verified'):
            # compliance_checks = [
            #     contract.constitution_s217_checked,
            #     contract.pfma_checked,
            #     contract.pppfa_checked,
            #     contract.bbbee_checked,
            #     contract.public_admin_act_checked,
            #     contract.paia_checked,
            #     contract.treasury_regulations_checked,
            #     contract.practice_notes_checked,
            # ]
            # if not all(compliance_checks):
            #     raise UserError(_(
            #         'Contract %(ref)s cannot be sent for vetting until all Legislative Compliance Checklist items are confirmed.',
            #         ref=contract.name,
            #     ))
            # if not contract.mandatory_clause_ok:
            #     missing_clauses = contract.clause_ids.filtered(
            #         lambda l: l.required and not l.confirmed
            #     ).mapped('name')
            #     raise UserError(_(
            #         'Contract %(ref)s cannot be sent for vetting. Confirm mandatory contract clauses first:\n%(items)s',
            #         ref=contract.name,
            #         items='\n'.join('• %s' % c for c in missing_clauses),
            #     ))
            # if not contract.compiled_by_id or not contract.recommended_by_id or not contract.supported_by_id:
            #     raise UserError(_(
            #         'Contract %(ref)s requires Compiled By, Recommended By, and Supported By records before vetting.',
            #         ref=contract.name,
            #     ))
            if not contract.legal_reviewer_id:
                raise UserError(_(
                    'Please assign a Reviewer/Quality Assurer before sending %(ref)s for vetting.',
                    ref=contract.name,
                ))

            reviewer_email = (
                contract.legal_reviewer_id.email
                or contract.legal_reviewer_id.partner_id.email
            )
            if not reviewer_email:
                raise UserError(_(
                    'Reviewer/Quality Assurer %(reviewer)s has no email address. '
                    'Add an email before sending %(ref)s for vetting.',
                    reviewer=contract.legal_reviewer_id.name,
                    ref=contract.name,
                ))

            contract.write({'state': 'legal_review'})
            contract.activity_schedule(
                'mail.mail_activity_data_todo',
                date_deadline=fields.Date.today() + relativedelta(days=5),
                summary=_('Contract vetting required'),
                note=_('Please vet contract %s and advise on vetting sign-off.', contract.name),
                user_id=contract.legal_reviewer_id.id,
            )
            contract._send_internal_template('ecdhs_contract_management.mail_template_legal_vetting_request')

    def action_approve(self):
        """SOP Step 9-10 – CFO or Delegated Official approves."""
        for contract in self:
            # if contract.requires_delegated_approval and not contract.delegated_official_id:
            #     raise UserError(_(
            #         'Contract %s exceeds R500,000. Please assign a Delegated Official '
            #         '(per PFMA delegation framework) before approving.',
            #         contract.name,
            #     ))
            # if not contract.cfo_id and not contract.delegated_official_id:
            #     raise UserError(_(
            #         'Please assign the CFO or Delegated Official responsible for approval of contract %s.',
            #         contract.name,
            #     ))
            contract.write({'state': 'approved'})

    def action_convene_signing(self):
        """SOP Step 11 – Validate signatories, generate the merged contract PDF,
        create a sign.template and open the template editor for field placement."""
        import base64  # local import; base64 already used in document upload model
        self.ensure_one()

        if self.state != 'provider_accepted':
            raise UserError(_('Provider must accept the draft before convening signing for contract %s.', self.name))

        # ── 1. Service Provider signatory must exist ──────────────────────────
        sp_sigs = self.signatory_ids.filtered(lambda s: s.is_service_provider)
        if not sp_sigs or not sp_sigs[0].partner_id:
            raise UserError(_(
                'A Service Provider signatory must be added to the Signatories tab '
                'before convening a signing ceremony on contract %(ref)s.',
                ref=self.name,
            ))

        # ── 2. At least 1 internal signatory must exist ────────────────────
        other_sigs = self.signatory_ids.filtered(
            lambda s: not s.is_service_provider and s.user_id
        )
        if len(other_sigs) < 1:
            raise UserError(_(
                'At least 1 internal signatory (besides the Service Provider) is '
                'required before convening a signing ceremony on contract %(ref)s. '
                '%(count)d internal signatory(ies) found.',
                ref=self.name,
                count=len(other_sigs),
            ))

        # ── 3. Cancel any in-progress sign request ────────────────────────────
        if self.sign_request_id and self.sign_request_id.state in ('sent', 'shared'):
            self.sign_request_id.cancel()

        # ── 4. Generate the full contract PDF (annexures included via merge) ──
        report_action = self.env.ref(
            'ecdhs_contract_management.action_report_contract_document'
        )
        pdf_bytes, _mime = self.env['ir.actions.report']._render_qweb_pdf(
            report_action.report_name, res_ids=[self.id],
        )

        # ── 5. Find-or-create sign.item.role per signatory role designation ───
        all_sigs = self.signatory_ids.sorted('sequence')
        role_names = []
        role_first_sequence = {}
        for sig in all_sigs:
            role_name = (sig.role_designation or (
                'Service Provider' if sig.is_service_provider else 'Signatory'
            )).strip()
            role_names.append(role_name)
            role_first_sequence.setdefault(role_name, sig.sequence)

        unique_role_names = list(dict.fromkeys(role_names))
        role_model = self.env['sign.item.role'].sudo()
        existing_roles = role_model.search([('name', 'in', unique_role_names)])
        role_by_name = {role.name: role for role in existing_roles}

        missing_names = [name for name in unique_role_names if name not in role_by_name]
        if missing_names:
            created_roles = role_model.create([
                {
                    'name': name,
                    'sequence': role_first_sequence.get(name, 10),
                }
                for name in missing_names
            ])
            for role in created_roles:
                role_by_name[role.name] = role

        role_ids = [role_by_name[name].id for name in role_names if name in role_by_name]

        # ── 6. Create attachment + sign.template ──────────────────────────────
        pdf_name = '%s - Contract Document.pdf' % self.name
        attachment = self.env['ir.attachment'].sudo().create({
            'name': pdf_name,
            'datas': base64.b64encode(pdf_bytes),
            'mimetype': 'application/pdf',
        })
        template = self.env['sign.template'].create({
            'attachment_id': attachment.id,
            'contract_id': self.id,
            'contract_role_ids': [(6, 0, role_ids)],
        })
        attachment.sudo().write({
            'res_model': 'sign.template',
            'res_id': template.id,
        })

        # ── 7. Advance state + store template reference ───────────────────────
        self.write({
            'state': 'signing',
            'sign_template_id': template.id,
        })

        # ── 8. Open the sign template editor (drag-and-drop field placement) ──
        return template.go_to_custom_template(sign_directly_without_mail=False)

    def action_restart_signing(self):
        """Cancel the current sign request, reset signatory statuses and relaunch
        the signing ceremony flow from scratch."""
        self.ensure_one()
        if self.sign_request_id and self.sign_request_id.state in ('sent', 'shared'):
            self.sign_request_id.cancel()

        # Reset all signatory lines to Pending
        self.signatory_ids.write({
            'status': 'Pending',
            'date': False,
            'sign_initials': False,
            'comment': False,
            'sign_request_item_id': False,
        })

        # Clear old template/request references so action_convene_signing starts fresh
        self.write({
            'sign_request_id': False,
            'sign_template_id': False,
            'signed_document_attachment_id': False,
            'state': 'approved',
        })
        return self.action_convene_signing()

    def action_open_sign_request(self):
        """Open the linked sign request form."""
        self.ensure_one()
        if not self.sign_request_id:
            return {'type': 'ir.actions.act_window_close'}
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sign Request'),
            'res_model': 'sign.request',
            'res_id': self.sign_request_id.id,
            'views': [(False, 'form')],
            'target': 'current',
        }

    def action_preview_signed_document(self):
        """Preview the completed signed contract PDF in-browser."""
        self.ensure_one()
        if not self.signed_document_attachment_id:
            raise UserError(_('No signed document is available for contract %s.', self.name))
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%d' % self.signed_document_attachment_id.id,
            'target': 'new',
        }

    def action_view_signed_document(self):
        """Download the completed signed contract PDF."""
        self.ensure_one()
        if not self.signed_document_attachment_id:
            raise UserError(_('No signed document is available for contract %s.', self.name))
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%d?download=true' % self.signed_document_attachment_id.id,
            'target': 'new',
        }

    def action_preview_provider_signed_document(self):
        """Preview the provider-signed contract PDF in-browser."""
        self.ensure_one()
        if not self.provider_signed_document_attachment_id:
            raise UserError(_('No provider-signed document is available for contract %s.', self.name))
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%d' % self.provider_signed_document_attachment_id.id,
            'target': 'new',
        }

    def action_view_provider_signed_document(self):
        """Download the provider-signed contract PDF."""
        self.ensure_one()
        if not self.provider_signed_document_attachment_id:
            raise UserError(_('No provider-signed document is available for contract %s.', self.name))
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%d?download=true' % self.provider_signed_document_attachment_id.id,
            'target': 'new',
        }

    def action_sign_internal_required_sections(self):
        """Mark all pending required internal signature sections as signed
        by the current backend user."""
        for contract in self:
            if contract.state != 'signing':
                raise UserError(_(
                    'Internal section signing is only allowed while contract %(ref)s is in Signing state.',
                    ref=contract.name,
                ))

            pending_sections = contract.signature_section_ids.filtered(
                lambda s: s.internal_signature_required and not s.internal_signed
            )
            if not pending_sections:
                raise UserError(_(
                    'There are no pending required internal sections to sign for contract %(ref)s.',
                    ref=contract.name,
                ))

            now = fields.Datetime.now()
            pending_sections.write({
                'internal_signed': True,
                'internal_signed_on': now,
                'internal_signatory_id': self.env.user.id,
            })

            contract.message_post(
                body=_(
                    'Internal required sections signed by <strong>%(user)s</strong> '
                    'for %(count)s section(s).',
                    user=self.env.user.display_name,
                    count=len(pending_sections),
                ),
                subtype_xmlid='mail.mt_note',
            )

    def action_send_to_provider_review(self):
        for contract in self:
            if contract.state not in ('contract_drafted', 'legal_review', 'approved', 'provider_rejected'):
                raise UserError(_('Contract %s must be drafted/vetted/approved (or provider rejected) before sending to provider.', contract.name))
            if not contract.contract_terms_summary:
                raise UserError(_('Please complete the Draft Contract Terms before sending to provider review.'))
            due_date = contract.provider_review_due_date or (fields.Date.today() + relativedelta(days=7))
            contract.write({
                'state': 'provider_review_sent',
                'provider_review_state': 'sent_for_review',
                'provider_review_due_date': due_date,
                'provider_last_sent_datetime': fields.Datetime.now(),
            })
            contract._send_provider_template('ecdhs_contract_management.mail_template_provider_draft_sent')

    def action_mark_provider_changes_requested(self):
        for contract in self:
            if contract.state not in ('provider_review_sent',):
                raise UserError(_('Provider changes can only be captured after draft has been sent to provider.'))
            contract.write({
                'state': 'provider_changes_requested',
                'provider_review_state': 'provider_changes_requested',
                'provider_last_response_datetime': fields.Datetime.now(),
            })

    def action_issue_revised_draft(self):
        for contract in self:
            if contract.state not in ('provider_changes_requested', 'provider_rejected'):
                raise UserError(_('Revised draft can only be issued after provider requested changes or rejected the draft.'))
            if not contract.contract_terms_summary:
                raise UserError(_('Please update the Draft Contract Terms before issuing a revised draft to the provider.'))
            due_date = contract.provider_review_due_date or (fields.Date.today() + relativedelta(days=5))
            contract.write({
                'state': 'provider_review_sent',
                'provider_review_state': 'revised_sent',
                'provider_review_due_date': due_date,
                'provider_last_sent_datetime': fields.Datetime.now(),
                'draft_version': (contract.draft_version or 1) + 1,
                'draft_revision_count': (contract.draft_revision_count or 0) + 1,
            })
            contract._send_provider_template('ecdhs_contract_management.mail_template_provider_revised_draft_sent')

    def action_mark_provider_accepted(self):
        for contract in self:
            if contract.state not in ('provider_review_sent', 'provider_changes_requested'):
                raise UserError(_('Provider acceptance can only be captured after draft circulation.'))
            contract.write({
                'state': 'provider_accepted',
                'provider_review_state': 'provider_accepted',
                'provider_acceptance_datetime': fields.Datetime.now(),
                'provider_last_response_datetime': fields.Datetime.now(),
            })
            contract._send_provider_template('ecdhs_contract_management.mail_template_provider_acceptance_ack')

    def action_mark_provider_rejected(self):
        for contract in self:
            if contract.state not in ('provider_review_sent',):
                raise UserError(_('Provider rejection can only be captured after draft circulation.'))
            contract.write({
                'state': 'provider_rejected',
                'provider_review_state': 'provider_rejected',
                'provider_last_response_datetime': fields.Datetime.now(),
            })

    def _get_contract_form_url(self):
        self.ensure_one()
        base_url = self.get_base_url()
        return '%s/web#id=%s&model=ecdhs.contract&view_type=form' % (base_url, self.id)

    def _create_contract_version(self, comment):
        self.ensure_one()
        version_count = self.env['ecdhs.contract.version'].search_count([
            ('contract_id', '=', self.id),
        ])
        return self.env['ecdhs.contract.version'].create({
            'contract_id': self.id,
            'version_number': 'v%s' % (version_count + 1),
            'comment': comment or _('Save Version'),
            'contract_name': self.name,
            'contract_terms_summary': self.contract_terms_summary,
        })

    def action_save_version(self):
        for contract in self:
            contract._create_contract_version(comment=_('Manual snapshot'))
            contract.message_post(
                body=_('A new contract version snapshot has been created.'),
                subtype_xmlid='mail.mt_note',
            )

    def action_save_as_template(self):
        for contract in self:
            if not contract.contract_terms_summary:
                raise UserError(_('Please enter contract terms before saving a template.'))
            template = self.env['ecdhs.contract.template'].sudo().create({
                'name': '%s - %s' % (contract.name, fields.Datetime.now().strftime('%Y-%m-%d %H:%M')),
                'is_addendum': False,
                'body_html': contract.contract_terms_summary,
            })
            contract.contract_template_id = template.id
            contract.message_post(
                body=_('Contract template <strong>%s</strong> has been created from this contract.', template.name),
                subtype_xmlid='mail.mt_note',
            )

    def action_open_request_changes_wizard(self):
        self.ensure_one()
        if self.state not in ('legal_review', 'approved'):
            raise UserError(_('Request Changes can only be raised during Vetting or Vetting Approved.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Request Changes'),
            'res_model': 'ecdhs.contract.request.changes.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_contract_id': self.id,
            },
        }

    def action_submit_change_request(self, section_reference, requested_change, due_date=False):
        self.ensure_one()
        if self.state not in ('legal_review', 'approved'):
            raise UserError(_('Contract must be in Vetting/Vetting Approved to request changes.'))

        self._create_contract_version(comment=_('Snapshot before requested changes'))

        change_request = self.env['ecdhs.contract.change.request'].create({
            'contract_id': self.id,
            'section_reference': section_reference,
            'requested_change': requested_change,
            'submitted_by': 'internal',
            'status': 'submitted',
            'due_date': due_date,
        })

        self.write({'state': 'changes_requested'})

        self.message_post(
            body=_(
                'Change request submitted.<br/>'
                '<strong>Section:</strong> %(section)s<br/>'
                '<strong>Requested Change:</strong><br/>%(details)s',
                section=section_reference,
                details=requested_change,
            ),
            subtype_xmlid='mail.mt_note',
        )

        creator = self.create_uid
        creator_email = creator.email or creator.partner_id.email
        if creator_email:
            contract_url = self._get_contract_form_url()
            template = self.env.ref(
                'ecdhs_contract_management.mail_template_contract_change_requested',
                raise_if_not_found=False,
            )
            if template:
                template.with_context(
                    recipient_name=creator.name,
                    change_section=section_reference,
                    change_details=requested_change,
                    contract_url=contract_url,
                ).send_mail(
                    self.id,
                    force_send=True,
                    email_values={'email_to': creator_email},
                )
            else:
                body_html = _(
                    '<p>Dear %(user)s,</p>'
                    '<p>A change request has been submitted for contract <strong>%(contract)s</strong>.</p>'
                    '<p><strong>Section:</strong> %(section)s</p>'
                    '<p><strong>Change Request:</strong><br/>%(details)s</p>'
                    '<p><a href="%(url)s">Open Contract</a></p>',
                    user=creator.name,
                    contract=self.name,
                    section=section_reference,
                    details=requested_change,
                    url=contract_url,
                )
                self._send_email_to_recipients(
                    subject=_('Contract Change Request - %s', self.name),
                    body_html=body_html,
                    emails=[creator_email],
                )

        return change_request

    def action_changes_completed(self):
        for contract in self:
            if contract.state != 'changes_requested':
                raise UserError(_('Changes Completed can only be used when status is Changes Requested.'))

            latest_request = contract.change_request_ids.sorted('id', reverse=True)[:1]
            if latest_request and latest_request.status not in ('incorporated', 'accepted'):
                latest_request.write({
                    'status': 'incorporated',
                    'resolved_by_id': self.env.user.id,
                    'resolved_on': fields.Datetime.now(),
                    'response_note': _('Contract changes have been updated and sent back to vetting.'),
                })

            contract.write({'state': 'legal_review'})

            contract.message_post(
                body=_('Requested changes were completed and contract has been returned to Vetting.'),
                subtype_xmlid='mail.mt_note',
            )

            if latest_request and latest_request.create_uid:
                requester_email = latest_request.create_uid.email or latest_request.create_uid.partner_id.email
                if requester_email:
                    contract_url = contract._get_contract_form_url()
                    template = contract.env.ref(
                        'ecdhs_contract_management.mail_template_contract_changes_completed',
                        raise_if_not_found=False,
                    )
                    if template:
                        template.with_context(
                            recipient_name=latest_request.create_uid.name,
                            contract_url=contract_url,
                        ).send_mail(
                            contract.id,
                            force_send=True,
                            email_values={'email_to': requester_email},
                        )
                    else:
                        body_html = _(
                            '<p>Dear %(user)s,</p>'
                            '<p>The requested contract changes for <strong>%(contract)s</strong> have been completed.</p>'
                            '<p><a href="%(url)s">Open Contract</a></p>',
                            user=latest_request.create_uid.name,
                            contract=contract.name,
                            url=contract_url,
                        )
                        contract._send_email_to_recipients(
                            subject=_('Contract Changes Completed - %s', contract.name),
                            body_html=body_html,
                            emails=[requester_email],
                        )

    def action_view_change_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Change Requests - %s') % self.name,
            'res_model': 'ecdhs.contract.change.request',
            'view_mode': 'list,form',
            'domain': [('contract_id', '=', self.id)],
            'context': {'default_contract_id': self.id},
        }

    def action_view_versions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Contract Versions - %s') % self.name,
            'res_model': 'ecdhs.contract.version',
            'view_mode': 'list,form',
            'domain': [('contract_id', '=', self.id)],
            'context': {'default_contract_id': self.id},
        }

    def action_send_cover_letter(self):
        """Send (or resend) contract cover letter to HOD and open Sign template editor."""
        for contract in self:
            if contract.state not in ('fully_signed', 'cover_letter_rejected', 'cover_letter_sent'):
                raise UserError(_(
                    'Cover letter can only be sent when contract %(ref)s is Fully Signed, Cover Letter Rejected, or already sent (resend scenario).',
                    ref=contract.name,
                ))
            if not contract.memo_id:
                raise UserError(_(
                    'Please link a Memo to contract %(ref)s before sending the cover letter to HOD.',
                    ref=contract.name,
                ))

            hod_signatories = contract.signatory_ids.filtered(
                lambda s: s.role_designation and 'hod' in s.role_designation.strip().lower()
            )
            if not hod_signatories:
                raise UserError(_(
                    'No signatories with role designation "HOD" were found on contract %(ref)s.',
                    ref=contract.name,
                ))

            hod_partners = hod_signatories.mapped('user_id.partner_id').filtered(lambda p: p and p.email)
            if not hod_partners:
                raise UserError(_(
                    'HOD signatories for contract %(ref)s do not have email addresses.',
                    ref=contract.name,
                ))

            package_pdf = contract._prepare_cover_letter_pdf_bytes()

            role_ids = []
            for sig in hod_signatories:
                role_name = sig.role_designation or 'HOD'
                role = self.env['sign.item.role'].sudo().search([('name', '=', role_name)], limit=1)
                if not role:
                    role = self.env['sign.item.role'].sudo().create({
                        'name': role_name,
                        'sequence': sig.sequence,
                    })
                role_ids.append(role.id)

            attachment = self.env['ir.attachment'].sudo().create({
                'name': '%s - Contract Cover Letter Package.pdf' % contract.name,
                'datas': base64.b64encode(package_pdf).decode(),
                'mimetype': 'application/pdf',
            })
            template = self.env['sign.template'].create({
                'attachment_id': attachment.id,
                'contract_id': contract.id,
                'contract_role_ids': [(6, 0, list(set(role_ids)))],
                'is_cover_letter_flow': True,
            })
            attachment.sudo().write({
                'res_model': 'sign.template',
                'res_id': template.id,
            })

            contract.write({'state': 'cover_letter_sent'})
            hod_emails = sorted({email for email in hod_partners.mapped('email') if email})
            template_mail = self.env.ref(
                'ecdhs_contract_management.mail_template_cover_letter_hod_request',
                raise_if_not_found=False,
            )
            if template_mail:
                template_mail.send_mail(
                    contract.id,
                    force_send=True,
                    email_values={'email_to': ','.join(hod_emails)},
                )
            else:
                contract._send_email_to_recipients(
                    subject=_('Contract Cover Letter Signature Request - %s', contract.name),
                    body_html=_(
                        '<p>Dear HOD,</p>'
                        '<p>The Contract Cover Letter package for <strong>%(contract)s</strong> is ready for digital signature.</p>'
                        '<p>Please open the signing request from the Sign app to sign the document.</p>',
                        contract=contract.name,
                    ),
                    emails=hod_emails,
                )

            contract.message_post(
                body=_(
                    'Contract cover letter has been sent to HOD signatories and opened in Sign template editor '
                    'for manual field placement. Memo linked: %(memo)s.',
                    memo=contract.memo_id.display_name or contract.memo_id.name or _('Memo'),
                ),
                subtype_xmlid='mail.mt_note',
            )

            return template.go_to_custom_template(sign_directly_without_mail=False)

    def action_resend_cover_letter(self):
        """Use the same sending flow as action_send_cover_letter."""
        return self.action_send_cover_letter()

    def action_activate(self):
        """SOP Step 12 – Contract signed; copy filed; contract now active."""
        for contract in self:
            if not contract.date_start:
                raise UserError(_(
                    'Please set a Contract Start Date before activating contract %s.', contract.name,
                ))

            sp_line = contract.signatory_ids.filtered(lambda s: s.is_service_provider)[:1]
            sp_signed = bool(sp_line and sp_line.status == 'Signed')
            sign_request_signed = bool(contract.sign_request_id and contract.sign_request_id.state == 'signed')

            # New logic: activation is driven by digital signature outcomes,
            # not legacy provider_review_state.
            if not (contract.state == 'fully_signed' or sp_signed or sign_request_signed):
                raise UserError(_(
                    'Service Provider digital signature is required before activating contract %s.',
                    contract.name,
                ))
            contract.write({'state': 'active', 'expiry_notice_sent': False})

    def action_print_contract(self):
        """Generate the draft contract PDF and open it inline (same behaviour as
        action_preview_signed_document / action_preview_provider_signed_document)."""
        self.ensure_one()
        report = self.env.ref('ecdhs_contract_management.action_report_contract_document_draft_preview')
        pdf_content, _mime = report.sudo()._render_qweb_pdf(
            report.report_name,
            res_ids=[self.id],
        )

        # Add watermark to PDF
        pdf_content = self._add_draft_watermark(pdf_content)

        attachment = self.env['ir.attachment'].sudo().create({
            'name': '%s - Draft Contract Preview.pdf' % (self.name or 'Contract'),
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'mimetype': 'application/pdf',
            'res_model': self._name,
            'res_id': self.id,
        })
        self.with_context(skip_fileplan_sync=True).sudo().write({'draft_watermarked_attachment_id': attachment.id})
        self.sudo()._sync_contract_key_documents_to_fileplan()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%d' % attachment.id,
            'target': 'new',
        }

    def _add_draft_watermark(self, pdf_bytes):
        """Add a slanted 'DRAFT DOCUMENT' watermark to each page of the PDF."""
        PdfReader, PdfWriter = _get_pdf_tools()
        if not PdfReader or not PdfWriter:
            # If PDF tools not available, return unchanged PDF
            return pdf_bytes

        try:
            from reportlab.pdfgen import canvas
        except ImportError:
            # If reportlab not available, return unchanged PDF
            return pdf_bytes

        try:
            # Read the input PDF
            input_pdf = io.BytesIO(pdf_bytes)
            reader = PdfReader(input_pdf)
            writer = PdfWriter()

            # Apply watermark to each page of the original PDF
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                page_width = float(page.mediabox.width or 595.0)
                page_height = float(page.mediabox.height or 842.0)

                # Build a watermark page with the exact same dimensions,
                # so merge_page overlays reliably on all page formats.
                watermark_buffer = io.BytesIO()
                c = canvas.Canvas(watermark_buffer, pagesize=(page_width, page_height))
                c.saveState()
                c.setFont("Helvetica-Bold", 50)
                c.setFillColorRGB(0.55, 0.55, 0.55)
                if hasattr(c, 'setFillAlpha'):
                    c.setFillAlpha(0.28)
                c.translate(page_width / 2.0, page_height / 2.0)
                c.rotate(35)

                text = "DRAFT DOCUMENT"
                max_span = int(max(page_width, page_height) * 1.6)
                for y in range(-max_span, max_span + 1, 150):
                    c.drawCentredString(0, y, text)

                c.restoreState()
                c.save()
                watermark_buffer.seek(0)
                watermark_page = PdfReader(watermark_buffer).pages[0]

                # Merge watermark onto the page
                page.merge_page(watermark_page)
                writer.add_page(page)

            # Write the output PDF
            output_buffer = io.BytesIO()
            writer.write(output_buffer)
            output_buffer.seek(0)
            return output_buffer.read()
        except Exception as e:
            _logger.warning("Failed to add watermark to PDF: %s", str(e))
            # If watermark fails, return unchanged PDF
            return pdf_bytes

    def action_set_draft(self):
        """Return a cancelled contract to draft for revision."""
        self.filtered(lambda c: c.state == 'cancelled').write({
            'state': 'draft',
            'all_documents_verified': False,
            'verify_without_annexures_confirmed': False,
            'verify_without_supporting_confirmed': False,
        })

    def action_cancel(self):
        """Cancel the contract (pre-signing)."""
        if any(c.state in ('active', 'expiring', 'terminated') for c in self):
            raise UserError(_(
                'Active or terminated contracts cannot be cancelled. Use "Terminate" instead.',
            ))
        self.write({'state': 'cancelled'})

    def action_terminate(self):
        """SOP Steps 18-19 – Open termination documentation wizard."""
        self.ensure_one()
        if self.state not in ('active', 'expiring'):
            raise UserError(_('Only active or expiring contracts can be terminated.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Terminate Contract'),
            'view_mode': 'form',
            'res_model': 'ecdhs.contract.terminate.wizard',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {'active_id': self.id, 'active_model': 'ecdhs.contract'},
        }

    # =========================================================================
    # Smart-button navigation
    # =========================================================================

    def action_view_addenda(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Addenda – %s') % self.name,
            'res_model': 'ecdhs.contract.addendum',
            'view_mode': 'list,form',
            'domain': [('contract_id', '=', self.id)],
            'context': {'default_contract_id': self.id},
        }

    def action_view_payments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payment Verifications – %s') % self.name,
            'res_model': 'ecdhs.contract.payment',
            'view_mode': 'list,form',
            'domain': [('contract_id', '=', self.id)],
            'context': {'default_contract_id': self.id},
        }

    def action_view_monitoring(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Contract Reviews – %s') % self.name,
            'res_model': 'ecdhs.contract.monitoring',
            'view_mode': 'list,form',
            'domain': [('contract_id', '=', self.id)],
            'context': {'default_contract_id': self.id},
        }

    # =========================================================================
    # Scheduled action – SOP Step 23: monthly 6-month expiry notices
    # =========================================================================

    @api.model
    def _cron_send_expiry_notices(self):
        """
        SOP Step 23: Issue monthly notices to end-users and contract officers on
        contracts expiring within the next 6 months.  Runs as a monthly cron job.
        """
        today = fields.Date.today()
        threshold = today + relativedelta(months=6)

        contracts = self.search([
            ('state', 'in', ['active', 'expiring']),
            ('is_indefinite', '=', False),
            ('date_end', '>=', today),
            ('date_end', '<=', threshold),
            ('expiry_notice_sent', '=', False),
        ])
        for contract in contracts:
            contract.write({'state': 'expiring', 'expiry_notice_sent': True})
            responsible_id = (
                contract.admin_officer_id.id
                or contract.deputy_director_id.id
                or self.env.uid
            )
            deadline = today + relativedelta(days=14)
            contract.activity_schedule(
                'mail.mail_activity_data_todo',
                date_deadline=deadline,
                summary=_('Contract expiring within 6 months – action required'),
                note=_(
                    'Contract %(ref)s with %(provider)s expires on %(date)s. '
                    'Initiate renewal procurement or prepare termination '
                    'documentation in accordance with the Contract Management SOP.',
                    ref=contract.name,
                    provider=contract.service_provider_id.name,
                    date=fields.Date.to_string(contract.date_end),
                ),
                user_id=responsible_id,
            )
            contract.message_post(
                body=_(
                    'Automated expiry notice: contract expires on %s.  '
                    'Please initiate renewal or termination proceedings.',
                    contract.date_end,
                )
            )

        # Reset the flag for contracts whose end date has been extended beyond the threshold
        renewed = self.search([
            ('state', '=', 'active'),
            ('expiry_notice_sent', '=', True),
            '|',
            ('is_indefinite', '=', True),
            ('date_end', '>', threshold),
        ])
        renewed.write({'expiry_notice_sent': False})

    @api.model
    def _cron_send_provider_review_reminders(self):
        today = fields.Date.today()
        contracts = self.search([
            ('provider_review_state', 'in', ['sent_for_review', 'revised_sent']),
            ('provider_review_due_date', '!=', False),
            ('provider_review_due_date', '<=', today),
        ])
        for contract in contracts:
            if contract.provider_last_reminder_date == today:
                continue
            contract._send_provider_template('ecdhs_contract_management.mail_template_provider_review_reminder')
            contract.write({'provider_last_reminder_date': today})
