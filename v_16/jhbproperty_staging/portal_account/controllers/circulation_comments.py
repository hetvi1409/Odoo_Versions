# -*- coding: utf-8 -*-
import werkzeug.utils
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers import portal

class PortalAccount(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'circulation_comment_count' in counters:
            circulation_comment_count = request.env[
                'circulation.comments'].sudo().search_count(
                [('user_id', '=', request.env.user.id)]
            )
            values['circulation_comment_count'] = circulation_comment_count or '0'
        return values

class CirculationCommentPortal(http.Controller):

    @http.route(['/my/circulation_comment'], type='http', auth='public',
                website=True)
    def my_circulation_comment(self):
        circulation_comment = request.env['circulation.comments'].sudo().search(
            [('user_id', '=', request.env.user.id)])
        return request.render('portal_account.my_circulation_comment',
                              {
                                  'circulation_comment': circulation_comment,
                                  'page_name': 'circulation_comment'
                              }
                              )

    @http.route(['/circulation_comment_details_portal/<model("circulation.comments"):circulation_comment>'],
                type='http', auth='public', website=True)
    def my_circulation_comment_details(self, circulation_comment):
        backend_url = '/web#id={}&model=circulation.comments&view_type=form'.format(
            circulation_comment.id)
        return werkzeug.utils.redirect(backend_url)
        # return http.request.render(
        #     'portal_account.circulation_comment_details',
        #     {'circulation_comment': circulation_comment,
        #      'page_name': 'circulation_comment_details'}
        # )

