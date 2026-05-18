from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class BudgetMixin(models.AbstractModel):
    _name = 'project.mixin_budget'
    _description = 'Budget Computation Mixin'

    budget_planned = fields.Monetary(
        string='Planned Budget',
        compute='_compute_budget',
        store=False
    )
    budget_actual = fields.Monetary(
        string='Actual Spend',
        compute='_compute_budget',
        store=False
    )
    budget_variance = fields.Monetary(
        string='Budget Variance',
        compute='_compute_budget',
        store=False
    )
    currency_id = fields.Many2one(
        'res.currency',
        # related='analytic_account_id.company_id.currency_id',
        store=True,
        readonly=True
    )

    def _compute_budget(self):
        for rec in self:
            aa = rec.analytic_account_id
            # planned = sum of budget lines on any crossovered.budget linked to this AA
            budget_amount = sum(self.env['budget.line'].search([('account_id', '=', aa.id)]).mapped('budget_amount'))
            print(budget_amount, )
            # actual = sum of analytic lines underneath this AA (SQL efficient with parent_left/right)
            # actual = self.env[
            #     'account.analytic.line'].read_group(
            #     [('account_id', '=', aa.id)], ['amount'], [])
            actual = sum(self.env[
                'account.analytic.line'].search(
                [('account_id', '=', aa.id)]).mapped('amount'))
            rec.budget_planned = budget_amount
            rec.budget_actual = actual
            rec.budget_variance = rec.budget_planned - rec.budget_actual
