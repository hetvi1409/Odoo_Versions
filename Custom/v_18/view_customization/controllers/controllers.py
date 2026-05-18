# -*- coding: utf-8 -*-
# from odoo import http


# class ViewCustomization(http.Controller):
#     @http.route('/view_customization/view_customization', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/view_customization/view_customization/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('view_customization.listing', {
#             'root': '/view_customization/view_customization',
#             'objects': http.request.env['view_customization.view_customization'].search([]),
#         })

#     @http.route('/view_customization/view_customization/objects/<model("view_customization.view_customization"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('view_customization.object', {
#             'object': obj
#         })

