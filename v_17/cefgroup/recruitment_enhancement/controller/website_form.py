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


class RecruitmentEnhancement(WebsiteForm):

    # Check and insert values from the form on the model <model>
    @http.route('/website/form/<string:model_name>', type='http', auth="public",
                methods=['POST'], website=True, csrf=False)
    def website_form(self, model_name, **kwargs):
        # Partial CSRF check, only performed when session is authenticated, as there
        # is no real risk for unauthenticated sessions here. It's a common case for
        # embedded forms now: SameSite policy rejects the cookies, so the session
        # is lost, and the CSRF check fails, breaking the post for no good reason.
        csrf_token = request.params.pop('csrf_token', None)
        if request.session.uid and not request.validate_csrf(csrf_token):
            raise BadRequest('Session expired (invalid CSRF token)')

        try:
            # The except clause below should not let what has been done inside
            # here be committed. It should not either roll back everything in
            # this controller method. Instead, we use a savepoint to roll back
            # what has been done inside the try clause.
            with request.env.cr.savepoint():
                if request.env['ir.http']._verify_request_recaptcha_token(
                        'website_form'):
                    applicant = request.env['applicant.profile'].sudo().search(
                        [('user_id', '=', request.env.user.id)], limit=1)
                    # request.params was modified, update kwargs to reflect the changes
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
                        base64_data = base64.b64encode(file_data)
                        resume_0_attachment = request.env['ir.attachment'].sudo().create({
                            'name': res.filename,
                            'datas': base64_data,
                        })
                        resume_0_attachment.write({'public': True})
                    for pic in picture_1:
                        file_data = pic.read()
                        base64_data = base64.b64encode(file_data)
                        picture_1_attachment = request.env['ir.attachment'].sudo().create({
                            'name': pic.filename,
                            'datas': base64_data,
                        })
                        picture_1_attachment.write({'public': True})
                    for qua2 in qualifications_2:
                        file_data = qua2.read()
                        base64_data = base64.b64encode(file_data)
                        qualifications_2_attachment = request.env['ir.attachment'].sudo().create({
                            'name': qua2.filename,
                            'datas': base64_data,
                        })
                        qualifications_2_attachment.write({'public': True})
                    for qua3 in qualifications_3:
                        file_data = qua3.read()
                        base64_data = base64.b64encode(file_data)
                        qualifications_3_attachment = request.env['ir.attachment'].sudo().create({
                            'name': qua3.filename,
                            'datas': base64_data,
                        })
                        qualifications_3_attachment.write({'public': True})

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
                    request.session['applicant'] = applicant.id
                    request.session.modified = True  # Force session save

                    job_id = request.env['hr.job'].sudo().browse(int(kwargs['job_id']))
                    # job_id = kwargs['job_id']
                    if not job_id.sudo().need_prescreening:
                        vals = self._handle_website_form(model_name, **kwargs)
                        vals_dict = json.loads(vals)
                        rec_id = (vals_dict["id"])
                        job_application_data = kwargs

                        applicants = request.env[
                            'applicant.profile'].sudo().search(
                            [('user_id', '=', request.env.user.id)], limit=1)
                        applicant = request.env['hr.applicant'].sudo().browse(rec_id)
                        applicant.sudo().write({
                            'partner_name': job_application_data.get('partner_name'),
                            'title_id': int(job_application_data.get('title_id')),
                            'job_id': int(job_application_data.get('job_id')),
                            'initial': job_application_data.get('initial'),
                            'surname': job_application_data.get('surname'),
                            'passport': job_application_data.get('passport'),
                            'country_id': int(job_application_data.get('country_id')),
                            'date_of_birth': job_application_data.get('date_of_birth'),
                            'language_id': int(job_application_data.get('language_id')),
                            'email_from': job_application_data.get('email_from'),
                            'partner_phone': job_application_data.get('partner_phone'),
                            'gender': job_application_data.get('gender'),
                            'race': job_application_data.get('race'),
                            'disability': job_application_data.get('disability'),
                            'desc_disability': job_application_data.get('desc_disability'),
                            'source_id': int(job_application_data.get('source_id')),
                            'higher_qualification': job_application_data.get(
                                'higher_qualification'),
                            'current_salary': job_application_data.get('current_salary'),
                            'employee_status': job_application_data.get('employee_status'),
                            'relocate': job_application_data.get('relocate'),
                            'notice_period': job_application_data.get('notice_period'),
                            'work_experience': job_application_data.get('work_experience'),
                            'last_role': job_application_data.get('last_role'),
                            'exp_by_role': job_application_data.get('exp_by_role'),
                            'have_honours': job_application_data.get('have_honours'),
                            'have_master': job_application_data.get('have_master'),
                            'professional_body': job_application_data.get(
                                'professional_body'),
                            'terms_conditions': job_application_data.get('terms_conditions'),
                            'applicant_id': applicants.id,
                            'skill_ids': applicants.sudo().skill_ids,
                            'applicant_skill_ids': applicants.sudo().applicant_skill_ids,
                            'cv_id': job_application_data.get('resume_0_attachment', False),
                            'qualification_id': job_application_data.get('qualifications_2_attachment',
                                                           False)
                        })

                        attachment_fields = ['resume_0_attachment',
                                             'picture_1_attachment',
                                             'qualifications_2_attachment',
                                             'qualifications_3_attachment']
                        for field in attachment_fields:
                            attachment_id = kwargs.get(field, None)
                            if attachment_id:
                                attachment = request.env[
                                    'ir.attachment'].sudo().browse(
                                    int(attachment_id))
                                if attachment.exists():
                                    attachment.write({
                                        'res_id': applicant.id,
                                        'res_model': applicant._name
                                    })
                    return json.dumps({'id': 3320})
            error = _("Suspicious activity detected by Google reCaptcha.")
        except (ValidationError, UserError) as e:
            error = e.args[0]
        return json.dumps({'error': error,})

    def _handle_website_form(self, model_name, **kwargs):
        job_id = int(kwargs.get('job_id'))
        email = kwargs.get('email_from')
        identification_no = kwargs.get('passport')
        multiple_records_by_mail = request.env[
            'hr.applicant'].sudo().search([
            ('job_id', '=', job_id),
            ('email_from', '=', email)
        ])
        multiple_records_by_identification = request.env[
            'hr.applicant'].sudo().search([
            ('job_id', '=', job_id), ('passport', '=', identification_no)
        ])
        multiple_records = request.env[
            'hr.applicant'].sudo().search([
            ('job_id', '=', job_id), ('passport', '=', identification_no),
            ('email_from', '=', email)])
        if multiple_records_by_mail:
            raise ValidationError(
                "Already submitted Application using this email address")
        elif multiple_records_by_identification:
            raise ValidationError(
                "Already submitted Application using this Identification Number")
        elif multiple_records:
            raise ValidationError("Already submitted Application")
        model_record = request.env['ir.model'].sudo().search(
            [('model', '=', model_name), ('website_form_access', '=', True)])
        if not model_record:
            return json.dumps({
                'error': _("The form's specified model does not exist")
            })

        try:
            data = self.extract_data(model_record, kwargs)
        # If we encounter an issue while extracting data
        except ValidationError as e:
            # I couldn't find a cleaner way to pass data to an exception
            return json.dumps({'error_fields': e.args[0]})

        try:
            id_record = self.insert_record(request, model_record,
                                           data['record'], data['custom'],
                                           data.get('meta'))
            if id_record:
                self.insert_attachment(model_record, id_record,
                                       data['attachments'])
                # in case of an email, we want to send it immediately instead of waiting
                # for the email queue to process

                if model_name == 'mail.mail':
                    form_has_email_cc = {'email_cc',
                                         'email_bcc'} & kwargs.keys() or \
                                        'email_cc' in kwargs[
                                            "website_form_signature"]
                    # remove the email_cc information from the signature
                    kwargs["website_form_signature"] = \
                        kwargs["website_form_signature"].split(':')[0]
                    if kwargs.get("email_to"):
                        value = kwargs['email_to'] + (
                            ':email_cc' if form_has_email_cc else '')
                        hash_value = hmac(model_record.env,
                                          'website_form_signature', value)
                        if not consteq(kwargs["website_form_signature"],
                                       hash_value):
                            raise AccessDenied('invalid website_form_signature')
                    request.env[model_name].sudo().browse(id_record).send()

        # Some fields have additional SQL constraints that we can't check generically
        # Ex: crm.lead.probability which is a float between 0 and 1
        # TODO: How to get the name of the erroneous field ?
        except IntegrityError:
            return json.dumps(False)

        request.session['form_builder_model_model'] = model_record.model
        request.session['form_builder_model'] = model_record.name
        request.session['form_builder_id'] = id_record

        return json.dumps({'id': id_record})

        # Constants string to make metadata readable on a text field

    _meta_label = _lt("Metadata")  # Title for meta data

    @http.route('/recruitment', type='http', auth='public', website=True,
                sitemap=False)
    def application_website_survey_form_redirect(self, *args, **kw):
        """Survey orm redirect"""
        applicant = request.website._website_form_last_record()
        job_application_data = request.session.get('job_application_data')

        website_model_name = request.session['website_model_name']
        job = request.env['hr.job'].sudo().browse(int(job_application_data.get('job_id')))
        if job.sudo().survey_id:
            user_input = request.env['survey.user_input'].sudo().create({
                'survey_id': job.sudo().survey_id.id,
                'partner_id': request.env.user.sudo().partner_id.id if request.env.user.sudo().partner_id else None,
                # 'application_id': applicant.sudo().id
            })
            url = user_input.get_start_url()
            request.session['survey_user_input'] = user_input.id
            url = werkzeug.urls.url_join(
                user_input.get_base_url(),
                user_input.get_start_url()) if user_input else False
            return request.redirect(url)
        else:
            return request.redirect('/job-thank-you')
