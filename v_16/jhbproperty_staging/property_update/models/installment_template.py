from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class InstallmentTemplate(models.Model):
    """Inherit the Installment template for add the constraints to
     check the months"""
    _inherit = 'installment.template'

