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
"""Fleet office job card."""
from odoo import api, fields, models


class FleetJobCard(models.Model):
    """Job card for fleet office work."""

    _name = "fleet.job.card"
    _description = "Fleet Job Card"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Job Card", required=True, copy=False, default="New")
    date = fields.Date(string="Date", default=fields.Date.today)
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle")
    driver_id = fields.Many2one("hr.employee", string="Driver")
    driver_sap_number = fields.Char(string="Driver SAP Number")
    hours_worked = fields.Float(string="Hours Worked")
    work_description = fields.Text(string="Work Description")
    client_name = fields.Char(string="Client Name")
    client_department = fields.Char(string="Client Department")
    po_number = fields.Char(string="PO Number")
    hours_with_client = fields.Float(string="Hours With Client")
    start_kms = fields.Float(string="Start KMs")
    end_kms = fields.Float(string="End KMs")
    service_feedback = fields.Text(string="Service Feedback")
    service_rating = fields.Selection(
        [("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")],
        string="Service Rating",
    )
    comments = fields.Text(string="Comments")
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    driver_signature = fields.Binary(string="Driver Signature")
    fleet_manager_signature = fields.Binary(string="Fleet Manager Signature")
    client_signature = fields.Binary(string="Client Signature")

    @api.model
    def create(self, vals):
        """Assign a sequence on creation."""
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fleet.job.card"
            ) or "New"
        return super().create(vals)
