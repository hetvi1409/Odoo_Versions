# -*- coding: utf-8 -*-
import werkzeug.utils
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers import portal

class PortalAccount(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'property_intelligence_count' in counters:
            property_intelligence_count = request.env[
                'property.intelligence'].sudo().search_count(
                [('user_id', '=', request.env.user.id)]
            )
            values['property_intelligence_count'] = property_intelligence_count or '0'
        return values

class PropertyIntelligencePortal(http.Controller):

    @http.route(['/my/property_intelligence'], type='http', auth='public',
                website=True)
    def my_property_intelligence(self):
        property_intelligence = request.env['property.intelligence'].sudo().search(
            [('user_id', '=', request.env.user.id)])
        return request.render('portal_account.my_property_intelligence',
                              {
                                  'property_intelligence': property_intelligence,
                                  'page_name': 'property_intelligence'
                              }
                              )

    @http.route(['/property_intelligence_details_portal/<model("property.intelligence"):property_intelligence>'],
                type='http', auth='public', website=True)
    def my_property_intelligence_details(self, property_intelligence):
        backend_url = '/web#id={}&model=property.intelligence&view_type=form'.format(
            property_intelligence.id)
        return werkzeug.utils.redirect(backend_url)
        # return http.request.render(
        #     'portal_account.property_intelligence_details',
        #     {'property_intelligence': property_intelligence,
        #      'page_name': 'property_intelligence_details'}
        # )

