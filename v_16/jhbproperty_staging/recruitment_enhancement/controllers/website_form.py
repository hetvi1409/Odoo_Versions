# -*- coding: utf-8 -*-
import base64
import werkzeug
from odoo import http, _
import json
from odoo.addons.website.controllers.form import WebsiteForm
from odoo.exceptions import ValidationError, UserError, AccessDenied
from odoo.http import request
from werkzeug.exceptions import BadRequest
from psycopg2 import IntegrityError
from odoo.tools.misc import hmac, consteq
from odoo.tools.translate import _, _lt
from werkzeug.datastructures import FileStorage


class RecruitmentEnhancement(WebsiteForm):

    # Check and insert values from the form on the model <model>
    @http.route('/website/form/<string:model_name>', type='http', auth="public",
                methods=['POST'], website=True, csrf=False)
    def website_form(self, model_name, **kwargs):
        csrf_token = request.params.pop('csrf_token', None)
        if request.session.uid and not request.validate_csrf(csrf_token):
            raise BadRequest('Session expired (invalid CSRF token)')

        try:
            with request.env.cr.savepoint():
                if not request.env['ir.http']._verify_request_recaptcha_token('website_form'):
                    return json.dumps({'error': _("Suspicious activity detected by Google reCaptcha.")})
                # Save the form attachments into ir.attachment
                resume_0 = request.httprequest.files.getlist('Resume[0][0]')
                picture_1 = request.httprequest.files.getlist('picture[1][0]')
                qualifications_2 = request.httprequest.files.getlist('qualification_copy[2][0]')
                qualifications_3 = request.httprequest.files.getlist('qualification_copy[3][0]')
                resume_0_attachment = False
                picture_1_attachment = False
                qualifications_2_attachment = False
                qualifications_3_attachment = False

                for res in resume_0:
                    file_data = res.read()
                    if file_data:
                        base64_data = base64.b64encode(file_data)
                        resume_0_attachment = request.env['ir.attachment'].sudo().create({
                            'name': res.filename,
                            'datas': base64_data,
                            'public': True,
                        })
                for pic in picture_1:
                    file_data = pic.read()
                    if file_data:
                        base64_data = base64.b64encode(file_data)
                        picture_1_attachment = request.env['ir.attachment'].sudo().create({
                            'name': pic.filename,
                            'datas': base64_data,
                            'public': True,
                        })
                for qua2 in qualifications_2:
                    file_data = qua2.read()
                    if file_data:
                        base64_data = base64.b64encode(file_data)
                        qualifications_2_attachment = request.env['ir.attachment'].sudo().create({
                            'name': qua2.filename,
                            'datas': base64_data,
                            'public': True,
                        })
                for qua3 in qualifications_3:
                    file_data = qua3.read()
                    if file_data:
                        base64_data = base64.b64encode(file_data)
                        qualifications_3_attachment = request.env['ir.attachment'].sudo().create({
                            'name': qua3.filename,
                            'datas': base64_data,
                            'public': True,
                        })

                # Store form kwargs into session
                kwargs = dict(request.params)
                kwargs.pop('model_name', None)
                kwargs.pop('Resume[0][0]', None)
                kwargs.pop('picture[1][0]', None)
                kwargs.pop('qualification_copy[2][0]', None)
                kwargs.pop('qualification_copy[3][0]', None)

                if resume_0_attachment:
                    kwargs['resume_0_attachment'] = resume_0_attachment.id
                if picture_1_attachment:
                    kwargs['picture_1_attachment'] = picture_1_attachment.id
                if qualifications_2_attachment:
                    kwargs['qualifications_2_attachment'] = qualifications_2_attachment.id
                if qualifications_3_attachment:
                    kwargs['qualifications_3_attachment'] = qualifications_3_attachment.id

                request.session['job_application_data'] = kwargs
                request.session['website_model_name'] = model_name
                # request.session.modified = True  # Force session save

                job_id = request.env['hr.job'].sudo().browse(int(kwargs['job_id']))

                # If the job DOES NOT need prescreening, process immediately
                if not job_id.sudo().requisition_id.need_prescreening:
                    vals = self._handle_website_form(model_name, **kwargs)
                    vals_dict = json.loads(vals)
                    if 'error' in vals_dict:
                        return vals
                    rec_id = vals_dict.get("id")

                    if rec_id:
                        applicant = request.env['hr.applicant'].sudo().browse(rec_id)
                        # Link attachments
                        if resume_0_attachment:
                            resume_0_attachment.write({'res_id': applicant.id, 'res_model': applicant._name})
                        if picture_1_attachment:
                            picture_1_attachment.write({'res_id': applicant.id, 'res_model': applicant._name})
                        if qualifications_2_attachment:
                            qualifications_2_attachment.write({'res_id': applicant.id, 'res_model': applicant._name})
                        if qualifications_3_attachment:
                            qualifications_3_attachment.write({'res_id': applicant.id, 'res_model': applicant._name})

                        applicant.sudo().write({
                            'job_id': int(kwargs.get('job_id')),
                            # 'first_name': kwargs.get('partner_name'),
                            'partner_name': kwargs.get('partner_name'),
                            'surname': kwargs.get('surname'),
                            # 'title': kwargs.get('title'),
                            # 'initial': kwargs.get('initial'),
                            # 'is_sa_citizen': kwargs.get('is_sa_citizen'),
                            # 'sa_id_number': kwargs.get('sa_id_number'),
                            'passport': kwargs.get('passport'),
                            'email_from': kwargs.get('email_from'),
                            'date_of_birth': kwargs.get('date_of_birth'),
                            'partner_phone': kwargs.get('partner_phone'),
                            # 'country_id':int(kwargs.get('country_id')) if kwargs.get('country_id') else False,
                            # 'language_id':int(kwargs.get('language_id')) if kwargs.get('language_id') else False,
                            'gender': kwargs.get('gender'),
                            # 'race': kwargs.get('race'),
                            'disability': kwargs.get('disability'),
                            # 'disability_specify': kwargs.get(
                            #     'disability_specify'),
                            # 'source_id': int(kwargs.get('source_id')) if kwargs.get('source_id') else False,
                            'current_salary': kwargs.get('current_salary'),
                            'higher_qualification': kwargs.get('higher_qualification'),
                            # 'other_higher_qualification': kwargs.get('other_higher_qualification'),
                            # 'field_study': kwargs.get('field_study'),
                            # 'other_field_study': kwargs.get('other_field_study'),
                            # 'award_sanction': kwargs.get('award_sanction'),
                            # 'criminal_record': kwargs.get('criminal_record'),
                            # 'criminal_act_type': kwargs.get('criminal_act_type'),
                            # 'criminal_case_date': kwargs.get('criminal_case_date'),
                            # 'outcome_judgment': kwargs.get('outcome_judgment'),
                            # 'relocate': kwargs.get('relocate'),
                            # 'notice_period': kwargs.get('notice_period'),
                            # 'employee_status': kwargs.get('employee_status'),
                            # 'employee_no': kwargs.get('employee_no'),
                            # 'work_experience': kwargs.get('work_experience'),
                            # 'last_role': kwargs.get('last_role'),
                            # 'exp_by_role': kwargs.get('exp_by_role'),
                            # 'have_honours': kwargs.get('have_honours'),
                            # 'have_master': kwargs.get('have_master'),
                            # 'professional_body': kwargs.get('professional_body'),
                            # 'profile_description': kwargs.get('profile_description'),
                            # 'terms_condition': kwargs.get('terms_condition'),
                            # 'cv_id': resume_0_attachment.id if resume_0_attachment else False,
                            # 'qualification_id': qualifications_2_attachment.id if qualifications_2_attachment else False,
                        })

                    return json.dumps({'id': rec_id})
                else:
                    # Job needs prescreening, return a truthy ID to trigger redirect
                    return json.dumps({'id': 'survey_redirect'})

        except (ValidationError, UserError) as e:
            error = e.args[0]
        except Exception as e:
            import traceback
            error = "Internal Error: " + str(e) + "\n" + traceback.format_exc()

        return json.dumps({'error': error})

    def _handle_website_form(self, model_name, **kwargs):
        job_id = int(kwargs.get('job_id'))
        email = kwargs.get('email_from')
        identification_no = kwargs.get('passport', '')

        domain = [('job_id', '=', job_id)]
        if email:
            multiple_records_by_mail = request.env['hr.applicant'].sudo().search(domain + [('email_from', '=', email)])
            if multiple_records_by_mail:
                raise ValidationError("Already submitted Application using this email address")

        if identification_no:
            multiple_records_by_identification = request.env['hr.applicant'].sudo().search(domain + [('passport', '=', identification_no)])
            if multiple_records_by_identification:
                raise ValidationError("Already submitted Application using this Identification Number")

        model_record = request.env['ir.model'].sudo().search([('model', '=', model_name), ('website_form_access', '=', True)])
        if not model_record:
            return json.dumps({'error': _("The form's specified model does not exist")})

        try:
            data = self.extract_data(model_record, kwargs)
        except ValidationError as e:
            return json.dumps({'error_fields': e.args[0]})

        try:
            id_record = self.insert_record(request, model_record, data['record'], data['custom'], data.get('meta'))
            if id_record:
                self.insert_attachment(model_record, id_record, data['attachments'])
        except IntegrityError:
            return json.dumps(False)

        request.session['form_builder_model_model'] = model_record.model
        request.session['form_builder_model'] = model_record.name
        request.session['form_builder_id'] = id_record

        return json.dumps({'id': id_record})

    @http.route('/recruitment', type='http', auth='public', website=True, sitemap=False)
    def application_website_survey_form_redirect(self, *args, **kw):
        """Survey form redirect"""
        job_application_data = request.session.get('job_application_data')
        if not job_application_data:
            return request.redirect('/job-thank-you')

        job = request.env['hr.job'].sudo().browse(int(job_application_data.get('job_id')))
        survey = job.sudo().requisition_id.survey_id

        if survey:
            user_input = request.env['survey.user_input'].sudo().create({
                'survey_id': survey.id,
                'partner_id': request.env.user.sudo().partner_id.id if request.env.user.sudo().partner_id else None,
            })
            url = user_input.get_start_url()
            request.session['survey_user_input'] = user_input.id
            url = werkzeug.urls.url_join(user_input.get_base_url(), user_input.get_start_url()) if user_input else False
            return request.redirect(url)
        else:
            return request.redirect('/job-thank-you')
