from odoo import api, fields, models, _


class HrRecruitmentDegree(models.Model):
    _name = 'hr.recruitment.degree'
    _description = "Applicant Degree"

    name = fields.Char("Degree Name", required=True, translate=True)
    score = fields.Float("Score", required=True, default=0)
    sequence = fields.Integer("Sequence", default=1)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the Degree of Recruitment must be unique!'),
        ('score_range', 'check(score >= 0 and score <= 100)', 'Score should be between 0 and 100!'),
    ]
