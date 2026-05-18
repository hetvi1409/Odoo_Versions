from odoo import api, fields, models, _
from collections import defaultdict
from datetime import date


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    paye_number = fields.Char(string="PAYE Number")
    uif_number = fields.Char(string="UIF Number")
    income_tax_number = fields.Char(string="Income Tax Number")
    cost_centre = fields.Char(string="Cost Centre")
    company_rule = fields.Char(string="Company Rule")
    employee_code = fields.Char(string="Employee Code", readonly=False, copy=False, index=True, )

    @api.model_create_multi
    def create(self, vals_list):
        """Support bulk create with employee code auto-generation"""
        for vals in vals_list:
            if not vals.get("employee_code"):
                vals["employee_code"] = self.env["ir.sequence"].next_by_code("hr.employee.code") or _("New")
        return super(HrEmployee, self).create(vals_list)

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    leave_balance_line_ids = fields.One2many(
        'report.balance.leave', 'payslip_id', 'Leave Balance Lines',
        compute='_compute_leave_balance_line_ids', readonly=False, copy=False)

    ytd_earnings = fields.Monetary(string="YTD Earnings", compute="_compute_ytd_values", store=True, readonly=False)
    ytd_deductions = fields.Monetary(string="YTD Deductions", compute="_compute_ytd_values", store=True, readonly=False)
    ytd_contributions = fields.Monetary(string="YTD Company Contributions", compute="_compute_ytd_values", store=True,
                                        readonly=False)
    ytd_taxable_income = fields.Monetary(string="YTD Taxable Income", compute="_compute_ytd_values", store=True,
                                         readonly=False)
    ytd_paye = fields.Monetary(string="PAYE (YTD)", compute="_compute_ytd_values", store=True, readonly=False)

    def _compute_leave_balance_line_ids(self):
        for payslip in self:
            payslip.leave_balance_line_ids.unlink()
            query = """
                        SELECT e.id AS emp_id,
                            lt.id AS leave_type_id,SUM(CASE WHEN al.state = 'validate' THEN al.number_of_days ELSE 0 END) AS allocated_days
                            ,SUM(CASE WHEN l.state ='validate' THEN l.number_of_days ELSE 0
                            END) AS taken_days,SUM(CASE WHEN al.state = 'validate' THEN al.number_of_days ELSE 0 END) - SUM(CASE WHEN 
                            l.state ='validate' THEN l.number_of_days ELSE 0 END) AS 
                            balance_days, e.company_id as company_id
                        FROM
                            hr_employee e
                            JOIN hr_leave_allocation al ON al.employee_id = e.id
                            JOIN hr_leave_type lt ON al.holiday_status_id = lt.id
                            LEFT JOIN hr_leave l ON l.employee_id = e.id AND 
                            l.holiday_status_id = lt.id
                        WHERE
                            e.active = True
                        AND
                            e.id = %(emp_id)s   
                        GROUP BY
                            e.id,
                            lt.id    
                    """
            self.env.cr.execute(query, {'emp_id': payslip.employee_id.id})
            query_result = self.env.cr.dictfetchall()
            print("\n\n===query_result===", query_result)

            # query_1 = """
            #             SELECT row_number() over(ORDER BY leaves.employee_id, leaves.leave_type) as id,
            #                 leaves.employee_id,
            #                 leaves.active_employee,
            #                 SUM(leaves.number_of_days) as number_of_days,
            #                 SUM(leaves.number_of_hours) as number_of_hours,
            #                 leaves.department_id,
            #                 leaves.leave_type,
            #                 leaves.holiday_status,
            #                 leaves.state,
            #                 leaves.company_id
            #             FROM (
            #                 /* --- ALLOCATED BALANCES --- */
            #                 SELECT
            #                     allocation.employee_id,
            #                     employee.active AS active_employee,
            #                     CASE
            #                         WHEN allocation.id = min_allocation_id.min_id
            #                             THEN aggregate_allocation.number_of_days - COALESCE(aggregate_leave.number_of_days, 0)
            #                         ELSE 0
            #                     END AS number_of_days,
            #                     CASE
            #                         WHEN allocation.id = min_allocation_id.min_id
            #                             THEN aggregate_allocation.number_of_hours - COALESCE(aggregate_leave.number_of_hours, 0)
            #                         ELSE 0
            #                     END AS number_of_hours,
            #                     allocation.department_id,
            #                     allocation.holiday_status_id AS leave_type,
            #                     allocation.state,
            #                     'balance' AS holiday_status,
            #                     allocation.employee_company_id AS company_id
            #                 FROM hr_leave_allocation AS allocation
            #                 INNER JOIN hr_employee AS employee ON allocation.employee_id = employee.id
            #
            #                 LEFT JOIN (
            #                     SELECT employee_id, holiday_status_id, MIN(id) AS min_id
            #                     FROM hr_leave_allocation
            #                     GROUP BY employee_id, holiday_status_id
            #                 ) min_allocation_id
            #                 ON allocation.employee_id = min_allocation_id.employee_id
            #                    AND allocation.holiday_status_id = min_allocation_id.holiday_status_id
            #
            #                 LEFT JOIN (
            #                     SELECT employee_id, holiday_status_id,
            #                            SUM(CASE WHEN state = 'validate' THEN number_of_days ELSE 0 END) AS number_of_days,
            #                            SUM(CASE WHEN state = 'validate' THEN number_of_hours_display ELSE 0 END) AS number_of_hours
            #                     FROM hr_leave_allocation
            #                     GROUP BY employee_id, holiday_status_id
            #                 ) aggregate_allocation
            #                 ON allocation.employee_id = aggregate_allocation.employee_id
            #                    AND allocation.holiday_status_id = aggregate_allocation.holiday_status_id
            #
            #                 LEFT JOIN (
            #                     SELECT employee_id, holiday_status_id,
            #                            SUM(CASE WHEN state IN ('validate', 'confirm') THEN number_of_days ELSE 0 END) AS number_of_days,
            #                            SUM(CASE WHEN state IN ('validate', 'confirm') THEN number_of_hours ELSE 0 END) AS number_of_hours
            #                     FROM hr_leave
            #                     WHERE date_to <= %(date_to)s
            #                     GROUP BY employee_id, holiday_status_id
            #                 ) aggregate_leave
            #                 ON allocation.employee_id = aggregate_leave.employee_id
            #                    AND allocation.holiday_status_id = aggregate_leave.holiday_status_id
            #
            #                 UNION ALL
            #
            #                 /* --- REQUESTED LEAVES --- */
            #                 SELECT
            #                     request.employee_id,
            #                     employee.active AS active_employee,
            #                     request.number_of_days,
            #                     request.number_of_hours,
            #                     request.department_id,
            #                     request.holiday_status_id AS leave_type,
            #                     request.state,
            #                     CASE
            #                         WHEN request.state IN ('confirm', 'validate') THEN 'taken'
            #                         WHEN request.state = 'confirm' THEN 'planned'
            #                         ELSE 'other'
            #                     END AS holiday_status,
            #                     request.employee_company_id AS company_id
            #                 FROM hr_leave AS request
            #                 INNER JOIN hr_employee AS employee ON request.employee_id = employee.id
            #                 WHERE request.state IN ('confirm', 'validate', 'validate1')
            #                   AND request.date_to <= %(date_to)s
            #             ) leaves
            #             GROUP BY
            #                 leaves.employee_id,
            #                 leaves.active_employee,
            #                 leaves.department_id,
            #                 leaves.leave_type,
            #                 leaves.holiday_status,
            #                 leaves.state,
            #                 leaves.company_id
            #             ORDER BY
            #                 leaves.employee_id,
            #                 leaves.leave_type;
            #             """
            # self.env.cr.execute(query_1, {'date_to': payslip.date_to})
            # query_1_result = self.env.cr.dictfetchall()
            # print("\n\n===query_1_result===", query_1_result)
            # data = defaultdict(lambda: {
            #     'allocated_days': 0.0,
            #     'taken_days': 0.0,
            #     'balance_days': 0.0,
            #     'company_id': None,
            # })
            #
            # for row in query_1_result:
            #     key = (row['employee_id'], row['leave_type'])
            #
            #     if row['holiday_status'] == 'balance':
            #         data[key]['allocated_days'] += row['number_of_days']
            #         data[key]['balance_days'] += row['number_of_days']
            #     elif row['holiday_status'] == 'taken':
            #         data[key]['taken_days'] += row['number_of_days']
            #         data[key]['balance_days'] -= row['number_of_days']
            #
            #     data[key]['company_id'] = row['company_id']
            #
            # # Step 2: Convert into the desired list of dicts
            # final_result = []
            # for (emp_id, leave_type_id), vals in data.items():
            #     final_result.append({
            #         'emp_id': emp_id,
            #         'leave_type_id': leave_type_id,
            #         'allocated_days': round(vals['allocated_days'], 2),
            #         'taken_days': round(vals['taken_days'], 2),
            #         'balance_days': round(vals['balance_days'], 2),
            #         'company_id': vals['company_id'],
            #     })
            # print("\n\n===final_result===", final_result)

            for res in query_result:
                self.env['report.balance.leave'].create({
                    'emp_id': res['emp_id'],
                    'payslip_id': payslip.id,
                    'leave_type_id': res['leave_type_id'],
                    'allocated_days': res['allocated_days'],
                    'taken_days': res['taken_days'],
                    'balance_days': res['balance_days'],
                    'company_id': res['company_id'],
                })

    # @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_ytd_values(self):
        for slip in self:
            if not slip.employee_id or not slip.date_from:
                slip.ytd_earnings = slip.ytd_deductions = slip.ytd_contributions = 0.0
                slip.ytd_taxable_income = slip.ytd_paye = 0.0
                continue

            year_start = date(slip.date_from.year, 1, 1)

            # Get all confirmed payslips for this employee in the same year up to current period
            payslips = self.env['hr.payslip'].sudo().search([
                ('employee_id', '=', slip.employee_id.id),
                ('state', 'in', ['verify', 'done', 'paid']),
                ('date_from', '>=', year_start),
                ('date_to', '<=', slip.date_to),
            ])

            earnings = deductions = contributions = 0.0
            taxable_income = 0.0
            paye_ytd = 0.0

            for ps in payslips:
                for line in ps.line_ids:
                    cat_code = line.category_id.code
                    amount = line.total

                    # 1. Earnings
                    if cat_code in ['BASIC', 'ALW', 'BONUS', 'COM', 'NON_TAX_DEDUCTION']:
                        earnings += amount

                    # 2. Deductions (PAYE, UIF employee, loans, retirement employee)
                    if cat_code in ['DED', 'TAX', 'NON_TAX_INCOME']:
                        deductions += -amount if amount < 0 else amount

                    # 3. Company Contributions (UIF Employer, SDL, Pension/Provident Employer)
                    if cat_code in ['COMP']:
                        contributions += -amount if amount < 0 else amount

                    # 4. SARS PAYE (YTD)
                    if cat_code == 'PAYE':
                        paye_ytd += -amount if amount < 0 else amount

                    if cat_code == 'GROSS':
                        taxable_income += -amount if amount < 0 else amount
            # 4. Taxable Income = YTD Earnings - Tax-deductible Contributions
            # Example: Retirement fund contributions, Medical aid credits
            # tax_deductible = 0.0
            # for ps in payslips:
            #     for line in ps.line_ids.filtered(lambda l: l.code in ['RETIRE', 'MEDICAL']):
            #         tax_deductible += -line.total if line.total < 0 else line.total

            taxable_income = taxable_income

            # Assign values
            slip.ytd_earnings = earnings
            slip.ytd_deductions = deductions
            slip.ytd_contributions = contributions
            slip.ytd_taxable_income = taxable_income
            slip.ytd_paye = paye_ytd


class ReportBalanceLeave(models.Model):
    _name = 'report.balance.leave'
    _description = 'Leave Balance Report'

    emp_id = fields.Many2one('hr.employee', string="Employee", readonly=True,
                             help="Employee name")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip", readonly=True,
                                 help="Payslip name")
    leave_type_id = fields.Many2one('hr.leave.type', string='Leave Type',
                                    readonly=True, help="Leave type of "
                                                        "employee")
    allocated_days = fields.Integer(string='Allocated Balance',
                                    help="Total leave assigned to "
                                         "the employee")
    taken_days = fields.Integer(string='Taken Leaves', help="Taken leaves of "
                                                            "employee")
    balance_days = fields.Integer(string='Remaining Balance',
                                  help="Remaining leaves of employee")
    company_id = fields.Many2one('res.company', string="Company",
                                 help="Company Name")
