from odoo import models, fields, api
from datetime import datetime


class TaxCertificateErrorReportWizard(models.TransientModel):
    _name = 'tax.certificate.error.report.wizard'
    _description = 'Tax Certificate Error Report Wizard'

    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)

    def print_pdf(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        return self.env.ref(
            'l10n_hr_za_reports.action_tax_certificate_error_pdf_report'
        ).report_action(self, data=data)


class ReportTaxCertificateError(models.AbstractModel):
    _name = 'report.l10n_hr_za_reports.tax_certificate_report'
    _description = 'Tax Certificate Error QWeb Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['tax.certificate.error.report.wizard'].browse(docids)

        tax_certificate_error_lines = [
            {
                'code': '3100',
                'field': 'Income Tax Reference Number',
                'error_message': 'Warning - The income tax reference number is omitted',
                'employee_name': 'Richardo Beyers',
            },
            {
                'code': '3136',
                'field': 'Business Telephone Number',
                'error_message': 'Rejected - The business telephone number is omitted.',
                'employee_name': 'Zola Dladla',
            },
            {
                'code': '3263',
                'field': 'Standard Industry Classification',
                'error_message': 'Rejected - The SIC code is omitted.',
                'employee_name': 'Amanda Dube',
            },
        ]

        return {
            'doc_ids': docids,
            'doc_model': 'tax.certificate.error.report.wizard',
            'docs': wizard,
            'company_name': self.env.company.name,
            'date_from': data.get('date_from'),
            'date_to': data.get('date_to'),
            'tax_certificate_error_lines': tax_certificate_error_lines,
            'printed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
