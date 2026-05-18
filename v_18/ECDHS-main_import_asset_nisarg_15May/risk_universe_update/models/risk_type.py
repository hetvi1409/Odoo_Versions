from odoo import fields, models


class RiskType(models.Model):
    _name = 'risk.type'
    _description = "Risk Type"

    name = fields.Char(string="Risk Type", required=True)
    oi_risk_type = fields.Selection(
        [('strategic', 'Strategic Risk Register'), ('operational', 'Operational Risk Register'),
         ('fraud', 'Fraud Risk Register'), ('project', 'Project Risk Register'), ('business', 'Business Unit Risks'),
         ('process', 'Process Risks'),('emerging','Emerging Risk Register')],string='Type')
