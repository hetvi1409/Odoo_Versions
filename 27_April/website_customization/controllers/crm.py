from odoo import http
from odoo.http import request


class WebsiteInquiry(http.Controller):

    # GET: Show form
    @http.route('/inquiry', type='http', auth='public', website=True)
    def inquiry_form(self, **kwargs):
        return request.render('website_customization.inquiry_form_template')

    # POST: Handle form submission
    @http.route('/inquiry/submit', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def inquiry_submit(self, **post):

        name = post.get('name')
        email = post.get('email')
        phone = post.get('phone')
        message = post.get('message')

        # Basic validation
        if not name or not email:
            return request.render('website_customization.inquiry_form_template', {
                'error': 'Name and Email are required'
            })

        # Create CRM Lead
        request.env['crm.lead'].sudo().create({
            'name': name,
            'email_from': email,
            'phone': phone,
            'description': message,
        })

        # Redirect to thank you page
        return request.redirect('/inquiry/thank-you')

    # Thank you page
    @http.route('/inquiry/thank-you', type='http', auth='public', website=True)
    def thank_you(self, **kwargs):
        return request.render('website_customization.thank_you_template')