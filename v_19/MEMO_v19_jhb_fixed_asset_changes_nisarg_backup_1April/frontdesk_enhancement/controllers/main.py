# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request
from odoo.addons.frontdesk.controllers.main import Frontdesk


class CustomFrontdesk(Frontdesk):

    @http.route('/frontdesk/<int:frontdesk_id>/<string:token>/prepare_visitor_data', type='jsonrpc', auth='public', methods=['POST'])
    def prepare_visitor_data(self, frontdesk_id, token, visitor_id=None, **kwargs):
        frontdesk = request.env['frontdesk.frontdesk'].sudo().browse(frontdesk_id)
        if not frontdesk.exists() or not self._verify_token(frontdesk, token):
            return request.not_found()

        visitor = request.env['frontdesk.visitor'].browse(visitor_id)
        vals = {'state': 'checked_in'}

        if visitor:
            if kwargs.get('drink_ids'):
                visitor.sudo().write({'drink_ids': [(4, d) for d in kwargs.get('drink_ids')]})
                return visitor._notify_to_people()
            return visitor.sudo().write(vals)
        else:
            vals.update({
                'station_id': frontdesk.id,
                'name': kwargs.get('name'),
                'phone': kwargs.get('phone'),
                'email': kwargs.get('email'),
                'type': kwargs.get('property_type'),
                'check_in': fields.Datetime.now(),
                'company': kwargs.get('company'),
                'department_id': int(kwargs.get('department')) if kwargs.get('department') else False,
                'host_ids': [(4, host_id) for host_id in kwargs.get('host_ids')] if kwargs.get('host_ids') != [
                    False] else False,
            })
            visitor = request.env['frontdesk.visitor'].sudo().create(vals)
            visitor._notify()
            return {'visitor_id': visitor.id}
