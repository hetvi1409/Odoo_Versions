from odoo import api, fields, models
import datetime

class DailyInvoiceReport(models.AbstractModel):
    """Model of Customer Activity Statement"""

    _name = 'report.mediswitch_integration.receipts_payments_report_document'
    _description = 'Daily Invoice Report'

    @api.model
    def _get_report_values(self, docids, data):
        today_date = datetime.date.today()
        print('\n\n\n\n\n\n\ncall------------report----->', today_date)
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        invoice = self.env['account.move'].search([('invoice_date', '>=', start_date),
                                                      ('invoice_date', '<=', end_date)])
        print('\n\n\n\n\ninvoice', invoice)
        return {
            'doc_ids': docids,
            'doc_model': 'daily.invoice',
            'name': 'abc',
            'data': {'date':today_date},
            'docs': self.env['daily.invoice'].browse(invoice),
            'report_type': data.get('report_type') if data else '',
        }
