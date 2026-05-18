from odoo import models, api
from datetime import date

class AccountDashboard(models.Model):
    _name = "account.dashboard.kpi"
    _description = "Accounting Dashboard Helper"

    @api.model
    def get_kpi_data(self, year):
        start_date = date(int(year), 1, 1)
        end_date = date(int(year), 12, 31)

        # 1. Define domains
        base_domain = [
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('move_id.state', '=', 'posted'),
        ]

        # 2. Account types
        account_obj = self.env['account.account']
        income_account_ids = account_obj.search([('user_type_id.type', '=', 'income')]).ids
        expense_account_ids = account_obj.search([('user_type_id.type', '=', 'expense')]).ids
        cogs_account_ids = account_obj.search([('user_type_id.type', '=', 'direct_cost')]).ids

        # 3. Aggregation function
        def sum_account_balances(account_ids):
            domain = base_domain + [('account_id', 'in', account_ids)]
            group = self.env['account.move.line'].read_group(domain, ['debit', 'credit'], [])
            return group[0]['debit'] - group[0]['credit'] if group else 0.0

        def sum_revenue_balances(account_ids):
            domain = base_domain + [('account_id', 'in', account_ids)]
            group = self.env['account.move.line'].read_group(domain, ['debit', 'credit'], [])
            return group[0]['credit'] - group[0]['debit'] if group else 0.0

        # 4. Calculate values
        revenue = sum_revenue_balances(income_account_ids)
        expenses = sum_account_balances(expense_account_ids)
        cogs = sum_account_balances(cogs_account_ids)
        gross_profit = revenue - cogs
        ebit = gross_profit - expenses
        net_profit = revenue - expenses
        net_profit_margin = (net_profit / revenue * 100) if revenue else 0.0

        # 5. Return formatted values (rounded, K format)
        def format_k(value):
            return round(value / 1000, 2)

        return {
            "revenue": format_k(revenue),
            "gross_profit": format_k(gross_profit),
            "ebit": format_k(ebit),
            "net_profit": format_k(net_profit),
            "net_profit_margin": round(net_profit_margin, 2),
            "expenses": format_k(expenses),
        }


# from odoo import models
# from collections import defaultdict
# from datetime import datetime
#
#
# class AccountingDashboard(models.Model):
#     _name = "account.dashboard.kpi"
#     _description = "Accounting Dashboard KPIs"
#
#
#     def get_kpis(self):
#         print('\n\n\n get_kpis--->',self)
#         # Example calculations
#         revenue = self.env['account.move'].search([
#             ('move_type', '=', 'out_invoice'),
#             ('state', '=', 'posted')
#         ]).mapped('amount_total_signed')
#         expenses = self.env['account.move'].search([
#             ('move_type', '=', 'in_invoice'),
#             ('state', '=', 'posted')
#         ]).mapped('amount_total_signed')
#
#         revenue_total = sum(revenue)
#         expenses_total = sum(expenses)
#         gross_profit = revenue_total - expenses_total
#         net_profit = gross_profit * 0.8  # placeholder
#
#         return {
#             "revenue": revenue_total,
#             "expenses": expenses_total,
#             "gross_profit": gross_profit,
#             "net_profit": net_profit,
#         }
#
#
#     def get_chart_data(self):
#         print('\n\n\n get_chart_data--->',self)
#         revenue_by_month = defaultdict(float)
#         expense_by_month = defaultdict(float)
#
#         invoices = self.env['account.move'].search([
#             ('state', '=', 'posted'),
#             ('move_type', 'in', ['out_invoice', 'in_invoice']),
#             ('invoice_date', '!=', False),
#         ])
#         print('invoices--->',invoices)
#
#         for move in invoices:
#             month_str = move.invoice_date.strftime('%b %Y')  # e.g., "Sep 2025"
#             if move.move_type == 'out_invoice':
#                 revenue_by_month[month_str] += move.amount_total_signed
#             elif move.move_type == 'in_invoice':
#                 expense_by_month[month_str] += move.amount_total_signed
#
#         # Combine all months
#         all_months = sorted(set(revenue_by_month.keys()) | set(expense_by_month.keys()),
#                             key=lambda m: datetime.strptime(m, '%b %Y'))
#
#         revenue_data = [revenue_by_month[m] for m in all_months]
#         expense_data = [expense_by_month[m] for m in all_months]
#
#         return {
#             "months": all_months,
#             "revenue": revenue_data,
#             "expenses": expense_data,
#         }
