# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.payment.controllers import portal as payment_portal


class CustomerJobApplicationsPortal(payment_portal.PaymentPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'job_application_count' in counters:
            values['job_application_count'] = 1
        return values

    @http.route(['/job_application_details_portal/<model("hr.applicant"):job_applications>'], type='http',
                auth='public', website=True)
    def my_job_application_details(self, job_applications):
        """Render fleet details view"""
        return http.request.render(
            'recruitment_enhancement.job_application_details',
            {'job_applications': job_applications, 'page_name': 'job_application_details'}
        )

    def _get_searchbar_inputs_reservation(self):
        """Define search bar inputs for fleet applications"""
        return {
            'fleet_number': {'input': 'fleet_number',
                             'label': 'Search in Name'},
        }
    #
    @http.route(['/my/job_applications'], type='http', auth='public', website=True)
    def my_job_applications(self):
        """Handle fleet applications view"""
        job_applications = request.env['hr.applicant'].sudo().search(
            [('email_from', '=', request.env.user.partner_id.email)])
        return request.render(
            'recruitment_enhancement.my_job_applications',
            {
                'job_applications': job_applications,
                'page_name': 'job_applications'
            }
        )
