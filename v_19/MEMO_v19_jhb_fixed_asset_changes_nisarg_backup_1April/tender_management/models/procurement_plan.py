from odoo import models, fields


class ProcurementPlan(models.Model):
    _name = 'procurement.plan'
    _description = 'Procurement Plan'

    name = fields.Char(string='Plan Name')
    year = fields.Char(string='Year')
    # department_id = fields.Many2one('res.department', string='Department', required=True)
    plan_description = fields.Text(string='Plan Description')
    demand_request_id = fields.Many2one('demand.management', string='Demand Request')
    # strategic_objectives_ids = fields.One2many('strategic.objectives', 'procurement_plan_id', string='Strategic Objectives')
    budget_for_year = fields.Float(string='Budget for the Year')
    strategic_objectives = fields.Text(string='Strategic Objectives')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')
