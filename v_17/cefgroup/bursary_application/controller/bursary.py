# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError, UserError, AccessDenied
import base64
import werkzeug


class BursaryWebsite(http.Controller):

    @http.route(['/bursaries'], type='http', auth='public', website=True)
    def bursary_list(self, **kwargs):
        bursaries = request.env['bursary.bursary'].sudo().search([('is_published', '=', True)])
        return request.render('bursary_application.bursary_template', {
            'bursaries': bursaries
        })

    @http.route(['/bursary/<int:bursary_id>'], type='http', auth='public', website=True)
    def bursary_detail(self, bursary_id, **kwargs):
        bursary = request.env['bursary.bursary'].sudo().browse(bursary_id)
        if not bursary.exists():
            return request.not_found()
        return request.render('bursary_application.bursary_detail_template', {
            'bursary': bursary,
            'bursary_id': bursary,
        })

    @http.route('/bursary_application', type='http', auth='public', website=True, csrf=True)
    def bursary_application(self, **post):
        if request.httprequest.method == 'POST':
            print('sssssssssssssssss', post)
            def get_file_binary(name):
                file = request.httprequest.files.get(name)
                return base64.b64encode(file.read()) if file else False
            bursary = request.env['bursary.bursary'].sudo().browse(int(post.get('bursary_id')))
            vals = {
                'name': post.get('name'),
                'date_of_birth': post.get('date_of_birth'),
                'id_number': post.get('id_number'),
                'nationality': post.get('nationality'),
                'race': post.get('race'),
                'gender': post.get('gender'),
                'surname': post.get('surname'),
                'place_of_birth': post.get('place_of_birth'),
                'current_activity': post.get('current_activity'),
                'disability': post.get('disability'),
                'student_number': post.get('student_email'),
                'student_email': post.get('student_number'),

                'disability_type': post.get('disability_type'),
                # 'province': post.get('province'),
                'province_id': int(post.get('province_id')),
                'contact_number': post.get('contact_number'),
                'alt_number': post.get('alt_number'),
                'email': post.get('email'),
                'address': post.get('address'),
                # 'income_below_600k': post.get('income_below_600k'),
                'mother_name': post.get('mother_name'),
                'father_name': post.get('father_name'),
                'guardian_name': post.get('guardian_name'),
                'annual_income': post.get('annual_income'),
                'parent_deceased': post.get('parent_deceased'),
                'highest_grade': post.get('highest_grade'),
                'grade12_avg': post.get('grade12_avg'),
                'currently_studying': 'currently_studying' in post,
                # 'has_previous_qualifications': post.get('has_previous_qualifications'),
                'current_qualification': post.get('current_qualification'),
                'institution': post.get('institution'),
                'year_of_completion': post.get('year_of_completion'),
                'funding_source': post.get('funding_source'),
                # 'age_16_26': post.get('age_16_26'),
                'age': post.get('age'),
                # 'is_citizen': post.get('is_citizen'),
                # 'further_study_post_undergrad': post.get('further_study_post_undergrad'),
                'applied_next_year': post.get('applied_next_year'),
                'institution_type': post.get('institution_type'),
                'proposed_institution': post.get('proposed_institution'),
                'qualification_type': post.get('qualification_type'),
                'applied_bursaries': post.get('applied_bursaries'),
                'received_bursary': post.get('received_bursary'),
                'bursary_details': post.get('bursary_details'),
                'declaration': "<p>Accepted by user</p>",
                'bursary_id': int(post.get('bursary_id')) if post.get('bursary_id') else False,

                # File uploads
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
            if not bursary.sudo().survey_id:
                bursary_id = int(post.get('bursary_id'))
                email = post.get('email')
                identification_no = post.get('id_number')
                multiple_records_by_mail = request.env[
                    'bursary.application'].sudo().search([
                    ('bursary_id', '=', bursary_id),
                    ('email', '=', email)
                ])
                multiple_records_by_identification = request.env[
                    'bursary.application'].sudo().search([
                    ('bursary_id', '=', bursary_id), ('id_number', '=', identification_no)
                ])
                multiple_records = request.env[
                    'bursary.application'].sudo().search([
                    ('bursary_id', '=', bursary_id), ('id_number', '=', identification_no),
                    ('email', '=', email)])
                if multiple_records_by_mail:
                    raise ValidationError(
                        "Already submitted Application using this email address")
                elif multiple_records_by_identification:
                    raise ValidationError(
                        "Already submitted Application using this Identification Number")
                elif multiple_records:
                    raise ValidationError("Already submitted Application")
                application = request.env['bursary.application'].sudo().create(vals)
            else:
                request.session['bursary_id'] = bursary.id
                request.session['bursary_data'] = vals
                user_input = request.env['survey.user_input'].sudo().create({
                    'survey_id': bursary.sudo().survey_id.id,
                    'partner_id': request.env.user.sudo().partner_id.id if request.env.user.sudo().partner_id else None,
                    # 'application_id': applicant.sudo().id
                })
                url = user_input.get_start_url()
                request.session['survey_user_input'] = user_input.id
                url = werkzeug.urls.url_join(
                    user_input.get_base_url(),
                    user_input.get_start_url()) if user_input else False
                return request.redirect(url)
            return request.redirect('/thank-you')

        bursary_id = post.get('bursary_id') or request.params.get('bursary_id')
        bursary = request.env['bursary.bursary'].sudo().browse(int(bursary_id))
        return request.render('bursary_application.application_pager', {
            'bursary_id': bursary_id,
            'bursary_name': bursary.name,
        })
