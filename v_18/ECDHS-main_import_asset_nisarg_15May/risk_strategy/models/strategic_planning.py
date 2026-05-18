from odoo import fields, models


class StrategicPlanning(models.Model):
    _inherit = "strategic.planning"


    risk_ids = fields.One2many('oi_risk_management.risk', 'strategy_id', readonly=True)