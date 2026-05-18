from odoo import http
from odoo.http import request
from datetime import date
import calendar
import json


class AccountingDashboardController(http.Controller):


    # Net Profit CALCULATION
    @http.route("/dashboard/expense_cost", type="json", auth="user")
    def get_expense_cost(self, **kwargs):
        data = json.loads(request.httprequest.data)
        year = int(data.get("year", date.today().year))
        print('Year received:', year)

        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        expense_cost_lines = request.env['account.move.line'].sudo().search([
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('account_id.account_type', '=', 'expense_direct_cost'),
            ('parent_state', '=', 'posted'),
        ])

        total_expense_cost = sum(expense_cost_lines.mapped('balance'))  # balance is signed value

        expense_cost_value = abs(total_expense_cost)
        print('expense_cost_value-->', expense_cost_value)

        return {
            "year": year,
            "expense_cost": round(expense_cost_value, 2),
        }
    # *************************************************************************************

    @http.route("/dashboard/revenue_vs_gross_monthly", type="json", auth="user")
    def get_revenue_vs_gross_monthly(self, **kwargs):
        data = json.loads(request.httprequest.data)
        year = int(data.get("year", date.today().year))
        print('Year received:', year)

        monthly_data = []

        for month in range(1, 13):
            start_date = date(year, month, 1)
            end_date = date(year, month, calendar.monthrange(year, month)[1])

            # Revenue
            revenue_lines = request.env['account.move.line'].sudo().search([
                ('date', '>=', start_date),
                ('date', '<=', end_date),
                ('account_id.account_type', '=', 'income'),
                ('parent_state', '=', 'posted'),
            ])
            total_revenue = abs(sum(revenue_lines.mapped('balance')))

            # Other Income
            other_income_lines = request.env['account.move.line'].sudo().search([
                ('date', '>=', start_date),
                ('date', '<=', end_date),
                ('account_id.account_type', '=', 'income_other'),
                ('parent_state', '=', 'posted'),
            ])
            total_other_income = abs(sum(other_income_lines.mapped('balance')))

            gross_profit = total_revenue + total_other_income

            monthly_data.append({
                "month": calendar.month_abbr[month],
                "revenue": round(total_revenue, 2),
                "gross_profit": round(gross_profit, 2),
            })
        print('monthly_data--->',monthly_data)

        return {
            "year": year,
            "data": monthly_data
        }

    @http.route("/dashboard/income_vs_expense", type="json", auth="user")
    def get_income_vs_expense(self, **kwargs):
        data = json.loads(request.httprequest.data)
        year = int(data.get("year", date.today().year))
        print('Year received:', year)

        monthly_data = []

        for month in range(1, 13):
            start_date = date(year, month, 1)
            end_date = date(year, month, calendar.monthrange(year, month)[1])

            # Income (Gross Profit = Revenue + Other Income)
            revenue_lines = request.env['account.move.line'].sudo().search([
                ('date', '>=', start_date),
                ('date', '<=', end_date),
                ('account_id.account_type', '=', 'income'),
                ('parent_state', '=', 'posted'),
            ])
            total_revenue = abs(sum(revenue_lines.mapped('balance')))
            # print('total_revenue---->',total_revenue)

            other_income_lines = request.env['account.move.line'].sudo().search([
                ('date', '>=', start_date),
                ('date', '<=', end_date),
                ('account_id.account_type', '=', 'income_other'),
                ('parent_state', '=', 'posted'),
            ])
            total_other_income = abs(sum(other_income_lines.mapped('balance')))

            gross_profit = total_revenue + total_other_income
            # print('gross_profit--->',gross_profit)

            # Expenses (all expense account types)
            expense_lines = request.env['account.move.line'].sudo().search([
                ('date', '>=', start_date),
                ('date', '<=', end_date),
                ('account_id.account_type', '=', 'expense'),
                ('parent_state', '=', 'posted'),
            ])
            total_expense = abs(sum(expense_lines.mapped('balance')))
            # print('total_expense--->',total_expense)

            monthly_data.append({
                "month": calendar.month_abbr[month],
                "income": round(gross_profit, 2),
                "expense": round(total_expense, 2),
            })
        print('monthly_data--->',monthly_data)

        return {
            "year": year,
            "data": monthly_data
        }

    # ****************************************************************************************************

    @http.route("/dashboard/revenue", type="json", auth="user")
    def get_revenue(self, **kwargs):

        data = json.loads(request.httprequest.data)
        year = int(data.get("year", date.today().year))
        print('Year received:', year)

        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        revenue_lines = request.env['account.move.line'].sudo().search([
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('account_id.account_type', '=', 'income'),
            ('parent_state', '=', 'posted'),
        ])

        total_revenue = sum(revenue_lines.mapped('balance'))  # balance is signed value
        revenue_value = abs(total_revenue)

        return {
            "year": year,
            "revenue": round(revenue_value, 2),
        }

    # Revenue
    # @http.route("/dashboard/revenue", type="json", auth="user")
    # def get_revenue(self, **kwargs):
    #     print('selft---->',self)
    #     print('self.env.user--->',request.env.user)
    #     print('self.env.user--->',request.env.user.company_id)
    #     print('self.env.user--->',request.env.user.company_id.name)
    #     year = int(kwargs.get("year", date.today().year))
    #
    #     start_date = date(year, 1, 1)
    #     end_date = date(year, 12, 31)
    #
    #     revenue_lines = request.env['account.move.line'].sudo().search([
    #         ('date', '>=', start_date),
    #         ('date', '<=', end_date),
    #         ('account_id.account_type', '=', 'income'),
    #         ('parent_state', '=', 'posted'),
    #     ])
    #
    #     total_revenue = sum(revenue_lines.mapped('balance'))  # balance is signed value
    #
    #     revenue_value = abs(total_revenue)
    #     print('revenue_value-->',revenue_value)
    #
    #     return {
    #         "year": year,
    #         "revenue": round(revenue_value,2),
    #     }

    # other_income for Gross Profit
    @http.route("/dashboard/other_income", type="json", auth="user")
    def get_other_income(self, **kwargs):
        data = json.loads(request.httprequest.data)
        year = int(data.get("year", date.today().year))
        print('Year received:', year)

        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        other_income_lines = request.env['account.move.line'].sudo().search([
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('parent_state', '=', 'posted'),
            ('account_id.account_type', '=', 'income_other')
        ])

        total_other_income_lines = sum(other_income_lines.mapped('balance'))
        other_income_value = abs(total_other_income_lines)
        print('other_income_value-->', other_income_value)

        return {
            "year": year,
            "other_income": round(other_income_value, 2),
        }

    # Expense
    @http.route("/dashboard/expenses", type="json", auth="user")
    def get_expense(self, **kwargs):
        data = json.loads(request.httprequest.data)
        year = int(data.get("year", date.today().year))
        print('Year received:', year)
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        expense_lines = request.env['account.move.line'].sudo().search([
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('account_id.account_type', '=', 'expense'),
            ('parent_state', '=', 'posted'),
        ])
        total_expenses = sum(expense_lines.mapped('balance'))
        expense_value = abs(total_expenses)
        return {
            "year": year,
            "expense": round(expense_value,2),
        }

    # DEPRECIATION
    @http.route("/dashboard/depreciation", type="json", auth="user")
    def get_depreciation(self, **kwargs):
        data = json.loads(request.httprequest.data)
        year = int(data.get("year", date.today().year))
        print('Year received:', year)
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        depreciation_lines = request.env['account.move.line'].sudo().search([
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('account_id.account_type', '=', 'expense_depreciation'),
            ('parent_state', '=', 'posted'),
        ])

        total_depreciation = sum(depreciation_lines.mapped('balance'))
        print('total_depreciation--->', total_depreciation)
        depreciation_value = abs(total_depreciation)
        print('depreciation_value--->', depreciation_value)

        return {
            "year": year,
            "depreciation": round(depreciation_value,2),
        }


    # net_profit_margin
    @http.route("/dashboard/net_profit_margin", type="json", auth="user")
    def get_net_profit_margin(self, **kwargs):
        data = json.loads(request.httprequest.data)
        year = int(data.get("year", date.today().year))
        print('Year received:', year)

        report = request.env['account.report'].sudo().search([
            ('name', '=', 'Executive Summary'),
        ], limit=1)
        if not report:
            raise UserError("No summary report found.")
        print("*****************************************")
        print("Found report:", report)
        lines = report.line_ids
        print('lines--->',lines)
        # lines - --> account.report.line(23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
        #                                 43, 44, 45, 46)
        net_profit_margin_line = None
        net_profit_line = None
        income_line = None
        for line in lines:
            print('line.name===>', line.name)

            if line.name == 'Net profit margin (net profit / income)':
                net_profit_margin_line = line

            if line.name == 'Net Profit':
                net_profit_line = line
                print('net_profit_line>>',net_profit_line)
                # net_profit_line >> account.report.line(33, )

            if line.name == 'Income':
                income_line = line
                print('income_line-->',income_line)
                # income_line --> account.report.line(29, )

        if net_profit_margin_line:
            print('net_profit_margin_line---->',net_profit_margin_line)
            # net_profit_margin_line - ---> account.report.line(40, )

            expression = net_profit_margin_line.expression_ids
            print('expression--->',expression)
            # expression - --> account.report.expression(39, )
            print('formula--->',expression.formula)
            # formula---> NEP.balance / INC.balance * 100



# here i get all 3 lines so using (net profit / income) this formula i want the value of  net_profit_margin_line
