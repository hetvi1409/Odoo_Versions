from odoo import models, fields, api


class DailyInvoice(models.TransientModel):
    _name = 'daily.invoice'

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')

    def export_pdf(self):
        receipts = self.env['account.payment'].search(
            [('payment_date', '>=', self.start_date), ('payment_date', '<=', self.end_date)])
        print(receipts)
        data = {'start_date': self.start_date,
                'end_date': self.end_date}
        return self.env.ref('mediswitch_integration.receipts_payments_report_document_action').report_action(self,
                                                                                                             data=data)
