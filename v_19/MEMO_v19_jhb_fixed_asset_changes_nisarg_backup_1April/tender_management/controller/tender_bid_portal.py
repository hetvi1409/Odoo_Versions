# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.payment.controllers import portal as payment_portal
import io
import zipfile
import base64

class TenderBidPortal(payment_portal.PaymentPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'bid_count' in counters:
            values['bid_count'] = 1
        return values

    @http.route([
        '/bid_application_details_portal/<model("tender.bid"):bid_applications>'],
        type='http',
        auth='public', website=True)
    def my_bid_application_details(self, bid_applications):
        """Render fleet details view"""
        print(bid_applications, 'bid_application')
        return http.request.render(
            'tender_management.bid_application_details',
            {'tender': bid_applications,
             'page_name': 'bid_applications_details'}
        )

    def _get_searchbar_inputs_reservation(self):
        """Define search bar inputs for Bid applications"""
        return {
            'bid_number': {'input': 'bid_number',
                           'label': 'Search in Name'},
        }

    @http.route(['/my/bid_applications'], type='http', auth='public',
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

