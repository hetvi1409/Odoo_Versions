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
"""Key register for fleet vehicles."""
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FleetVehicleKeyRegister(models.Model):
    """Track key issue and return."""

    _name = "fleet.vehicle.key.register"
    _description = "Vehicle Key Register"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Key Register", required=True, copy=False,
                       default="New")
    state = fields.Selection(
        [("out", "Out"), ("returned", "Returned")],
        default="out",
        tracking=True,
    )
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle", required=True)
    key_number = fields.Char(string="Key Number", required=True)
    issued_to_id = fields.Many2one("hr.employee", string="Issued To", required=True)
    issued_by_id = fields.Many2one(
        "res.users", string="Issued By", default=lambda self: self.env.user
    )
    issued_datetime = fields.Datetime(
        string="Issued On", default=fields.Datetime.now, required=True
    )
    returned_datetime = fields.Datetime(string="Returned On")
    odometer_at_issue = fields.Float(string="Odometer at Issue")
    odometer_at_return = fields.Float(string="Odometer at Return")
    notes = fields.Html(string="Notes")
    request_id = fields.Many2one(
        "fleet.vehicle.request", string="Vehicle Request"
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    @api.model
    def create(self, vals):
        """Assign a sequence on creation."""
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fleet.vehicle.key.register"
            ) or "New"
        return super().create(vals)

    @api.constrains("vehicle_id", "key_number", "state")
    def _check_unique_key_out(self):
        """Allow only one open key record per vehicle/key."""
        for rec in self:
            if rec.state != "out":
                continue
            domain = [
                ("vehicle_id", "=", rec.vehicle_id.id),
                ("key_number", "=", rec.key_number),
                ("state", "=", "out"),
                ("id", "!=", rec.id),
            ]
            if self.search_count(domain):
                raise ValidationError(
                    "A key register entry is already open for this vehicle and key."
                )

    def action_return(self):
        """Mark key as returned."""
        self.write({"state": "returned", "returned_datetime": fields.Datetime.now()})
