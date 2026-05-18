from odoo import models, fields
import io
import json
from odoo.tools import json_default
import xlsxwriter

class FuelCardTransactionWizard(models.TransientModel):
    _name = 'fuel.card.transaction.wizard'
    _description = 'Card Transaction Report Wizard'

    date_from = fields.Datetime(string="From Date", required=True)
    date_to = fields.Datetime(string="To Date", required=True)

    def fuel_card_report_excel(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'fuel.card.transaction.wizard',
                     'options': json.dumps(data,
                                           default=json_default),
                     'output_format': 'xlsx_reports',
                     'report_name': 'Fuel Card Transaction Report',
                     },
            'report_type': 'xlsx_reports',
        }


    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format(
            {'font_size': '12px', 'align': 'center'})
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px'})
        datetime_format = workbook.add_format(
                    {'num_format': 'yyyy-mm-dd hh:mm:ss'})
        wrap_format = workbook.add_format({'text_wrap': True})
        txt = workbook.add_format({'font_size': '10px', 'align': 'center'})
        transactions = self.env['fuel.card.transaction'].search([('date_issued', '>=', data.get('date_from')),
            ('date_issued', '<=', data.get('date_to')),], order='date_issued')
        sheet.merge_range('B2:I3', 'Fuel Card Transaction Report', head)
        headers = [
                    'Transaction Reference',
                    'Fuel Card',
                    'Driver',
                    'Vehicle',
                    'Date Issued',
                    'Issued By',
                    'Date Returned',
                    'Returned To',
                    'Status',
                    'Notes',
                ]
        for col_num, header in enumerate(headers):
            sheet.write(8, col_num, header, cell_format)
        for row_num, txn in enumerate(transactions, start=9):
            sheet.write(row_num, 0, txn.name or '')
            sheet.write(row_num, 1, txn.card_id.name or '')
            sheet.write(row_num, 2, txn.driver_id.name or '')
            sheet.write(row_num, 3, txn.vehicle_id.name or '')
            if txn.date_issued:
                sheet.write_datetime(row_num, 4, txn.date_issued,
                                         datetime_format)
            else:
                sheet.write(row_num, 4, '')
            sheet.write(row_num, 5, txn.issued_by_id.name or '',txt)
            if txn.date_returned:
                sheet.write_datetime(row_num, 6, txn.date_returned,
                                         datetime_format)
            else:
                sheet.write(row_num, 6, '')
            sheet.write(row_num, 7, txn.returned_to_id.name or '',txt)
            sheet.write(row_num, 8,
                            dict(txn._fields['status'].selection).get(
                                txn.status, '') or '',txt)
            sheet.write(row_num, 9, txn.notes or '', wrap_format)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()