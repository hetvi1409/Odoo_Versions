# -*- coding: utf-8 -*-
import werkzeug.utils
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers import portal


class PortalAccount(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'legal_count' in counters:
            legal_count = request.env['helpdesk.ticket'].sudo().search_count(
                [('team_id.is_legal_team', '=', True),'|', '|', '|', '|',('activity_user_id', '=', request.env.user.id),
                 ('domain_user_ids', 'in', request.env.user.ids), ('create_uid', '=', request.env.user.id),
                 ('user_id', '=', request.env.user.id), ('write_uid', '=', request.env.user.id)]) if request.env[
                'helpdesk.ticket'].check_access_rights('read', raise_exception=False) else 0
            values['legal_count'] = legal_count or '0'
        return values


class LegalPortal(http.Controller):

    @http.route(['/my/legal'], type='http', auth='public',
                website=True)
    def my_legal(self):
        legal = request.env['helpdesk.ticket'].sudo().search(
            [('team_id.is_legal_team', '=', True), '|', '|', '|', '|', ('activity_user_id', '=', request.env.user.id),
             ('domain_user_ids', 'in', request.env.user.ids), ('create_uid', '=', request.env.user.id),
             ('user_id', '=', request.env.user.id), ('write_uid', '=', request.env.user.id)])
        return request.render('portal_account.my_legal',
                              {
                                  'legal': legal,
                                  'page_name': 'legal'
                              }
                              )

    @http.route(['/legal_details_portal/<model("helpdesk.ticket"):legal>'],
                type='http', auth='public', website=True)
    def my_legal_details(self, legal):
        backend_url = '/web#id={}&model=helpdesk.ticket&view_type=form'.format(
            legal.id)
        return werkzeug.utils.redirect(backend_url)
        # return http.request.render(
        #     'portal_account.assessment_valuation_details',
        #     {'assessment_valuation': assessment_valuation,
        #      'page_name': 'assessment_valuation_details'}
        # )
