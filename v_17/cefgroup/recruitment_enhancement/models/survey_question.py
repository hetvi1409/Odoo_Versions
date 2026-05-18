# -*- coding: utf-8 -*-
from odoo import fields, models


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    elimination_question = fields.Boolean(string='Is Elimination Question', default=False)

