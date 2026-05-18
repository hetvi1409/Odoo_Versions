from odoo import fields, models

class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    application_id = fields.Many2one('hr.applicant', string='Application')

    def _mark_done(self):
        res = super(SurveyUserInput, self)._mark_done()
        if self.application_id:
            self.application_id.calculate_screening_point()
        return res
