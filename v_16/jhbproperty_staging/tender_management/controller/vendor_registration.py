from odoo import http
from odoo.http import request
import logging
import time

_logger = logging.getLogger(__name__)


class VendorRegistration(http.Controller):

    _rate_limit_store = {}

    def _int_config(self, key, default_value):
        value = request.env['ir.config_parameter'].sudo().get_param(key, str(default_value))
        try:
            return int(value)
        except (TypeError, ValueError):
            return default_value

    def _is_rate_limited(self, bucket_name, max_requests, window_seconds):
        ip = request.httprequest.remote_addr or 'unknown'
        now = time.time()
        bucket_key = f"{bucket_name}:{ip}"
        bucket = self._rate_limit_store.get(bucket_key, [])
        window_start = now - window_seconds
        bucket = [ts for ts in bucket if ts >= window_start]
        if len(bucket) >= max_requests:
            self._rate_limit_store[bucket_key] = bucket
            return True
        bucket.append(now)
        self._rate_limit_store[bucket_key] = bucket
        return False

    @http.route('/vendor/registration', type='http', auth='public',
                website=True)
    def vendor_registration_form(self, **kwargs):
        return http.request.render(
            'tender_management.vendor_registration_template',
            {'error_message': False})

    @http.route('/vendor/registration/submit', auth='public', website=True, csrf=True, methods=['POST'])
    def vendor_registration_submit(self, **kwargs):
        _logger.info("Vendor Registration Submit - Request received")

        max_requests = self._int_config('tender_management.rate_limit.vendor_registration.max_requests', 5)
        window_seconds = self._int_config('tender_management.rate_limit.vendor_registration.window_seconds', 300)
        if self._is_rate_limited('vendor_registration', max_requests, window_seconds):
            return request.render('tender_management.vendor_registration_template', {
                'error_message': 'Too many registration attempts from your network. Please wait a few minutes and try again.',
            })

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

        if not name or not email:
            return request.render('tender_management.vendor_registration_template', {
                'error_message': 'Name and email are required for registration.',
            })

        country_id = int(country_id) if country_id and str(country_id).isdigit() else False

        # Create the partner record
        partner = request.env['res.partner'].sudo().create({
            'name': name,
            'email': email,
            'phone': phone,
            'company_name': company_name,
            'street': street,
            'city': city,
            'state_id': False,
            'country_id': country_id,
            'vat': vat,
            'website': website,
            'comment': (description or '') + ("\nState/Province: %s" % state_id if state_id else ''),
            'supplier_rank': 1,
        })

        _logger.info("Created Partner ID: %s", partner.id)

        # Render success template
        return request.render('tender_management.vendor_registration_success', {})
