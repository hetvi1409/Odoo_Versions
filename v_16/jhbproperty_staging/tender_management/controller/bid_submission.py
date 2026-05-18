import io
import zipfile
import base64
import time
import hmac
import hashlib
from datetime import datetime
from odoo import fields, http
from odoo.http import request, content_disposition


class TenderInformation(http.Controller):

    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB per file
    ALLOWED_UPLOAD_EXTENSIONS = {'.pdf', '.doc', '.docx'}
    _rate_limit_store = {}
    BLOCKED_BID_STATES = {'closed', 'adjudication_in_progress', 'awarded'}

    def _archive_years(self):
        current_year = datetime.utcnow().year
        return [current_year - 1, current_year - 2, current_year - 3]

    def _int_config(self, key, default_value):
        value = request.env['ir.config_parameter'].sudo().get_param(key, str(default_value))
        try:
            return int(value)
        except (TypeError, ValueError):
            return default_value

    def _timer_secret(self):
        return request.env['ir.config_parameter'].sudo().get_param('database.secret', '') or ''

    def _get_timer_token(self, tender_id):
        payload = str(int(tender_id)).encode('utf-8')
        return hmac.new(self._timer_secret().encode('utf-8'), payload, hashlib.sha256).hexdigest()

    def _is_valid_timer_token(self, tender_id, token):
        if not token:
            return False
        expected = self._get_timer_token(tender_id)
        return hmac.compare_digest(expected, token)

    def _is_rate_limited(self, bucket_name, max_requests, window_seconds):
        ip = request.httprequest.remote_addr or 'unknown'
        now = time.time()
        bucket_key = f"{bucket_name}:{ip}"
        bucket = self._rate_limit_store.get(bucket_key, [])
        window_start = now - window_seconds
        bucket = [ts for ts in bucket if ts >= window_start]
        if len(bucket) >= max_requests:
            self._rate_limit_store[bucket_key] = bucket
            return True
        bucket.append(now)
        self._rate_limit_store[bucket_key] = bucket
        return False

    def _is_internal_user(self):
        return request.env.user.has_group('base.group_user')

    def _can_access_tender_documents(self, tender):
        return bool(tender and tender.exists() and (tender.website_published or self._is_internal_user()))

    def _can_access_bid_documents(self, bid):
        if not bid or not bid.exists():
            return False
        if self._is_internal_user():
            return True
        return bool(request.env.user and not request.env.user._is_public() and bid.vendor_id == request.env.user.partner_id)

    def _validate_uploads(self, documents):
        for document in documents:
            name = (document.filename or '').strip()
            if not name:
                continue

            ext = '.' + name.rsplit('.', 1)[-1].lower() if '.' in name else ''
            if ext not in self.ALLOWED_UPLOAD_EXTENSIONS:
                return "Only PDF, DOC, and DOCX files are allowed."

            size = 0
            if getattr(document, 'content_length', None):
                size = int(document.content_length or 0)
            else:
                current_pos = document.stream.tell()
                document.stream.seek(0, io.SEEK_END)
                size = document.stream.tell()
                document.stream.seek(current_pos)

            if size > self.MAX_UPLOAD_SIZE:
                return "Each uploaded file must be smaller than 10MB."
        return False


    @http.route(['/tenders'], auth='public', website=True, csrf=True,
                methods=['GET'])
    def tenders_details(self, **kw):
        """Route to display published tenders."""
        user = request.env.user
        values = {
            'user': user,
            'archive_years': self._archive_years(),
        }
        return http.request.render('tender_management.tender_information_list',
                                   values)

    @http.route(['/tenders-rfqs', '/tenders-rfqs/page/<int:page>'], auth='public', website=True, csrf=True)
    def tender_rfq_details(self, page=1, **kwargs):
        """Render RFQ tenders on website."""
        tender_model = request.env['tender.tender']
        domain = [
            ('type', '=', 'rfq'),
            ('website_published', '=', True),
            ('state', 'not in', ['adjudication_in_progress', 'awarded']),
        ]
        if kwargs.get('searchRefNo'):
            domain.append(('name', 'ilike', kwargs.get('searchRefNo')))
        # Pagination setup
        items_per_page = 10
        total = tender_model.search_count(domain)

        pager = request.website.pager(url='/tenders-rfqs/', total=total, page=page, step=items_per_page, scope=10)

        rfqs = tender_model.search(domain, limit=items_per_page, offset=pager['offset'], order='start_time desc, id desc')
        return request.render("tender_management.tender_rfq_information_list", {
            'rfqs': rfqs,
            'pager': pager,
            'page': page,
            'searchRefNo': kwargs.get('searchRefNo'),
            'archive_years': self._archive_years(),
        })

    @http.route(['/tenders-rfps', '/tenders-rfps/page/<int:page>'], auth='public', website=True, csrf=True)
    def tender_rfp_details(self, page=1, **kwargs):
        """Render RFP tenders on website."""
        tender_model = request.env['tender.tender']
        domain = [
            ('type', '=', 'rfp'),
            ('website_published', '=', True),
            ('state', 'not in', ['adjudication_in_progress', 'awarded']),
        ]
        if kwargs.get('searchRefNo'):
            domain.append(('name', 'ilike', kwargs.get('searchRefNo')))
        # Pagination setup
        items_per_page = 10
        total = tender_model.search_count(domain)

        pager = request.website.pager(url='/tenders-rfps/', total=total, page=page, step=items_per_page, scope=10)

        rfps = tender_model.search(domain, limit=items_per_page, offset=pager['offset'], order='start_time desc, id desc')
        return request.render("tender_management.tender_rfp_information_list", {
            'rfps': rfps,
            'pager': pager,
            'page': page,
            'searchRefNo': kwargs.get('searchRefNo'),
            'archive_years': self._archive_years(),
        })

    @http.route([
        '/tenders-archive',
        '/tenders-archive/page/<int:page>',
        '/tenders-archive/<int:year>',
        '/tenders-archive/<int:year>/page/<int:page>',
    ], auth='public', website=True, csrf=True)
    def tender_archive_information_list(self, year=None, page=1, **kwargs):
        """Archive tenders by opening year for the previous 3 years."""
        tender_model = request.env['tender.tender']
        current_year = datetime.utcnow().year
        archive_years = [current_year - 1, current_year - 2, current_year - 3]

        selected_year = year if year in archive_years else archive_years[0]
        year_start = '%s-01-01 00:00:00' % selected_year
        next_year_start = '%s-01-01 00:00:00' % (selected_year + 1)

        domain = [
            ('website_published', '=', True),
            ('start_time', '>=', year_start),
            ('start_time', '<', next_year_start),
        ]
        if kwargs.get('searchRefNo'):
            query = kwargs.get('searchRefNo')
            domain += ['|', ('name', 'ilike', query), ('sequence_number', 'ilike', query)]

        items_per_page = 10
        total = tender_model.search_count(domain)
        pager = request.website.pager(
            url='/tenders-archive/%s' % selected_year,
            total=total,
            page=page,
            step=items_per_page,
            scope=10,
        )

        archive_tenders = tender_model.search(
            domain,
            limit=items_per_page,
            offset=pager['offset'],
            order='start_time desc, id desc'
        )
        return request.render("tender_management.tender_archive_information_list", {
            'archive_tenders': archive_tenders,
            'archive_years': archive_years,
            'selected_archive_year': selected_year,
            'pager': pager,
            'page': page,
            'searchRefNo': kwargs.get('searchRefNo')
        })

    @http.route(['/bid-status', '/bid-status/page/<int:page>'], auth="public", website=True, csrf=True)
    def tender_bid_status(self, page=1, **kwargs):
        """Bid status based on post-closing tender workflow states."""
        tender_model = request.env['tender.tender']
        domain = [
            ('website_published', '=', True),
            ('type', 'in', ['rfq', 'rfp', 'rfi']),
            ('state', 'in', ['adjudication_in_progress', 'awarded']),
        ]
        if kwargs.get('searchRefNo'):
            query = kwargs.get('searchRefNo')
            domain += ['|', ('name', 'ilike', query), ('sequence_number', 'ilike', query)]

        items_per_page = 10
        total = tender_model.search_count(domain)

        pager = request.website.pager(url='/bid-status/', total=total,
                                      page=page, step=items_per_page, scope=10)

        bid_status_tenders = tender_model.search(
            domain,
            limit=items_per_page,
            offset=pager['offset'],
            order='closing_date desc, start_time desc, id desc'
        )
        return request.render("tender_management.tender_bid_status_information", {
            'bid_status_tenders': bid_status_tenders,
            'pager': pager,
            'page': page,
            'searchRefNo': kwargs.get('searchRefNo'),
            'archive_years': self._archive_years(),
        })
    @http.route('/published_tenders', auth='public', website=True, csrf=True,
                methods=['GET', 'POST'])
    def tender_information(self, **kw):
        """Route to display published tenders."""
        user = request.env.user
        domain = [
            ('is_tender_published', '=', True)]  # Only search published tenders

        # Adding domain based on bid type selection
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
            'archive_years': self._archive_years(),
        }
        return http.request.render('tender_management.tender_information',
                                   values)

    @http.route('/tender/<model("tender.tender"):tender>', type='http', auth='public',
                website=True)
    def tender_detail(self, tender, **kwargs):
        """Route to display detailed information about a tender."""
        if not tender.exists():
            return request.render('tender_management.error_template', {
                'error_message': 'The tender you are looking for does not exist or is not published.',
                'archive_years': self._archive_years(),
            })

        # Prevent exposing unpublished tenders on public/portal website routes.
        is_internal_user = request.env.user.has_group('base.group_user')
        if not is_internal_user and not tender.website_published:
            return request.render('tender_management.error_template', {
                'error_message': 'The tender you are looking for does not exist or is not published.',
                'archive_years': self._archive_years(),
            })

        tender = tender.sudo()

        # Warning message for non-logged-in users
        warning_message = ''
        if request.env.user._is_public():
            warning_message = 'Please log in before proceeding to submit bids.'

        return request.render('tender_management.tender_detail_template', {
            'tender': tender,
            'warning_message': warning_message,
            'timer_token': self._get_timer_token(tender.id),
            'archive_years': self._archive_years(),
        })

    @http.route('/bid_submit/<int:tender_id>', type='http', auth='public',
                website=True)
    def bid_submit(self, tender_id, **kwargs):
        """Route to display detailed information about a tender."""
        tender = request.env['tender.tender'].sudo().browse(tender_id)
        if not tender.exists():
            return request.render('tender_management.error_template', {
                'error_message': 'The tender you are looking for does not exist.',
                'archive_years': self._archive_years(),
            })

        if tender.state in self.BLOCKED_BID_STATES:
            return request.render('tender_management.error_template', {
                'error_message': 'Bid submission is closed for this tender.',
                'archive_years': self._archive_years(),
            })

        return request.render('tender_management.bid_submission_template',
                              {
                                  'tender': tender,
                                  'archive_years': self._archive_years(),
                              })

    @http.route('/tender/timer', type='json', auth='public', csrf=False)
    def auction_timer(self, **kwargs):
        tender = kwargs.get('tender')
        token = kwargs.get('token')
        if not tender:
            return {'start_time': False, 'end_time': False, 'state': False}

        try:
            tender = int(tender)
        except (TypeError, ValueError):
            return {'start_time': False, 'end_time': False, 'state': False}

        if not self._is_valid_timer_token(tender, token):
            return {'start_time': False, 'end_time': False, 'state': False}

        tender = request.env['tender.tender'].sudo().browse(tender)
        if not tender.exists() or not tender.closing_date:
            return {
                'start_time': fields.Datetime.to_string(tender.start_time) if tender.exists() and tender.start_time else False,
                'end_time': False,
                'state': tender.state if tender.exists() else False,
            }

        end_time = fields.Datetime.context_timestamp(tender, tender.closing_date)
        values = {
            'start_time': fields.Datetime.to_string(tender.start_time) if tender.start_time else False,
            'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S') if end_time else False,
            'state': tender.state,
        }
        return values

    @http.route('/submit_bid', auth='user', website=True, csrf=True, methods=['POST'])
    def submit_bid(self, **kw):
        tender_id = kw.get('tender_id')
        user = request.env.user

        max_requests = self._int_config('tender_management.rate_limit.submit_bid.max_requests', 10)
        window_seconds = self._int_config('tender_management.rate_limit.submit_bid.window_seconds', 300)
        if self._is_rate_limited('submit_bid', max_requests, window_seconds):
            return request.render('tender_management.error_template', {
                'error_message': 'Too many bid submissions from your network. Please wait a few minutes and try again.',
                'archive_years': self._archive_years(),
            })

        try:
            tender_id = int(tender_id)
        except (TypeError, ValueError):
            return request.render('tender_management.error_template', {
                'error_message': 'Invalid tender reference.',
                'archive_years': self._archive_years(),
            })

        documents = request.httprequest.files.getlist('bid_documents_ids') if 'bid_documents_ids' in request.httprequest.files else []
        valid_documents = [doc for doc in documents if doc and doc.filename]
        if not valid_documents:
            return request.render('tender_management.error_template', {
                'error_message': 'Upload Documents is mandatory before submission.',
                'archive_years': self._archive_years(),
            })

        upload_error = self._validate_uploads(valid_documents)
        if upload_error:
            return request.render('tender_management.error_template', {
                'error_message': upload_error,
                'archive_years': self._archive_years(),
            })

        # Fetch the tender record
        tender = request.env['tender.tender'].sudo().browse(tender_id)
        if (
            not tender.exists()
            or not tender.website_published
            or not tender.allow_bidding
            or tender.state in self.BLOCKED_BID_STATES
        ):
            return request.render('tender_management.error_template', {
                'error_message': 'This tender is not available for bid submission.',
                'archive_years': self._archive_years(),
            })

        # Create a new tender bid record
        bid = request.env['tender.bid'].sudo().create({
            'tender_id': tender.id,
            'vendor_id': user.partner_id.id,
            'bid_type': tender.type
            # Assuming `type` is a field in tender.tender that represents the tender type
        })
        # Handle document uploads
        if valid_documents:
            for document in valid_documents:
                data = document.read()
                name = document.filename
                # Create tender.document record

                attachment = request.env['ir.attachment'].sudo().create({
                    'name': name,
                    'type': 'binary',
                    'datas': base64.b64encode(data),
                    'res_model': 'tender.bid',
                    'res_id': bid.id,
                    'mimetype': document.mimetype or 'application/octet-stream',
                })
                request.env['tender.document'].sudo().with_context(
                    allow_non_draft_tender_document_write=True
                ).create({
                    'name': name,
                    # 'file': base64.b64encode(data),
                    'tender_id': tender_id,
                    'bid_id': bid.id,
                    'attachment_id': attachment.id
                })

                folder_id = request.env[
                    'ir.config_parameter'].sudo().get_param(
                    'tender_management.folder_id')
                if not folder_id:
                    folder_id = request.env['documents.folder'].sudo().search(
                        [('name', '=', 'Tender'),
                         ('parent_folder_id', '=', request.env['documents.folder'].sudo().search(
                        [('name', '=', 'Property Development')], limit=1).id)],)
                document = request.env['documents.document'].sudo().create({
                    'name': attachment.name,
                    'attachment_id': attachment.id,
                    'folder_id': int(folder_id),
                    'res_model': 'tender.bid',
                    'res_id': bid.id,
                })


        # Call the action_submit method on the newly created bid to change its state
        bid.sudo().action_submit()
        # Redirect to the thank-you page with the bid reference number
        return http.request.render('tender_management.thank_you_page', {
            'reference_number': bid.name,
            'archive_years': self._archive_years(),
            'archive_years': self._archive_years(),
            # Pass the bid reference number to the template
        })

    @http.route('/download/document/<model("tender.document"):document_id>',
                auth='public', website=True)
    def download_document(self, document_id, **kw):
        if document_id:
            if document_id.tender_rfq_id and not self._can_access_tender_documents(document_id.tender_rfq_id):
                return request.render('tender_management.error_template', {
                    'error_message': 'You are not authorized to download this document.',
                    'archive_years': self._archive_years(),
                })
            if document_id.tender_id and not self._can_access_tender_documents(document_id.tender_id):
                return request.render('tender_management.error_template', {
                    'error_message': 'You are not authorized to download this document.',
                    'archive_years': self._archive_years(),
                })
            if document_id.bid_id and not self._can_access_bid_documents(document_id.bid_id):
                return request.render('tender_management.error_template', {
                    'error_message': 'You are not authorized to download this document.',
                    'archive_years': self._archive_years(),
                })

            file_content = base64.b64decode(document_id.file)
            file_name = document_id.name
            return request.make_response(file_content, [
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', content_disposition(file_name)),
            ])
        return request.not_found()

    @http.route('/download/all_rfq_documents/<model("tender.tender"):tender_id>',
                auth='public', website=True)
    def download_all_rfq_documents(self, tender_id, **kw):
        if not self._can_access_tender_documents(tender_id):
            return request.render('tender_management.error_template', {
                'error_message': 'You are not authorized to download these documents.',
                'archive_years': self._archive_years(),
            })

        documents = tender_id.rfq_document_ids
        if not documents:
            return request.render('tender_management.error_template', {
                'error_message': 'No RFQ documents are available for this tender yet.',
                'archive_years': self._archive_years(),
            })

        if len(documents) == 1:
            document = documents[0]
            file_content = base64.b64decode(document.file)
            return request.make_response(file_content, [
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', content_disposition(document.name)),
            ])

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w',
                             zipfile.ZIP_DEFLATED) as zip_file:
            for document in documents:
                file_content = base64.b64decode(document.file)
                zip_file.writestr(document.name, file_content)
        zip_buffer.seek(0)
        return request.make_response(zip_buffer.getvalue(), [
            ('Content-Type', 'application/zip'),
            ('Content-Disposition',
             'attachment; filename="All_Documents_%s.zip"' % tender_id.name),
        ])
    @http.route('/download/all_documents/<model("tender.tender"):tender_id>',
                auth='public', website=True)
    def download_all_documents(self, tender_id, **kw):
        if not self._can_access_tender_documents(tender_id):
            return request.render('tender_management.error_template', {
                'error_message': 'You are not authorized to download these documents.',
                'archive_years': self._archive_years(),
            })

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
        if not self._can_access_tender_documents(tender):
            return request.render('tender_management.error_template', {
                'error_message': 'You are not authorized to preview this document.',
                'archive_years': self._archive_years(),
            })
        pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
            'tender_management.tender_tender_report_action', tender.id, )[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', content_disposition('Tender.pdf')),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)
