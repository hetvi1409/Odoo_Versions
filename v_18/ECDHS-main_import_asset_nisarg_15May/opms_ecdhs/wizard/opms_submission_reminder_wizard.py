from odoo import api, fields, models
from odoo.exceptions import ValidationError


class OpmsSubmissionReminderWizard(models.TransientModel):
    _name = "opms.submission.reminder.wizard"
    _description = "Send OPMS Submission Reminder Wizard"

    quarter_id = fields.Many2one(
        "opms.quarter",
        string="Quarter",
        required=True,
        readonly=True,
    )
    reminder_type = fields.Selection(
        [
            ("pre_open_15", "15th Of Prior Month"),
            ("pre_open_25", "25th Of Prior Month"),
            ("before_open", "One Day Before Opening"),
            ("open_day", "Opening Day"),
            ("before_close", "One Day Before Closing"),
            ("close_day", "Closing Day"),
            ("custom", "Custom Reminder"),
        ],
        string="Reminder Type",
        required=True,
        default="custom",
    )
    notification_date = fields.Date(
        string="Notification Date",
        required=True,
        default=lambda self: fields.Date.context_today(self),
        help="Date to include in the reminder email content.",
    )
    custom_subject = fields.Char(
        string="Custom Subject",
        help="Optional. If provided, this subject is used instead of the template subject.",
    )
    custom_note = fields.Text(
        string="Additional Note",
        help="Optional note appended to the reminder message.",
    )

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        result = super().fields_get(allfields=allfields, attributes=attributes)
        term = self.env["opms.label.service"].get_effective_terms().get("quarter", {})
        quarter_label = term.get("singular") or "Quarter"
        if "quarter_id" in result:
            result["quarter_id"]["string"] = quarter_label
        return result

    def action_send(self):
        self.ensure_one()
        if not self.quarter_id:
            raise ValidationError("Quarter is required to send a reminder.")

        self.quarter_id.action_send_submission_reminder(
            reminder_key=self.reminder_type,
            notification_date=self.notification_date,
            custom_note=self.custom_note,
            custom_subject=self.custom_subject,
        )
        return {"type": "ir.actions.act_window_close"}
