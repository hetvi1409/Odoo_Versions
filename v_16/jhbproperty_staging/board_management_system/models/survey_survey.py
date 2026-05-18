from odoo import api, fields, models


class SurveySurvey(models.Model):
    """class for add votes in meeting based on this"""
    _inherit = 'survey.survey'

    meetings_id = fields.Many2one('calendar.event', string="Meeting",
                                 help="Meeting")

    @api.model
    def create(self, vals):
        """generate purchase requisition sequence"""
        result = super(SurveySurvey, self).create(vals)
        if self.env.context.get('meeting'):
            if self.env.context.get('active_model') == 'calendar.event':
                if self.env.context.get('active_id'):
                    meeting = self.env['calendar.event'].browse(
                        int(self.env.context.get('active_id')))
                    result.meetings_id = int(self.env.context.get('active_id'))
                    meeting.survey_id = result.id
        return result

