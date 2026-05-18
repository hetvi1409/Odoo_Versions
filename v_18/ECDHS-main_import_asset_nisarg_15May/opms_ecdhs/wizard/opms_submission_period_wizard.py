from odoo import api, fields, models
from odoo.exceptions import UserError


class OpmsSubmissionPeriodWizard(models.TransientModel):
    _name = "opms.submission.period.wizard"
    _description = "Manual Submission Period Override Wizard"

    quarter_id = fields.Many2one(
        "opms.quarter",
        string="Quarter",
        required=True,
        readonly=True,
    )
    action_type = fields.Selection(
        [("open", "Force Open"), ("close", "Force Close")],
        string="Action",
        required=True,
        readonly=True,
    )
    manual_override_until = fields.Date(
        string="Override Expires On",
        required=True,
        help=(
            "The manual override automatically clears on this date and automatic "
            "scheduling resumes.\n"
            "• Force-Open: set to the day after the submission close date so "
            "auto-close still fires on schedule.\n"
            "• Force-Close: set to the submission open date so auto-open still "
            "fires on schedule."
        ),
    )

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        result = super().fields_get(allfields=allfields, attributes=attributes)
        term = self.env["opms.label.service"].get_effective_terms().get("quarter", {})
        quarter_label = term.get("singular") or "Quarter"
        if "quarter_id" in result:
            result["quarter_id"]["string"] = quarter_label
        return result

    @api.constrains("manual_override_until")
    def _check_override_until_future(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.manual_override_until and rec.manual_override_until <= today:
                raise UserError(
                    "Override Expires On must be a future date. "
                    "The override will auto-clear on that date and restore the automatic schedule."
                )

    def action_confirm(self):
        self.ensure_one()
        quarter = self.quarter_id
        if self.action_type == "open":
            quarter.write({
                "submission_period_state": "open",
                "submission_manual_override": True,
                "manual_override_until": self.manual_override_until,
            })
        else:
            quarter.write({
                "submission_period_state": "closed",
                "submission_manual_override": True,
                "manual_override_until": self.manual_override_until,
            })
        return {"type": "ir.actions.act_window_close"}
