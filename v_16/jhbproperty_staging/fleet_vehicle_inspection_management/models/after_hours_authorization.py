# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author:Anjhana A K(<https://www.cybrosys.com>)
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
"""After-hours authorization for fleet vehicles."""
from odoo import api, fields, models


class FleetAfterHoursAuthorization(models.Model):
    """Two-step approval for after-hours vehicle use."""

    _name = "fleet.after.hours.authorization"
    _description = "After-Hours Authorization"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Authorization", required=True, copy=False,
                       default="New", tracking=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("manager_approved", "Manager Approved"),
            ("fleet_approved", "Fleet Office Approved"),
            ("rejected", "Rejected"),
            ("expired", "Expired"),
        ],
        default="draft",
        tracking=True,
    )
    requester_id = fields.Many2one(
        "res.users",
        string="Requester",
        default=lambda self: self.env.user,
        required=True,
    )
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle")
    start_datetime = fields.Datetime(string="Start", required=True)
    end_datetime = fields.Datetime(string="End", required=True)
    reason = fields.Text(string="Reason")
    request_id = fields.Many2one(
        "fleet.vehicle.request", string="Vehicle Request"
    )
    manager_approved_by_id = fields.Many2one(
        "res.users", string="Manager Approved By", readonly=True
    )
    fleet_approved_by_id = fields.Many2one(
        "res.users", string="Fleet Office Approved By", readonly=True
    )
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "fleet_after_hours_ir_attachment_rel",
        "authorization_id",
        "attachment_id",
        string="Attachments",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    @api.model
    def create(self, vals):
        """Assign a sequence on creation."""
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fleet.after.hours.authorization"
            ) or "New"
        return super().create(vals)

    def action_submit(self):
        """Submit for manager approval."""
        self.write({"state": "submitted"})

    def action_manager_approve(self):
        """Manager approval step."""
        self.write(
            {"state": "manager_approved", "manager_approved_by_id": self.env.user.id}
        )

    def action_fleet_approve(self):
        """Fleet office approval step."""
        self.write(
            {"state": "fleet_approved", "fleet_approved_by_id": self.env.user.id}
        )

    def action_reject(self):
        """Reject authorization."""
        self.write({"state": "rejected"})

    def action_expire(self):
        """Expire authorization."""
        self.write({"state": "expired"})
