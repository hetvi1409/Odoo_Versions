from odoo import fields, models
from odoo.exceptions import ValidationError


class OpmsRejectionReasonWizard(models.TransientModel):
    _name = "opms.rejection.reason.wizard"
    _description = "Reject OPMS Submission"

    submission_id = fields.Many2one(
        "opms.reporting.submission",
        string="Submission",
        required=True,
        readonly=True,
    )
    rejection_reason = fields.Text(
        string="Reason for Rejection",
        required=True,
        help="Provide a clear reason for rejecting this submission. This will be stored on the record and posted to the chatter.",
    )

    def action_confirm_rejection(self):
        self.ensure_one()
        if not self.rejection_reason or not self.rejection_reason.strip():
            raise ValidationError("A reason for rejection is required.")

        submission = self.submission_id

        submission.write({
            "workflow_status": "rejected",
            "rejection_reason": self.rejection_reason.strip(),
        })

        return {"type": "ir.actions.act_window_close"}
