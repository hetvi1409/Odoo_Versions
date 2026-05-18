# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Home

class Website(Home):
   @http.route('/', auth="public", website=True, sitemap=True)
   def index(self, **kw):
       return request.render('custom_website_design.eastern_homepage')