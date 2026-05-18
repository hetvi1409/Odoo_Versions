# -*- coding: utf-8 -*-
# Eastern Cape Department of Human Settlements
# Sign-module integration for the ECDHS Contract signing ceremony.

import logging

from markupsafe import Markup
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

_CHATTER_GREEN_BOX_STYLE = (
    'background-color:#dcefe0;'
    'border:1px solid #b8d8bf;'
    'border-radius:8px;'
    'padding:18px 20px;'
    'color:#2f3b4a;'
)


# ─────────────────────────────────────────────────────────────────────────────
# sign.template  –  carries a back-reference to the originating contract
#                   also exposes the allowed role IDs so the JS patch can
#                   restrict which roles are shown in the template editor.
# ─────────────────────────────────────────────────────────────────────────────

class SignTemplate(models.Model):
    _inherit = 'sign.template'

    contract_id = fields.Many2one(
        'ecdhs.contract',
        string='Contract',
        ondelete='set null',
        copy=False,
        index=True,
    )
    addendum_id = fields.Many2one(
        'ecdhs.contract.addendum',
        string='Addendum',
        ondelete='set null',
        copy=False,
        index=True,
    )
    # IDs of sign.item.role records that belong to this contract's signatories.
    # Read by the JS fetchSignRoles patch to restrict the editor role dropdown.
    contract_role_ids = fields.Many2many(
        'sign.item.role',
        'sign_template_contract_role_rel',
        'template_id',
        'role_id',
        string='Contract Roles',
        copy=False,
    )
    is_cover_letter_flow = fields.Boolean(
        string='Cover Letter Flow',
        copy=False,
        default=False,
    )


# ─────────────────────────────────────────────────────────────────────────────
# sign.item.role  –  filter to this contract's roles when a template_id context
#                   key is provided (used by the JS editor role-restriction patch)
# ─────────────────────────────────────────────────────────────────────────────

class SignItemRole(models.Model):
    _inherit = 'sign.item.role'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **kwargs):
        """Optionally restrict roles to those linked to a contract template.

        The restriction is intentionally opt-in via context key
        ``restrict_contract_sign_roles`` to avoid impacting native Sign editor
        behavior in generic template flows.
        """
        template_id = self.env.context.get('sign_template_id')
        should_restrict = bool(self.env.context.get('restrict_contract_sign_roles'))
        if should_restrict and template_id:
            template = self.env['sign.template'].browse(int(template_id))
            if template.exists() and template.contract_role_ids:
                domain = list(domain or []) + [('id', 'in', template.contract_role_ids.ids)]
        return super().search_read(domain=domain, fields=fields, offset=offset,
                                   limit=limit, order=order, **kwargs)


# ─────────────────────────────────────────────────────────────────────────────
# sign.request  –  links back to contract; reacts to completion / refusal
# ─────────────────────────────────────────────────────────────────────────────

