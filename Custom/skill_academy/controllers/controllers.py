# from odoo import http


# class SkillAcademy(http.Controller):
#     @http.route('/skill_academy/skill_academy', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/skill_academy/skill_academy/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('skill_academy.listing', {
#             'root': '/skill_academy/skill_academy',
#             'objects': http.request.env['skill_academy.skill_academy'].search([]),
#         })

#     @http.route('/skill_academy/skill_academy/objects/<model("skill_academy.skill_academy"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('skill_academy.object', {
#             'object': obj
#         })

