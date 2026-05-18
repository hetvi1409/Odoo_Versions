# -*- coding: utf-8 -*-
# from odoo import http


# class SaleDashboard(http.Controller):
#     @http.route('/sale_dashboard/sale_dashboard', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_dashboard/sale_dashboard/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_dashboard.listing', {
#             'root': '/sale_dashboard/sale_dashboard',
#             'objects': http.request.env['sale_dashboard.sale_dashboard'].search([]),
#         })

#     @http.route('/sale_dashboard/sale_dashboard/objects/<model("sale_dashboard.sale_dashboard"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_dashboard.object', {
#             'object': obj
#         })

