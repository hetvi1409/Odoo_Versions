# -*- coding: utf-8 -*-
import werkzeug.utils
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers import portal


class PortalAccount(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'enquiry_assessment_count' in counters:
            enquiry_assessment_count = request.env[
                'enquiry.assessment'].sudo().search_count(
                [('user_id', '=', request.env.user.id)]
            )
            values['enquiry_assessment_count'] = enquiry_assessment_count or '0'
        return values

class EnquiryAssessmentPortal(http.Controller):

    @http.route(['/my/enquiry_assessment'], type='http', auth='public',
                website=True)
    def my_enquiry_assessment(self):
        enquiry_assessment = request.env['enquiry.assessment'].sudo().search(
            [('user_id', '=', request.env.user.id)])
        return request.render('portal_account.my_enquiry_assessment',
                              {
                                  'enquiry_assessment': enquiry_assessment,
                                  'page_name': 'enquiry_assessment'
                              }
                              )

    @http.route(['/enquiry_assessment_details_portal/<model("enquiry.assessment"):enquiry_assessment>'],
                type='http', auth='public', website=True)
    def my_enquiry_assessment_details(self, enquiry_assessment):
        backend_url = '/web#id={}&model=enquiry.assessment&view_type=form'.format(
            enquiry_assessment.id)
        return werkzeug.utils.redirect(backend_url)
        # return http.request.render(
        #     'portal_account.enquiry_assessment_details',
        #     {'enquiry_assessment': enquiry_assessment,
        #      'page_name': 'enquiry_assessment_details'}
        # )

