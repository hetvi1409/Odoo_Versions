# -*- coding: utf-8 -*-
# from odoo import http


# class RiskReport(http.Controller):
#     @http.route('/risk_report/risk_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/risk_report/risk_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('risk_report.listing', {
#             'root': '/risk_report/risk_report',
#             'objects': http.request.env['risk_report.risk_report'].search([]),
#         })

#     @http.route('/risk_report/risk_report/objects/<model("risk_report.risk_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('risk_report.object', {
#             'object': obj
#         })

