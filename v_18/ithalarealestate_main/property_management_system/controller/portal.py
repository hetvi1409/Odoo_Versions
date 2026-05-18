from odoo import http, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class PortalAccount(CustomerPortal):
    """Class for the portal view of the enquiry"""

    def _prepare_home_portal_values(self, counters):
        """Function to add total service created by the current user"""
        values = super()._prepare_home_portal_values(counters)
        if 'property_enquiry' in counters:
            values['property_enquiry'] = request.env['property.enquiry'].sudo().search_count([])
        return values

    @http.route(['/my/enquiry'], type='http', auth='public',
                website=True)
    def my_enquiry(self, search=None, search_in='All', sortby=None):
        """function to create the tree view"""
        partner = request.env.user.partner_id
        domain = [('partner_id', '=', partner.id)]
        searchbar_inputs = {
            'All': {'label': 'All', 'input': 'All', 'domain': []},
            'Name': {'label': 'Name', 'input': 'Name',
                     'domain': [('name', 'ilike', search)]}
        }
        search_domain = searchbar_inputs[search_in]['domain']
        domain += search_domain
        searchbar_sorting = {
            'date': {'label': _('Date'), 'order': 'date desc'},
            'state': {'label': _('State'), 'order': 'state desc'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sorting[sortby]['order']
        enquires = request.env['property.enquiry'].sudo().search(domain, order=order)
        return request.render(
            'property_management_system.my_portal_property_enquiry',
            {'enquires': enquires,
             'page_name': 'property_enquiry',
             'searchbar_sortings': searchbar_sorting,
             'sortby': sortby,
             'searchbar_inputs': searchbar_inputs,
             'search_in': search_in,
             'search': search,
             })

    @http.route(['/enquiry_portal/<model("property.enquiry"):enquiry>'],
                type='http', auth="public", website=True)
    def my_enquiry_details(self, enquiry):
        """function to add form view of the car service"""
        return http.request.render(
            'property_management_system.portal_enquiry_details',
            {'enquiry': enquiry,
             'page_name': 'property_enquiry'
             })
