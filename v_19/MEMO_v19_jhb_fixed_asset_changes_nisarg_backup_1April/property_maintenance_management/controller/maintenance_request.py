import base64
from datetime import datetime
from odoo import http, _
from odoo.http import request


class MaintenanceRequest(http.Controller):

    @http.route('/maintenance_request', auth='user', website=True, csrf=False)
    def maintenance(self, **kw):
        """Maintenance request"""
        return http.request.render(
            'property_maintenance_management.maintenance_form_1', kw)

    @http.route('/maintenance/submit-1', auth='user', website=True, csrf=False)
    def maintenance_submit_1(self, **kw):
        """maintenance Submit"""
        if not kw['surname']:
            kw['error'] = 'Please Add the Surname'
            return http.request.render(
                'property_maintenance_management.maintenance_form_1', kw)
        if not kw['title']:
            kw['error'] = 'Please Add the Title'
            return http.request.render(
                'property_maintenance_management.maintenance_form_1', kw)
        if not kw['first_name']:
            kw['error'] = 'Please Add the First name'
            return http.request.render(
                'property_maintenance_management.maintenance_form_1', kw)
        if not kw['cell_phone']:
            kw['error'] = 'Please Add the Cell Phone number'
            return http.request.render(
                'property_maintenance_management.maintenance_form_1', kw)
        if not kw['jmc_number']:
            kw['error'] = 'Please Add the JMC number'
            return http.request.render(
                'property_maintenance_management.maintenance_form_1', kw)
        partner_name = kw['first_name']
        partner = request.env['res.partner'].search([('name', '=', partner_name)],
                                       limit=1)
        if not partner:
            partner = request.env['res.partner'].create({
                'name': partner_name,
                'is_company': True,
            })
        maintenance = request.env['helpdesk.ticket']
        maintenance.create({
            'is_maintenance_request': True,
            'name': kw['subject'],
            'property_name': kw['property_name'],
            'jmc_number': kw['jmc_number'],
            # 'name': kw['subject'],
            'description': kw['description'],
            'type': kw['type'],
            'partner_email': kw['email'],
            'partner_id': partner.id,
            'partner_phone': kw['cell_phone'],
            'location': kw['street'],
            # 'street2': kw['street_1'],
            # 'city': kw['city'],
            # 'zip': kw['zip_code']
        })
        return http.request.render(
            'property_maintenance_management.maintenance_form_submit', {'maintenance': maintenance.id})

