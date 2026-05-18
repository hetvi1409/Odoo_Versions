# -*- coding: utf-8 -*-
import werkzeug.utils
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers import portal

class PortalAccount(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'client_enquiry_count' in counters:
            client_enquiry_count = request.env[
                'client.enquiry'].sudo().search_count(
                [('user_id', '=', request.env.user.id)]
            )
            values['client_enquiry_count'] = client_enquiry_count or '0'
        return values

class ClientEnquiryPortal(http.Controller):

    @http.route(['/my/client_enquiry'], type='http', auth='public',
                website=True)
    def my_client_enquiry(self):
        client_enquiry = request.env['client.enquiry'].sudo().search(
            [('user_id', '=', request.env.user.id)])
        return request.render('portal_account.my_client_enquiry',
                              {
                                  'client_enquiry': client_enquiry,
                                  'page_name': 'client_enquiry'
                              }
                              )

    @http.route(['/client_enquiry_details_portal/<model("client.enquiry"):client_enquiry>'],
                type='http', auth='public', website=True)
    def my_client_enquiry_details(self, client_enquiry):
        backend_url = '/web#id={}&model=client.enquiry&view_type=form'.format(
            client_enquiry.id)
        return werkzeug.utils.redirect(backend_url)


