# -*- coding: utf-8 -*-
import werkzeug.utils
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers import portal


class PortalAccount(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'memo_count' in counters:
            memo_count = request.env['memo.memo'].sudo().search_count(
                [('requester_id', '=', request.env.user.id)]
            )
            values['memo_count'] = memo_count or '0'
        return values


class MemoPortal(http.Controller):

    @http.route(['/my/memo'], type='http', auth='public',
                website=True)
    def my_memo(self):
        memo = request.env['memo.memo'].sudo().search(
            [('requester_id', '=', request.env.user.id)])
        return request.render('e_system.my_memo',
                              {
                                  'memo': memo,
                                  'page_name': 'memo'
                              }
                              )

    @http.route(['/memo_details_portal/<model("memo.memo"):memo>'],
                type='http', auth='public', website=True)
    def my_memo_details(self, memo):
        backend_url = '/web#id={}&model=memo.memo&view_type=form'.format(
            memo.id)
        return werkzeug.utils.redirect(backend_url)
