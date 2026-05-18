# -*- coding: utf-8 -*-
import werkzeug.utils
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers import portal

class PortalAccount(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'transaction_count' in counters:
            transaction_count = request.env[
                'client.transaction'].sudo().search_count(
                [('user_id', '=', request.env.user.id)]
            )
            values['transaction_count'] = transaction_count or '0'
        return values

class ClientTransactionPortal(http.Controller):

    @http.route(['/my/transaction'], type='http', auth='public',
                website=True)
    def my_transaction(self):
        transaction = request.env['client.transaction'].sudo().search(
            [('user_id', '=', request.env.user.id)])
        return request.render('portal_account.my_transaction',
                              {
                                  'transaction': transaction,
                                  'page_name': 'transaction'
                              }
                              )

    @http.route(['/transaction_details_portal/<model("client.transaction"):transaction>'],
                type='http', auth='public', website=True)
    def my_transaction_details(self, transaction):
        backend_url = '/web#id={}&model=client.transaction&view_type=form'.format(
            transaction.id)
        return werkzeug.utils.redirect(backend_url)
        # return http.request.render(
        #     'portal_account.transaction_details',
        #     {'transaction': transaction,
        #      'page_name': 'transaction_details'}
        # )

