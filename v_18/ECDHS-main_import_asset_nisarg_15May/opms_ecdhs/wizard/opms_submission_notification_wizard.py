from odoo import fields, models
from odoo.exceptions import ValidationError


class OpmsSubmissionNotificationWizard(models.TransientModel):
    _name = "opms.submission.notification.wizard"
    _description = "Send OPMS Submission Notification"

    submission_ids = fields.Many2many(
        "opms.reporting.submission",
        relation="opms_notif_wizard_submission_rel",
        string="Submissions",
        required=True,
    )
    notification_type = fields.Selection(
        [
            ("manager_submission_alert", "Manager Submission Alert"),
            ("submitter_rejection_alert", "Submitter Rejection Alert"),
        ],
        string="Notification Type",
        required=True,
        default="manager_submission_alert",
        help=(
            "Manager Submission Alert: notifies active OPMS Managers linked to the "
            "selected submission's directorate.\n"
            "Submitter Rejection Alert: sends the rejection email to each submission's "
            "Submitted By user and logs the event in chatter."
        ),
    )
    custom_note = fields.Text(
        string="Additional Note",
        help="Optional note appended to the notification email.",
    )

    def action_send(self):
        self.ensure_one()
        if not self.submission_ids:
            raise ValidationError("Please select at least one submission to notify about.")

        if self.notification_type == "manager_submission_alert":
            self.submission_ids._notify_managers_submission_completed(
                custom_note=self.custom_note or False,
            )
        elif self.notification_type == "submitter_rejection_alert":
            non_rejected = self.submission_ids.filtered(lambda rec: rec.workflow_status != "rejected")
            if non_rejected:
                raise ValidationError(
                    "Submitter Rejection Alert can only be sent for submissions in the Rejected stage."
                )
            self.submission_ids._notify_submitter_submission_rejected(
                custom_note=self.custom_note or False,
            )

        return {"type": "ir.actions.act_window_close"}
