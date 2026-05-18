import io
import zipfile
import base64
from odoo import fields, http
from odoo.http import request, content_disposition


class TenderInformation(http.Controller):

    @http.route('/published_tenders', auth='public', website=True, csrf=True,
                methods=['GET', 'POST'])
    def tender_information(self, **kw):
        """Route to display published tenders."""
        user = request.env.user
        domain = [
            ('is_tender_published', '=', True)]  # Only search published tenders

        # Adding domain based on bid type selection
        print("kw-----", kw)
        if 'searchBidTypes' in kw and kw['searchBidTypes']:
            bid_type = kw['searchBidTypes']
            domain.append(('type', '=', bid_type))

        if 'searchRefNo' in kw:
            search_ref_no = kw.get('searchRefNo')
            if search_ref_no:
                domain.append(('sequence_number', 'ilike', search_ref_no))

        # Adding domain based on category
        if 'categories' in kw and kw['categories']:
            category_id = kw['categories']
            if category_id:
                domain.append(('category_id', '=', int(category_id)))

        # Adding domain based on status
        if 'searchStatus' in kw and kw['searchStatus']:
            status = kw['searchStatus']
            if status:
                if status == 'CONCLUDED':
                    domain.append(('state', '=', 'closed'))
                elif status == 'CANCEL_APPROVED':
                    domain.append(('state', '=', 'open'))

        # Adding domain based on open date range
        if 'searchPublishDateFrom' in kw and 'searchPublishDateTo' in kw:
            open_date_from = kw.get('searchPublishDateFrom')
            open_date_to = kw.get('searchPublishDateTo')
            if open_date_from and open_date_to:
                domain.append(('start_time', '>=', open_date_from))
                domain.append(('start_time', '<=', open_date_to))
            elif open_date_from:
                domain.append(('start_time', '>=', open_date_from))
            elif open_date_to:
                domain.append(('start_time', '<=', open_date_to))

        # Adding domain based on closing date range
        if 'searchClosingDateFrom' in kw and 'searchClosingDateTo' in kw:
            closing_date_from = kw.get('searchClosingDateFrom')
            closing_date_to = kw.get('searchClosingDateTo')
            if closing_date_from and closing_date_to:
                domain.append(('closing_date', '>=', closing_date_from))
                domain.append(('closing_date', '<=', closing_date_to))
            elif closing_date_from:
                domain.append(('closing_date', '>=', closing_date_from))
            elif closing_date_to:
                domain.append(('closing_date', '<=', closing_date_to))

        tenders_information = request.env['tender.tender'].search(domain)

        values = {
            'tenders_information': tenders_information,
            'user': user,
        }
        return http.request.render('tender_management.tender_information',
                                   values)

    @http.route('/tender/<model("tender.tender"):tender>', type='http', auth='user',
                website=True)
    def tender_detail(self, tender, **kwargs):
        """Route to display detailed information about a tender."""
        # print(tender_id, 'aaaaaa')
        # tender = request.env['tender.tender'].sudo().browse(tender_id)

        if not tender.exists() :
            return request.render('tender_management.error_template', {
                'error_message': 'The tender you are looking for does not exist or is not published.'
            })

        # Warning message for non-logged-in users
        warning_message = ''
        if request.env.user._is_public():
            warning_message = 'Please log in before proceeding to submit bids.'

        return request.render('tender_management.tender_detail_template', {
            'tender': tender,
            'warning_message': warning_message
        })

    @http.route('/bid_submit/<int:tender_id>', type='http', auth='public',
                website=True)
    def bid_submit(self, tender_id, **kwargs):
        """Route to display detailed information about a tender."""
        tender = request.env['tender.tender'].sudo().browse(tender_id)
        if not tender.exists():
            return request.render('tender_management.error_template', {
                'error_message': 'The tender you are looking for does not exist.'
            })

        return request.render('tender_management.bid_submission_template',
                              {'tender': tender})

    @http.route('/tender/timer', type='json', auth='public', csrf=False)
    def auction_timer(self, **kwargs):
        tender = kwargs.get('tender')
        if tender:
            tender = request.env['tender.tender'].sudo().browse(int(tender))
            values = {
                'start_time': tender.start_time,
                'end_time': fields.Datetime.context_timestamp(tender,
                                                              tender.closing_date),
                'state': tender.state,
            }
            return values

    @http.route('/submit_bid', auth='public', website=True, csrf=False)
    def submit_bid(self, **kw):
        tender_id = kw.get('tender_id')
        user = request.env.user
        # Fetch the tender record
        tender = request.env['tender.tender'].sudo().browse(int(tender_id))
        # Create a new tender bid record
        bid = request.env['tender.bid'].sudo().create({
            'tender_id': tender.id,
            'vendor_id': user.partner_id.id,
            'bid_type': tender.type
            # Assuming `type` is a field in tender.tender that represents the tender type
        })
        # Handle document uploads
        if 'bid_documents_ids' in request.httprequest.files:
            documents = request.httprequest.files.getlist('bid_documents_ids')
            for document in documents:
                data = document.read()
                name = document.filename
                # Create tender.document record

                attachment = request.env['ir.attachment'].sudo().create({
                    'name': name,
                    'type': 'binary',
                    'datas': base64.b64encode(data),
                    'res_model': 'tender.bid',
                    'res_id': bid.id,
                    'mimetype': 'application/pdf',
                })
                request.env['tender.document'].sudo().create({
                    'name': name,
                    # 'file': base64.b64encode(data),
                    'tender_id': int(tender_id),
                    'bid_id': bid.id,
                    'attachment_id': attachment.id
                })

                folder_id = request.env[
                    'ir.config_parameter'].sudo().get_param(
                    'tender_management.folder_id')
                document = request.env['documents.document'].sudo().create({
                    'name': attachment.name,
                    'attachment_id': attachment.id,
                    'folder_id': int(folder_id) if folder_id else "",
                    'res_model': 'tender.bid',
                    'res_id': bid.id,
                })


        # Call the action_submit method on the newly created bid to change its state
        bid.sudo().action_submit()
        # Redirect to the thank-you page with the bid reference number
        return http.request.render('tender_management.thank_you_page', {
            'reference_number': bid.name
            # Pass the bid reference number to the template
        })

    @http.route('/download/document/<model("tender.document"):document_id>',
                auth='public', website=True)
    def download_document(self, document_id, **kw):
        if document_id:
            file_content = base64.b64decode(document_id.file)
            file_name = document_id.name
            return request.make_response(file_content, [
                ('Content-Type', 'application/octet-stream'),
                (
                    'Content-Disposition',
                    'attachment; filename="%s"' % file_name),
            ])
        return request.not_found()

    @http.route('/download/all_documents/<model("tender.tender"):tender_id>',
                auth='public', website=True)
    def download_all_documents(self, tender_id, **kw):
        # if tender_id and tender_id.document_ids:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w',
                             zipfile.ZIP_DEFLATED) as zip_file:
            for document in tender_id.document_ids:
                file_content = base64.b64decode(document.file)
                zip_file.writestr(document.name, file_content)
        zip_buffer.seek(0)
        return request.make_response(zip_buffer.getvalue(), [
            ('Content-Type', 'application/zip'),
            ('Content-Disposition',
             'attachment; filename="All_Documents_%s.zip"' % tender_id.name),
        ])
        return request.not_found()

    @http.route('/print_bid1/<int:tender_id>', type='http',
                auth='public', website=True)
    def print_bid(self, tender_id):
        tender = request.env['tender.tender'].browse(int(tender_id))
        pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
            'tender_management.tender_tender_report_action', tender.id, )[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', content_disposition('Tender.pdf')),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)
