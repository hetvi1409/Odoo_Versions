# -*- coding: utf-8 -*-
# Eastern Cape Department of Human Settlements
# Contract Management – Public Provider Portal Controller

import logging

from odoo import fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ContractSignThankYouController(http.Controller):
    """Serves the custom thank-you page after a signer completes a contract."""

    @http.route(
        '/ecdhs/sign/thank-you',
        type='http',
        auth='public',
        website=False,
        sitemap=False,
    )
    def sign_thank_you(self, **kwargs):
        return request.render(
            'ecdhs_contract_management.sign_thank_you_page',
            {},
            headers={'X-Frame-Options': 'SAMEORIGIN'},
        )


class ContractPortalController(http.Controller):
    """
    Provides a token-authenticated, login-free portal for service providers to:
      1. Read the draft contract terms in full.
      2. Sign each required section by entering their full name.
      3. View the signed status after submission.

    URL pattern: /contract/review/<contract_id>/<access_token>
    The access_token is a 32-char UUID hex stored on the contract record.
    Backend users can also open this URL to review the contract and signatures.
    """

    @http.route(
        '/contract/review/<int:contract_id>/<string:access_token>',
        type='http',
        auth='public',
        methods=['GET', 'POST'],
        csrf=False,
        save_session=False,
    )
    def contract_review(self, contract_id, access_token, **kwargs):
        # ── Token authentication ────────────────────────────────────────────
        Contract = request.env['ecdhs.contract'].sudo()
        contract = Contract.browse(contract_id)
        if not contract.exists() or contract.provider_access_token != access_token:
            return request.not_found()

        error = None
        success = None

        # ── Handle provider POST actions ────────────────────────────────────
        if request.httprequest.method == 'POST':
            action_type = (kwargs.get('provider_action') or 'sign').strip()
            now = fields.Datetime.now()

            if action_type == 'request_changes':
                section_reference = (kwargs.get('section_reference') or '').strip()
                requested_change = (kwargs.get('requested_change') or '').strip()
                if contract.provider_review_state not in (
                    'sent_for_review',
                    'revised_sent',
                    'provider_changes_requested',
                ):
                    error = 'Change requests are only allowed while a draft is under provider review.'
                elif not section_reference:
                    error = 'Please specify the section/reference where changes are required.'
                elif not requested_change:
                    error = 'Please describe the requested changes before submitting.'
                else:
                    request.env['ecdhs.contract.change.request'].sudo().create({
                        'contract_id': contract.id,
                        'section_reference': section_reference,
                        'requested_change': requested_change,
                        'submitted_by': 'provider',
                        'status': 'submitted',
                        'requested_on': now,
                        'due_date': contract.provider_review_due_date,
                    })
                    contract.write({
                        'provider_review_state': 'provider_changes_requested',
                        'provider_last_response_datetime': now,
                    })
                    contract.message_post(
                        body='Provider requested draft changes via the portal. '
                             'Section: <strong>%s</strong>.' % (section_reference,),
                        subtype_xmlid='mail.mt_note',
                    )
                    success = 'Your change request has been submitted successfully.'

            elif action_type == 'reject':
                rejection_reason = (kwargs.get('rejection_reason') or '').strip()
                if contract.provider_review_state not in ('sent_for_review', 'revised_sent', 'provider_changes_requested'):
                    error = 'Rejection is only allowed while a draft is under provider review.'
                elif not rejection_reason:
                    error = 'Please provide a rejection reason before submitting.'
                else:
                    request.env['ecdhs.contract.change.request'].sudo().create({
                        'contract_id': contract.id,
                        'section_reference': 'Entire Draft',
                        'requested_change': rejection_reason,
                        'submitted_by': 'provider',
                        'status': 'rejected',
                        'requested_on': now,
                        'due_date': contract.provider_review_due_date,
                    })
                    contract.write({
                        'provider_review_state': 'provider_rejected',
                        'provider_last_response_datetime': now,
                    })
                    contract.message_post(
                        body='Provider rejected the draft via portal. Reason: <strong>%s</strong>.' % (
                            rejection_reason,
                        ),
                        subtype_xmlid='mail.mt_note',
                    )
                    success = 'Your draft rejection has been recorded.'

            elif action_type == 'accept':
                if contract.provider_review_state not in ('sent_for_review', 'revised_sent'):
                    error = 'Draft acceptance is only available while a draft is under active provider review.'
                else:
                    contract.write({
                        'provider_review_state': 'provider_accepted',
                        'provider_acceptance_datetime': now,
                        'provider_last_response_datetime': now,
                    })
                    contract.message_post(
                        body='Provider <strong>%s</strong> confirmed acceptance of draft v%s via the provider portal on %s.' % (
                            contract.service_provider_id.name,
                            contract.draft_version,
                            fields.Datetime.to_string(now),
                        ),
                        subtype_xmlid='mail.mt_note',
                    )
                    success = 'Your acceptance of this draft has been recorded. The ECDHS team has been notified.'

            else:
                signatory_name = (kwargs.get('signatory_name') or '').strip()
                if not signatory_name:
                    error = 'Please enter your full legal name before signing.'
                else:
                    pending = contract.signature_section_ids.filtered(
                        lambda s: s.provider_signature_required and not s.provider_signed
                    )
                    if not pending:
                        error = 'All required sections have already been signed.'
                    else:
                        pending.write({
                            'provider_signed': True,
                            'provider_signed_on': now,
                            'provider_signatory_name': signatory_name,
                        })
                        # Flush all env caches so the next reads hit the database
                        contract.env.invalidate_all()
                        # Auto-transition: check ONLY provider signatures.
                        # Internal signatures are handled separately in the backend
                        # and must not block the provider-accepted gate.
                        provider_required = contract.signature_section_ids.filtered(
                            lambda s: s.provider_signature_required
                        )
                        all_provider_done = bool(provider_required) and all(
                            s.provider_signed for s in provider_required
                        )
                        if all_provider_done and contract.provider_review_state in (
                            'sent_for_review', 'revised_sent', 'provider_changes_requested'
                        ):
                            contract.write({
                                'provider_review_state': 'provider_accepted',
                                'provider_acceptance_datetime': now,
                                'provider_last_response_datetime': now,
                            })
                            contract.message_post(
                                body='Provider <strong>%s</strong> has signed all required contract sections '
                                     'via the provider portal on %s.' % (
                                         signatory_name,
                                         fields.Datetime.to_string(now),
                                     ),
                                subtype_xmlid='mail.mt_note',
                            )
                        success = (
                            'Your signature has been recorded successfully. '
                            'Signed by: %s.' % signatory_name
                        )

        # ── Build context for template ──────────────────────────────────────
        all_sections = contract.signature_section_ids.sorted('sequence')
        provider_pending = all_sections.filtered(
            lambda s: s.provider_signature_required and not s.provider_signed
        )
        provider_signed = all_sections.filtered(
            lambda s: s.provider_signature_required and s.provider_signed
        )
        all_provider_signed = bool(provider_signed) and not bool(provider_pending)

        prs = contract.provider_review_state
        values = {
            'contract': contract,
            'access_token': access_token,
            'all_sections': all_sections,
            'provider_pending': provider_pending,
            'provider_signed': provider_signed,
            'all_provider_signed': all_provider_signed,
            # Forms are only interactive when the draft is actively under review
            'can_submit_feedback': prs in ('sent_for_review', 'revised_sent'),
            # Locked states — show informative banners instead of action forms
            'changes_pending': prs == 'provider_changes_requested',
            'draft_rejected': prs == 'provider_rejected',
            'error': error,
            'success': success,
        }
        return request.render(
            'ecdhs_contract_management.portal_contract_review', values
        )
