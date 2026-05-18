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
"""Trip log book."""
from odoo import api, fields, models


class FleetVehicleTripLog(models.Model):
    """Daily trip log and condition report."""

    _name = "fleet.vehicle.trip.log"
    _description = "Fleet Vehicle Trip Log"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Trip Log", required=True, copy=False, default="New")
    date = fields.Date(string="Date", default=fields.Date.today, required=True)
    date_end = fields.Date(
        string="End Date",
        compute="_compute_date_end",
        store=True,
    )
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle", required=True)
    driver_id = fields.Many2one("hr.employee", string="Driver")
    start_time = fields.Datetime(string="Start of Duty")
    end_time = fields.Datetime(string="End of Duty")
    start_odometer = fields.Float(string="Start Odometer")
    end_odometer = fields.Float(string="End Odometer")
    distance = fields.Float(string="Distance Covered")
    destination = fields.Char(string="Destination")
    remarks = fields.Text(string="Remarks")
    request_id = fields.Many2one(
        "fleet.vehicle.request", string="Vehicle Request"
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    @api.depends("date")
    def _compute_date_end(self):
        """Mirror date for calendar view end date."""
        for rec in self:
            rec.date_end = rec.date

    @api.model
    def create(self, vals):
        """Assign a sequence on creation."""
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fleet.vehicle.trip.log"
            ) or "New"
        return super().create(vals)