class SignRequest(models.Model):
    _inherit = 'sign.request'

    contract_id = fields.Many2one(
        'ecdhs.contract',
        string='Contract',
        ondelete='set null',
        copy=False,
        index=True,
    )
    addendum_id = fields.Many2one(
        'ecdhs.contract.addendum',
        string='Addendum',
        ondelete='set null',
        copy=False,
        index=True,
    )
    is_cover_letter_flow = fields.Boolean(
        string='Cover Letter Flow',
        copy=False,
        default=False,
    )

    @staticmethod
    def _is_completion_certificate_attachment(attachment):
        name = (attachment.name or '').strip().lower()
        return 'certificate of completion' in name

    def _get_primary_completed_attachment(self):
        self.ensure_one()
        attachments = self.sudo().completed_document_attachment_ids.sorted('id')
        if not attachments:
            return False
        non_certificate = attachments.filtered(
            lambda a: not self._is_completion_certificate_attachment(a)
        )
        return non_certificate[-1:] or attachments[-1:]

    def write(self, vals):
        """Intercept state→'signed' transition to update the contract immediately.

        This runs in the SAME transaction as the sign.request state change, so
        the contract update is atomic with the sign state.  It fires BEFORE
        _send_completed_document() (which sends emails) so the contract state is
        always updated even if email delivery raises an exception.
        """
        res = super().write(vals)
        if vals.get('state') == 'signed':
            # Handle addendum requests first and exclusively so parent contract
            # status is never updated for an addendum signing ceremony.
            for req in self.filtered(lambda r: r.addendum_id):
                try:
                    addendum = req.sudo().addendum_id
                    if addendum.state in ('signed', 'signature_refused'):
                        continue
                    _logger.info(
                        'ECDHS sign: request %s -> signed; updating addendum %s',
                        req.id, addendum.name,
                    )
                    addendum.sudo()._apply_signed_state()
                except Exception:
                    _logger.exception(
                        'ECDHS sign: error updating addendum on state=signed '
                        '(sign.request id=%s)', req.id,
                    )
            for req in self.filtered(lambda r: r.contract_id and not r.addendum_id):
                try:
                    contract = req.sudo().contract_id
                    if req.is_cover_letter_flow:
                        if contract.state in ('cover_letter_signed', 'cover_letter_rejected'):
                            continue
                    elif contract.state in ('fully_signed', 'signature_refused'):
                        continue
                    _logger.info(
                        'ECDHS sign: request %s → signed; updating contract %s',
                        req.id, contract.name,
                    )
                    req._sync_contract_signatories()
                    target_state = 'cover_letter_signed' if req.is_cover_letter_flow else 'fully_signed'
                    contract.sudo().write({'state': target_state})
                    if target_state == 'fully_signed':
                        # Auto-record the actual signing date as the contract start date.
                        contract.sudo().write({'date_start': fields.Date.today()})
                    contract.sudo().message_post(
                        body=_('Contract has been fully signed digitally. '
                               'The signed document will be attached shortly.')
                        if not req.is_cover_letter_flow else
                        _('Contract cover-letter package has been fully signed digitally. '
                          'The signed document will be attached shortly.'),
                        message_type='notification',
                    )
                except Exception:
                    _logger.exception(
                        'ECDHS sign: error updating contract on state=signed '
                        '(sign.request id=%s)', req.id,
                    )
        return res

    def _send_completed_document(self):
        """Send completion emails then attach the signed PDF to the contract or addendum.

        Contract state is already updated by the write() hook above.
        This method only handles the PDF attachment (which is generated by
        super()._generate_completed_document() inside super()).
        """
        super()._send_completed_document()
        try:
            if not self.sudo().completed_document_attachment_ids:
                return
            att = self._get_primary_completed_attachment()
            if not att:
                return
            contract = self.sudo().contract_id
            if contract:
                att.sudo().write({
                    'res_model': 'ecdhs.contract',
                    'res_id': contract.id,
                })
                if self.is_cover_letter_flow or not contract.sudo().signed_document_attachment_id:
                    contract.sudo().write({'signed_document_attachment_id': att.id})
                # Always snapshot the provider-signed PDF for the first (non-cover-letter) flow.
                if not self.is_cover_letter_flow and not contract.sudo().provider_signed_document_attachment_id:
                    contract.sudo().write({'provider_signed_document_attachment_id': att.id})
                contract.sudo()._sync_contract_key_documents_to_fileplan()
            addendum = self.sudo().addendum_id
            if addendum:
                att.sudo().write({
                    'res_model': 'ecdhs.contract.addendum',
                    'res_id': addendum.id,
                })
                if not addendum.sudo().signed_document_attachment_id:
                    addendum.sudo().write({'signed_document_attachment_id': att.id})
                addendum.sudo()._sync_signed_document_to_fileplan()
                addendum.sudo()._sync_completion_certificates_to_fileplan()
        except Exception:
            _logger.exception(
                'ECDHS sign: error attaching signed PDF (sign.request id=%s)',
                self.id,
            )

    def _refuse(self, refuser, refusal_reason):
        """After a signer refuses: sync signatory lines and mark contract or addendum."""
        super()._refuse(refuser, refusal_reason)
        try:
            addendum = self.sudo().addendum_id
            if addendum:
                addendum.sudo().write({'state': 'signature_refused'})
                addendum.sudo().message_post(
                    body=_('Signature refused by %s. Reason: %s',
                           refuser.name if refuser else _('Unknown'),
                           refusal_reason or _('No reason given')),
                    message_type='notification',
                )
                return
            contract = self.sudo().contract_id
            if contract:
                self._sync_contract_signatories()
                refusal_state = 'cover_letter_rejected' if self.is_cover_letter_flow else 'signature_refused'
                contract.sudo().write({'state': refusal_state})
                contract.sudo().message_post(
                    body=_('Signature refused by %s. Reason: %s',
                           refuser.name if refuser else _('Unknown'),
                           refusal_reason or _('No reason given')),
                    message_type='notification',
                )
        except Exception:
            _logger.exception(
                'ECDHS sign: error updating after refusal (sign.request id=%s)',
                self.id,
            )

    def _sync_contract_signatories(self):
        """Push sign.request.item states back to ecdhs.contract.signatory lines."""
        self.ensure_one()
        contract = self.sudo().contract_id
        for item in self.sudo().request_item_ids:
            partner = item.partner_id
            if not partner:
                continue
            # Try direct link first (most reliable), fall back to partner match
            sig_line = contract.signatory_ids.filtered(
                lambda s, i=item: s.sign_request_item_id == i
            )
            if not sig_line:
                sig_line = contract.signatory_ids.filtered(
                    lambda s, p=partner: (
                        (s.is_service_provider and s.partner_id == p)
                        or (not s.is_service_provider
                            and s.user_id and s.user_id.partner_id == p)
                    )
                )
            if not sig_line:
                continue
            if item.state == 'completed':
                sig_line[:1].sudo().write({
                    'status': 'Signed',
                    'date': fields.Datetime.now(),
                    'sign_initials': partner.avatar_128,
                })
            elif item.state == 'canceled':
                sig_line[:1].sudo().write({'status': 'Declined'})

    def action_request_changes(self, requested_change, requester=None):
        """Provider requests contract updates/changes before signing (7.2).

        Creates a change request record and updates contract state to 'provider_changes_requested'.
        Keeps the sign request open for eventual acceptance or closure.
        """
        self.ensure_one()
        try:
            contract = self.sudo().contract_id
            if not contract:
                _logger.warning(
                    'ECDHS sign: cannot request changes - no contract linked '
                    '(sign.request id=%s)', self.id
                )
                return False

            if not requested_change or not requested_change.strip():
                _logger.error(
                    'ECDHS sign: cannot request changes - reason is empty '
                    '(sign.request id=%s)', self.id
                )
                return False

            # Create a change request record
            change_request = self.env['ecdhs.contract.change.request'].sudo().create({
                'contract_id': contract.id,
                'section_reference': _('Contract Terms (via Digital Signature)'),
                'requested_change': requested_change.strip(),
                'submitted_by': 'provider',
                'status': 'submitted',
                'requested_on': fields.Datetime.now(),
            })

            # Update contract state to track pending changes
            if contract.state not in ('provider_changes_requested', 'signature_refused'):
                contract.sudo().write({'state': 'provider_changes_requested'})

            # Log the change request in contract chatter
            requester_name = requester.name if requester else _('Service Provider')
            contract.sudo().message_post(
                body=_('%(requester)s has requested changes before signing:\n'
                       '<strong>%(change)s</strong>\n\n'
                       'This contract is now in "Changes Requested" status. '
                       'Please review and update accordingly.',
                       requester=requester_name,
                       change=requested_change.strip()),
                message_type='notification',
            )

            # Update signatory line status
            self._sync_contract_signatories()

            _logger.info(
                'ECDHS sign: provider requested changes via sign request %s '
                '(contract %s, change_request id=%s)',
                self.id, contract.name, change_request.id
            )

            return change_request

        except Exception as e:
            _logger.exception(
                'ECDHS sign: error recording change request (sign.request id=%s): %s',
                self.id, str(e)
            )
            return False


