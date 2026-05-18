from odoo import http, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class PortalAccount(CustomerPortal):
    """Class for the portal view of the enquiry"""

    def _prepare_home_portal_values(self, counters):
        """Function to add total service created by the current user"""
        values = super()._prepare_home_portal_values(counters)
        undertaker = request.env['undertaker.undertaker'].sudo().search([
            ('user_id', '=', request.env.uid)])
        if undertaker:
            if 'burial_application' in counters:
                values['burial_application'] = request.env['cemetery.application'].sudo().search_count([('interment_type', '=', 'burial'), ('undertaker_id', '=', undertaker.id)])
            if 'cremation_application' in counters:
                values['cremation_application'] = request.env['cemetery.application'].sudo().search_count([('interment_type', '=', 'cremation'), ('undertaker_id', '=', undertaker.id)])
        return values

    @http.route(['/my/burial'], type='http', auth='public',
                website=True)
    def my_burial(self, search=None, search_in='All', sortby=None):
        """function to create the tree view"""
        # # enquiry = request.env['enquiry.enquiry'].sudo().search([])
        undertaker = request.env['undertaker.undertaker'].sudo().search([
            ('user_id', '=', request.env.uid)])
        domain = [('interment_type', '=' ,'burial'),  ('undertaker_id', '=', undertaker.id)]
        searchbar_inputs = {
            'All': { 'label': 'All', 'input': 'All', 'domain': [] },
            'Name': { 'label': 'Name', 'input': 'Name',
                      'domain': [('name', 'ilike', search)]}
        }
        search_domain = searchbar_inputs[search_in]['domain']
        domain += search_domain
        searchbar_sorting = {
            'date_issue': {'label': _('Date'), 'order': 'date_issue desc'},
            'state': {'label': _('State'), 'order': 'state desc'},
        }
        if not sortby:
            sortby = 'date_issue'
        order = searchbar_sorting[sortby]['order']
        application = request.env['cemetery.application'].sudo().search(domain, order=order)
        return request.render(
            'cemetery_management.my_portal_burial_applications',
            {'applications': application,
             'page_name': 'burial_application',
             'searchbar_sortings': searchbar_sorting,
             'sortby': sortby,
             'searchbar_inputs': searchbar_inputs,
             'search_in': search_in,
             'search': search,
             })

    @http.route(['/burial_portal/<int:application>'],
                type='http', auth="public", website=True)
    def my_burial_application_details(self, application):
        """Function to add form view """
        application = request.env['cemetery.application'].sudo().browse(int(application))
        return http.request.render(
            'cemetery_management.my_portal_burial_applications_details',
            {'burial_application': application,
             'page_name': 'burial_application'
             })

    @http.route(['/my/cremation'], type='http', auth='public',
                website=True)
    # def my_cremation(self, ):
    def my_cremation(self, search=None, search_in='All', sortby=None):
        """Function to create the tree view"""
        order = ""
        undertaker = request.env['undertaker.undertaker'].sudo().search([
            ('user_id', '=', request.env.uid)])
        domain = [('interment_type', '=' , 'cremation'),  ('undertaker_id', '=', undertaker.id)]
        searchbar_inputs = {
            'All': {'label': 'All', 'input': 'All', 'domain': []},
            'Name': {'label': 'Name', 'input': 'Name',
                     'domain': [('name', 'ilike', search)]}
        }
        search_domain = searchbar_inputs[search_in]['domain']
        domain += search_domain
        searchbar_sorting = {
            'date_issue': {'label': _('Date'), 'order': 'date_issue desc'},
            'state': {'label': _('State'), 'order': 'state desc'},
        }
        if not sortby:
            sortby = 'date_issue'
        order = searchbar_sorting[sortby]['order']
        application = request.env['cemetery.application'].sudo().search(domain, order=order)
        return request.render(
            'cemetery_management.my_portal_cremation_applications',
            {'applications': application,
             'page_name': 'cremation_application',
             'searchbar_sortings': searchbar_sorting,
             'sortby': sortby,
                 'searchbar_inputs': searchbar_inputs,
                 'search_in': search_in,
                 'search': search,
             })

    @http.route(['/cremation_portal/<int:application>'],
                type='http', auth="public", website=True)
    def my_cremation_application_details(self, application):
        """function to add form view """
        application = request.env['cemetery.application'].sudo().browse(int(application))
        return http.request.render(
            'cemetery_management.my_portal_cremation_applications_details',
            {'cremation_application': application,
             'page_name': 'cremation_application'
             })
