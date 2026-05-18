from odoo import models, fields, api


class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    active = fields.Boolean("Active", default=True, tracking=True)
    job_id = fields.Many2one('hr.job', string="Related Job Position")
    required_score = fields.Float(string='Required Score', copy=False, required=True, default=0.0)
    total_score = fields.Float(string='Total Score', copy=False, required=True,
                               compute='_compute_total_score')

    @api.depends('question_and_page_ids', 'question_and_page_ids.is_scored_question', 'question_and_page_ids.answer_score', 'question_and_page_ids.suggested_answer_ids')
    def _compute_total_score(self):
        for rec in self:
            total_possible_score = 0
            for question in rec.question_and_page_ids:
                if question.question_type == 'simple_choice':
                    total_possible_score += max([score for score in
                                                 question.mapped(
                                                     'suggested_answer_ids.answer_score')
                                                 if score > 0], default=0)
                elif question.question_type == 'multiple_choice':
                    total_possible_score += sum(score for score in
                                                question.mapped(
                                                    'suggested_answer_ids.answer_score')
                                                if score > 0)
                elif getattr(question, 'is_scored_question', False):
                    total_possible_score += question.answer_score
            rec.total_score = total_possible_score
