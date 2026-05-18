from odoo import api, models


class PayrollReports(models.AbstractModel):
    _name = 'report.l10n_hr_za_reports.report_payroll_all_employees'
    _description = 'Payroll Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('_get_report_values')
        sql_query = """Select employee.id as code, employee.name as name
                        from hr_employee as employee"""
        sql_query = """SELECT 
                emp.id AS employee_id,
                emp.name AS employee_name,
                line.amount AS taxable_salary_amount,
                slip.net_wage
            FROM 
                hr_employee AS emp
            JOIN 
                hr_payslip AS slip ON slip.employee_id = emp.id
            JOIN 
                hr_payslip_line AS line ON line.slip_id = slip.id
            JOIN 
                hr_salary_rule AS rule ON line.salary_rule_id = rule.id
            JOIN 
                hr_salary_rule_category AS cat ON rule.category_id = cat.id
            WHERE 
                cat.name->>'en_US' = 'Taxable Salary';
            """
        sql_query = """
        SELECT 
    emp.id AS employee_id,
    emp.name AS employee_name,
    SUM(DISTINCT slip.net_wage) AS total_net_wage,
    SUM(line.amount) AS total_taxable_salary
FROM 
    hr_employee AS emp
JOIN 
    hr_payslip AS slip ON slip.employee_id = emp.id
JOIN 
    hr_payslip_line AS line ON line.slip_id = slip.id
JOIN 
    hr_salary_rule AS rule ON line.salary_rule_id = rule.id
JOIN 
    hr_salary_rule_category AS cat ON rule.category_id = cat.id
WHERE 
    cat.name->>'en_US' = 'Taxable Salary'
GROUP BY 
    emp.id, emp.name;

        """
        sql_query = """SELECT 
            emp.id AS employee_id,
            emp.name AS employee_name,
        
            -- This Month
            SUM(DISTINCT slip.net_wage) FILTER (
                WHERE date_trunc('month', slip.date_from) = date_trunc('month', CURRENT_DATE)
            ) AS this_month_net_wage,
        
            SUM(line.amount) FILTER (
                WHERE date_trunc('month', slip.date_from) = date_trunc('month', CURRENT_DATE)
            ) AS this_month_taxable_salary,
        
            -- This Year
            SUM(DISTINCT slip.net_wage) FILTER (
                WHERE date_trunc('year', slip.date_from) = date_trunc('year', CURRENT_DATE)
            ) AS this_year_net_wage,
        
            SUM(line.amount) FILTER (
                WHERE date_trunc('year', slip.date_from) = date_trunc('year', CURRENT_DATE)
            ) AS this_year_taxable_salary
        
        FROM 
            hr_employee AS emp
        JOIN 
            hr_payslip AS slip ON slip.employee_id = emp.id
        JOIN 
            hr_payslip_line AS line ON line.slip_id = slip.id
        JOIN 
            hr_salary_rule AS rule ON line.salary_rule_id = rule.id
        JOIN 
            hr_salary_rule_category AS cat ON rule.category_id = cat.id
        WHERE 
            cat.name->>'en_US' = 'Taxable Salary'
        GROUP BY 
            emp.id, emp.name;
        """
        sql_query = """SELECT 
            emp.id AS employee_id,
            emp.name AS employee_name,
        
            -- This Month: Taxable Salary
            SUM(line.amount) FILTER (
                WHERE date_trunc('month', slip.date_from) = date_trunc('month', CURRENT_DATE)
                AND cat.name->>'en_US' = 'Taxable Salary'
            ) AS this_month_taxable_salary,
            
            -- This Month: Net Wage
            SUM(DISTINCT slip.net_wage) FILTER (
                WHERE date_trunc('month', slip.date_from) = date_trunc('month', CURRENT_DATE)
            ) AS this_month_net_wage,
        
            -- This Month: SDL
            SUM(line.amount) FILTER (
                WHERE date_trunc('month', slip.date_from) = date_trunc('month', CURRENT_DATE)
                AND cat.sdl = TRUE
            ) AS this_month_sdl_amount,
        
            -- This Month: UIF
            SUM(line.amount) FILTER (
                WHERE date_trunc('month', slip.date_from) = date_trunc('month', CURRENT_DATE)
                AND cat.uif = TRUE
            ) AS this_month_uif_amount,
        
        
            -- This Year: Net Wage
            SUM(DISTINCT slip.net_wage) FILTER (
                WHERE date_trunc('year', slip.date_from) = date_trunc('year', CURRENT_DATE)
            ) AS this_year_net_wage,
        
            -- This Year: SDL
            SUM(line.amount) FILTER (
                WHERE date_trunc('year', slip.date_from) = date_trunc('year', CURRENT_DATE)
                AND cat.sdl = TRUE
            ) AS this_year_sdl_amount,
            
            -- This Year: UIF
            SUM(line.amount) FILTER (
                WHERE date_trunc('year', slip.date_from) = date_trunc('year', CURRENT_DATE)
                AND cat.uif = TRUE
            ) AS this_year_uif_amount
        
        
        FROM 
            hr_employee AS emp
        JOIN 
            hr_payslip AS slip ON slip.employee_id = emp.id
        JOIN 
            hr_payslip_line AS line ON line.slip_id = slip.id
        JOIN 
            hr_salary_rule AS rule ON line.salary_rule_id = rule.id
        JOIN 
            hr_salary_rule_category AS cat ON rule.category_id = cat.id
        
        GROUP BY 
            emp.id, emp.name;
    """
        # self.env.cr.execute(sql_query)
        # result = self.env.cr.fetchall()
        sql_total_qurey = """SELECT 
    NULL AS employee_id,
    'TOTAL' AS employee_name,


    SUM(line.amount) FILTER (
        WHERE date_trunc('month', slip.date_from) = date_trunc('month', CURRENT_DATE)
        AND cat.name->>'en_US' = 'Taxable Salary'
    ) AS this_month_taxable_salary,
    
    SUM(DISTINCT slip.net_wage) FILTER (
        WHERE date_trunc('month', slip.date_from) = date_trunc('month', CURRENT_DATE)
    ) AS this_month_net_wage,

    SUM(line.amount) FILTER (
        WHERE date_trunc('month', slip.date_from) = date_trunc('month', CURRENT_DATE)
        AND cat.sdl = TRUE
    ) AS this_month_sdl_amount,
    
    SUM(line.amount) FILTER (
        WHERE date_trunc('month', slip.date_from) = date_trunc('month', CURRENT_DATE)
        AND cat.uif = TRUE
    ) AS this_month_uif_amount,


    SUM(DISTINCT slip.net_wage) FILTER (
        WHERE date_trunc('year', slip.date_from) = date_trunc('year', CURRENT_DATE)
    ) AS this_year_net_wage,

    SUM(line.amount) FILTER (
        WHERE date_trunc('year', slip.date_from) = date_trunc('year', CURRENT_DATE)
        AND cat.sdl = TRUE
    ) AS this_year_sdl_amount,
    
    SUM(line.amount) FILTER (
        WHERE date_trunc('year', slip.date_from) = date_trunc('year', CURRENT_DATE)
        AND cat.uif = TRUE
    ) AS this_year_uif_amount


FROM 
    hr_employee AS emp
JOIN hr_payslip AS slip ON slip.employee_id = emp.id
JOIN hr_payslip_line AS line ON line.slip_id = slip.id
JOIN hr_salary_rule AS rule ON line.salary_rule_id = rule.id
JOIN hr_salary_rule_category AS cat ON rule.category_id = cat.id;
"""

        # self.env.cr.execute(sql_total_qurey)
        # result_total = self.env.cr.fetchall()
        # print(result)
        docs = []
        return {
            'doc_ids': docs,
            'doc_model': 'hr.payslip',
            'docs': docs,
            # 'data': result,
            # 'total': result_total
        }
