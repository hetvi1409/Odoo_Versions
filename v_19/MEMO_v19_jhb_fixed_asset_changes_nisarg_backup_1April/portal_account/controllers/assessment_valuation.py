# -*- coding: utf-8 -*-
import werkzeug.utils
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers import portal

class PortalAccount(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'assessment_valuation_count' in counters:
            assessment_valuation_count = request.env[
                'assessment.valuation'].sudo().search_count(
                [('user_id', '=', request.env.user.id)]
            )
            values['assessment_valuation_count'] = assessment_valuation_count or '0'
        return values

class AssessmentValuationPortal(http.Controller):

    @http.route(['/my/assessment_valuation'], type='http', auth='public',
                website=True)
    def my_assessment_valuation(self):
        assessment_valuation = request.env['assessment.valuation'].sudo().search(
            [('user_id', '=', request.env.user.id)])
        return request.render('portal_account.my_assessment_valuation',
                              {
                                  'assessment_valuation': assessment_valuation,
                                  'page_name': 'assessment_valuation'
                              }
                              )

    @http.route(['/assessment_valuation_details_portal/<model("assessment.valuation"):assessment_valuation>'],
                type='http', auth='public', website=True)
    def my_assessment_valuation_details(self, assessment_valuation):
        backend_url = '/web#id={}&model=assessment.valuation&view_type=form'.format(
            assessment_valuation.id)
        return werkzeug.utils.redirect(backend_url)
        # return http.request.render(
        #     'portal_account.assessment_valuation_details',
        #     {'assessment_valuation': assessment_valuation,
        #      'page_name': 'assessment_valuation_details'}
        # )


