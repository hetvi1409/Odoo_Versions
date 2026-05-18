# -*- coding: utf-8 -*-
import werkzeug.utils
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers import portal


class PortalAccount(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'eac_count' in counters:
            eac_count = request.env[
                'eac.process'].sudo().search_count(
                [('user_id', '=', request.env.user.id)]
            )
            values['eac_count'] = eac_count or '0'
        return values

class EACPortal(http.Controller):

    @http.route(['/my/eac'], type='http', auth='public',
                website=True)
    def my_eac(self):
        eac = request.env['eac.process'].sudo().search(
            [('user_id', '=', request.env.user.id)])
        return request.render('portal_account.my_eac',
                              {
                                  'eac': eac,
                                  'page_name': 'eac'
                              }
                              )

    @http.route(['/eac_details_portal/<model("eac.process"):eac>'],
                type='http', auth='public', website=True)
    def my_eac_details(self, eac):
        backend_url = '/web#id={}&model=eac.process&view_type=form'.format(
            eac.id)
        return werkzeug.utils.redirect(backend_url)
        # return http.request.render(
        #     'portal_account.eac_details',
        #     {'eac': eac,
        #      'page_name': 'eac_details'}
        # )

