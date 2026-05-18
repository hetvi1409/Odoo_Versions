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
"""Policy documents for fleet operations."""
from odoo import api, fields, models


class FleetPolicyDocument(models.Model):
    """Store fleet policy documents."""

    _name = "fleet.policy.document"
    _description = "Fleet Policy Document"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Policy", required=True, copy=False, default="New")
    policy_type = fields.Selection(
        [
            ("fleet", "Fleet Policy"),
            ("after_hours", "After-Hours Policy"),
            ("usage", "Vehicle Usage"),
            ("other", "Other"),
        ],
        string="Policy Type",
        default="fleet",
    )
    effective_date = fields.Date(string="Effective Date")
    description = fields.Text(string="Summary")
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "fleet_policy_ir_attachment_rel",
        "policy_id",
        "attachment_id",
        string="Attachments",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    signature = fields.Binary(string='Signature')
    policy_to = fields.Char(string='To')
    policy_from = fields.Char(string='From')
    subject = fields.Char(string='Subject')

    @api.model
    def create(self, vals):
        """Assign a sequence on creation."""
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fleet.policy.document"
            ) or "New"
        return super().create(vals)
