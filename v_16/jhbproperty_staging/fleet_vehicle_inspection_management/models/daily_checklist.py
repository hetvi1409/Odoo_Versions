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
"""Daily vehicle checklist."""
from odoo import api, fields, models


class FleetVehicleDailyChecklist(models.Model):
    """Daily checklist mapped from the vehicle checklist sheet."""

    _name = "fleet.vehicle.daily.checklist"
    _description = "Vehicle Daily Checklist"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Checklist", required=True, copy=False,
                       default="New")
    date = fields.Date(string="Date", default=fields.Date.today, required=True)
    depot_name = fields.Char(string="Depot Name")
    region = fields.Char(string="Region")
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle", required=True)
    driver_id = fields.Many2one("hr.employee", string="Driver")
    sap_no = fields.Char(string="SAP No")
    odometer_reading = fields.Float(string="Odometer Reading")
    request_id = fields.Many2one(
        "fleet.vehicle.request", string="Vehicle Request"
    )
    defects_reported = fields.Selection(
        [("yes", "Yes"), ("no", "No")], string="Defects Reported"
    )
    notes = fields.Text(string="Comments")

    license_cof_valid = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        string="License, COF, Operator Card Valid",
    )
    tyres_roadworthy = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        string="All tyres roadworthy, spare included",
    )
    wheel_nuts_secure = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        string="All wheel nuts present and secure",
    )
    logbook_up_to_date = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        string="Logbook up to date",
    )
    damage_check = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        string="Check for damage on the vehicle",
    )
    sufficient_fuel = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        string="Sufficient fuel in vehicle",
    )
    lights_working = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        string="All lights working",
    )
    number_plates = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        string="Number plates",
    )
    vehicle_leaks = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        string="Any leaks on the vehicle",
    )
    jack_and_spanner = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        string="Jack and wheel spanner",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    driver_signature = fields.Binary(string="Driver Signature")
    transport_officer_signature = fields.Binary(string="Transport Officer Signature")
    lto_signature = fields.Binary(string="LTO Signature")

    @api.model
    def create(self, vals):
        """Assign a sequence on creation."""
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fleet.vehicle.daily.checklist"
            ) or "New"
        return super().create(vals)
