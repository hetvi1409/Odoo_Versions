# -*- coding: utf-8 -*-
from email.policy import default

from odoo import fields, models


class DwellingTypes(models.Model):
    _name = "x.dwelling.types"
    _description = "Dwelling Types"

    x_active = fields.Boolean(string='Active', default=False)
    x_name = fields.Char(string='Name')
    x_studio_notes = fields.Html(
        string="Notes"
    )
    x_studio_partner_phone = fields.Char(
        string="Phone",
        related="x_studio_partner_id.phone",
        store=True
    )
    x_studio_sequence = fields.Integer(
        string="Sequence"
    )

    # Related partner field (not shown in XML, but required for related phone)
    x_studio_partner_id = fields.Many2one(
        "res.partner",
        string="Partner"
    )