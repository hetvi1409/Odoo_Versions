from odoo import fields, models, _
from odoo.exceptions import AccessError


class HousingGrantReview(models.TransientModel):
    """Housing Grant Review"""
    _name = "housing.grant.review"

    comments = fields.Char(string="Comments", required=True)
    case_id = fields.Many2one('housing.emergency', string="Emergency Case", required=True, ondelete='cascade')

    def action_submit(self):
        self.ensure_one()
        if not self.env.user.has_group("emergency_housing.group_emergency_housing_municipality_officer"):
            raise AccessError(_("Only Municipality Officers can send feedback."))

        self.case_id.municipality_send_feedback(self.comments)
    # def action_submit(self):
    #     self.case_id.message_post(
    #         body=_('Emergency Housing Grant review: %s - By %s') % (self.comments, self.env.user.name))
