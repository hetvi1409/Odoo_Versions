from odoo import fields, models
from odoo.exceptions import UserError

class ExecutiveSummaryReportInherit(models.Model):
    _inherit = 'account.report'

    def _report_custom_engine_executive_summary_ndays(self, expressions, options, date_scope,
                                                      current_groupby, next_groupby,
                                                      offset=0, limit=None, warnings=None):
        print("Custom called", self)
        return super()._report_custom_engine_executive_summary_ndays(
            expressions, options, date_scope, current_groupby, next_groupby, offset, limit, warnings
        )






# from odoo import fields, models
# from odoo.exceptions import UserError
#
# class ExecutiveSummaryReport(models.Model):
#     _inherit = 'account.report'
#
#     def custom_report_custom_engine_executive_summary_ndays(self, expressions=None, options=None, date_from=None,
#                                                             date_to=None,
#                                                             current_groupby=None, next_groupby=None, offset=0,
#                                                             limit=None, warnings=None):
#         print('custom_report_custom_engine_executive_summary_ndays----->', self)
#
#         # Ensure that groupby is not used (this method doesn't support it)
#         if current_groupby or next_groupby:
#             raise UserError("NDays expressions of executive summary report don't support the 'group by' feature.")
#
#         # Validate the arguments for options and date range
#         if options is None:
#             raise ValueError("Options must be provided for the report.")
#         if 'date' not in options or 'date_from' not in options['date'] or 'date_to' not in options['date']:
#             raise ValueError("Options must contain both 'date_from' and 'date_to'.")
#
#         # Extract the date range from options (Odoo sends 'date_from' and 'date_to' in options)
#         date_from = fields.Date.from_string(options['date']['date_from'])
#         date_to = fields.Date.from_string(options['date']['date_to'])
#
#         # Get financial data (net profit and income)
#         net_profit = self.env['account.move'].search([
#             ('date', '>=', date_from),
#             ('date', '<=', date_to),
#             ('move_type', '=', 'out_invoice'),  # Assuming you're interested in invoices
#             ('state', '=', 'posted')  # Only consider posted invoices
#         ])
#         total_net_profit = sum(net_profit.mapped('amount_total'))
#
#         income = self.env['account.move'].search([
#             ('date', '>=', date_from),
#             ('date', '<=', date_to),
#             ('move_type', '=', 'out_invoice'),
#             ('state', '=', 'posted')
#         ])
#         total_income = sum(income.mapped('amount_untaxed'))
#
#         # Calculate Net Profit Margin
#         if total_income != 0:
#             net_profit_margin = (total_net_profit / total_income) * 100
#         else:
#             net_profit_margin = 0
#
#         # Calculate the date difference (keeping existing logic)
#         date_diff = date_to - date_from
#
#         # Return both the net profit margin and date difference
#         return {
#             'result': {
#                 'net_profit_margin': net_profit_margin,
#                 'date_diff_days': date_diff.days
#             }
#         }

