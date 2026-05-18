from odoo import fields, models, _


class JobCardDecline(models.TransientModel):
    _name = 'job.card.decline'
    _description = 'Job Card Decline'

    decline_id = fields.Many2one('job.card')
    reason = fields.Text()

    def action_decline(self):
        """Decline Job Card"""
        self.decline_id.is_decline = True
        self.decline_id.write({'decline_reason': self.reason})
        self.decline_id.state = 'declined'
        self.decline_id.helpdesk_job_card_id.is_card_decline = True
