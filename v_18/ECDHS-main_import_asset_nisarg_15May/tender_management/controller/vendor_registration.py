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
        company_registration_number = kwargs.get('company_registration_number')
        csd_number = kwargs.get('csd_number')
        street = kwargs.get('street')
        city = kwargs.get('city')
        state_id = kwargs.get('state_id')
        country_id = kwargs.get('country_id')
        vat = kwargs.get('vat')
        website = kwargs.get('website')
        description = kwargs.get('description')

        # Check for existing suppliers to prevent duplicates
        Partner = request.env['res.partner'].sudo()
        duplicate_checks = []

        if email:
            existing = Partner.search([
                ('email', '=', email),
                ('supplier_rank', '>', 0)
            ], limit=1)
            if existing:
                duplicate_checks.append(f'Email "{email}" is already registered to supplier: {existing.name}')

        if csd_number:
            existing = Partner.search([('csd_number', '=', csd_number)], limit=1)
            if existing:
                duplicate_checks.append(f'CSD Number "{csd_number}" is already registered to: {existing.name}')

        if company_registration_number:
            existing = Partner.search([('company_registration_number', '=', company_registration_number)], limit=1)
            if existing:
                duplicate_checks.append(f'Company Registration Number "{company_registration_number}" is already registered to: {existing.name}')

        # If duplicates found, return error page
        if duplicate_checks:
            return request.render('tender_management.vendor_registration_duplicate', {
                'errors': duplicate_checks,
                'name': name,
                'email': email,
            })

        # Check for existing user with same email
        existing_user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        if existing_user:
            return request.render('tender_management.vendor_registration_duplicate', {
                'errors': [f'A user with email "{email}" already exists.'],
                'name': name,
                'email': email,
            })

        # Prepare partner values
        partner_vals = {
            'name': name,
            'email': email,
            'phone': phone,
            'street': street,
            'city': city,
            'supplier_rank': 1,
        }

        # Add optional fields only if they have values
        if company_name:
            partner_vals['company_name'] = company_name
        if company_registration_number:
            partner_vals['company_registration_number'] = company_registration_number
        if csd_number:
            partner_vals['csd_number'] = csd_number
        if country_id:
            partner_vals['country_id'] = int(country_id)
        if state_id:
            partner_vals['state_id'] = int(state_id)
        if vat:
            partner_vals['vat'] = vat
        if website:
            partner_vals['website'] = website
        if description:
            partner_vals['comment'] = description

        try:
            # Create the partner record
            partner = Partner.create(partner_vals)

            # Create the user and link it to the partner record
            user = request.env['res.users'].sudo().create({
                'name': name,
                'login': email,
                'partner_id': partner.id,
                'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])]
            })

            _logger.info("Created Partner ID: %s and User ID: %s", partner.id, user.id)

            # Render success template
            return request.render('tender_management.vendor_registration_success', {})

        except Exception as e:
            _logger.error("Error creating vendor registration: %s", str(e))
            return request.render('tender_management.vendor_registration_duplicate', {
                'errors': [f'Registration failed: {str(e)}'],
                'name': name,
                'email': email,
            })
