from odoo import api, fields, models, _


class ApplicantSkill(models.Model):
    _inherit = 'hr.applicant.skill'

    profile_id = fields.Many2one('applicant.profile', string="Profile")
    applicant_id = fields.Many2one(
        comodel_name='hr.applicant',
        required=False,
        ondelete='cascade')

