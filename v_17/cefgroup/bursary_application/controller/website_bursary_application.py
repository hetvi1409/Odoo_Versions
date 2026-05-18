# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import base64

class BursaryApplicationController(http.Controller):

    @http.route('/bursary_application', type='http', auth='public', website=True, csrf=True)
    def bursary_application(self, **post):
        if request.httprequest.method == 'POST':
            print('posttttt', post)
            # File fields (binary) - needs handling separately
            def get_file_binary(name):
                file = request.httprequest.files.get(name)
                return base64.b64encode(file.read()) if file else False

            vals = {
                'name': post.get('name'),
                'date_of_birth': post.get('date_of_birth'),
                'id_number': post.get('id_number'),
                'nationality': post.get('nationality'),
                'race': post.get('race'),
                'student_number': post.get('student_email'),
                'student_email': post.get('student_number'),
                'gender': post.get('gender'),
                'disability': 'disability' in post,
                'disability_type': post.get('disability_type'),
                'province': post.get('province'),
                'contact_number': post.get('contact_number'),
                'alt_number': post.get('alt_number'),
                'email': post.get('email'),
                'address': post.get('address'),
                'income_below_600k': 'income_below_600k' in post,
                'mother_name': post.get('mother_name'),
                'father_name': post.get('father_name'),
                'guardian_name': post.get('guardian_name'),
                'annual_income': post.get('annual_income'),
                'parent_deceased': 'parent_deceased' in post,
                'highest_grade': post.get('highest_grade'),
                'grade12_avg': post.get('grade12_avg'),
                'currently_studying': 'currently_studying' in post,
                'current_qualification': post.get('current_qualification'),
                'institution': post.get('institution'),
                'year_of_completion': post.get('year_of_completion'),
                'funding_source': post.get('funding_source'),
                'age_16_26': 'age_16_26' in post,
                'applied_next_year': 'applied_next_year' in post,
                'institution_type': post.get('institution_type'),
                'proposed_institution': post.get('proposed_institution'),
                'qualification_type': post.get('qualification_type'),
                'applied_bursaries': 'applied_bursaries' in post,
                'received_bursary': 'received_bursary' in post,
                'bursary_details': post.get('bursary_details'),
                'declaration': "<p>Accepted by user</p>",

                # Binary file fields
                'payslips': get_file_binary('payslips'),
                'death_certificate': get_file_binary('death_certificate'),
                'academic_records': get_file_binary('academic_records'),
                'mother_id': get_file_binary('mother_id'),
                'father_id': get_file_binary('father_id'),
                'mother_payslip': get_file_binary('mother_payslip'),
                'father_payslip': get_file_binary('father_payslip'),
                'student_id': get_file_binary('student_id'),
                'matric_results': get_file_binary('matric_results'),
                'tertiary_results': get_file_binary('tertiary_results'),
                'proof_of_registration': get_file_binary('proof_of_registration'),
                'guardian_death_certificate': get_file_binary('guardian_death_certificate'),
            }

            # Create the record
            request.env['bursary.application'].sudo().create(vals)

            # Redirect to thank-you page
            return request.redirect('/thank-you')

        # Show the form again on GET
        return request.render('bursary_application.application_page')