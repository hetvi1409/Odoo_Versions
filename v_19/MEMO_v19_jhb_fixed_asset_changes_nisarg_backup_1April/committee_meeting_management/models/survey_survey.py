from odoo import api, fields, models


class SurveySurvey(models.Model):
    """class for add votes in meeting based on this"""
    _inherit = 'survey.survey'

    meeting_id = fields.Many2one('committee.meeting', string="Meeting",
                                 help="Meeting")

    @api.model
    def create(self, vals):
        """generate purchase requisition sequence"""
        result = super(SurveySurvey, self).create(vals)
        if self.env.context.get('meeting'):
            if self.env.context.get('active_model') == 'committee.meeting':
                if self.env.context.get('active_id'):
                    committee = self.env['committee.meeting'].browse(
                        int(self.env.context.get('active_id')))
                    result.meeting_id = int(self.env.context.get('active_id'))
                    committee.survey_id = result.id
        return result

