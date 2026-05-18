import base64
import io
from io import BytesIO
from PyPDF2 import PdfFileReader, PdfFileWriter
import logging
_logger = logging.getLogger(__name__)
from odoo import api, models


class TenderReportTemplate(models.AbstractModel):
    """ Pdf reports """
    _name = 'report.tender_management.tender_report_template'
    _description = 'Tender Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """ The method collects task data to the pdf report. """
        tenders = self.env['tender.tender'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'tender.tender',
            'docs': tenders,
            'data': data,
        }


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        res = super()._render_qweb_pdf(report_ref, res_ids, data)
        original_pdf_data = res[0]
        original_pdf_reader = PdfFileReader(io.BytesIO(original_pdf_data))
        writer = PdfFileWriter()

        # Append the original PDF pages first
        for page_num in range(original_pdf_reader.getNumPages()):
            writer.addPage(original_pdf_reader.getPage(page_num))

        # Collect pages from tender documents
        if report_ref == 'tender_management.tender_report_template':
            tenders = self.env['tender.tender'].browse(res_ids)
            for tender in tenders:
                for document in tender.document_ids:
                    if document.file:
                        try:
                            file_data = base64.b64decode(document.file)
                            pdf_reader = PdfFileReader(BytesIO(file_data))
                            for page_num in range(pdf_reader.numPages):
                                writer.addPage(pdf_reader.getPage(page_num))
                            _logger.info(
                                f"Processed document {document.name} with {pdf_reader.numPages} pages.")
                        except Exception as e:
                            _logger.error(
                                f"Error processing document {document.name}: {str(e)}")

        # Create a new attachment for the merged PDF
        merged_pdf = BytesIO()
        writer.write(merged_pdf)
        merged_pdf.seek(0)

        with io.BytesIO() as result_stream:
            writer.write(result_stream)
            combined_pdf_content = result_stream.getvalue()

        return combined_pdf_content, 'pdf'
