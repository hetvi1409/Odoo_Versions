# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError

class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'audit_request_count' in counters:
            audit_request_count = request.env['custom.audit.request'].sudo().search_count([
                                                                        ('partner_id.id', 'child_of', request.env.user.commercial_partner_id.id)])
            values['audit_request_count'] = audit_request_count
        return values
    
    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        audit_request_count = request.env['custom.audit.request'].sudo().search_count([
                                                                        ('partner_id.id', 'child_of', request.env.user.commercial_partner_id.id)])
        values['audit_request_count'] = audit_request_count
        return values
    
    @http.route(['/custom/audit/request', '/custom/audit/request/page/<int:page>'], type='http', auth="user", website=True)
    def custom_portal_my_external_audit_request(self, page=1, sortby=None, search=None):
        values = self._prepare_portal_layout_values()
        audit_request_obj = request.env['custom.audit.request']
        domain = [('partner_id.id', 'child_of', request.env.user.commercial_partner_id.id)]
        searchbar_sortings = {
            'name': {'label': _('Name'), 'order': 'name'},
            'sequence_name': {'label': _('Number'), 'order': 'sequence_name desc'},
        }
        searchbar_inputs = {
            'name': {'input': 'name', 'label': _('Search in Name')},
            'sequence_name': {'input': 'sequence_name', 'label': _('Search in Number')},
        }
        if not sortby:
            sortby = 'sequence_name'
        order = searchbar_sortings[sortby]['order']
        
        if search:
            search_domain = ['|', ('name', 'ilike', search), ('sequence_name', 'ilike', search)]
            domain += search_domain
        audit_request_count = audit_request_obj.sudo().search_count(domain)
        pager = portal_pager(
            url="/custom/audit/request",
            url_args={'search': search, 'sortby': sortby},
            total=audit_request_count,
            page=page,
            step=self._items_per_page
        )
        audit_requests = audit_request_obj.sudo().search(domain, order=order, limit=20, offset=pager['offset'])
        values.update({
            'audit_requests': audit_requests,
            'page_name': 'audit_request',
            'pager': pager,
            'default_url': '/custom/audit/request',
            'searchbar_inputs': searchbar_inputs,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("odoo_audit_request_form.custom_portal_audit_request_list_probc", values)
    
    def _custom_prepare_audit_request_form(self, request_id=None, **kw):
        audit_request = request.env['custom.audit.request'].sudo().browse(request_id)
        return {
                'audit_request': audit_request,
                }
        
    @http.route(['/custom/audit/request/form/<int:request_id>'], type='http', auth="user", website=True)
    def custom_portal_external_audit_request_form(self, request_id=None, access_token=None, **kw):
        values = self._custom_prepare_audit_request_form(request_id, **kw)
        try:
            audit_request_sudo = self._document_check_access('custom.audit.request', request_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return request.render("odoo_audit_request_form.custom_portal_audit_request_detail_form_probc", values)

