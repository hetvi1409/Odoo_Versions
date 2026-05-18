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
"""Fuel register with monthly lines."""
from odoo import api, fields, models


class FleetFuelRegister(models.Model):
    """Monthly fuel register."""

    _name = "fleet.fuel.register"
    _description = "Fleet Fuel Register"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Fuel Register", required=True, copy=False,
                       default="New")
    month = fields.Selection(
        [
            ("01", "January"),
            ("02", "February"),
            ("03", "March"),
            ("04", "April"),
            ("05", "May"),
            ("06", "June"),
            ("07", "July"),
            ("08", "August"),
            ("09", "September"),
            ("10", "October"),
            ("11", "November"),
            ("12", "December"),
        ],
        string="Month",
        required=True,
    )
    year = fields.Integer(string="Year", required=True)
    depot_name = fields.Char(string="Depot Name")
    line_ids = fields.One2many(
        "fleet.fuel.register.line", "register_id", string="Fuel Lines"
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    @api.model
    def create(self, vals):
        """Assign a sequence on creation."""
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fleet.fuel.register"
            ) or "New"
        return super().create(vals)


class FleetFuelRegisterLine(models.Model):
    """Fuel register line items."""

    _name = "fleet.fuel.register.line"
    _description = "Fleet Fuel Register Line"

    register_id = fields.Many2one("fleet.fuel.register", string="Register")
    date = fields.Date(string="Date", required=True)
    driver_id = fields.Many2one("hr.employee", string="Driver")
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle")
    opening_odometer = fields.Float(string="Opening Odometer")
    closing_odometer = fields.Float(string="Closing Odometer")
    total_kms = fields.Float(string="Total KMs")
    liters = fields.Float(string="Liters")
    fuel_value = fields.Monetary(string="Fuel Value")
    currency_id = fields.Many2one(
        "res.currency",
        related="register_id.company_id.currency_id",
        string="Currency",
        readonly=True,
    )
