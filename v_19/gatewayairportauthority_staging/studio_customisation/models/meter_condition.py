# -*- coding: utf-8 -*-
from odoo import  fields, models


class MeterCondition(models.Model):
    _name = "x.meter.condition"
    _description = "Meter Condition"

    x_studio_notes = fields.Html(
        string="Notes"
    )
    x_studio_partner_phone = fields.Char(
        string="Phone",
        related="x_studio_partner_id.phone",
        store=True
    )

    # Related partner field (required for related phone)
    x_studio_partner_id = fields.Many2one(
        "res.partner",
        string="Partner"
    )
    x_name = fields.Char(string='Name')
