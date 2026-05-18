from datetime import timedelta
from datetime import datetime, date
from odoo import api, fields, models


class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'
    """The class has been inherited to include the fields for Monthly Actual 
    and Adjusted Budget."""

    monthly_actual = fields.Float(compute='_compute_monthly_actual',
        string='Monthly Actual Report')
    adjust_budget = fields.Float(string='Adjust Budget')

    def _compute_monthly_actual(self):
        """ The function for calculating the 'Monthly Actual' is designed to
        exclusively consider expenditure and revenue specific to the current
        month"""
        for line in self:
            line.monthly_actual = False
            # Get the current date
            today = date.today()

            # Get the first day of the current month
            first_day = today.replace(day=1)

            acc_ids = line.general_budget_id.account_ids.ids
            if line.analytic_account_id.id:
                analytic_line_obj = self.env['account.analytic.line']
                domain = [('account_id', '=', line.analytic_account_id.id),
                          ('date', '>=', first_day),
                          ('date', '<=', today),
                          ]
                if acc_ids:
                    domain += [('general_account_id', 'in', acc_ids)]

                where_query = analytic_line_obj._where_calc(domain)
                analytic_line_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT SUM(amount) from " + from_clause + " where " + where_clause

            else:
                aml_obj = self.env['account.move.line']
                domain = [('account_id', 'in',
                           line.general_budget_id.account_ids.ids),
                          ('date', '>=', first_day),
                          ('date', '<=', today),
                          ('parent_state', '=', 'posted')
                          ]
                where_query = aml_obj._where_calc(domain)
                aml_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT sum(credit)-sum(debit) from " + from_clause + " where " + where_clause

            self.env.cr.execute(select, where_clause_params)
            line.monthly_actual = self.env.cr.fetchone()[0] or 0.0

    @api.depends('date_from', 'date_to')
    def _compute_theoritical_amount(self):
        """Rewrite the compute function for the "Theoretical Amount"
        field to incorporate the necessary conditions for the "Adjust Budget"
        feature when updates are made to the Adjust Budget."""
        # beware: 'today' variable is mocked in the python tests and thus, its implementation matter
        today = fields.Date.today()
        for line in self:
            if not line.adjust_budget:
                if line.paid_date:
                    if today <= line.paid_date:
                        theo_amt = 0.00
                    else:
                        theo_amt = line.planned_amount
                else:
                    if not line.date_from or not line.date_to:
                        line.theoritical_amount = 0
                        continue
                    # One day is added since we need to include the start and end date in the computation.
                    # For example, between April 1st and April 30th, the timedelta must be 30 days.
                    line_timedelta = line.date_to - line.date_from + timedelta(
                        days=1)
                    elapsed_timedelta = today - line.date_from + timedelta(days=1)

                    if elapsed_timedelta.days < 0:
                        # If the budget line has not started yet, theoretical amount should be zero
                        theo_amt = 0.00
                    elif line_timedelta.days > 0 and today < line.date_to:
                        # If today is between the budget line date_from and date_to
                        theo_amt = (
                                               elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * line.planned_amount
                    else:
                        theo_amt = line.planned_amount
                line.theoritical_amount = theo_amt
            else:
                if line.paid_date:
                    if today <= line.paid_date:
                        theo_amt = 0.00
                    else:
                        theo_amt = line.adjust_budget
                else:
                    if not line.date_from or not line.date_to:
                        line.theoritical_amount = 0
                        continue
                    # One day is added since we need to include the start and end date in the computation.
                    # For example, between April 1st and April 30th, the timedelta must be 30 days.
                    line_timedelta = line.date_to - line.date_from + timedelta(
                        days=1)
                    elapsed_timedelta = today - line.date_from + timedelta(
                        days=1)

                    if elapsed_timedelta.days < 0:
                        # If the budget line has not started yet, theoretical amount should be zero
                        theo_amt = 0.00
                    elif line_timedelta.days > 0 and today < line.date_to:
                        # If today is between the budget line date_from and date_to
                        theo_amt = (
                                           elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * line.adjust_budget
                    else:
                        theo_amt = line.adjust_budget
                line.theoritical_amount = theo_amt
