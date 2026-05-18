# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class WebsiteProperty(http.Controller):

    @http.route(['/properties'], type='http', auth='public', website=True)
    def list_properties(self, page=1, **kwargs):
        view_type = kwargs.get('view', 'kanban')  # default to kanban
        # page = int(page)
        # per_page = 12  # number of units per page

        Product = request.env['product.template'].sudo()
        domain = [
            ('is_property', '=', True),
            ('state', '=', 'free'),
            ('website_published', '=', True)
        ]
        # total_count = Product.search_count(domain)
        units = Product.search(domain)

        # total_pages = (total_count + per_page - 1) // per_page  # ceil division

        return request.render(
            'property_management_system.property_list_template', {
                'units': units,
                'view_type': view_type,
                'page': page,
                # 'total_pages': total_pages,
                # 'per_page': per_page,
                # 'total_count': total_count,
            })

    @http.route(['/properties/<model("product.template"):unit>'], type='http', auth='public', website=True)
    def property_detail(self, unit, **kwargs):
        return request.render('property_management_system.property_detail_template', {
            'unit': unit
        })

    @http.route(['/for-sale'], type='http', auth='public', website=True)
    def for_sale(self, **kwargs):
        """Unified controller for property search & listing (Buy menu)."""
        province_id = kwargs.get('province_id')
        search_location = kwargs.get('location')
        city_id = kwargs.get('city_id')
        properties = ""
        province_name = ""
        city_name = ""
        cities = ""
        provinces = request.env['res.province'].sudo().search([])
        domain = [('is_property', '=', True)]

        # Filters
        if province_id:
            try:
                province_name = request.env['res.province'].sudo().browse(int(province_id))
                domain.append(('province_id', '=', int(province_id)))
                cities = request.env['res.district.city'].sudo().search([('province_id', '=', int(province_id))])
            except ValueError:
                pass
        if city_id:
            try:
                city_name = request.env['res.district.city'].sudo().browse(int(city_id))
                city_id = int(city_id)
                domain.append(('city_id', '=', city_id))
            except ValueError:
                city_id = None
        if search_location:
            domain.append(('name', 'ilike', search_location))

        # Fetch properties
        if province_id:
            properties = request.env['product.template'].sudo().search(domain)
        property_count = request.env['product.template'].sudo().search_count(domain)

        # Render unified template
        return request.render(
            "property_management_system.website_property_search_page", {
                'provinces': provinces,
                'properties': properties,
                'property_count': property_count,
                'province_id': int(
                    province_id) if province_id else None,
                'city_name': city_name.name if city_name else None,
                'province_name': province_name.name if province_name else None,
                'cities': cities,
                'city_id': city_id
            })

    @http.route(['/for-rent'], type='http', auth='public', website=True)
    def for_rent(self, **kwargs):
        """Unified controller for property search & listing (Buy menu)."""
        province_id = kwargs.get('province_id')
        search_location = kwargs.get('location')
        city_id = kwargs.get('city_id')
        properties = ""
        province_name = ""
        city_name = ""
        cities = ""
        provinces = request.env['res.province'].sudo().search([])
        domain = [('is_property', '=', True)]

        # Filters
        if province_id:
            try:
                province_name = request.env['res.province'].sudo().browse(int(province_id))
                domain.append(('province_id', '=', int(province_id)))
                cities = request.env['res.district.city'].sudo().search([('province_id', '=', int(province_id))])
            except ValueError:
                pass
        if city_id:
            try:
                city_name = request.env['res.district.city'].sudo().browse(int(city_id))
                city_id = int(city_id)
                domain.append(('city_id', '=', city_id))
            except ValueError:
                city_id = None
        if search_location:
            domain.append(('name', 'ilike', search_location))

        # Fetch properties
        if province_id:
            properties = request.env['product.template'].sudo().search(domain)
        property_count = request.env['product.template'].sudo().search_count(domain)

        # Render unified template
        return request.render(
            "property_management_system.website_property_search_rent_page", {
                'provinces': provinces,
                'properties': properties,
                'property_count': property_count,
                'province_id': int(
                    province_id) if province_id else None,
                'city_name': city_name.name if city_name else None,
                'province_name': province_name.name if province_name else None,
                'cities': cities,
                'city_id': city_id
            })

    # @http.route(['/for-sale',], type='http', auth='public', website=True)
    # def for_sale(self, **kwargs):
    #     provinces = request.env['res.province'].sudo().search([])
    #
    #     domain = [('is_property', '=', True)]
    #     properties = request.env['product.template'].sudo().search(domain)
    #     property_count = len(properties)
    #     return request.render(
    #         'property_management_system.website_property_search_page', {
    #             'provinces': provinces,
    #             'property_count': property_count
    #         })
    #
    # @http.route(['/property/search'], type='http', auth="public", website=True)
    # def property_search(self, **kwargs):
    #     """Handle property search by location and province."""
    #     province_id = kwargs.get('province_id')
    #
    #     provinces = request.env['res.province'].sudo().search([])
    #
    #     # Example: search your property model
    #     domain = [('is_property', '=', True)]
    #     if province_id:
    #         domain.append(('province_id', '=', int(province_id)))
    #
    #     properties = request.env['product.template'].sudo().search(domain)
    #     property_count = len(properties)
    #
    #     # Render result page (you can create this template)
    #     return request.render("property_management_system.website_property_search_page", {
    #         'properties': properties,
    #         'provinces': provinces,
    #         'province_id': int(province_id),
    #         'property_count': property_count,
    #     })
