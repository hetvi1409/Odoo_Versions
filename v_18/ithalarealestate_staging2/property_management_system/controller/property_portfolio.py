# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class WebsitePortfolioProperty(http.Controller):
    """Portfolio Property"""

    @http.route(['/property-portfolio'], type='http', auth='public', website=True)
    def property_portfolio(self, **kwargs):
        """Unified Controller for Property Portfolio"""
        print(kwargs)
        return request.render(
            "property_management_system.overview_page", {
            })
