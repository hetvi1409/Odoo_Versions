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
"""Accident report model."""
from odoo import api, fields, models


class FleetVehicleAccidentReport(models.Model):
    """Accident/incident report for fleet vehicles."""

    _name = "fleet.vehicle.accident.report"
    _description = "Vehicle Accident Report"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Accident Report", required=True, copy=False,
                       default="New")
    accident_date = fields.Date(string="Accident Date", required=True)
    accident_time = fields.Char(string="Accident Time")
    location = fields.Char(string="Location")
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle", required=True)
    driver_id = fields.Many2one("hr.employee", string="Driver")
    odometer = fields.Float(string="Odometer")
    policy_number = fields.Char(string="Policy Number")
    claim_number = fields.Char(string="Claim Number")
    insurer = fields.Char(string="Insurer")
    description = fields.Text(string="Description")
    accident_description = fields.Text(string="Accident Description")
    damage_to_vehicle = fields.Text(string="Damage to Vehicle")
    other_vehicles = fields.Text(string="Other Vehicles Involved")
    injuries = fields.Text(string="Injuries")
    witness_details = fields.Text(string="Witness Details")
    police_called = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        string="Police Called",
    )
    police_report_number = fields.Char(string="Police Report Number")
    action_taken = fields.Text(string="Action Taken")
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "fleet_vehicle_accident_ir_attachment_rel",
        "report_id",
        "attachment_id",
        string="Attachments",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
        # --- Driver Details ---
    driver_license_number = fields.Char(string="Driver License Number")
    driver_phone = fields.Char(string="Driver Phone")
    driver_address = fields.Char(string="Driver Address")

    # --- Vehicle Details ---
    vehicle_registration_no = fields.Char(string="Vehicle Registration No")
    vehicle_make = fields.Char(string="Vehicle Make")
    vehicle_model = fields.Char(string="Vehicle Model")
    vehicle_year = fields.Char(string="Manufacturing Year")
    chassis_number = fields.Char(string="Chassis Number")
    engine_number = fields.Char(string="Engine Number")
    vehicle_use = fields.Char(string="Vehicle Use")

    # --- Accident Conditions ---
    weather_condition = fields.Selection([
        ("clear", "Clear"),
        ("rain", "Rain"),
        ("fog", "Fog"),
        ("storm", "Storm"),
        ("other", "Other"),
    ], string="Weather Condition")

    road_type = fields.Selection([
        ("highway", "Highway"),
        ("city", "City Road"),
        ("rural", "Rural Road"),
        ("other", "Other"),
    ], string="Road Type")

    road_condition = fields.Selection([
        ("dry", "Dry"),
        ("wet", "Wet"),
        ("mud", "Mud"),
        ("other", "Other"),
    ], string="Road Condition")

    light_condition = fields.Selection([
        ("day", "Daylight"),
        ("night", "Night"),
        ("dawn", "Dawn/Dusk"),
    ], string="Light Condition")

    estimated_speed = fields.Float(string="Estimated Speed (km/h)")
    alcohol_test = fields.Selection([
        ("yes", "Yes"),
        ("no", "No"),
    ], string="Alcohol Test Conducted")

    # --- Third Party Details ---
    third_party_name = fields.Char(string="Third Party Name")
    third_party_contact = fields.Char(string="Third Party Contact")
    third_party_vehicle_no = fields.Char(string="Third Party Vehicle Number")
    third_party_insurer = fields.Char(string="Third Party Insurer")

    # --- Passenger / Injury Details ---
    passenger_count = fields.Integer(string="Number of Passengers")
    passenger_injuries = fields.Text(string="Passenger Injuries Details")

    hospital_name = fields.Char(string="Hospital Name")
    hospital_address = fields.Char(string="Hospital Address")

    # --- Damage / Cost ---
    property_damage_details = fields.Text(string="Property Damage Details")
    towing_required = fields.Boolean(string="Towing Required")
    towing_company = fields.Char(string="Towing Company")
    towing_cost = fields.Float(string="Towing Cost")
    repair_estimate = fields.Float(string="Estimated Repair Cost")

    # --- Claim & Insurance Tracking ---
    claim_intimation_date = fields.Date(string="Claim Intimation Date")
    surveyor_name = fields.Char(string="Surveyor Name")
    survey_date = fields.Date(string="Survey Date")
    policy_expiry_date = fields.Date(string="Policy Expiry Date")

    # --- Reporter Details ---
    reported_by = fields.Char(string="Reported By")
    reporter_contact = fields.Char(string="Reporter Contact")

    # --- Declaration / Signature ---
    driver_signature = fields.Binary(string="Driver Signature")
    officer_signature = fields.Binary(string="Officer Signature")

    @api.model
    def create(self, vals):
        """Assign a sequence on creation."""
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fleet.vehicle.accident.report"
            ) or "New"
        return super().create(vals)
