from odoo import api, fields, models


class SurveySurvey(models.Model):
    """class for add votes in meeting based on this"""
    _inherit = 'survey.survey'

    meetings_id = fields.Many2one('calendar.event', string="Meeting",
                                 help="Meeting")

    @api.model_create_multi
    def create(self, vals_list):
        """Generate purchase requisition sequence and link to meeting if in context."""
        records = super(SurveySurvey, self).create(vals_list)

        # Only handle context-based meeting linking if relevant
        if self.env.context.get('meeting'):
            active_model = self.env.context.get('active_model')
            active_id = self.env.context.get('active_id')
            if active_model == 'calendar.event' and active_id:
                meeting = self.env['calendar.event'].browse(int(active_id))
                for record in records:
                    record.meetings_id = int(active_id)
                    meeting.survey_id = record.id

        return records

