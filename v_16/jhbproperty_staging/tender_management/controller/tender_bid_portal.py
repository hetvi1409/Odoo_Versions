# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.payment.controllers import portal as payment_portal
import io
import zipfile
import base64
import hmac
import hashlib

class TenderBidPortal(payment_portal.PaymentPortal):

    def _timer_secret(self):
        return request.env['ir.config_parameter'].sudo().get_param('database.secret', '') or ''

    def _get_timer_token(self, tender_id):
        payload = str(int(tender_id)).encode('utf-8')
        return hmac.new(self._timer_secret().encode('utf-8'), payload, hashlib.sha256).hexdigest()

    def _is_internal_user(self):
        return request.env.user.has_group('base.group_user')

    def _can_access_bid(self, bid):
        if not bid or not bid.exists():
            return False
        if self._is_internal_user():
            return True
        return bool(request.env.user and not request.env.user._is_public() and bid.vendor_id == request.env.user.partner_id)

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'bid_count' in counters:
            values['bid_count'] = 1
        return values

    @http.route([
        '/bid_application_details_portal/<model("tender.bid"):bid_applications>'],
        type='http',
        auth='user', website=True)
    def my_bid_application_details(self, bid_applications):
        """Render fleet details view"""
        if not self._can_access_bid(bid_applications):
            return request.render('tender_management.error_template', {
                'error_message': 'You are not authorized to access this bid application.',
            })
        tender_id = bid_applications.tender_id.id if bid_applications.tender_id else False
        return http.request.render(
            'tender_management.bid_application_details',
            {'tender': bid_applications,
             'timer_tender_id': tender_id,
             'timer_token': self._get_timer_token(tender_id) if tender_id else False,
             'page_name': 'bid_applications_details'}
        )

    def _get_searchbar_inputs_reservation(self):
        """Define search bar inputs for Bid applications"""
        return {
            'bid_number': {'input': 'bid_number',
                           'label': 'Search in Name'},
        }

    @http.route(['/my/bid_applications'], type='http', auth='user',
                website=True)
    def my_bid_applications(self):
        """Handle bid applications view"""
        bid_applications = request.env['tender.bid'].sudo().search(
            [('vendor_id', '=', request.env.user.partner_id.id)])
        return request.render(
            'tender_management.my_bid_applications',
            {
                'bid_applications': bid_applications,
                'page_name': 'bid_applications'
            }
        )

    @http.route('/download/all_bid_documents/<model("tender.bid"):tender_id>',
                auth='user', website=True)
    def download_all_documents(self, tender_id, **kw):
        if not self._can_access_bid(tender_id):
            return request.render('tender_management.error_template', {
                'error_message': 'You are not authorized to download these bid documents.',
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

