# -*- coding: utf-8 -*-
# Eastern Cape DSD – Contract Addendum Model
# SOP Steps 13-15 and PFMA variation limits

import base64
import io
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class EcdhsContractAddendum(models.Model):
    _name = 'ecdhs.contract.addendum'
    _description = 'Contract Addendum'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'contract_id, sequence, date'

    contract_id = fields.Many2one(
        'ecdhs.contract', string='Contract',
        required=True, ondelete='cascade', tracking=True,
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(
        'Addendum Reference', required=True, copy=False, tracking=True,
        default=lambda self: _('New'),
        readonly=True,
    )
    date = fields.Date('Addendum Date', default=fields.Date.today, tracking=True)

    addendum_type = fields.Selection([
        ('date_extension', 'Extension of Time'),
        ('scope', 'Extension of Scope'),
        ('price_variation', 'Variation Order – Price / Value Change'),
        ('cession', 'Cession Change'),
        ('other', 'Other'),
    ], string='Type of Change', required=True, tracking=True)

    # -------------------------------------------------------------------------
    # PFMA Variation Controls  –  SOP Step 13
    # -------------------------------------------------------------------------
    service_category = fields.Selection([
        ('construction', 'Construction / Works / Infrastructure'),
        ('goods_services', 'Goods and Other Services'),
    ], string='Service Category',
       help='Determines the PFMA maximum variation limit:\n'
            '• Construction / Works: 20%\n'
            '• Goods and Other Services: 15%',
    )
    currency_id = fields.Many2one(
        'res.currency', related='contract_id.currency_id', readonly=True,
    )
    original_value = fields.Monetary(
        'Original Contract Value',
        related='contract_id.contract_value', readonly=True,
    )
    variation_amount = fields.Monetary(
        'Variation Amount', tracking=True,
        help='Monetary difference introduced by this addendum (positive = increase).',
    )
    variation_percentage = fields.Float(
        'Variation (%)',
        compute='_compute_variation_percentage', store=True, digits=(5, 2),
    )
    variation_limit = fields.Float(
        'Allowable Limit (%)',
        compute='_compute_variation_limit', store=True, digits=(5, 2),
    )
    variation_exceeds_limit = fields.Boolean(
        'Exceeds PFMA Limit',
        compute='_compute_variation_percentage', store=True,
    )
    requires_treasury_approval = fields.Boolean(
        'Requires Provincial Treasury Approval',
        compute='_compute_variation_percentage', store=True,
        help='Variations above the PFMA limit must be pre-approved by Provincial Treasury.',
    )

    # -------------------------------------------------------------------------
    # Change details
    # -------------------------------------------------------------------------
    addendum_template_id = fields.Many2one(
        'ecdhs.contract.template',
        string='Addendum Template',
        domain=[('is_addendum', '=', True)],
        tracking=True,
        help='Selecting a template overwrites Description of Change with the template body.',
    )
    addendum_sequence_name = fields.Char(
        string='Addendum Sequence Name',
        compute='_compute_addendum_sequence_name',
    )
    change_description = fields.Html(
        'Description of Change', required=True,
    )
    new_date_end = fields.Date(
        'New Contract End Date', tracking=True,
        help='Populate when the addendum extends the contract end date.',
    )

    # -------------------------------------------------------------------------
    # Approval workflow  –  SOP Step 14
    # -------------------------------------------------------------------------
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Approval'),
        ('approved', 'Approved'),
        ('signing', 'Signing'),
        ('signed', 'Signed'),
        ('signature_refused', 'Signature Refused'),
        ('rejected', 'Rejected'),
    ], default='draft', tracking=True, string='Status')

    approved_by_id = fields.Many2one('res.users', 'Approved By', tracking=True, copy=False)
    approved_date = fields.Date('Approval Date', tracking=True, copy=False)
    signed_date = fields.Date('Signing Date', tracking=True, copy=False)
    notes = fields.Text('Notes')

    # -------------------------------------------------------------------------
    # Digital Signature fields
    # -------------------------------------------------------------------------
    sign_template_id = fields.Many2one(
        'sign.template', string='Sign Template',
        copy=False, readonly=True,
        help='Sign template created for this addendum signing ceremony.',
    )
    sign_request_id = fields.Many2one(
        'sign.request', string='Signature Request',
        copy=False, readonly=True,
        help='Active sign.request for this addendum.',
    )
    signed_document_attachment_id = fields.Many2one(
        'ir.attachment', string='Signed Addendum Document',
        copy=False, readonly=True,
    )

    # -------------------------------------------------------------------------
    # Document Filing System
    # -------------------------------------------------------------------------
    folder_id = fields.Many2one(
        'documents.document',
        string='Document Folder',
        readonly=True,
        domain="[('type', '=', 'folder')]",
        help='Folder for storing addendum documents, linked to parent contract.'
    )

    # =========================================================================
    # Computed
    # =========================================================================

    @api.depends('service_category')
    def _compute_variation_limit(self):
        for addendum in self:
            addendum.variation_limit = (
                20.0 if addendum.service_category == 'construction' else 15.0
            )

    @api.depends('variation_amount', 'original_value', 'variation_limit')
    def _compute_variation_percentage(self):
        for addendum in self:
            if addendum.original_value:
                pct = abs(addendum.variation_amount) / addendum.original_value * 100.0
            else:
                pct = 0.0
            addendum.variation_percentage = pct
            exceeds = pct > addendum.variation_limit and bool(addendum.variation_amount)
            addendum.variation_exceeds_limit = exceeds
            addendum.requires_treasury_approval = exceeds

    @api.depends('contract_id', 'contract_id.addendum_ids', 'contract_id.addendum_ids.sequence')
    def _compute_addendum_sequence_name(self):
        for addendum in self:
            label = 'ADDENDUM'
            contract = addendum.contract_id
            if contract:
                ordered = contract.addendum_ids.sorted(key=lambda r: (r.sequence, r.id))
                index = ordered.ids.index(addendum.id) if addendum.id in ordered.ids else 0
                n = index + 1
                label = 'ADDENDUM %s' % n
            addendum.addendum_sequence_name = label

    # =========================================================================
    # Constraints
    # =========================================================================

    @api.constrains('variation_amount', 'original_value', 'service_category', 'state')
    def _check_variation_limit(self):
        for addendum in self:
            if addendum.state in ('approved', 'signed') and addendum.variation_exceeds_limit:
                raise ValidationError(_(
                    'Addendum %(name)s: the variation of %(pct).1f%% exceeds the PFMA '
                    'allowable limit of %(limit).0f%% for this service category. '
                    'Provincial Treasury approval must be on file before finalising.',
                    name=addendum.name,
                    pct=addendum.variation_percentage,
                    limit=addendum.variation_limit,
                ))


    # =========================================================================
    # ORM overrides
    # =========================================================================

    def _get_reference_year(self, date_value):
        parsed_date = fields.Date.to_date(date_value) if date_value else fields.Date.context_today(self)
        return parsed_date.year

    def _format_addendum_reference(self, contract, year, seq_n):
        contract_ref = contract.name or 'CONTRACT'
        return 'ADDENDUM/%s/%03d-%s' % (year, seq_n, contract_ref)

    def _ensure_reference_name(self):
        new_label = _('New')
        for addendum in self:
            if addendum.contract_id and (not addendum.name or addendum.name == new_label):
                year = self._get_reference_year(addendum.date)
                seq_n = self.sudo().search_count([
                    ('contract_id', '=', addendum.contract_id.id),
                    ('date', '>=', '%s-01-01' % year),
                    ('date', '<=', '%s-12-31' % year),
                    ('id', '!=', addendum.id),
                ]) + 1
                addendum.name = addendum._format_addendum_reference(addendum.contract_id, year, seq_n)

    # =========================================================================
    # State transitions
    # =========================================================================

    def action_submit(self):
        self._ensure_reference_name()
        self.write({'state': 'submitted'})

    def action_approve(self):
        self._ensure_reference_name()
        self.write({
            'state': 'approved',
            'approved_by_id': self.env.uid,
            'approved_date': fields.Date.today(),
        })

    def action_sign(self):
        """SOP Step 15 – Generate addendum PDF, create a sign.template using
        the parent contract's signatories, and open the sign template editor.
        On completion the sign module callbacks update the addendum state."""
        self.ensure_one()
        self._ensure_reference_name()

        contract = self.contract_id

        # ── 1. Must have at least one signatory on the parent contract ─────────
        all_sigs = contract.signatory_ids.sorted('sequence')
        if not all_sigs:
            raise UserError(_(
                'The parent contract %s has no signatories configured. '
                'Please add signatories before sending for signature.',
                contract.name,
            ))

        # ── 2. Cancel any in-progress sign request for this addendum ───────────
        if self.sign_request_id and self.sign_request_id.state in ('sent', 'shared'):
            self.sign_request_id.cancel()

        # ── 3. Generate addendum PDF (cover + content merged) ──────────────────
        try:
            from pypdf import PdfReader, PdfWriter
        except ImportError:
            from PyPDF2 import PdfReader, PdfWriter

        _ADDENDUM_COVER = 'ecdhs_contract_management.report_addendum_cover_template'
        _ADDENDUM_CONTENT = 'ecdhs_contract_management.report_addendum_content_template'
        writer = PdfWriter()
        for report_xmlid in (_ADDENDUM_COVER, _ADDENDUM_CONTENT):
            try:
                pdf_bytes, _ = self.env['ir.actions.report']._render_qweb_pdf(
                    report_xmlid, res_ids=[self.id],
                )
                reader = PdfReader(io.BytesIO(pdf_bytes))
                for page in reader.pages:
                    writer.add_page(page)
            except Exception as exc:
                _logger.warning(
                    'ecdhs addendum sign: could not render %s for %s – %s',
                    report_xmlid, self.name, exc,
                )
        output = io.BytesIO()
        writer.write(output)
        merged_pdf = output.getvalue()

        if not merged_pdf:
            raise UserError(_('Could not generate addendum PDF for %s.', self.name))

        # ── 4. Find-or-create sign.item.role per signatory role designation ────
        role_ids = []
        for sig in all_sigs:
            role_name = sig.role_designation or (
                'Service Provider' if sig.is_service_provider else 'Signatory'
            )
            existing_role = self.env['sign.item.role'].sudo().search(
                [('name', '=', role_name)], limit=1
            )
            if not existing_role:
                existing_role = self.env['sign.item.role'].sudo().create({
                    'name': role_name,
                    'sequence': sig.sequence,
                })
            role_ids.append(existing_role.id)

        # ── 5. Create attachment + sign.template ───────────────────────────────
        pdf_name = '%s - Addendum.pdf' % self.name
        attachment = self.env['ir.attachment'].sudo().create({
            'name': pdf_name,
            'datas': base64.b64encode(merged_pdf).decode(),
            'mimetype': 'application/pdf',
        })
        template = self.env['sign.template'].with_context(default_contract_id=False).create({
            'attachment_id': attachment.id,
            'contract_id': False,
            'addendum_id': self.id,
            'contract_role_ids': [(6, 0, role_ids)],
        })
        attachment.sudo().write({
            'res_model': 'sign.template',
            'res_id': template.id,
        })

        # ── 6. Advance state + store template reference ────────────────────────
        self.write({
            'state': 'signing',
            'sign_template_id': template.id,
        })

        # ── 7. Open the sign template editor ──────────────────────────────────
        return template.go_to_custom_template(sign_directly_without_mail=False)

    def _apply_signed_state(self):
        """Called by sign callbacks when all parties have signed."""
        for addendum in self:
            addendum.write({'state': 'signed', 'signed_date': fields.Date.today()})
            if addendum.addendum_type == 'date_extension' and addendum.new_date_end:
                addendum.contract_id.write({
                    'date_end': addendum.new_date_end,
                    'expiry_notice_sent': False,
                })
                addendum.contract_id.message_post(
                    body=_(
                        'Contract end date extended to %s via addendum %s.',
                        addendum.new_date_end, addendum.name,
                    )
                )
            addendum.message_post(
                body=_('Addendum has been fully signed digitally.'),
                message_type='notification',
            )

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_view_signed_addendum(self):
        """Download the completed signed addendum PDF."""
        self.ensure_one()
        if not self.signed_document_attachment_id:
            raise UserError(_('No signed document is available for addendum %s.', self.name))
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%d?download=true' % self.signed_document_attachment_id.id,
            'target': 'new',
        }

    def action_preview_addendum(self):
        """Open addendum in a separate form for quick preview from one2many lines."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Addendum Preview'),
            'res_model': 'ecdhs.contract.addendum',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {'form_view_initial_mode': 'readonly'},
        }

    def _sync_signed_document_to_fileplan(self):
        """Create/update documents.document so signed addenda appear in File Plan."""
        for addendum in self:
            if not addendum.signed_document_attachment_id or not addendum.folder_id:
                continue
            owner = (addendum.contract_id.end_user_id.id if addendum.contract_id else False) or self.env.user.id
            vals = {
                'attachment_id': addendum.signed_document_attachment_id.id,
                'folder_id': addendum.folder_id.id,
                'owner_id': owner,
                'res_model': addendum._name,
                'res_id': addendum.id,
                'name': _('%s - Signed Addendum', addendum.name),
            }
            document = self.env['documents.document'].sudo().search([
                ('attachment_id', '=', addendum.signed_document_attachment_id.id),
            ], limit=1)
            if document:
                document.sudo().write(vals)
            else:
                self.env['documents.document'].sudo().create(vals)

    def _sync_completion_certificates_to_fileplan(self):
        """Store addendum completion certificates as separate file-plan copies."""
        for addendum in self:
            if not addendum.folder_id:
                continue

            requests = self.env['sign.request'].sudo().search([
                ('addendum_id', '=', addendum.id),
                ('state', '=', 'signed'),
            ])
            cert_attachments = requests.mapped('completed_document_attachment_ids').filtered(
                lambda a: 'certificate of completion' in (a.name or '').strip().lower()
            )
            if not cert_attachments:
                continue

            owner = (addendum.contract_id.end_user_id.id if addendum.contract_id else False) or self.env.user.id
            cert_name = _('%s - Signed Addendum - Certificate of Completion', addendum.name)
            for cert in cert_attachments:
                vals = {
                    'attachment_id': cert.id,
                    'folder_id': addendum.folder_id.id,
                    'owner_id': owner,
                    'res_model': addendum._name,
                    'res_id': addendum.id,
                    'name': cert_name,
                }
                document = self.env['documents.document'].sudo().search([
                    ('attachment_id', '=', cert.id),
                ], limit=1)
                if document:
                    document.sudo().write(vals)
                else:
                    self.env['documents.document'].sudo().create(vals)

    def _apply_addendum_template_description(self, template):
        """Overwrite addendum change description with selected template body."""
        self.ensure_one()
        if not template:
            return
        self.change_description = template.body_html or False

    @api.onchange('addendum_template_id')
    def _onchange_addendum_template_id(self):
        for addendum in self:
            if addendum.addendum_template_id:
                addendum._apply_addendum_template_description(addendum.addendum_template_id)
            else:
                addendum.change_description = False

    @api.model_create_multi
    def create(self, vals_list):
        new_label = _('New')
        per_contract_counters = {}

        for vals in vals_list:
            if vals.get('name') and vals.get('name') != new_label:
                continue

            contract_id = vals.get('contract_id') or self.env.context.get('default_contract_id')
            if not contract_id:
                vals['name'] = new_label
                continue

            year = self._get_reference_year(vals.get('date'))
            counter_key = (contract_id, year)

            if counter_key not in per_contract_counters:
                base_count = self.sudo().search_count([
                    ('contract_id', '=', contract_id),
                    ('date', '>=', '%s-01-01' % year),
                    ('date', '<=', '%s-12-31' % year),
                ])
                per_contract_counters[counter_key] = base_count

            per_contract_counters[counter_key] += 1
            contract = self.env['ecdhs.contract'].browse(contract_id)
            vals['name'] = self._format_addendum_reference(contract, year, per_contract_counters[counter_key])

        records = super().create(vals_list)
        for addendum in records:
            if addendum.addendum_template_id:
                addendum._apply_addendum_template_description(addendum.addendum_template_id)
            # Assign addendum to Addendums subfolder of parent contract
            if addendum.contract_id and addendum.contract_id.folder_id:
                addendums_folder = addendum.contract_id._get_contract_subfolder('Addendums')
                if addendums_folder:
                    addendum.sudo().write({'folder_id': addendums_folder.id})
        records._sync_signed_document_to_fileplan()
        return records

    def write(self, vals):
        res = super().write(vals)

        if 'contract_id' in vals:
            self._ensure_reference_name()
            # Re-assign folder if contract changes
            for addendum in self:
                if addendum.contract_id and addendum.contract_id.folder_id:
                    addendums_folder = addendum.contract_id._get_contract_subfolder('Addendums')
                    if addendums_folder:
                        addendum.sudo().write({'folder_id': addendums_folder.id})

        if 'addendum_template_id' in vals:
            template_id = vals.get('addendum_template_id')
            if template_id:
                template = self.env['ecdhs.contract.template'].browse(template_id)
                for addendum in self:
                    addendum._apply_addendum_template_description(template)
            else:
                super(EcdhsContractAddendum, self).write({'change_description': False})

        if 'signed_document_attachment_id' in vals or 'folder_id' in vals or 'contract_id' in vals:
            self._sync_signed_document_to_fileplan()
            self._sync_completion_certificates_to_fileplan()
        return res
