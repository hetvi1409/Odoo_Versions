from odoo import api, fields, models, _
from collections import defaultdict
from itertools import groupby


class ApplicantSkill(models.Model):
    _inherit = 'hr.applicant.skill'

    profile_id = fields.Many2one('applicant.profile', string="Profile")
    applicant_id = fields.Many2one(
        comodel_name='hr.applicant',
        required=False,
        ondelete='cascade')
    valid_to = fields.Date(string="Validity Stop")

    def _get_current_skills_by_applicant(self):
        sorted_skills = self.sorted(key=lambda a_s: (a_s.applicant_id.id, a_s.skill_id.id))

        applicant_skill_grouped = groupby(
            sorted_skills,
            key=lambda a_s: (a_s.applicant_id, a_s.skill_id)
        )

        result_dict = defaultdict(lambda: self.env["hr.applicant.skill"])

        for (applicant, skill), applicant_skills_iter in applicant_skill_grouped:
            applicant_skills = self.browse([a_s.id for a_s in applicant_skills_iter])

            result_dict[applicant.id] += applicant_skills

        return result_dict

