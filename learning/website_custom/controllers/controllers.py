# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class WebsiteCustomerContactController(http.Controller):

    # -------------------------------------------------------------------------
    # Website Form Page  →  /contact-us-form
    # -------------------------------------------------------------------------
    @http.route('/contact-us-form', type='http', auth='public', website=True)
    def contact_form(self, **kwargs):
        countries = request.env['res.country'].sudo().search([])
        return request.render('website_custom.website_contact_form_page', {
            'countries': countries,
            'error': {},
            'values': {},
        })

    @http.route('/contact-us-form/submit', type='http', auth='public',
                website=True, methods=['POST'], csrf=True)
    def contact_form_submit(self, **post):
        countries = request.env['res.country'].sudo().search([])
        error = {}

        # Validate required fields
        required = {'name': 'Full Name', 'email': 'Email'}
        for field, label in required.items():
            if not post.get(field, '').strip():
                error[field] = f'{label} is required.'

        if error:
            return request.render('website_custom.website_contact_form_page', {
                'countries': countries,
                'error': error,
                'values': post,
            })

        country_id = int(post.get('country_id') or 0) or False

        vals = {
            'name': post.get('name', '').strip(),
            'email': post.get('email', '').strip(),
            'phone': post.get('phone', '').strip() or False,
            'mobile': post.get('mobile', '').strip() or False,
            'company_name': post.get('company_name', '').strip() or False,
            'street': post.get('street', '').strip() or False,
            'city': post.get('city', '').strip() or False,
            'zip': post.get('zip', '').strip() or False,
            'country_id': country_id,
            'message': post.get('message', '').strip() or False,
            'partner_id': request.env.user.partner_id.id
            if request.env.user and request.env.user != request.env.ref('base.public_user')
            else False,
        }
        request.env['website.customer.contact'].sudo().create(vals)
        return request.redirect('/contact-us-form/thank-you')

    @http.route('/contact-us-form/thank-you', type='http', auth='public', website=True)
    def contact_thank_you(self, **kwargs):
        return request.render('website_custom.website_contact_thank_you', {})

    # -------------------------------------------------------------------------
    # Portal List Page  →  /my/contacts
    # -------------------------------------------------------------------------
    @http.route('/my/contacts', type='http', auth='user', website=True)
    def portal_contacts(self, **kwargs):
        partner = request.env.user.partner_id
        contacts = request.env['website.customer.contact'].sudo().search([
            ('partner_id', '=', partner.id)
        ])
        return request.render('website_custom.portal_contacts_list', {
            'contacts': contacts,
            'page_name': 'customer_contact',
        })

    # -------------------------------------------------------------------------
    # Portal Detail Page  →  /my/contacts/<id>
    # -------------------------------------------------------------------------
    @http.route('/my/contacts/<int:contact_id>', type='http', auth='user', website=True)
    def portal_contact_detail(self, contact_id, **kwargs):
        contact = request.env['website.customer.contact'].sudo().browse(contact_id)
        if not contact.exists():
            return request.redirect('/my/contacts')
        return request.render('website_custom.portal_contact_detail', {
            'customer_contact_portal': contact,
            'page_name': 'customer_contact_details',
        })
