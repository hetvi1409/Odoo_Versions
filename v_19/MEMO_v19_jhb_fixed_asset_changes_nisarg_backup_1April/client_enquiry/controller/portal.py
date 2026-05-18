from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):
    """Class for the portal view of the enquiry"""

    def _prepare_home_portal_values(self, counters):
        """Function to add total service created by the current user"""
        values = super()._prepare_home_portal_values(counters)
        if 'enquiry_count' in counters:
            values['enquiry_count'] = request.env['client.enquiry'].sudo().search_count([('partner_id', '=', request.env.user.partner_id.id)])
        if 'loan_count' in counters:
            values['loan_count'] = request.env['enquiry.assessment'].sudo().search_count([('partner_ids', 'in', request.env.user.partner_id.id)])
        return values

    @http.route(['/my/enquiry'], type='http', auth='public',
                website=True)
    def my_enquiry(self):
        """function to create the tree view car service"""
        enquiry = request.env['client.enquiry'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id)])
        return request.render('client_enquiry.portal_enquiry',
                              {'enquiry': enquiry,
                               'page_name': 'enquiry'})

    @http.route(['/enquiry_portal/<model("client.enquiry"):enquiry>'],
                type='http', auth="public", website=True)
    def my_enquiry_details(self, enquiry):
        """function to add form view of the car service"""
        return http.request.render(
            'client_enquiry.portal_enquiry_details',
            {'enquiry': enquiry,
             'page_name': 'enquiry'
         })

    @http.route(['/my/assessment'], type='http', auth='public',
                website=True)
    def my_enquiry_assessment(self):
        """function to create the tree view car service"""
        assessment = request.env['enquiry.assessment'].sudo().search([('partner_ids', 'in', request.env.user.partner_id.id)], order="id desc")
        return request.render('client_enquiry.portal_enquiry_assessment',
                              {'assessment': assessment,
                               'page_name': 'assessment'})

    @http.route(['/assessment_portal/<int:assessment>'],
                type='http', auth="public", website=True)
    def my_enquiry_assessment_details(self, assessment):
        """function to add form view of the car service"""
        assessment = request.env['enquiry.assessment'].sudo().browse(assessment)
        return http.request.render(
            'client_enquiry.portal_enquiry_assessment_details',
            {'assessment': assessment,
             'page_name': 'assessment'
         })
