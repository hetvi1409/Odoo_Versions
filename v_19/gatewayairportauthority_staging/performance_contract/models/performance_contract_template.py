from odoo import models, fields

class PerformanceContractTemplate(models.Model):
    _name = "performance.contract.template"
    _description = "Performance Contract Template"

    name = fields.Char(required=True)
    description = fields.Text()
    # kpi_ids = fields.One2many(
    #     "hr.appraisal.goal", "template_id", string="KPIs"
    # )
    active = fields.Boolean(default=True)