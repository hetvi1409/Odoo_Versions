# -*- coding: utf-8 -*-
from odoo.addons.survey.controllers.main import Survey
from odoo import http
from odoo.http import request


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

    @http.route('/survey/submit/<string:survey_token>/<string:answer_token>', type='json', auth='public', website=True)
    def survey_submit(self, survey_token, answer_token, **post):
        """ Submit a page from the survey.
            This incorporates website job application submission logic.
        """
        response = super().survey_submit(survey_token, answer_token, **post)

        job_application_data = request.session.get('job_application_data')
        if not job_application_data:
            return response

        website_model_name = request.session.get('website_model_name')
        survey_user_input_id = request.session.get('survey_user_input')
        if website_model_name != 'hr.applicant' or not survey_user_input_id:
            return response

        survey_user_input = request.env['survey.user_input'].sudo().browse(survey_user_input_id)
        if not survey_user_input.exists() or survey_user_input.state != 'done':
            # Only create the application when the survey is completed.
            return response

        # Avoid duplicates on refresh / retry.
        if not survey_user_input.application_id:
            def _to_int(value):
                try:
                    return int(value)
                except Exception:
                    return False

            def _to_bool(value):
                if value is True:
                    return True
                if not value:
                    return False
                return str(value).strip().lower() in ('1', 'true', 'yes', 'y', 'on')

            vals = {
                'job_id': _to_int(job_application_data.get('job_id')) or False,
                'name': job_application_data.get('partner_name'),
                # 'first_name': job_application_data.get('partner_name'),
                'partner_name': job_application_data.get('partner_name'),
                # 'surname': job_application_data.get('surname'),
                # 'title': job_application_data.get('title'),
                # 'initial': job_application_data.get('initial'),
                # 'is_sa_citizen': job_application_data.get('is_sa_citizen'),
                # 'sa_id_number': job_application_data.get('sa_id_number'),
                # 'passport': job_application_data.get('passport'),
                'email_from': job_application_data.get('email_from'),
                # 'dob': job_application_data.get('date_of_birth'),
                'partner_phone': job_application_data.get('partner_phone'),
                # 'country_id': _to_int(job_application_data.get('country_id')) or False,
                # 'language_id': _to_int(job_application_data.get('language_id')) or False,
                # 'gender': job_application_data.get('gender'),
                # 'race': job_application_data.get('race'),
                # 'disability': job_application_data.get('disability'),
                # 'disability_specify': job_application_data.get('disability_specify'),
                # 'source_id': _to_int(job_application_data.get('source_id')) or False,
                # 'current_salary': job_application_data.get('current_salary'),
                # 'higher_qualification': job_application_data.get('higher_qualification'),
                # 'other_higher_qualification': job_application_data.get('other_higher_qualification'),
                # 'field_study': job_application_data.get('field_study'),
                # 'other_field_study': job_application_data.get('other_field_study'),
                # 'award_sanction': job_application_data.get('award_sanction'),
                # 'criminal_record': job_application_data.get('criminal_record'),
                # 'criminal_act_type': job_application_data.get('criminal_act_type'),
                # 'criminal_case_date': job_application_data.get('criminal_case_date'),
                # 'outcome_judgment': job_application_data.get('outcome_judgment'),
                # 'relocate': job_application_data.get('relocate'),
                # 'notice_period': job_application_data.get('notice_period'),
                # 'employee_status': job_application_data.get('employee_status'),
                # 'employee_no': job_application_data.get('employee_no'),
                # 'work_experience': job_application_data.get('work_experience'),
                # 'last_role': job_application_data.get('last_role'),
                # 'exp_by_role': job_application_data.get('exp_by_role'),
                # 'have_honours': job_application_data.get('have_honours'),
                # 'have_master': job_application_data.get('have_master'),
                # 'professional_body': job_application_data.get('professional_body'),
                # 'profile_description': job_application_data.get('profile_description'),
                # 'terms_condition': _to_bool(job_application_data.get('terms_condition')),
            }

            # Skills selected on the website form (if any)
            skill_lines = []
            skill_types = (job_application_data.get('skill_type[]') or '').split(',')
            skill_ids = (job_application_data.get('skill_ids[]') or '').split(',')
            skill_levels = (job_application_data.get('skill_level_ids[]') or '').split(',')
            for st, si, sl in zip(skill_types, skill_ids, skill_levels):
                st_i, si_i, sl_i = _to_int(st), _to_int(si), _to_int(sl)
                if st_i and si_i and sl_i:
                    skill_lines.append((0, 0, {
                        'skill_type_id': st_i,
                        'skill_id': si_i,
                        'skill_level_id': sl_i,
                    }))
            if skill_lines:
                vals['applicant_skill_ids'] = skill_lines

            applicant = request.env['hr.applicant'].sudo().create(vals)

            # Assign attachments that were uploaded in the previous step
            attachment_keys = [
                'resume_0_attachment',
                'picture_1_attachment',
                'qualifications_2_attachment',
                'qualifications_3_attachment',
            ]
            for key in attachment_keys:
                attachment_id = _to_int(job_application_data.get(key))
                if attachment_id:
                    attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
                    if attachment.exists():
                        attachment.write({'res_id': applicant.id, 'res_model': applicant._name})

            cv_id = _to_int(job_application_data.get('resume_0_attachment'))
            qualification_id = _to_int(job_application_data.get('qualifications_2_attachment'))
            applicant.sudo().write({
                'cv_id': cv_id or False,
                'qualification_id': qualification_id or False,
            })

            survey_user_input.write({'application_id': applicant.id})
            applicant.calculate_screening_point()

        # Cleanup session safely once the application has been created or linked.
        for key in ('job_application_data', 'website_model_name', 'survey_user_input'):
            request.session.pop(key, None)

        return response
