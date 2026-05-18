# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    x_studio_name_of_property_owneroccupant = fields.Char(
        string="Name of Property Owner/Occupant"
    )
    x_studio_inspection_comments = fields.Char(
        string="Inspection Comments"
    )
    x_studio_meter_number = fields.Char(
        string="Meter Number"
    )
    x_studio_serial_number = fields.Char(
        string="Serial Number"
    )
    x_studio_readings_comments = fields.Char(
        string="Readings Comments"
    )
    x_studio_condition_comments = fields.Char(
        string="Condition Comments"
    )
    x_studio_account_number = fields.Char(
        string="Account Number"
    )

    x_studio_selection_field_25n_1i5pnigh2 = fields.Selection(
        [
            ('new', 'New'),
            ('partially_verified', 'Partially Verified'),
            ('audited', 'Audited')
        ],
        string="Stages",
        default="new"
    )
    x_studio_meter_audit = fields.Boolean(string='Meter Audit', default=False)