# ─────────────────────────────────────────────────────────────────────────────
# sign.request.item  –  update the contract signatory line in real time after
#                       each individual signer completes their signature
# ─────────────────────────────────────────────────────────────────────────────

class SignRequestItem(models.Model):
    _inherit = 'sign.request.item'

    def _post_fill_request_item(self):
        """Called immediately after a signer completes all fields."""
        super()._post_fill_request_item()
        req = self.sign_request_id
        if not req.contract_id:
            return
        if self.state != 'completed':
            return
        partner = self.partner_id
        contract = req.contract_id
        # Use the direct link first, then fall back to partner matching
        sig_line = contract.signatory_ids.filtered(
            lambda s, i=self: s.sign_request_item_id == i
        )
        if not sig_line:
            sig_line = contract.signatory_ids.filtered(
                lambda s, p=partner: (
                    (s.is_service_provider and s.partner_id == p)
                    or (not s.is_service_provider
                        and s.user_id and s.user_id.partner_id == p)
                )
            )
        if sig_line:
            sig_line[:1].sudo().write({
                'status': 'Signed',
                'date': fields.Datetime.now(),
                'sign_initials': partner.avatar_128,
            })


# ─────────────────────────────────────────────────────────────────────────────
# sign.send.request  –  pre-populate signers from contract signatory sequence
#                       enforce signing order (SP first) by default
#                       link the new sign.request back to the contract
# ─────────────────────────────────────────────────────────────────────────────

