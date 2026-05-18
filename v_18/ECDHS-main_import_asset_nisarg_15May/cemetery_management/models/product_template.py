from odoo import fields, models


class TariffProductTemplate(models.Model):
    """Tariff Product Template"""
    _inherit = "product.template"

    is_cemetery = fields.Boolean(string="Cemetery")
