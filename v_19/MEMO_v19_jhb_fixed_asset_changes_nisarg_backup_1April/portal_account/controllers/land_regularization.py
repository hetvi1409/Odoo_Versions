# -*- coding: utf-8 -*-
import werkzeug.utils
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers import portal

class PortalAccount(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'land_regularization_count' in counters:
            land_regularization_count = request.env[
                'land.regularization'].sudo().search_count(
                [('user_id', '=', request.env.user.id)]
            )
            values['land_regularization_count'] = land_regularization_count or '0'
        return values

class LandRegularizationPortal(http.Controller):

    @http.route(['/my/land_regularization'], type='http', auth='public',
                website=True)
    def my_land_regularization(self):
        land_regularization = request.env['land.regularization'].sudo().search(
            [('user_id', '=', request.env.user.id)])
        return request.render('portal_account.my_land_regularization',
                              {
                                  'land_regularization': land_regularization,
                                  'page_name': 'land_regularization'
                              }
                              )

    @http.route(['/land_regularization_details_portal/<model("land.regularization"):land_regularization>'],
                type='http', auth='public', website=True)
    def my_land_regularization_details(self, land_regularization):
        backend_url = '/web#id={}&model=land.regularization&view_type=form'.format(
            land_regularization.id)
        return werkzeug.utils.redirect(backend_url)
        # return http.request.render(
        #     'portal_account.land_regularization_details',
        #     {'land_regularization': land_regularization,
        #      'page_name': 'land_regularization_details'}
        # )

