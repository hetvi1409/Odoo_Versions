# from odoo import http


# class PerformanceContract(http.Controller):
#     @http.route('/performance_contract/performance_contract', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/performance_contract/performance_contract/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('performance_contract.listing', {
#             'root': '/performance_contract/performance_contract',
#             'objects': http.request.env['performance_contract.performance_contract'].search([]),
#         })

#     @http.route('/performance_contract/performance_contract/objects/<model("performance_contract.performance_contract"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('performance_contract.object', {
#             'object': obj
#         })

