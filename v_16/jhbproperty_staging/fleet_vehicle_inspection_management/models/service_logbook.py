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
"""Service logbook entries."""
from odoo import api, fields, models


class FleetVehicleServiceLogbook(models.Model):
    """Service logbook mapped from manual logbook sheet."""

    _name = "fleet.vehicle.service.logbook"
    _description = "Fleet Vehicle Service Logbook"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Service Logbook", required=True, copy=False,
                       default="New")
    date = fields.Date(string="Date", default=fields.Date.today, required=True)
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle", required=True)
    driver_id = fields.Many2one("hr.employee", string="Driver")
    depot_name = fields.Char(string="Depot Name")
    opening_odometer = fields.Float(string="Opening Odometer")
    closing_odometer = fields.Float(string="Closing Odometer")
    total_kms = fields.Float(string="Total KMs")
    service_department = fields.Char(string="Service Department")
    service_maintenance = fields.Text(string="Service/Maintenance")
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    @api.model
    def create(self, vals):
        """Assign a sequence on creation."""
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fleet.vehicle.service.logbook"
            ) or "New"
        return super().create(vals)
