# -*- coding: utf-8 -*-
from odoo.addons.survey.controllers.main import Survey
from odoo.http import request
from odoo.exceptions import ValidationError, UserError, AccessDenied
from odoo import http, _


class SurveyController(Survey):

    @http.route('/survey/submit/<string:survey_token>/<string:answer_token>',
                type='json', auth='public', website=True)
    def survey_submit(self, survey_token, answer_token, **post):
        if 'bursary_data' in request.session:
            bursary_data = request.session['bursary_data']
            bursary_id = request.session['bursary_id']

            email = bursary_data.get('email')
            identification_no = bursary_data.get('id_number')
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
            application = request.env['bursary.application'].sudo().create(bursary_data)
            survey_user_input = request.session['survey_user_input']

            survey_user_input = request.env['survey.user_input'].sudo().browse(survey_user_input)
            survey_user_input.write({'bursary_application_id': application.id})
            for key in ['bursary_data', 'bursary_id']:
                request.session.pop(key, None)

        response = super().survey_submit(survey_token, answer_token, **post)
        return response