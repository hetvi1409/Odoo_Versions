# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request
from odoo.addons.frontdesk.controllers.main import Frontdesk


class CustomFrontdesk(Frontdesk):

    @http.route('/frontdesk/get_departments', type='json', auth='public', methods=['POST'])
    def get_all_departments(self, **kwargs):
        """ Return all departments (for dropdown) """
        departments = request.env['hr.department'].sudo().search([], order="name asc")
        return [{"id": dept.id, "display_name": dept.name} for dept in departments]

    @http.route('/frontdesk/<int:frontdesk_id>/<string:token>/search_departments', type='json', auth='user')
    def search_departments(self, frontdesk_id, token, name=''):
        """ Return filtered departments by name """
        departments = request.env['hr.department'].sudo().search([('name', 'ilike', name)])
        return [{"id": d.id, "display_name": d.name} for d in departments]

    @http.route('/frontdesk/<int:frontdesk_id>/<string:token>/prepare_visitor_data', type='json', auth='public', methods=['POST'])
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
                'check_in': fields.Datetime.now(),
                'company': kwargs.get('company'),
                'host_ids': [(4, host_id) for host_id in kwargs.get('host_ids') or []],
                'category': kwargs.get('category') or False,
                'department_id': kwargs.get('department_id') or False,
                'visitor_leptop_register': kwargs.get('visitor_leptop_register') or False,
                'make': kwargs.get('make') or "",
                'surname': kwargs.get('surname') or "",
                'serial_number_or_tag': kwargs.get('serial_number_or_tag') or "",
                'id_number': kwargs.get('id_number') or "",
                'office_visiting': kwargs.get('office_visiting') or "",
                'purpose_of_the_meeting': kwargs.get('purpose_of_the_meeting') or "",
                'x_has_firearm': kwargs.get('x_has_firearm') or "",
                'x_firearm_name': kwargs.get('x_firearm_name') or "",
                'x_firearm_serial': kwargs.get('x_firearm_serial') or "",
            })
            visitor = request.env['frontdesk.visitor'].sudo().create(vals)
            visitor._notify()
            return {'visitor_id': visitor.id}
