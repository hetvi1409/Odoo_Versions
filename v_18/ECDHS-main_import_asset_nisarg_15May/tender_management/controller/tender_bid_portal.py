# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.payment.controllers import portal as payment_portal


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
        return http.request.render(
            'tender_management.bid_application_details',
            {'bid_applications': bid_applications,
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
