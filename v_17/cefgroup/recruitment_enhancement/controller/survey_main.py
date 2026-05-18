# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo.addons.survey.controllers.main import Survey
from odoo import http, fields
from odoo.http import request
from dateutil.relativedelta import relativedelta
import werkzeug
from odoo import http, _
import json
from odoo.addons.website.controllers.form import WebsiteForm
from odoo.exceptions import ValidationError, UserError, AccessDenied
from werkzeug.exceptions import BadRequest
from psycopg2 import IntegrityError
from odoo.tools.misc import hmac, consteq
from odoo.tools.translate import _, _lt


class SurveyController(Survey):

    @http.route('/survey/submit/<string:survey_token>/<string:answer_token>',
                type='json', auth='public', website=True)
    def survey_submit(self, survey_token, answer_token, **post):
        """ Submit a page from the survey.
        This will take into account the validation errors and store the answers to the questions.
        If the time limit is reached, errors will be skipped, answers will be ignored and
        survey state will be forced to 'done'.
        Also returns the correct answers if the scoring type is 'scoring_with_answers_after_page'."""
        # Survey Validation

        access_data = self._get_access_data(survey_token, answer_token,
                                            ensure_token=True)
        if 'job_application_data' in request.session:
            # start
            kwargs = request.session['job_application_data']
            website_model_name = request.session['website_model_name']
            applicant = request.session['applicant']
            applicant = request.env['applicant.profile'].sudo().browse(applicant)

            survey_user_input = request.session['survey_user_input']

            vals = self._handle_website_form(website_model_name, **kwargs)
            vals_dict = json.loads(vals)
            rec_id = (vals_dict["id"])
            if website_model_name == 'hr.applicant':
                request.session.rec_id = rec_id
                job = request.env['hr.applicant'].sudo().browse(rec_id)
                attachment_fields = ['resume_0_attachment', 'picture_1_attachment', 'qualifications_2_attachment','qualifications_3_attachment']
                if job.exists():
                    for field in attachment_fields:
                        attachment_id = kwargs.get(field, None)
                        if attachment_id:
                            attachment = request.env['ir.attachment'].sudo().browse(int(attachment_id))
                            if attachment.exists():
                                attachment.write({
                                    'res_id': job.id,
                                    'res_model': job._name
                                })

                job.sudo().write({
                    'partner_name': kwargs.get('partner_name'),
                    'title_id': int(kwargs.get('title_id')),
                    'job_id': int(kwargs.get('job_id')),
                    'initial': kwargs.get('initial'),
                    'surname': kwargs.get('surname'),
                    'passport': kwargs.get('passport'),
                    'country_id': int(kwargs.get('country_id')),
                    'date_of_birth': kwargs.get('date_of_birth'),
                    'language_id': int(kwargs.get('language_id')),
                    'email_from': kwargs.get('email_from'),
                    'partner_phone': kwargs.get('partner_phone'),
                    'gender': kwargs.get('gender'),
                    'race': kwargs.get('race'),
                    'disability': kwargs.get('disability'),
                    'desc_disability': kwargs.get('desc_disability'),
                    'source_id': int(kwargs.get('source_id')),
                    'higher_qualification': kwargs.get(
                        'higher_qualification'),
                    'current_salary': kwargs.get('current_salary'),
                    'employee_status': kwargs.get('employee_status'),
                    'relocate': kwargs.get('relocate'),
                    'notice_period': kwargs.get('notice_period'),
                    'work_experience': kwargs.get('work_experience'),
                    'last_role': kwargs.get('last_role'),
                    'exp_by_role': kwargs.get('exp_by_role'),
                    'have_honours': kwargs.get('have_honours'),
                    'have_master': kwargs.get('have_master'),
                    'professional_body': kwargs.get(
                        'professional_body'),
                    'terms_conditions': kwargs.get('terms_conditions'),
                    'applicant_id': applicant.id,
                    'skill_ids': applicant.sudo().skill_ids,
                    'applicant_skill_ids': applicant.sudo().applicant_skill_ids,
                    'cv_id': kwargs.get('resume_0_attachment', False),
                    'qualification_id': kwargs.get('qualifications_2_attachment', False)
                })

            survey_user_input = request.env['survey.user_input'].sudo().browse(survey_user_input)
            if survey_user_input.exists() and job.id:
                survey_user_input.write({'application_id': job.id})
            # Safely delete session keys if they exist
            for key in ['job_application_data', 'website_model_name',
                        'applicant']:
                request.session.pop(key, None)  # removes key safely

            response = super().survey_submit(survey_token, answer_token, **post)
            return response
        else:
            response = super().survey_submit(survey_token, answer_token, **post)
            return response
            # End
        # if access_data['validity_code'] is not True:
        #     return {}, {'error': access_data['validity_code']}
        # survey_sudo, answer_sudo = access_data['survey_sudo'], access_data[
        #     'answer_sudo']
        # answer_sudo.application_id.active = True
        # # application_id = request.env['hr.applicant'].sudo().search(
        # #     [('survey_id', '=', survey_sudo.id)], limit=1)
        # # application_id.write({'access_token': answer_token})
        # if answer_sudo.state == 'done':
        #     return {}, {'error': 'unauthorized'}
        #
        # questions, page_or_question_id = survey_sudo._get_survey_questions(
        #     answer=answer_sudo,
        #     page_id=post.get('page_id'),
        #     question_id=post.get('question_id'))
        #
        # if not answer_sudo.test_entry and not survey_sudo._has_attempts_left(
        #         answer_sudo.partner_id, answer_sudo.email,
        #         answer_sudo.invite_token):
        #     # prevent cheating with users creating multiple 'user_input' before their last attempt
        #     return {}, {'error': 'unauthorized'}
        #
        # if answer_sudo.survey_time_limit_reached or answer_sudo.question_time_limit_reached:
        #     if answer_sudo.question_time_limit_reached:
        #         time_limit = survey_sudo.session_question_start_time + relativedelta(
        #             seconds=survey_sudo.session_question_id.time_limit
        #         )
        #         time_limit += timedelta(seconds=3)
        #     else:
        #         time_limit = answer_sudo.start_datetime + timedelta(
        #             minutes=survey_sudo.time_limit)
        #         time_limit += timedelta(seconds=10)
        #     if fields.Datetime.now() > time_limit:
        #         # prevent cheating with users blocking the JS timer and taking all their time to answer
        #         return {}, {'error': 'unauthorized'}
        #
        # errors = {}
        # # Prepare answers / comment by question, validate and save answers
        # for question in questions:
        #     inactive_questions = request.env[
        #         'survey.question'] if answer_sudo.is_session_answer else answer_sudo._get_inactive_conditional_questions()
        #     if question in inactive_questions:  # if question is inactive, skip validation and save
        #         continue
        #     answer, comment = self._extract_comment_from_answers(question,
        #                                                          post.get(
        #                                                              str(question.id)))
        #     errors.update(question.validate_question(answer, comment))
        #     if not errors.get(question.id):
        #         answer_sudo._save_lines(question, answer, comment,
        #                                 overwrite_existing=survey_sudo.users_can_go_back or question.save_as_nickname or question.save_as_email)
        #
        # if errors and not (
        #         answer_sudo.survey_time_limit_reached or answer_sudo.question_time_limit_reached):
        #     return {}, {'error': 'validation', 'fields': errors}
        #
        # if not answer_sudo.is_session_answer:
        #     answer_sudo._clear_inactive_conditional_answers()
        #
        # # Get the page questions correct answers if scoring type is scoring after page
        # correct_answers = {}
        # if survey_sudo.scoring_type == 'scoring_with_answers_after_page':
        #     scorable_questions = (
        #             questions - answer_sudo._get_inactive_conditional_questions()).filtered(
        #         'is_scored_question')
        #     correct_answers = scorable_questions._get_correct_answers()
        #
        # if answer_sudo.survey_time_limit_reached or survey_sudo.questions_layout == 'one_page':
        #     answer_sudo._mark_done()
        # elif 'previous_page_id' in post:
        #     # when going back, save the last displayed to reload the survey where the user left it.
        #     answer_sudo.last_displayed_page_id = post['previous_page_id']
        #     # Go back to specific page using the breadcrumb. Lines are saved and survey continues
        #     return correct_answers, self._prepare_question_html(survey_sudo,
        #                                                         answer_sudo,
        #                                                         **post)
        # elif 'next_skipped_page_or_question' in post:
        #     answer_sudo.last_displayed_page_id = page_or_question_id
        #     return correct_answers, self._prepare_question_html(survey_sudo,
        #                                                         answer_sudo,
        #                                                         next_skipped_page=True)
        # else:
        #     if not answer_sudo.is_session_answer:
        #         page_or_question = request.env['survey.question'].sudo().browse(
        #             page_or_question_id)
        #         if answer_sudo.survey_first_submitted and answer_sudo._is_last_skipped_page_or_question(
        #                 page_or_question):
        #             next_page = request.env['survey.question']
        #         else:
        #             next_page = survey_sudo._get_next_page_or_question(
        #                 answer_sudo, page_or_question_id)
        #         if not next_page:
        #             if survey_sudo.users_can_go_back and answer_sudo.user_input_line_ids.filtered(
        #                     lambda a: a.skipped and a.question_id.constr_mandatory):
        #                 answer_sudo.write({
        #                     'last_displayed_page_id': page_or_question_id,
        #                     'survey_first_submitted': True,
        #                 })
        #                 return correct_answers, self._prepare_question_html(
        #                     survey_sudo, answer_sudo, next_skipped_page=True)
        #             else:
        #                 answer_sudo._mark_done()
        #
        #     answer_sudo.last_displayed_page_id = page_or_question_id
        #
        # return correct_answers, self._prepare_question_html(survey_sudo,
        #                                                     answer_sudo)

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
            # data = self.extract_data(model_record, kwargs)
            website_form = WebsiteForm()
            data = website_form.extract_data(model_record, kwargs)
        # If we encounter an issue while extracting data
        except ValidationError as e:
            # I couldn't find a cleaner way to pass data to an exception
            return json.dumps({'error_fields': e.args[0]})

        try:
            website_form = WebsiteForm()
            id_record = website_form.insert_record(request, model_record,
                                           data['record'], data['custom'],
                                           data.get('meta'))
            if id_record:
                website_form.insert_attachment(model_record, id_record,
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

