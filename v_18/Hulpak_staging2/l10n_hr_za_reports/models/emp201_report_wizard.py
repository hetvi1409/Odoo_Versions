from odoo import models, fields, api
from datetime import datetime

class EMP201ReportWizard(models.TransientModel):
    _name = 'emp201.report.wizard'
    _description = 'EMP201 Report Wizard'

    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def generate_report(self):
        data = {
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
            }
        }
        return self.env.ref('l10n_hr_za_reports.action_emp201_pdf_report').report_action(self, data=data)
    
    def print_pdf(self):
        data = {
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
            }
        }
        return self.env.ref('l10n_hr_za_reports.action_emp201_pdf_report').report_action(self, data=data)
    
    

class ReportEmp201(models.AbstractModel):
    _name = 'report.l10n_hr_za_reports.emp201_report_template'
    _description = 'Emp201 QWeb Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['emp201.report.wizard'].browse(docids)

        employee_lines = [
            {
                'code': 'EL07',
                'name': 'Ibrahim Hlatshwayo',
                'eti_amount': 2220.00,
                'paye': 110.00,
                'sdl': 220.00,
                'uif': 92.00,
                'paye_ytd': 560.00,
                'sdl_ytd': 640.00,
                'uif_ytd': 327.46,
            },
            {
                'code': 'EL23',
                'name': 'Marcia Hlatshwayo',
                'eti_amount': 1500.00,
                'paye': 870.00,
                'sdl': 450.00,
                'uif': 51.46,
                'paye_ytd': 650.00,
                'sdl_ytd': 340.00,
                'uif_ytd': 269.38,
            },
            {
                'code': 'EL25',
                'name': 'Aenna Hlatshwayo',
                'eti_amount': 5400.00,
                'paye': 540.00,
                'sdl': 670.00,
                'uif': 44.46,
                'paye_ytd': 220.00,
                'sdl_ytd': 220.00,
                'uif_ytd': 169.38,
            },
            {
                'code': 'EL27',
                'name': 'Maira Hlatshwayo',
                'eti_amount': 1500.00,
                'paye': 30.00,
                'sdl': 540.00,
                'uif': 51.46,
                'paye_ytd': 40.00,
                'sdl_ytd': 450.00,
                'uif_ytd': 269.38,
            },
            {
                'code': 'EL20',
                'name': 'Naima Hlatshwayo',
                'eti_amount': 1500.00,
                'paye': 220.00,
                'sdl': 110.00,
                'uif': 51.46,
                'paye_ytd': 320.00,
                'sdl_ytd': 324.00,
                'uif_ytd': 169.38,
            },
            # Added dummy employee records (real data can be fetched)
        ]

        # Totals
        total_eti = sum(emp['eti_amount'] for emp in employee_lines)
        total_paye = sum(emp['paye'] for emp in employee_lines)
        total_sdl = sum(emp['sdl'] for emp in employee_lines)
        total_uif = sum(emp['uif'] for emp in employee_lines)
        total_paye_ytd = sum(emp['paye_ytd'] for emp in employee_lines)
        total_sdl_ytd = sum(emp['sdl_ytd'] for emp in employee_lines)
        total_uif_ytd = sum(emp['uif_ytd'] for emp in employee_lines)

        # calculates month name for display in the report, based on date_to
        #selected_month = data['form']['date_to']
        #month_label = datetime.strptime(str(selected_month), "%Y-%m-%d").strftime("%B")

        # generates proper month label for a range (e.g., "January 2025 to June 2025")
        date_from_obj = datetime.strptime(str(data['form']['date_from']), "%Y-%m-%d")
        date_to_obj = datetime.strptime(str(data['form']['date_to']), "%Y-%m-%d")
        month_label = f"{date_from_obj.strftime('%B %Y')} to {date_to_obj.strftime('%B %Y')}"  # Multi-month label

        # report_data = {
        #     'company_name': self.env.company.name,
        #     'date_from': data['form']['date_from'],
        #     'date_to': data['form']['date_to'],
        #     'employee_lines': employee_lines,
        #     'total_eti': total_eti,
        #     'total_paye': total_paye,
        #     'total_sdl': total_sdl,
        #     'total_uif': total_uif,
        #     'total_paye_ytd': total_paye_ytd,
        #     'total_sdl_ytd': total_sdl_ytd,
        #     'total_uif_ytd': total_uif_ytd,
        #     'grand_total': total_paye + total_sdl + total_uif,
        #     'printed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        #     'page_number': 1,
        #     'page_count': 1,
        # }

        # return {
        #     'doc_ids': docids,
        #     'doc_model': 'emp201.report.wizard',
        #     'docs': report_data,
        # }
        return {
            'doc_ids': docids,
            'doc_model': 'emp201.report.wizard',
            'docs': wizard,
            'company_name': self.env.company.name,
            'date_from': data['form']['date_from'],
            'date_to': data['form']['date_to'],
            'month_label': month_label,  # passes month name to report template (Qweb)
            'employee_lines': employee_lines,
            'total_eti': total_eti,
            'total_paye': total_paye,
            'total_sdl': total_sdl,
            'total_uif': total_uif,
            'total_paye_ytd': total_paye_ytd,
            'total_sdl_ytd': total_sdl_ytd,
            'total_uif_ytd': total_uif_ytd,
            'grand_total': total_paye + total_sdl + total_uif,
            'printed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'page_number': 1,
            'page_count': 1,
            'paye_number': self.env.company.paye_number or '', #displaying PAYE value 
            'uif_number': self.env.company.uif_number or '', #displaying UIF value
            'sdl_number': self.env.company.sdl_number or '', #displaying SDL vlaue
        }