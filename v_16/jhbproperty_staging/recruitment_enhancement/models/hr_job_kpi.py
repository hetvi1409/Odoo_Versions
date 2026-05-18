from odoo import api, fields, models, _


class HrJobKpi(models.Model):
    _name = 'hr.job.kpi'
    _description = 'Job KPI Tags'
    _order = 'name'

    name = fields.Char(string='KPI Name', required=True, translate=True)
    color = fields.Integer(string='Color Index', default=0)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'KPI name must be unique!')
    ]
