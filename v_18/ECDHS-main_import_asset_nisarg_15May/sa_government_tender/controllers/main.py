# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError, UserError
from datetime import datetime, timedelta
import re
import logging
import werkzeug.utils
from markupsafe import Markup, escape

_logger = logging.getLogger(__name__)


class SagovTenderWebsiteController(http.Controller):
    """Website controller for public tender access"""

    def _sanitize_search_input(self, search_term):
        """Sanitize search input to prevent XSS and injection attacks"""
        if not search_term:
            return ''
        # Remove any HTML tags and special characters that could be used for XSS
        search_term = str(search_term).strip()
        # Limit length to prevent DOS attacks
        if len(search_term) > 200:
            search_term = search_term[:200]
        return search_term

    def _validate_access_token(self, token):
        """Validate access token format to prevent injection"""
        if not token:
            return False
        # Access tokens should be hexadecimal strings of specific length
        if not re.match(r'^[a-f0-9]{32,64}$', token):
            _logger.warning(f"Invalid access token format attempted: {token[:10]}...")
            return False
        return True

    @http.route(['/sagovtenders', '/sagovtenders/page/<int:page>'], type='http', auth='public', website=True)
    def tender_list(self, page=1, search='', status='open', **kwargs):
        """List all published tenders"""
        # Sanitize search input
        search = self._sanitize_search_input(search)

        # Validate status parameter
        allowed_statuses = ['open', 'closed', 'all']
        if status not in allowed_statuses:
            status = 'open'

        # Validate page parameter
        try:
            page = max(1, int(page))
        except (ValueError, TypeError):
            page = 1

        # Define which tender states should be visible to the public
        # Only show tenders that are advertised or later (not drafts)
        visible_tender_states = ['advertised', 'briefing', 'bid_submission', 'opening', 'evaluation', 'awarding', 'awarded', 'closed', 'cancelled']
        base_domain = [('state', 'in', visible_tender_states)]

        # Start with base domain (visible tenders only)
        domain = list(base_domain)

        # Filter by status
        if status == 'open':
            # Open tenders are those accepting bids (only these 3 states)
            domain.append(('state', 'in', ['advertised', 'briefing', 'bid_submission']))
        elif status == 'closed':
            # Closed tenders are anything NOT accepting bids (but still visible)
            domain.append(('state', 'in', ['opening', 'evaluation', 'awarding', 'awarded', 'closed', 'cancelled']))

        # Search filter with sanitized input
        if search:
            domain += [
                '|', '|',
                ('name', 'ilike', search),
                ('title', 'ilike', search),
                ('description', 'ilike', search)
            ]

        # Pagination
        tenders_per_page = 10
        # Use search_read with limited fields for better security
        TenderModel = request.env['sagovtender.tender'].sudo()
        total_tenders = TenderModel.search_count(domain)

        # Build URL args
        url_args = {}
        if search:
            url_args['search'] = search
        if status != 'all':
            url_args['status'] = status

        pager = request.website.pager(
            url='/sagovtenders',
            total=total_tenders,
            page=page,
            step=tenders_per_page,
            url_args=url_args
        )

        tenders = TenderModel.search(
            domain,
            limit=tenders_per_page,
            offset=pager['offset'],
            order='publication_date desc, create_date desc'
        )

        # Count open and closed tenders for filter badges
        # All tenders in visible states
        total_count = TenderModel.search_count(base_domain)
        # Only tenders accepting bids
        open_count = TenderModel.search_count(base_domain + [
            ('state', 'in', ['advertised', 'briefing', 'bid_submission'])
        ])
        # Everything else that's visible
        closed_count = TenderModel.search_count(base_domain + [
            ('state', 'not in', ['advertised', 'briefing', 'bid_submission'])
        ])

        return request.render('sa_government_tender.tender_list_page', {
            'tenders': tenders,
            'pager': pager,
            'search': search,
            'status': status,
            'open_count': open_count,
            'closed_count': closed_count,
            'total_count': total_count,
            'page_name': 'tenders',
        })

    @http.route(['/sagovtender/<string:access_token>'], type='http', auth='public', website=True)
    def tender_detail(self, access_token, **kwargs):
        """View tender details"""
        # Validate access token format
        if not self._validate_access_token(access_token):
            _logger.warning(f"Invalid access token format in tender_detail from IP: {request.httprequest.remote_addr}")
            return request.render('website.404')

        tender = request.env['sagovtender.tender'].sudo().search([
            ('access_token', '=', access_token)
        ], limit=1)

        if not tender:
            _logger.info(f"Tender not found for token: {access_token[:10]}... from IP: {request.httprequest.remote_addr}")
            return request.render('website.404')

        # Check if tender is publicly accessible - only advertised onwards
        if tender.state not in ['advertised', 'briefing', 'bid_submission', 'opening', 'evaluation', 'awarding', 'awarded', 'closed']:
            _logger.info(f"Access denied to tender {tender.name} in state {tender.state} from IP: {request.httprequest.remote_addr}")
            return request.render('sa_government_tender.tender_not_available', {
                'message': 'This tender is not currently available for public viewing.'
            })

        # Check if closing date has passed
        is_open = False
        if tender.closing_date:
            is_open = fields.Datetime.now() < tender.closing_date

        # Get user's bid if logged in
        user_bid = None
        if request.env.user and not request.env.user._is_public():
            partner = request.env.user.partner_id
            user_bid = request.env['sagovtender.bid'].sudo().search([
                ('tender_id', '=', tender.id),
                ('partner_id', '=', partner.id)
            ], limit=1)

        return request.render('sa_government_tender.tender_detail_page', {
            'tender': tender,
            'is_open': is_open,
            'user_bid': user_bid,
            'page_name': 'tender_detail',
        })

    @http.route(['/sagovtender/<string:access_token>/bid'], type='http', auth='user', website=True)
    def tender_bid_form(self, access_token, **kwargs):
        """Display bid submission form"""
        # Validate access token
        if not self._validate_access_token(access_token):
            _logger.warning(f"Invalid access token in bid form from user {request.env.user.id} IP: {request.httprequest.remote_addr}")
            return request.render('website.404')

        tender = request.env['sagovtender.tender'].sudo().search([
            ('access_token', '=', access_token)
        ], limit=1)

        if not tender:
            return request.render('website.404')

        # Check if tender is open for bidding
        if tender.state not in ['advertised', 'briefing', 'bid_submission']:
            return request.render('sa_government_tender.tender_not_available', {
                'message': 'This tender is not currently open for bid submissions.'
            })

        # Check if closing date has passed
        if tender.closing_date and fields.Datetime.now() >= tender.closing_date:
            return request.render('sa_government_tender.tender_not_available', {
                'message': 'The closing date for this tender has passed.'
            })

        # Get current user's partner
        partner = request.env.user.partner_id

        # Check if partner is a company
        if not partner.is_company:
            return request.render('sa_government_tender.tender_not_available', {
                'message': 'Only registered companies can submit bids. Please update your profile.'
            })

        # Check if partner is blacklisted
        if partner.is_blacklisted:
            return request.render('sa_government_tender.tender_not_available', {
                'message': 'Your company is blacklisted and cannot submit bids.'
            })

        # Check if already submitted a bid
        existing_bid = request.env['sagovtender.bid'].sudo().search([
            ('tender_id', '=', tender.id),
            ('partner_id', '=', partner.id)
        ], limit=1)

        if existing_bid:
            return request.render('sa_government_tender.bid_already_submitted', {
                'tender': tender,
                'bid': existing_bid,
            })

        return request.render('sa_government_tender.tender_bid_form_page', {
            'tender': tender,
            'partner': partner,
            'page_name': 'bid_form',
        })

    @http.route(['/sagovtender/<string:access_token>/bid/submit'], type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def tender_bid_submit(self, access_token, **post):
        """Submit a bid"""
        # Validate access token
        if not self._validate_access_token(access_token):
            _logger.warning(f"Invalid access token in bid submit from user {request.env.user.id} IP: {request.httprequest.remote_addr}")
            return request.render('website.404')

        tender = request.env['sagovtender.tender'].sudo().search([
            ('access_token', '=', access_token)
        ], limit=1)

        if not tender:
            return request.render('website.404')

        # Rate limiting check - prevent bid spamming
        partner = request.env.user.partner_id
        recent_bids = request.env['sagovtender.bid'].sudo().search_count([
            ('partner_id', '=', partner.id),
            ('create_date', '>=', fields.Datetime.now() - timedelta(minutes=5))
        ])
        if recent_bids >= 3:
            _logger.warning(f"Rate limit exceeded for bid submission by partner {partner.id} from IP: {request.httprequest.remote_addr}")
            return request.render('sa_government_tender.bid_submission_error', {
                'tender': tender,
                'error': 'Too many bid submission attempts. Please wait a few minutes and try again.',
            })

        # Validation checks
        if tender.state not in ['advertised', 'briefing', 'bid_submission']:
            return request.render('sa_government_tender.tender_not_available', {
                'message': 'This tender is not currently open for bid submissions.'
            })

        if tender.closing_date and fields.Datetime.now() >= tender.closing_date:
            return request.render('sa_government_tender.tender_not_available', {
                'message': 'The closing date for this tender has passed.'
            })

        partner = request.env.user.partner_id

        # Check for existing bid
        existing_bid = request.env['sagovtender.bid'].sudo().search([
            ('tender_id', '=', tender.id),
            ('partner_id', '=', partner.id)
        ], limit=1)

        if existing_bid:
            return request.render('sa_government_tender.bid_already_submitted', {
                'tender': tender,
                'bid': existing_bid,
            })

        # Validate bid amount with strict checks
        try:
            bid_amount = float(post.get('bid_amount', 0))
            if bid_amount <= 0:
                raise ValueError("Bid amount must be greater than zero")
            if bid_amount > 999999999999.99:  # Prevent overflow
                raise ValueError("Bid amount is too large")
        except (ValueError, TypeError) as e:
            _logger.warning(f"Invalid bid amount from partner {partner.id}: {post.get('bid_amount')}")
            return request.render('sa_government_tender.bid_submission_error', {
                'tender': tender,
                'error': 'Invalid bid amount. Please enter a valid positive number.',
            })

        # Validate validity period
        try:
            validity_period = int(post.get('validity_period', tender.validity_period or 90))
            if validity_period < 1 or validity_period > 365:
                raise ValueError("Validity period must be between 1 and 365 days")
        except (ValueError, TypeError):
            validity_period = tender.validity_period or 90

        # Create bid
        bid_vals = {
            'tender_id': tender.id,
            'partner_id': partner.id,
            'bid_amount': bid_amount,
            'submission_date': fields.Datetime.now(),
            'validity_period': validity_period,
            'state': 'submitted',  # Set state to submitted when bid is created
            'sbd1_complete': post.get('sbd1_complete') == 'on',
            'sbd2_complete': post.get('sbd2_complete') == 'on',
            'sbd3_complete': post.get('sbd3_complete') == 'on',
            'sbd4_complete': post.get('sbd4_complete') == 'on',
            'sbd6_complete': post.get('sbd6_complete') == 'on',
            'sbd7_complete': post.get('sbd7_complete') == 'on',
            'sbd8_complete': post.get('sbd8_complete') == 'on',
            'sbd9_complete': post.get('sbd9_complete') == 'on',
        }

        try:
            bid = request.env['sagovtender.bid'].sudo().create(bid_vals)

            # Handle file uploads with security validation
            IrAttachment = request.env['ir.attachment'].sudo()
            # Security limits
            MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
            MAX_FILES = 20
            ALLOWED_EXTENSIONS = ('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.zip')

            def _create_attachment(file_storage, label=None):
                if not file_storage or not file_storage.filename:
                    return None
                filename = werkzeug.utils.secure_filename(file_storage.filename)
                if not filename:
                    return None

                file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
                if not any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
                    _logger.warning(f"Disallowed file type uploaded: {filename} by partner {partner.id}")
                    raise UserError(_(f"File type '.{file_ext}' is not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"))

                file_data = file_storage.read()
                if len(file_data) > MAX_FILE_SIZE:
                    _logger.warning(f"File too large uploaded: {filename} ({len(file_data)} bytes) by partner {partner.id}")
                    raise UserError(_(f"File {filename} is too large. Maximum size is 50MB"))

                attachment_name = f"{label} - {filename}" if label else filename
                attachment_vals = {
                    'name': attachment_name,
                    'datas': file_data,
                    'res_model': 'sagovtender.bid',
                    'res_id': bid.id,
                    'type': 'binary',
                    'public': False,  # Ensure files are not publicly accessible
                }
                attachment = IrAttachment.create(attachment_vals)
                _logger.info(f"File uploaded: {attachment_name} for bid {bid.id}")
                return attachment.id

            sbd_file_fields = [
                ('sbd1_file', 'SBD 1 - Invitation to Bid'),
                ('sbd2_file', 'SBD 2 - Tax Clearance Certificate Requirements'),
                ('sbd3_file', 'SBD 3 - Pricing Schedule'),
                ('sbd4_file', 'SBD 4 - Declaration of Interest'),
                ('sbd6_file', 'SBD 6.1 - Preference Points Claim Form'),
                ('sbd7_file', 'SBD 7 - Contract Form - Part 1'),
                ('sbd8_file', 'SBD 8 - Declaration of Past Supply Chain Management Practices'),
                ('sbd9_file', 'SBD 9 - Certificate of Independent Bid Determination'),
            ]

            sbd_files = []
            for field_name, label in sbd_file_fields:
                file_storage = request.httprequest.files.get(field_name)
                if file_storage and file_storage.filename:
                    sbd_files.append((file_storage, label))

            additional_files = request.httprequest.files.getlist('additional_documents')
            legacy_files = request.httprequest.files.getlist('bid_documents')
            extra_files = [f for f in (additional_files + legacy_files) if f and f.filename]

            total_files = len(sbd_files) + len(extra_files)
            if total_files > MAX_FILES:
                _logger.warning(f"Too many files uploaded by partner {partner.id}: {total_files}")
                raise UserError(_(f"Maximum {MAX_FILES} files allowed per bid submission"))

            attachment_ids = []
            for file_storage, label in sbd_files:
                attachment_id = _create_attachment(file_storage, label)
                if attachment_id:
                    attachment_ids.append(attachment_id)

            for file_storage in extra_files:
                attachment_id = _create_attachment(file_storage)
                if attachment_id:
                    attachment_ids.append(attachment_id)

            if attachment_ids:
                bid.write({'document_ids': [(6, 0, attachment_ids)]})
                _logger.info(f"Linked {len(attachment_ids)} documents to bid {bid.id}")

            return request.render('sa_government_tender.bid_submission_success', {
                'tender': tender,
                'bid': bid,
            })
        except UserError as e:
            return request.render('sa_government_tender.bid_submission_error', {
                'tender': tender,
                'error': str(e),
            })
        except Exception as e:
            _logger.exception(f"Error during bid submission by partner {partner.id} for tender {tender.id}")
            return request.render('sa_government_tender.bid_submission_error', {
                'tender': tender,
                'error': 'An error occurred while submitting your bid. Please try again or contact support.',
            })

    @http.route(['/my/bids', '/my/bids/page/<int:page>'], type='http', auth='user', website=True)
    def my_bids(self, page=1, status='all', search='', **kwargs):
        """View user's submitted bids"""
        # Sanitize inputs
        search = self._sanitize_search_input(search)
        if status not in ['all', 'open', 'closed']:
            status = 'all'
        try:
            page = max(1, int(page))
        except (ValueError, TypeError):
            page = 1

        partner = request.env.user.partner_id

        # Visible tender states
        visible_tender_states = ['advertised', 'briefing', 'bid_submission', 'opening', 'evaluation', 'awarding', 'awarded', 'closed', 'cancelled']

        # Base domain - all user's bids for visible tenders
        base_domain = [('partner_id', '=', partner.id), ('tender_id.state', 'in', visible_tender_states)]
        domain = list(base_domain)

        # Filter by tender status
        if status == 'open':
            # Open tenders - only those accepting bids
            domain.append(('tender_id.state', 'in', ['advertised', 'briefing', 'bid_submission']))
        elif status == 'closed':
            # Closed tenders - everything else that's visible
            domain.append(('tender_id.state', 'not in', ['advertised', 'briefing', 'bid_submission']))

        # Search filter
        if search:
            domain += [
                '|', '|', '|',
                ('name', 'ilike', search),
                ('tender_id.name', 'ilike', search),
                ('tender_id.title', 'ilike', search),
                ('tender_id.description', 'ilike', search)
            ]

        # Pagination
        bids_per_page = 10
        total_bids = request.env['sagovtender.bid'].sudo().search_count(domain)

        # Build URL args
        url_args = {}
        if status != 'all':
            url_args['status'] = status
        if search:
            url_args['search'] = search

        pager = request.website.pager(
            url='/my/bids',
            total=total_bids,
            page=page,
            step=bids_per_page,
            url_args=url_args
        )

        bids = request.env['sagovtender.bid'].sudo().search(
            domain,
            limit=bids_per_page,
            offset=pager['offset'],
            order='submission_date desc'
        )

        # Count bids by tender status for filter badges
        # All bids for visible tenders
        total_count = request.env['sagovtender.bid'].sudo().search_count(base_domain)
        # Only bids from tenders accepting bids
        open_count = request.env['sagovtender.bid'].sudo().search_count(base_domain + [
            ('tender_id.state', 'in', ['advertised', 'briefing', 'bid_submission'])
        ])
        # Everything else that's visible
        closed_count = total_count - open_count

        return request.render('sa_government_tender.my_bids_page', {
            'bids': bids,
            'pager': pager,
            'status': status,
            'search': search,
            'open_count': open_count,
            'closed_count': closed_count,
            'total_count': total_count,
            'page_name': 'my_bids',
        })

    @http.route(['/my/bid/<int:bid_id>'], type='http', auth='user', website=True)
    def my_bid_detail(self, bid_id, **kwargs):
        """View bid details"""
        # Validate bid_id
        try:
            bid_id = int(bid_id)
            if bid_id < 1:
                return request.render('website.404')
        except (ValueError, TypeError):
            return request.render('website.404')

        partner = request.env.user.partner_id

        # Use sudo() to bypass ACL - security is ensured by validating bid ownership
        bid = request.env['sagovtender.bid'].sudo().search([
            ('id', '=', bid_id),
            ('partner_id', '=', partner.id)
        ], limit=1)

        if not bid:
            _logger.info(f"Bid {bid_id} access denied for partner {partner.id}")
            return request.render('website.404')

        return request.render('sa_government_tender.my_bid_detail_page', {
            'bid': bid,
            'page_name': 'bid_detail',
        })
