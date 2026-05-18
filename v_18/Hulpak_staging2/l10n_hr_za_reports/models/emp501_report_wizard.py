from odoo import models, fields, api
from datetime import datetime
from collections import defaultdict
from dateutil.relativedelta import relativedelta


class EMP501ReportWizard(models.TransientModel):
    _name = 'emp501.report.wizard'
    _description = 'EMP501 Report Wizard'

    date_from = fields.Date(string='Start Date', required=True,default=lambda self: fields.Date.today() + relativedelta(day=1, month=3))
    date_to = fields.Date(string='End Date', required=True,default=lambda self: fields.Date.today() + relativedelta(years=1, day=1, month=2))
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def generate_report(self):
        data = {
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
            }
        }
        return self.env.ref('l10n_hr_za_reports.action_emp501_pdf_report').report_action(self, data=data)

    def print_pdf(self):
        data = {
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
            }
        }
        return self.env.ref('l10n_hr_za_reports.action_emp501_pdf_report').report_action(self, data=data)

class ReportEmp501(models.AbstractModel):
    _name = 'report.l10n_hr_za_reports.emp501_report_template'
    _description = 'Emp201 QWeb Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        months = ['March', 'April', 'May', 'June', 'July', 'August', 'September',
                  'October', 'November', 'December', 'January', 'February']

        year_start = data['form']['date_from']
        year_end = data['form']['date_to']

        slips = self.env['hr.payslip'].search([
            ('date_from', '>=', year_start),
            ('date_to', '<=', year_end),
            ('state', '=', 'done')
        ])

        result = []
        for emp in slips.mapped('employee_id'):
            emp_lines = defaultdict(lambda: {'description': '', 'months': [0.0] * 12, 'total': 0.0})
            emp_slips = slips.filtered(lambda s: s.employee_id == emp)

            for slip in emp_slips:
                month_index = slip.date_from.month - 3 if slip.date_from.month >= 3 else slip.date_from.month + 9
                for line in slip.line_ids.filtered(lambda l: l.category_id.name in ['Basic', 'Taxable Salary', 'Tax','Company Contribution']):
                    emp_lines[line.code]['description'] = line.name
                    emp_lines[line.code]['months'][month_index] += line.total
                    emp_lines[line.code]['total'] += line.total

            result.append({
                'name': emp.name,
                'code': emp.identification_id or '',
                'period': f"{year_start} - {year_end}",
                'lines': list(emp_lines.values())
            })

        return {
            'doc_ids': [],
            'doc_model': 'hr.payslip',
            'data': data,
            'data_lines': result,
            'months': months,
            'data': result,
            'company_name': self.env.company.name,
            'printed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'page_number': 1,
            'page_count': 1,
        }