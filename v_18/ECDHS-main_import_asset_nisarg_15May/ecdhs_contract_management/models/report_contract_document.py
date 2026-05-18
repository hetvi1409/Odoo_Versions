# -*- coding: utf-8 -*-
# Eastern Cape Department of Human Settlements
# PDF merge override: appends annexures and addenda directly after the
# main contract body, giving:
#   [Contract body]
#   [Cover page: ANNEXURE A]  ← generated from QWeb cover template
#   [Annexure A PDF pages]    ← uploaded attachment
#   [Cover page: ANNEXURE B]
#   [Annexure B PDF pages]
#   [Cover page: ADDENDUM A]
#   [Addendum A content (change_description)]
#   [Cover page: ADDENDUM B]
#   [Addendum B content]
#   …

import base64
import io
import logging

from odoo import models

_logger = logging.getLogger(__name__)

_CONTRACT_REPORT = 'ecdhs_contract_management.report_contract_document_template'
_CONTRACT_DRAFT_REPORT = 'ecdhs_contract_management.report_contract_document_draft_template'
_COVER_REPORT    = 'ecdhs_contract_management.report_annexure_cover_template'
_ADDENDUM_COVER_REPORT = 'ecdhs_contract_management.report_addendum_cover_template'
_ADDENDUM_CONTENT_REPORT = 'ecdhs_contract_management.report_addendum_content_template'


def _get_pdf_merger():
    """Return (PdfWriter, PdfReader) from pypdf or PyPDF2, or (None, None)."""
    try:
        from pypdf import PdfWriter, PdfReader   # pypdf ≥ 3 (Odoo 17/18 default)
        return PdfWriter, PdfReader
    except ImportError:
        pass
    try:
        from PyPDF2 import PdfWriter, PdfReader  # legacy fallback
        return PdfWriter, PdfReader
    except ImportError:
        pass
    return None, None


class IrActionsReportContractDocument(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        result, fmt = super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)

        # Only intercept main contract document reports (standard and draft preview)
        try:
            report = self._get_report(report_ref)
            if report.report_name not in (_CONTRACT_REPORT, _CONTRACT_DRAFT_REPORT):
                return result, fmt
        except Exception:
            return result, fmt

        if fmt != 'pdf' or not res_ids:
            return result, fmt

        PdfWriter, PdfReader = _get_pdf_merger()
        if not PdfWriter:
            _logger.warning(
                'ecdhs_contract_management: pypdf / PyPDF2 not available – '
                'addenda/annexure PDFs will not be appended to the contract report.'
            )
            return result, fmt

        contracts = self.env['ecdhs.contract'].browse(res_ids)

        # Collect all addenda in sequence order
        all_addenda = []
        for contract in contracts:
            for addendum in contract.addendum_ids.sorted(key=lambda r: (r.sequence, r.id)):
                all_addenda.append(addendum)

        # Collect all annexures that have an uploaded attachment (in sequence order)
        all_annexures = []
        for contract in contracts:
            for ann in contract.annexure_document_upload_ids.sorted(
                    key=lambda r: (r.sequence, r.id)):
                all_annexures.append(ann)

        if not all_addenda and not all_annexures:
            return result, fmt

        # Build merged PDF
        try:
            writer = PdfWriter()

            # 1. Add all pages from the base contract PDF
            base_reader = PdfReader(io.BytesIO(result))
            for page in base_reader.pages:
                writer.add_page(page)

            # 2. For each annexure: cover page PDF + attachment PDF
            for ann in all_annexures:
                # --- Cover page (generated via the annexure cover QWeb template) ---
                try:
                    cover_bytes, _ = self.env['ir.actions.report']._render_qweb_pdf(
                        _COVER_REPORT,
                        res_ids=[ann.id],
                    )
                    cover_reader = PdfReader(io.BytesIO(cover_bytes))
                    for page in cover_reader.pages:
                        writer.add_page(page)
                except Exception as exc:
                    _logger.warning(
                        'ecdhs_contract_management: could not render cover for %s – %s',
                        ann.annexure_sequence_name, exc,
                    )

                # --- Uploaded annexure PDF (from ir.attachment) ---
                if ann.attachment_id and ann.attachment_id.datas:
                    try:
                        pdf_bytes = base64.b64decode(ann.attachment_id.datas)
                        ann_reader = PdfReader(io.BytesIO(pdf_bytes))
                        for page in ann_reader.pages:
                            writer.add_page(page)
                    except Exception as exc:
                        _logger.warning(
                            'ecdhs_contract_management: could not append PDF for %s – %s',
                            ann.name, exc,
                        )

            # 3. For each addendum: cover page PDF + content page PDF
            for addendum in all_addenda:
                try:
                    add_cover_bytes, _ = self.env['ir.actions.report']._render_qweb_pdf(
                        _ADDENDUM_COVER_REPORT,
                        res_ids=[addendum.id],
                    )
                    add_cover_reader = PdfReader(io.BytesIO(add_cover_bytes))
                    for page in add_cover_reader.pages:
                        writer.add_page(page)
                except Exception as exc:
                    _logger.warning(
                        'ecdhs_contract_management: could not render addendum cover for %s – %s',
                        addendum.name, exc,
                    )

                try:
                    add_content_bytes, _ = self.env['ir.actions.report']._render_qweb_pdf(
                        _ADDENDUM_CONTENT_REPORT,
                        res_ids=[addendum.id],
                    )
                    add_content_reader = PdfReader(io.BytesIO(add_content_bytes))
                    for page in add_content_reader.pages:
                        writer.add_page(page)
                except Exception as exc:
                    _logger.warning(
                        'ecdhs_contract_management: could not render addendum content for %s – %s',
                        addendum.name, exc,
                    )

            output = io.BytesIO()
            writer.write(output)
            result = output.getvalue()

        except Exception as exc:
            _logger.error(
                'ecdhs_contract_management: PDF merge failed, returning base report – %s',
                exc,
            )

        return result, fmt
