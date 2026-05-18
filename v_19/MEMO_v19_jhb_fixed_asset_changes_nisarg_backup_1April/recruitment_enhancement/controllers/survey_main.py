# -*- coding: utf-8 -*-
from odoo.addons.survey.controllers.main import Survey
from odoo import http, fields
from odoo.http import request
import json
from odoo.exceptions import ValidationError


class SurveyController(Survey):


    @http.route('/get/skill/levels', type='json', auth='public', website=True)
    def get_skill_levels(self, **kwargs):
        skill_id = kwargs.get('skill_id')
        skill_record = request.env['hr.skill'].sudo().browse(int(skill_id))
        skill_type = skill_record.skill_type_id

        if not skill_id:
            return []

        levels = request.env['hr.skill.level'].sudo().search([('skill_type_id', '=', skill_type.id)])

        return [{'id': l.id, 'name': l.name} for l in levels]

    @http.route('/get/skills', type='json', auth='public', website=True)
    def get_skills(self, **kwargs):
        skill_type_id = kwargs.get('skill_type_id')
        if not skill_type_id:
            return []

        skills = request.env['hr.skill'].sudo().search([('skill_type_id', '=', int(skill_type_id))])

        return [{'id': s.id, 'name': s.name} for s in skills]

    @http.route('/survey/submit/<string:survey_token>/<string:answer_token>', type='jsonrpc', auth='public', website=True)
    def survey_submit(self, survey_token, answer_token, **post):
        """ Submit a page from the survey.
            This incorporates website job application submission logic.
        """
        # Call super early to validate tokens and ensure we have basic context
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)

        # Determine if this survey submission completes a job application
        if 'job_application_data' in request.session:
            kwargs = request.session['job_application_data']
            website_model_name = request.session['website_model_name']
            survey_user_input_id = request.session.get('survey_user_input')

            # We need to rely on the website_form logic to insert the record.
            # However, `WebsiteForm` is not directly accessible here via super so we use env fallback
            # But wait, we can just use the standard insert_record if we wanted, or simpler just create it manually since we have all data.
            # To be safe, let's process the application creation directly:
            if website_model_name == 'hr.applicant':
                # Map fields
                vals = {
                    'partner_name': kwargs.get('partner_name'),
                    'job_id': int(kwargs.get('job_id')) if kwargs.get('job_id') else False,
                    'email_from': kwargs.get('email_from'),
                    'partner_phone': kwargs.get('partner_phone'),
                    'applicant_notes': kwargs.get('description', ''),
                }

                skill_lines = []

                skill_types = kwargs.get('skill_type[]', '').split(',')
                skill_ids = kwargs.get('skill_ids[]', '').split(',')
                skill_levels = kwargs.get('skill_level_ids[]', '').split(',')

                if skill_types and skill_ids and skill_levels:
                    for st, si, sl in zip(skill_types, skill_ids, skill_levels):
                        if st and si and sl:
                            skill_lines.append((0, 0, {
                                'skill_type_id': int(st),
                                'skill_id': int(si),
                                'skill_level_id': int(sl),
                            }))

                if skill_lines:
                    vals['current_applicant_skill_ids'] = skill_lines


                # Additional custom fields (from kwargs if they exist)
                custom_fields = ['title_id', 'initial', 'surname', 'passport', 'country_id',
                                 'date_of_birth', 'language_id', 'gender', 'race',
                                 'disability', 'desc_disability', 'source_id',
                                 'higher_qualification', 'current_salary', 'employee_status',
                                 'relocate', 'notice_period', 'work_experience', 'last_role',
                                 'exp_by_role', 'have_honours', 'have_master','current_applicant_skill_ids'
                                 'professional_body', 'terms_conditions','skill_type','skill_ids','skill_level_ids']

                for field in custom_fields:
                    if field in kwargs and kwargs[field]:
                        # Handle Many2ones
                        if field in ['title_id', 'country_id', 'language_id', 'source_id']:
                            vals[field] = int(kwargs[field])
                        else:
                            vals[field] = kwargs[field]
                job = request.env['hr.applicant'].sudo().create(vals)

                # Assign attachments that were uploaded in the previous step
                attachment_fields = ['resume_0_attachment', 'picture_1_attachment',
                                     'qualifications_2_attachment', 'qualifications_3_attachment']

                if job:
                    for field in attachment_fields:
                        attachment_id = kwargs.get(field, None)
                        if attachment_id:
                            attachment = request.env['ir.attachment'].sudo().browse(int(attachment_id))
                            if attachment.exists():
                                attachment.write({'res_id': job.id, 'res_model': job._name})

                    job.sudo().write({
                        'cv_id': kwargs.get('resume_0_attachment', False),
                        'qualification_id': kwargs.get('qualifications_2_attachment', False)
                    })

                # Now link the survey input
                if survey_user_input_id:
                    survey_user_input = request.env['survey.user_input'].sudo().browse(survey_user_input_id)
                    if survey_user_input.exists() and job.id:
                        survey_user_input.write({'application_id': job.id})

            # Cleanup session safely
            for key in ['job_application_data', 'website_model_name', 'survey_user_input']:
                request.session.pop(key, None)

            # Continue original Odoo survey submit
            response = super().survey_submit(survey_token, answer_token, **post)
            return response
        else:
            # Normal survey submission
            response = super().survey_submit(survey_token, answer_token, **post)
            return response
