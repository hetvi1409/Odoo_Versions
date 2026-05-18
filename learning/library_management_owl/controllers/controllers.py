# -*- coding: utf-8 -*-
# from odoo import http


# class LibraryManagementOwl(http.Controller):
#     @http.route('/library_management_owl/library_management_owl', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/library_management_owl/library_management_owl/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('library_management_owl.listing', {
#             'root': '/library_management_owl/library_management_owl',
#             'objects': http.request.env['library_management_owl.library_management_owl'].search([]),
#         })

#     @http.route('/library_management_owl/library_management_owl/objects/<model("library_management_owl.library_management_owl"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('library_management_owl.object', {
#             'object': obj
#         })

