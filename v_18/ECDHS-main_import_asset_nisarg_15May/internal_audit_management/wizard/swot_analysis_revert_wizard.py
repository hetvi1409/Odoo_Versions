from odoo import fields, models, _
from datetime import date

class SwotAnalysisRevert(models.TransientModel):
    """Swot Analysis revert"""
    _name = 'swot.analysis.revert.wizard'

    swot_details  = fields.Many2one('swot.analysis',string="SWOT Analysis")
    comments = fields.Text(string="Comments", required=True)

    def action_submit_revert(self):
        task = self.swot_details
        if task.stages == 'first_reviewer':
            task.tracking_ids.create({
                'tracking_id': task.id,
                'previous': 'First Reviewer',
                'new_state': 'Reverted',
                'user_id': self.env.user.id,
                'comment': self.comments,
                'date_updated': date.today(),
            })
        if task.stages == 'second_reviewer':
            task.tracking_ids.create({
                'tracking_id': task.id,
                'previous': 'Second Reviewer',
                'new_state': 'Reverted',
                'user_id': self.env.user.id,
                'comment': self.comments,
                'date_updated': date.today(),
            })
        if task.stages == 'rejected':
            task.tracking_ids.create({
                'tracking_id': task.id,
                'previous': 'Rejected',
                'new_state': 'Reverted',
                'user_id': self.env.user.id,
                'comment': self.comments,
                'date_updated': date.today(),
            })
        res_user_id = ""
        if task.stages == 'second_reviewer':
            res_user_id = task.preparer_id
        if task.stages == 'approved':
            res_user_id = task.reviewer_id
        self.env['audit.revert'].create({
            'res_id': task.id,
            'res_model': task._name,
            'comments': self.comments,
            'user_id': task.env.uid,
            'record_state': task.stages,
            'reference_type': 'swot_analysis',
            'res_user_id': res_user_id.id if res_user_id else None,
        })
        task.stages = 'reverted'
        task.feedback = self.comments

