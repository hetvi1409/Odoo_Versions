from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from werkzeug.urls import url_encode


class PortalAccount(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'buildings_count' in counters:
            user = request.env.user.sudo()
            regions = user.region_ids.ids
            domain = [('id', '=', 0)]
            if regions:
                domain = [('region_id', 'in', regions)]
            values['buildings_count'] = request.env['building'].sudo().search_count(domain)
        return values


class BuildingPortal(http.Controller):

    @http.route(['/my/buildings', '/my/buildings/page/<int:page>'], type='http', auth='user', website=True)
    def my_buildings(self, page=1, **kw):
        user = request.env.user.sudo()
        allowed_regions = user.region_ids

        try:
            selected_region_id = int(kw.get('region_id', 0) or 0)
        except (TypeError, ValueError):
            selected_region_id = 0
        selected_region = allowed_regions.filtered(lambda region: region.id == selected_region_id)

        domain = [('id', '=', 0)]
        if selected_region:
            domain = [('region_id', '=', selected_region.id)]

        building_model = request.env['building'].sudo()
        building_fields = building_model._fields

        jmc_number = (kw.get('jmc_number') or '').strip()
        erf_number = (kw.get('erf_number') or '').strip()
        ward = (kw.get('ward') or '').strip()
        stand_number = (kw.get('stand_number') or '').strip()
        address = (kw.get('address') or '').strip()
        sortby = (kw.get('sortby') or 'erf_asc').strip()
        page_size_raw = (kw.get('page_size') or '20').strip()

        try:
            page_size = int(page_size_raw)
        except (TypeError, ValueError):
            page_size = 20
        if page_size not in (20, 50, 100):
            page_size = 20

        advanced_active = bool(
            jmc_number or erf_number or ward or stand_number or address
            or sortby != 'erf_asc' or page_size != 20
        )

        sort_options = {
            'erf_asc': 'name asc',
            'erf_desc': 'name desc',
            'jmc_asc': 'jmc_number asc',
            'jmc_desc': 'jmc_number desc',
            'ward_asc': 'ward asc',
            'ward_desc': 'ward desc',
            'address_asc': 'address asc',
            'address_desc': 'address desc',
        }
        order = sort_options.get(sortby, 'name asc')

        if jmc_number and 'jmc_number' in building_fields:
            domain.append(('jmc_number', 'ilike', jmc_number))
        if erf_number and 'name' in building_fields:
            domain.append(('name', 'ilike', erf_number))
        if ward and 'ward' in building_fields:
            domain.append(('ward', 'ilike', ward))
        if stand_number and 'stand_number' in building_fields:
            domain.append(('stand_number', 'ilike', stand_number))
        if address and 'address' in building_fields:
            domain.append(('address', 'ilike', address))

        url_args = {
            'region_id': selected_region.id if selected_region else '',
            'jmc_number': jmc_number,
            'erf_number': erf_number,
            'ward': ward,
            'stand_number': stand_number,
            'address': address,
            'sortby': sortby,
            'page_size': page_size,
        }

        building_keep_query = url_encode({
            key: value for key, value in url_args.items()
            if value not in (False, None, '', [])
        })

        total = building_model.search_count(domain)
        pager = portal_pager(
            url='/my/buildings',
            total=total,
            page=page,
            step=page_size,
            url_args=url_args,
        )

        buildings = building_model.search(
            domain,
            order=order,
            limit=page_size,
            offset=pager['offset'],
        )
        page_records = len(buildings)

        return request.render(
            'portal_account.my_buildings',
            {
                'page_name': 'buildings',
                'buildings': buildings,
                'regions': allowed_regions,
                'selected_region_id': selected_region.id if selected_region else False,
                'region_selected': bool(selected_region),
                'jmc_number': jmc_number,
                'erf_number': erf_number,
                'ward': ward,
                'stand_number': stand_number,
                'address': address,
                'sortby': sortby,
                'page_size': page_size,
                'advanced_active': advanced_active,
                'pager': pager,
                'total_records': total,
                'page_records': page_records,
                'building_keep_query': building_keep_query,
            }
        )

    @http.route(['/my/buildings/<int:building_id>'], type='http', auth='user', website=True)
    def my_building_detail(self, building_id, **kw):
        user = request.env.user.sudo()
        building = request.env['building'].sudo().search([
            ('id', '=', building_id),
            ('region_id', 'in', user.region_ids.ids),
        ], limit=1)
        if not building:
            return request.not_found()

        back_query = url_encode({
            key: value for key, value in kw.items()
            if value not in (False, None, '', [])
        })
        back_url = '/my/buildings'
        if back_query:
            back_url = '%s?%s' % (back_url, back_query)

        backend_form_url = '/web#id=%s&model=building&view_type=form' % building.id

        return request.render(
            'portal_account.my_building_detail',
            {
                'page_name': 'buildings',
                'building': building,
                'back_url': back_url,
                'backend_form_url': backend_form_url,
            }
        )
