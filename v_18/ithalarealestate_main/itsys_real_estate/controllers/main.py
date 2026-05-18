# -*- coding: utf-8 -*-
from odoo.addons.website.controllers import form

# class WebsiteForm(form.WebsiteForm):
#     def insert_record(self, request, model, values, custom, meta=None):
#         if model.model == 'repair.order':
#             visitor_sudo = request.env['website.visitor']._get_visitor_from_request()
#             visitor_partner = visitor_sudo.partner_id
#             if visitor_partner:
#                 values['partner_id'] = visitor_partner.id
#
#         return super().insert_record(request, model, values, custom, meta=meta)

