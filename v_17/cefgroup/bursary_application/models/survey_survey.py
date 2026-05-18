from odoo import models, fields, api


class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    bursary_id = fields.Many2one('bursary.bursary', string="Bursary")

class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    bursary_application_id =fields.Many2one('bursary.application', string='Bursary Application')

    def _mark_done(self):
        res = super(SurveyUserInput, self)._mark_done()
        if self.bursary_application_id:
            self.bursary_application_id.action_elimination()
        return res
