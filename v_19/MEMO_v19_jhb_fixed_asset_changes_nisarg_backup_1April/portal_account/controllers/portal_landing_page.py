# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.web.controllers.home import Home

from odoo.http import request


class CustomLoginRedirect(Home):

    @http.route('/web/login', type='http', auth="none", sitemap=False, csrf=False)
    def web_login(self, redirect=None, **kw):
        response = super(CustomLoginRedirect, self).web_login(redirect, **kw)
        if response.location == '/web' and request.params.get('login_success') and redirect==None:
            response.location = '/my/home'  # Redirect to the desired account page
        return response
