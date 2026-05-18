# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class MrpPortal(CustomerPortal):

    @http.route(['/my/mrp', '/my/mrp/page/<int:page>'], type='http',auth='user', website=True)
    def portal_my_mrp(self, page=1, **kw):
        MrpProduction = request.env['mrp.production']
        print('\n\n Protal_my_mrp-->',self)
        return request.render("practical_2_may.portal_my_mrp_list", {})

