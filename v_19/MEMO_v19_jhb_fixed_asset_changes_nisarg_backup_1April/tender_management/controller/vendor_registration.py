from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class VendorRegistration(http.Controller):

    @http.route('/vendor/registration', type='http', auth='public',
                website=True)
    def vendor_registration_form(self, **kwargs):
        return http.request.render(
            'tender_management.vendor_registration_template',
            {})

    @http.route('/vendor/registration/submit', auth='public', website=True, csrf=False)
    def vendor_registration_submit(self, **kwargs):
        _logger.info("Vendor Registration Submit - Form Data: %s", kwargs)

        # Extracting form data
        name = kwargs.get('name')
        email = kwargs.get('email')
        phone = kwargs.get('phone')
        company_name = kwargs.get('company_name')
        street = kwargs.get('street')
        city = kwargs.get('city')
        state_id = kwargs.get('state')
        country_id = kwargs.get('country_id')
        vat = kwargs.get('vat')
        website = kwargs.get('website')
        description = kwargs.get('description')

        # Create the partner record
        partner = request.env['res.partner'].sudo().create({
            'name': name,
            'email': email,
            'phone': phone,
            'company_name': company_name,
            'street': street,
            'city': city,
            'state_id': state_id,
            'country_id': country_id,
            'vat': vat,
            'website': website,
            'comment': description,
            'supplier_rank': 1,
        })

        # Create the user and link it to the partner record
        user = request.env['res.users'].sudo().create({
            'name': name,
            'login': email,
            'partner_id': partner.id,
            'group_ids': [(6, 0, [request.env.ref('base.group_portal').id])]
        })

        _logger.info("Created Partner ID: %s and User ID: %s", partner.id, user.id)

        # Render success template
        return request.render('tender_management.vendor_registration_success', {})
