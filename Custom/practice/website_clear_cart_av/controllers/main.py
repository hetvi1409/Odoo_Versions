# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class ClearCartAllProducts(http.Controller):

    @http.route(['/shop/clear/cart'], type='http', auth='public', website=True, sitemap=False)
    def clear_cart(self, **kwargs):
        """Clear all products from the current website cart."""
        order = request.cart
        if not order:
            return request.redirect('/shop/cart')

        order.order_line.sudo().unlink()
        return request.redirect('/shop/cart')
