from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PmIntake(models.Model):
    _name = "pm.intake"
    _description = "Project Intake"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # === Fields ===
    name = fields.Char(string="Request Title", required=True, tracking=True)

    requester_id = fields.Many2one(
        "res.users",
        string="Requester",
        help="User who submitted the request",
        tracking=True,
    )
    requester_name = fields.Char(
        string="Requester Name",
        help="Optional name if submitted via public form",
    )
    requester_email = fields.Char(
        string="Requester Email",
        help="Optional email if submitted via public form",
    )

    dept_id = fields.Many2one("hr.department", string="Department")

    summary = fields.Text(string="Summary / Business Need")

    requested_budget = fields.Monetary(string="Requested Budget")
    estimated_effort_days = fields.Float(string="Estimated Effort (days)")

    attachments = fields.Many2many(
        "ir.attachment",
        "pm_intake_attachment_rel",
        "intake_id",
        "attachment_id",
        string="Attachments",
    )

    state = fields.Selection(
        [
            ("submitted", "Submitted"),
            ("pmo_review", "PMO Review"),
            ("business_review", "Business Review"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("converted", "Converted"),
        ],
        string="Status",
        default="submitted",
        tracking=True,
    )

    # approvals_request_id = fields.Many2one(
    #     "approvals.request",
    #     string="Approval Request",
    #     help="Linked approvals workflow if used",
    # )

    project_id = fields.Many2one(
        "project.project",
        string="Converted Project",
        readonly=True,
    )

    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id
    )

    # === Business Logic ===
    def action_submit(self):
        for rec in self:
            rec.state = "submitted"

    def action_pmo_review(self):
        for rec in self:
            rec.state = "pmo_review"

    def action_business_review(self):
        for rec in self:
            rec.state = "business_review"

    def action_approve(self):
        for rec in self:
            rec.state = "approved"

    def action_reject(self):
        for rec in self:
            rec.state = "rejected"

    def action_convert_to_project(self):
        """Create project.project from intake"""
        Project = self.env["project.project"]
        for rec in self:
            if rec.project_id:
                raise UserError(_("This intake has already been converted to a project."))
            project = Project.create(
                {
                    "name": rec.name,
                    "user_id": rec.requester_id.id or False,
                    "description": rec.summary,
                    # "planned_date_begin": fields.Date.today(),
                    # "planned_date_end": rec.estimated_effort_days
                    # and fields.Date.today() + fields.Date.timedelta(days=int(rec.estimated_effort_days))
                    # or False,
                    # "budget_total": rec.requested_budget,
                }
            )
            rec.project_id = project.id
            rec.state = "converted"
            rec.message_post(body=_("Converted to Project: %s") % project.display_name)
        return True
