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
"""Vehicle request workflow."""
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class FleetVehicleRequest(models.Model):
    """Vehicle request with two-step approval."""

    _name = "fleet.vehicle.request"
    _description = "Fleet Vehicle Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Request", required=True, copy=False,
                       default="New", tracking=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("manager_approved", "Manager Approved"),
            ("fleet_approved", "Fleet Office Approved"),
            ("allocated", "Allocated"),
            ("completed", "Completed"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        tracking=True,
    )
    requester_id = fields.Many2one(
        "res.users",
        string="Requester",
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )
    department_id = fields.Many2one("hr.department", string="Department")
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle")
    driver_id = fields.Many2one("hr.employee", string="Driver")
    requested_vehicle_model_id = fields.Many2one(
        "fleet.vehicle.model", string="Requested Model"
    )
    requested_vehicle_type = fields.Char(string="Requested Type")
    purpose = fields.Text(string="Purpose")
    pickup_location = fields.Char(string="Pickup Location")
    destination = fields.Char(string="Destination")
    transport_type = fields.Selection(
        [
            ("one_way", "One Way"),
            ("return", "Return"),
            ("multi_stop", "Multiple Stops"),
        ],
        default="return",
        string="Transport Type",
        tracking=True,
    )
    number_of_passengers = fields.Integer(string="Passengers", default=1)
    passenger_names = fields.Text(string="Passenger Names")
    distance_km = fields.Float(string="Estimated Distance (KM)")
    start_datetime = fields.Datetime(string="Start")
    end_datetime = fields.Datetime(string="End")
    after_hours_id = fields.Many2one(
        "fleet.after.hours.authorization",
        string="After-Hours Authorization",
    )
    is_urgent = fields.Boolean(string="Urgent", default=False, tracking=True)
    priority = fields.Selection(
        [
            ("0", "Low"),
            ("1", "Normal"),
            ("2", "High"),
            ("3", "Very High"),
        ],
        string="Priority",
        default="1",
        tracking=True,
    )
    notes = fields.Html(string="Notes")
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "fleet_vehicle_request_ir_attachment_rel",
        "request_id",
        "attachment_id",
        string="Attachments",
    )
    manager_approved_by_id = fields.Many2one(
        "res.users", string="Manager Approved By", readonly=True
    )
    fleet_approved_by_id = fields.Many2one(
        "res.users", string="Fleet Office Approved By", readonly=True
    )
    trip_log_id = fields.Many2one(
        "fleet.vehicle.trip.log", string="Trip Log", readonly=True
    )
    key_register_id = fields.Many2one(
        "fleet.vehicle.key.register", string="Key Register", readonly=True
    )
    checklist_ids = fields.One2many(
        "fleet.vehicle.daily.checklist",
        "request_id",
        string="Daily Checklists",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    @api.model
    def create(self, vals):
        """Assign a sequence on creation."""
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fleet.vehicle.request"
            ) or "New"
        return super().create(vals)

    def action_submit(self):
        """Submit for manager approval."""
        self._validate_request()
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

    def action_allocate(self):
        """Allocate vehicle/driver."""
        for rec in self:
            if not rec.vehicle_id or not rec.driver_id:
                raise UserError("Select a vehicle and driver before allocation.")
            values = {"state": "allocated"}
            if not rec.trip_log_id:
                trip_log = self.env["fleet.vehicle.trip.log"].create({
                    "vehicle_id": rec.vehicle_id.id,
                    "driver_id": rec.driver_id.id,
                    "date": fields.Date.context_today(self),
                    "start_time": rec.start_datetime,
                    "destination": rec.destination,
                    "remarks": rec.purpose,
                    "request_id": rec.id,
                })
                values["trip_log_id"] = trip_log.id
            if not rec.key_register_id:
                license_plate = rec.vehicle_id.license_plate or rec.vehicle_id.name
                key_number = f"KEY-{(license_plate or 'UNKNOWN').replace(' ', '')}"
                key_register = self.env["fleet.vehicle.key.register"].create({
                    "vehicle_id": rec.vehicle_id.id,
                    "issued_to_id": rec.driver_id.id,
                    "key_number": key_number,
                    "issued_datetime": fields.Datetime.now(),
                    "notes": f"Auto-issued for request {rec.name}.",
                    "request_id": rec.id,
                })
                values["key_register_id"] = key_register.id
            rec.write(values)

    def action_complete(self):
        """Mark request as completed."""
        for rec in self:
            if rec.trip_log_id and not rec.trip_log_id.end_time:
                rec.trip_log_id.end_time = rec.end_datetime or fields.Datetime.now()
            if rec.key_register_id and rec.key_register_id.state == "out":
                rec.key_register_id.action_return()
            rec.write({"state": "completed"})

    def action_reject(self):
        """Reject request."""
        self.write({"state": "rejected"})

    def action_view_trip_log(self):
        """Open the linked trip log."""
        self.ensure_one()
        action = self.env.ref(
            "fleet_vehicle_inspection_management.fleet_trip_log_action"
        ).read()[0]
        if self.trip_log_id:
            action["domain"] = [("id", "=", self.trip_log_id.id)]
            action["views"] = [(False, "form")]
            action["res_id"] = self.trip_log_id.id
        else:
            action["domain"] = [("request_id", "=", self.id)]
        return action

    def action_view_key_register(self):
        """Open the linked key register entry."""
        self.ensure_one()
        action = self.env.ref(
            "fleet_vehicle_inspection_management.fleet_key_register_action"
        ).read()[0]
        if self.key_register_id:
            action["domain"] = [("id", "=", self.key_register_id.id)]
            action["views"] = [(False, "form")]
            action["res_id"] = self.key_register_id.id
        else:
            action["domain"] = [("request_id", "=", self.id)]
        return action

    def action_view_checklists(self):
        """Open daily checklists linked to this request."""
        self.ensure_one()
        action = self.env.ref(
            "fleet_vehicle_inspection_management.fleet_daily_checklist_action"
        ).read()[0]
        action["domain"] = [("request_id", "=", self.id)]
        return action

    def action_create_checklist(self):
        """Create a daily checklist for the allocated vehicle."""
        self.ensure_one()
        if not self.vehicle_id:
            raise UserError("Assign a vehicle before creating a checklist.")
        checklist = self.env["fleet.vehicle.daily.checklist"].create({
            "vehicle_id": self.vehicle_id.id,
            "driver_id": self.driver_id.id,
            "date": fields.Date.context_today(self),
            "request_id": self.id,
        })
        return {
            "type": "ir.actions.act_window",
            "res_model": "fleet.vehicle.daily.checklist",
            "view_mode": "form",
            "res_id": checklist.id,
        }

    @api.constrains("start_datetime", "end_datetime")
    def _check_dates(self):
        for rec in self:
            if rec.start_datetime and rec.end_datetime and rec.end_datetime < rec.start_datetime:
                raise ValidationError("End time must be after start time.")

    @api.constrains("number_of_passengers")
    def _check_passengers(self):
        for rec in self:
            if rec.number_of_passengers < 1:
                raise ValidationError("Number of passengers must be at least 1.")

    def _validate_request(self):
        if self.start_datetime and self.end_datetime and self.end_datetime < self.start_datetime:
            raise ValidationError("End time must be after start time.")
