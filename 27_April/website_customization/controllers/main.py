from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class StockWarningController(http.Controller):

    @http.route('/shop/product/stock', type='json', auth='public', website=True)
    def get_product_stock(self, product_id, **kwargs):
        print('\n\n\n GET PRODUCT STOCK===>', product_id)
        """Return available stock quantity for a product."""
        try:
            product = request.env['product.product'].sudo().browse(int(product_id))
            if not product.exists():
                return {'qty': 0, 'error': 'Product not found'}

            # Check if stock management is enabled for this product
            if product.type != 'consu' and product.type != 'product':
                # Service products have unlimited qty
                return {'qty': -1, 'manage_stock': False}

            if not product.product_tmpl_id.sale_ok:
                return {'qty': 0, 'error': 'Product not available'}

            # Get the virtual available quantity (on-hand - reserved + incoming)
            qty_available = product.with_context(
                warehouse=request.website.warehouse_id.id
                if request.website.warehouse_id else None
            ).virtual_available

            return {
                'qty': int(qty_available),
                'manage_stock': True,
            }
        except Exception as e:
            return {'qty': 0, 'error': str(e)}




# class WebsiteSaleInherit(WebsiteSale):

#     @http.route(['/shop'], type='http', auth="public", website=True)
#     def shop(self, page=0, category=None, search='', **post):

#         min_price = post.get('min_price')
#         max_price = post.get('max_price')

#         response = super().shop(page=page, category=category, search=search, **post)

#         products = response.qcontext.get('products')

#         domain = []

#         if min_price:
#             domain.append(('list_price', '>=', float(min_price)))

#         if max_price:
#             domain.append(('list_price', '<=', float(max_price)))

#         if domain:
#             products = products.filtered(lambda p:
#                 (not min_price or p.list_price >= float(min_price)) and
#                 (not max_price or p.list_price <= float(max_price))
#             )

#         response.qcontext.update({
#             'products': products
#         })

#         return response