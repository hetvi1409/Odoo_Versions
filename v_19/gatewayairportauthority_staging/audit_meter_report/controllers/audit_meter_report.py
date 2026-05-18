import io
from odoo import http, fields
from odoo.http import request, content_disposition
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
import base64
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)
import zipfile
from ast import literal_eval




class AuditExcelReportController(http.Controller):

    @http.route([
        '/audit_meter_report',
    ], type='http', auth="user", csrf=False)
    def get_audit_meter_report(self, **args):
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition',
                 content_disposition('Meter Audit Report' + '.xlsx'))
            ]
        )
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        # get data for the report.
        accounts_payable = []
        data = args
        report_sub_lines = []
        query = """"""

        # SELECT
        #                 auditor.id AS auditor_id,
        #                 partner.name,
        #                 COUNT(audit.id) AS total,
        #                 COUNT(CASE WHEN meter_condition.id = 1 THEN 1 ELSE NULL END) AS good_meter,
        #                 COUNT(meter_condition.id) AS can_audit,
        #                 0 AS no_access,
        #                 0 AS access_denied,
        #                 0 AS empty_stand,
        #                 COUNT(CASE WHEN meter_condition.id = 5 THEN 1 ELSE NULL END) AS no_electricity,
        #                 COUNT(CASE WHEN meter_condition.id = 2 THEN 1 ELSE NULL END) AS damaged_meter,
        #                 partner.city
        #             FROM
        #                 res_users AS auditor
        #             JOIN
        #                 res_partner AS partner
        #                 ON auditor.partner_id = partner.id
        #             LEFT JOIN
        #                 res_partner AS audit
        #                 ON audit.x_studio_meter_audit = 'true'
        #                 AND auditor.id = audit.user_id
        #             LEFT JOIN
        #                 x_meter_condition AS meter_condition
        #                 ON audit.x_studio_meter_condition = meter_condition.id
        #             WHERE
        #                 auditor.active = 'true'
        #             GROUP BY
        #                 auditor.id,
        #                 partner.id,
        #                 partner.name,
        #                 partner.city;
        request._cr.execute(query)
        report_by_order_details = request._cr.dictfetchall()
        report_sub_lines.append(report_by_order_details)
        report_lines = report_sub_lines
        # prepare excel sheet styles and formats
        head = workbook.add_format(
            {'font_size': 18, 'align': 'center', 'color': '#00008B',
             'bold': True})
        text_style = workbook.add_format({'font_size': '9px', })

        sheet = workbook.add_worksheet("Account")
        sheet.write(1, 0, 'Auditor', text_style)
        sheet.write(1, 1, 'Total', text_style)
        sheet.write(1, 2, 'Can Audit', text_style)
        sheet.write(1, 3, 'No Access', text_style)
        sheet.write(1, 4, 'Good Meter', text_style)
        sheet.write(1, 5, 'Damaged Meter', text_style)
        sheet.write(1, 6, 'Access Denied', text_style)
        sheet.write(1, 7, 'No Meter', text_style)
        sheet.write(1, 8, 'City', text_style)

        row = 2
        number = 1
        # write the report lines to the excel document
        for line in report_lines[0]:
            # sheet.set_row(row, 20)
            sheet.write(row, 0, line['name'], text_style)
            sheet.write(row, 1, line['total'], text_style)
            sheet.write(row, 2, line['can_audit'], text_style)
            sheet.write(row, 3, line['no_access'], text_style)
            sheet.write(row, 4, line['good_meter'], text_style)
            sheet.write(row, 5, line['damaged_meter'], text_style)
            sheet.write(row, 6, line['access_denied'], text_style)
            sheet.write(row, 7, line['no_electricity'], text_style)
            sheet.write(row, 8, line['city'], text_style)
            row += 1
            number += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response

    @http.route('/download/pdf_reports', type='http', auth='user')
    def download_pdf_reports(self, **kwargs):
        # Get the active_ids from the context
        docids = kwargs.get('docids')  # Adjust if needed for your context
        zip_filename = kwargs.get('filename')

        # Create in-memory ZIP
        zip_buffer = io.BytesIO()

        # Generate the ZIP file with individual images for each selected record
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            docs = request.env['res.partner'].browse(literal_eval(docids))  # Replace with your actual model

            for doc in docs:
                try:
                    
                    pdf = request.env['ir.actions.report'].with_context(force_report_rendering=True)._render_qweb_pdf(
                        'audit_meter_report.action_report_partner_custom', res_ids=doc.id)
                    # Extract PDF content and name
                    pdf_content = pdf[0]  # This is the bytes content of the PDF
                    pdf_name = f'report_{doc.id}.pdf'

                    # Fetch the binary image content for each docid
                    # image_content = doc.x_studio_property_image  # Assuming this contains the image data as bytes
                    # if not image_content:
                    #     raise ValueError(f"No image content found for document ID: {doc.id}")
                    # 
                    # try:
                    #     image_content = base64.b64decode(image_content)
                    # except Exception as decode_error:
                    #     raise ValueError(f"Error decoding base64 content for docid {doc.id}: {decode_error}")
                    # 
                    # # Define the image name in the ZIP
                    # image_name = f'image_{doc.id}.png'  # Adjust the extension as needed

                    # Add the image directly to the ZIP archive
                    zf.writestr(pdf_name, pdf_content)

                except Exception as e:
                    # Log the error or handle it appropriately
                    _logger.error(f"Error adding image for docid {doc.id}: {e}")

        # Ensure to seek back to the start of the buffer before returning
        zip_buffer.seek(0)

        # Serve the ZIP file for download
        return request.make_response(
            zip_buffer.getvalue(),
            headers=[
                ('Content-Type', 'application/zip'),
                ('Content-Disposition', f'attachment; filename="{zip_filename}"'),
            ]
        )