class SignSendRequest(models.TransientModel):
    _inherit = 'sign.send.request'

    mail_template_message_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain="[('model', '=', 'ecdhs.contract')]",
        help="Pick a mail template to auto-fill the signature request message.",
    )
    mail_template_cc_id = fields.Many2one(
        'mail.template',
        string='CC Email Template',
        domain="[('model', '=', 'ecdhs.contract')]",
        help="Pick a mail template to auto-fill the contacts-in-copy message.",
    )

    def _resolve_contract_for_template(self):
        """Return the ecdhs.contract linked to the current sign template, if any."""
        tmpl = self.template_id
        if not tmpl:
            return False
        if tmpl.contract_id:
            return tmpl.contract_id
        if tmpl.addendum_id:
            return tmpl.addendum_id.contract_id
        return False

    def _get_contract_signer_commands(self, template, contract, set_sign_order=True):
        """Build signer command values from contract signatories for this template.

        Guarantees one signer entry per role used in the sign template whenever at
        least one valid partner candidate exists.
        """
        # Keep role order stable based on the template fields placement.
        template_roles = []
        seen_role_ids = set()
        for item in template.sign_item_ids.sorted('id'):
            role = item.responsible_id
            if role and role.id not in seen_role_ids:
                template_roles.append(role)
                seen_role_ids.add(role.id)

        if not template_roles:
            return []

        is_cover_letter = bool(template.is_cover_letter_flow)
        all_sigs = contract.signatory_ids.sorted('sequence')
        if is_cover_letter:
            all_sigs = all_sigs.filtered(lambda s: not s.is_service_provider and s.user_id)

        candidates = []
        for sig in all_sigs:
            if sig.is_service_provider:
                partner = contract.service_provider_id or sig.partner_id
            else:
                partner = sig.user_id.partner_id if sig.user_id else False
            if not partner:
                continue
            role_name = (sig.role_designation or (
                'Service Provider' if sig.is_service_provider else 'Signatory'
            )).strip().lower()
            candidates.append({
                'partner': partner,
                'role_name': role_name,
            })

        if not candidates:
            return []

        role_assignments = {}
        used_candidate_idx = set()

        # 1) Exact role name match (case-insensitive)
        for role in template_roles:
            wanted = (role.name or '').strip().lower()
            for idx, cand in enumerate(candidates):
                if idx in used_candidate_idx:
                    continue
                if cand['role_name'] == wanted:
                    role_assignments[role.id] = cand['partner']
                    used_candidate_idx.add(idx)
                    break

        # 2) Fill remaining roles with any unused candidates (legacy template labels)
        unused_idx = [i for i in range(len(candidates)) if i not in used_candidate_idx]
        for role in template_roles:
            if role.id in role_assignments:
                continue
            if not unused_idx:
                break
            idx = unused_idx.pop(0)
            role_assignments[role.id] = candidates[idx]['partner']

        # 3) Final fallback: if roles still remain, reuse first candidate partner.
        # This avoids the generic Odoo validation error and lets users proceed.
        fallback_partner = candidates[0]['partner']
        for role in template_roles:
            if role.id not in role_assignments:
                role_assignments[role.id] = fallback_partner

        signer_vals = []
        for order, role in enumerate(template_roles, start=1):
            signer_vals.append((0, 0, {
                'role_id': role.id,
                'partner_id': role_assignments[role.id].id,
                'mail_sent_order': order if set_sign_order else 1,
            }))

        return signer_vals

    @api.onchange('mail_template_message_id')
    def _onchange_mail_template_message_id(self):
        tpl = self.mail_template_message_id
        if not tpl:
            return
        contract = self._resolve_contract_for_template()
        if contract:
            try:
                rendered = tpl._render_field('body_html', [contract.id])[contract.id]
                self.message = rendered
                return
            except Exception:
                pass
        self.message = tpl.body_html

    @api.onchange('mail_template_cc_id')
    def _onchange_mail_template_cc_id(self):
        tpl = self.mail_template_cc_id
        if not tpl:
            return
        contract = self._resolve_contract_for_template()
        if contract:
            try:
                rendered = tpl._render_field('body_html', [contract.id])[contract.id]
                self.message_cc = rendered
                return
            except Exception:
                pass
        self.message_cc = tpl.body_html

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        # Resolve the template being used
        template_id = res.get('template_id')
        if not template_id and self.env.context.get('active_model') == 'sign.template':
            template_id = self.env.context.get('active_id')
        if not template_id:
            return res

        template = self.env['sign.template'].browse(int(template_id))
        if not template.exists() or not (template.contract_id or template.addendum_id):
            return res

        # Resolve the contract to pull signatories from
        contract = template.contract_id or (
            template.addendum_id.contract_id if template.addendum_id else False
        )
        if not contract:
            return res

        # Always enforce signing order for contract/addendum signing ceremonies
        res['set_sign_order'] = True
        signer_vals = self._get_contract_signer_commands(template, contract, set_sign_order=True)

        if signer_vals:
            res['signer_ids'] = signer_vals

        # Auto-populate the email template picker and render the message body
        if template.is_cover_letter_flow:
            mail_tpl_xml_id = 'ecdhs_contract_management.mail_template_hod_cover_letter_sign_request'
        else:
            mail_tpl_xml_id = 'ecdhs_contract_management.mail_template_provider_sign_request'

        mail_tpl = self.env.ref(mail_tpl_xml_id, raise_if_not_found=False)
        if mail_tpl:
            res['mail_template_message_id'] = mail_tpl.id
            try:
                rendered = mail_tpl._render_field('body_html', [contract.id])[contract.id]
                res['message'] = rendered
            except Exception:
                res['message'] = mail_tpl.body_html

        return res

    @api.onchange('template_id', 'set_sign_order')
    def _onchange_template_id(self):
        """Replace native single-role current-user defaults with contract signatories."""
        super()._onchange_template_id()

        template = self.template_id
        if not template:
            return
        contract = template.contract_id or (
            template.addendum_id.contract_id if template.addendum_id else False
        )
        if not contract:
            return

        signer_vals = self._get_contract_signer_commands(
            template,
            contract,
            set_sign_order=bool(self.set_sign_order),
        )
        if signer_vals:
            self.signer_ids = [(5, 0, 0)] + signer_vals

        # Ensure signing order is always on for contract ceremonies
        self.set_sign_order = True

    def create_request(self):
        """After standard creation: store the sign.request on the contract or
        addendum and link each request_item back to the signatory line."""
        sign_request = super().create_request()

        template = self.template_id
        if not template:
            return sign_request

        # Set custom thank-you redirect on the sign template so signers land
        # on our branded page after completing their signature.
        try:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
            thank_you_url = (base_url.rstrip('/') + '/ecdhs/sign/thank-you') if base_url else ''
            if thank_you_url and not template.redirect_url:
                template.sudo().write({
                    'redirect_url': thank_you_url,
                    'redirect_url_text': _('Close'),
                })
        except Exception:
            _logger.exception('ECDHS sign: error setting redirect_url on template %s', template.id)

        # ── Addendum signing ───────────────────────────────────────────
        # Prioritize addendum in case template.contract_id is populated
        # from context defaults.
        if template.addendum_id:
            addendum = template.addendum_id
            sign_request.write({
                'addendum_id': addendum.id,
                'contract_id': False,
                'is_cover_letter_flow': bool(template.is_cover_letter_flow),
            })
            addendum.write({'sign_request_id': sign_request.id})

        # ── Contract signing ────────────────────────────────────────────
        elif template.contract_id:
            contract = template.contract_id
            sign_request.write({
                'contract_id': contract.id,
                'is_cover_letter_flow': bool(template.is_cover_letter_flow),
            })
            contract.write({'sign_request_id': sign_request.id})

            # Link each sign.request.item back to the matching contract signatory
            for item in sign_request.request_item_ids:
                partner = item.partner_id
                if not partner:
                    continue
                sig_line = contract.signatory_ids.filtered(
                    lambda s, p=partner: (
                        (s.is_service_provider and s.partner_id == p)
                        or (not s.is_service_provider
                            and s.user_id and s.user_id.partner_id == p)
                    )
                )
                if sig_line:
                    sig_line[:1].write({'sign_request_item_id': item.id})

            # Post chatter message to the contract
            try:
                self._post_sign_request_chatter(contract, sign_request)
            except Exception:
                _logger.exception(
                    'ECDHS sign: error posting chatter message for sign.request %s',
                    sign_request.id,
                )

        return sign_request

    def _post_sign_request_chatter(self, contract, sign_request):
        """Log the signature request send to the contract's chatter."""
        self.ensure_one()
        if not contract:
            return

        is_cover_letter = bool(sign_request.is_cover_letter_flow)
        flow_label = _('Cover Letter Signing') if is_cover_letter else _('Contract Signing')

        # Build signer list
        signers = ', '.join([
            item.partner_id.display_name
            for item in sign_request.request_item_ids
            if item.partner_id
        ])

        # Build message body with proper HTML
        body_html = '<p><strong>%s Request Sent</strong></p>' % flow_label
        body_html += '<p><strong>Signers:</strong> %s</p>' % signers

        if self.subject:
            body_html += '<p><strong>Subject:</strong> %s</p>' % self.subject

        if self.message:
            body_html += '<p><strong>Message:</strong></p>%s' % self.message

        wrapped_body = '<div data-ecdhs-green-mail="1" style="%s">%s</div>' % (
            _CHATTER_GREEN_BOX_STYLE,
            body_html,
        )

        contract.sudo().message_post(
            body=Markup(wrapped_body),
            subtype_xmlid='mail.mt_note',
        )
