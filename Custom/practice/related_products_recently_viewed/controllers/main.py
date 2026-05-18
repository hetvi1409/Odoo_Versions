# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class ProductCarouselController(http.Controller):

    @http.route('/product_carousel/get_accessory_products', type='json', auth='public', website=True)
    def get_accessory_products(self, product_template_id):
        """Get accessory products for a given product template"""
        try:
            if not product_template_id:
                return []
            
            # Query the product_accessory_rel table directly
            request.env.cr.execute(
                "SELECT dest_id FROM product_accessory_rel WHERE src_id = %s",
                (product_template_id,)
            )
            accessory_tmpl_ids = [row[0] for row in request.env.cr.fetchall()]
            
            if not accessory_tmpl_ids:
                return []
            
            # Get the accessory product templates
            accessory_templates = request.env['product.template'].sudo().browse(accessory_tmpl_ids).filtered('website_published')
            
            if not accessory_templates:
                return []
            
            # Convert to product variants
            accessory_products = []
            for template in accessory_templates:
                if template.product_variant_id:
                    accessory_products.append({
                        'id': template.product_variant_id.id,
                        'name': template.product_variant_id.display_name,
                        'price': template.product_variant_id.list_price,
                        'image_url': f'/web/image/product.product/{template.product_variant_id.id}/image_1024',
                        'url': f'/shop/product/{template.product_variant_id.id}',
                    })
            
            return accessory_products[:20]  # Limit to 20 products
            
        except Exception as e:
            return []
