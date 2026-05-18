from odoo import models, fields, _
from odoo.exceptions import ValidationError, AccessError
from odoo import api


class InterviewEvaluation(models.Model):
    _name = "interview.evaluation"
    _description = "Interview Evaluation"
    _rec_name = "applicant_id"

    applicant_id = fields.Many2one("hr.applicant", string="Applicant", required=True)
    interviewer_id = fields.Many2one("res.users", string="Interviewer", required=True)
    technical_score = fields.Float(string="Technical Score")
    communication_score = fields.Float(string="Communication Score")
    experience_score = fields.Float(string="Experience Score")
    cultural_fit_score = fields.Float(string="Cultural Fit Score")
    total_score = fields.Float(string="Total Score", compute="_compute_total_score", store=True)

    recommendation = fields.Selection([
        ('strong_hire', 'Strong Hire'),
        ('hire', 'Hire'),
        ('hold', 'Hold'),
        ('reject', 'Reject')
    ])

    comments = fields.Text()

    @api.depends('technical_score', 'communication_score', 'experience_score', 'cultural_fit_score')
    def _compute_total_score(self):
        for rec in self:
            scores = [
                rec.technical_score,
                rec.communication_score,
                rec.experience_score,
                rec.cultural_fit_score
            ]
            total_score = sum(scores)
            rec.total_score = (total_score / len(scores)) if len(scores) > 0 else 0.0
