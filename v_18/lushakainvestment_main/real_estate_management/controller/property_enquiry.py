import base64

from odoo import http
from odoo.http import request
from odoo import fields


class WebsitePropertyEnquiry(http.Controller):

    @http.route(['/property/enquiry'], type='http', auth='public', website=True)
    def property_enquiry_form(self, **kwargs):
        """Render the property enquiry form"""
        districts = request.env['res.district'].sudo().search([])
        cities = request.env['res.district.city'].sudo().search([])
        titles = request.env['res.partner.title'].sudo().search([])
        return request.render('real_estate_management.website_property_enquiry_template', {
            'districts': districts,
            'cities': cities,
            'titles': titles,
        })

    @http.route(['/property/enquiry'], type='http', auth='public', website=True)
    def property_enquiry(self, property_id=None, **kwargs):
        """
        Display a property enquiry form for the given property.
        `property_id` is passed as a URL parameter.
        """
        property_record = None
        if property_id:
            property_record = request.env['product.template'].sudo().browse(int(property_id))
        districts = request.env['res.district'].sudo().search([])
        cities = request.env['res.district.city'].sudo().search([])
        titles = request.env['res.partner.title'].sudo().search([])
        partner = ""
        if request.env.ref('base.public_user') != request.env.user:
            partner = request.env.user.partner_id
        return request.render('real_estate_management.website_property_enquiry_template', {
            'property_name': property_record.name,
            'building_name': property_record.building_id.name,
            'property_id': property_record.id,
            'districts': districts,
            'cities': cities,
            'titles': titles,
            'partner': partner.id if partner else False,
            'contact_name': partner.name if partner else False,
            'email': partner.email if partner else False,
            'phone': partner.phone if partner else False,
            'title': partner.title.id if partner else False ,
        })

    @http.route(['/property/enquiry/submit'], type='http', auth='public', methods=['POST'], csrf=False, website=True)
    def property_enquiry_submit(self, **post):
        """Handle form submission and create record"""
        print(post)

        files = request.httprequest.files
        def file_to_binary(field_name):
            file = files.getlist(field_name)[0]
            print(file, 'sdfsdf')
            return base64.b64encode(file.read()) if file else False
        vals = {
            'partner_id': int(post.get('partner')) if post.get('partner') else False,
            'building_id': int(post.get('property_id')),
            'property_id': request.env['product.template'].browse(int(post.get('property_id'))).building_id.id,
            'district_id': post.get('district_id'),
            'city_id': post.get('city_id'),
            'date': fields.Date.today(),
            'property_type': post.get('property_type'),
            'mooring_length': post.get('mooring_length'),
            'mooring_width': post.get('mooring_width'),
            'min_area': post.get('min_area') or 0.0,
            'max_area': post.get('max_area') or 0.0,
            'capacity': post.get('capacity'),
            'title': post.get('title_id'),
            'name': post.get('subject'),
            'description': post.get('description'),
            'contact_name': post.get('contact_name'),
            'contact_surname': post.get('contact_surname'),
            'email_from': post.get('email'),
            'phone': post.get('phone'),
            'business_type': post.get('business_type'),
            'business_status': post.get('business_status'),
            'operations_began_date': post.get('operations_began_date') if post.get('operations_began_date') else False,
            'nature_of_business': post.get('nature_of_business'),
            'heard_about_us': post.get('heard_about_us'),
            'medium_name': post.get('medium_name'),
            'communication_method': post.get('communication_method'),
            'enquiry_type': post.get('enquiry_type'),
            'type': 'lead',
            'company_type': post.get('company_type'),
            'reg_number': post.get('reg_number'),
            'id_number': post.get('id_number'),
            'vat': post.get('vat'),
            'passport_number': post.get('passport_number'),
            'trust_number': post.get('trust_number'),
            'id_passport_copy': file_to_binary('id_passport_copy'),
            'home_affairs_immigration': file_to_binary('home_affairs_immigration'),
            'utility_bill_lease_bank_statement': file_to_binary('utility_bill_lease_bank_statement'),
            'sars_document': file_to_binary('sars_document'),
            'cipc_certificate': file_to_binary('cipc_certificate'),
            'notice_cipc_certificate': file_to_binary('notice_cipc_certificate'),
            'moi_founding_statement': file_to_binary('moi_founding_statement'),
            'id_proof_address': file_to_binary('id_proof_address'),
            'utility_bill_lease': file_to_binary('utility_bill_lease'),
            'sars_certificate': file_to_binary('sars_certificate'),
            'certified_trust_deed': file_to_binary('certified_trust_deed'),
            'master_letter_authority': file_to_binary('master_letter_authority'),
            'trustee_id_proof_address': file_to_binary('trustee_id_proof_address'),
        }
        record = request.env['crm.lead'].sudo().create(vals)
        # record.action_send_enquiry_acknowledgement()
        return request.render('real_estate_management.website_property_enquiry_success', {
            'enquiry_ref': record.name
        })
