from odoo.tools import date_utils
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
from odoo import fields, models, _


class AssetAcquisitionReports(models.TransientModel):
    _name = 'asset.acquisition.reports'
    _description = "Asset acquisition reports"
    """Assets acquisition reports"""

    to_date = fields.Date(string="To Date", help="To date")
    from_date = fields.Date(string="From Date", help="From date")

    def print_sample_report(self):
        data = {
            'to_date': self.to_date,
            'from_date': self.from_date
        }
        return self.env.ref(
            'asset_reports.action_report_asset_acquisition').report_action(None, data=data)

    def print_xlsx(self):
        data = {
            'to_date': self.to_date,
            'from_date': self.from_date
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'asset.acquisition.reports',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx_reports',
                     'report_name': 'Assets Acquisition',
                     },
            'report_type': 'xlsx_reports',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format({'font_size': 12, 'align': 'center'})
        head = workbook.add_format({'font_size': 18, 'align': 'center', 'color': '#00008B', 'bold': True})
        txt = workbook.add_format({'font_size': '9px', })
        sheet.merge_range('C1:H2', _("  Asset Acquisition"), head)

        sheet.write('A4', 'Asset Register ID', cell_format)
        sheet.write('B4', 'Parent Asset Register Item ID', cell_format)
        sheet.write('C4', 'General Ledger Document Number', cell_format)
        sheet.write('D4', 'Acquisition Date', cell_format)
        sheet.write('E4', 'Asset Description', cell_format)
        sheet.write('F4', 'Barcode', cell_format)
        sheet.write('G4', 'Department', cell_format)
        sheet.write('H4', 'Asset Class', cell_format)
        sheet.write('I4', 'Quantity', cell_format)
        sheet.write('J4', 'Location', cell_format)
        sheet.write('K4', 'Purchase Amount', cell_format)

        sql_query = """SELECT a.identification_number,  a.acquisition_date, 
                        a.description, a.asset_barcode, ac.name, at.name, 
                        '', a.original_value, a.identification_number
                        FROM account_asset AS a
                        LEFT JOIN asset_category as ac ON ac.id = a.asset_category_id
                        LEFT JOIN asset_type as at ON at.id = a.asset_type_id
                        LEFT JOIN account_asset as ap ON ap.id = a.account_asset_id
                        WHERE a.state != 'model'"""
        if data['from_date']:
            sql_query = sql_query + """ AND a.acquisition_date > '%s'""" % (
            data['from_date'])
        if data['to_date']:
            sql_query = sql_query + """ AND a.acquisition_date < '%s'""" % (
            data['to_date'])

        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        row = 4
        col = 0
        for res in result:
            sheet.write(row, col, res[0], txt)
            sheet.write(row, col + 1, res[8], txt)
            sheet.write(row, col + 3, res[1], txt)
            sheet.write(row, col + 4, res[2], txt)
            sheet.write(row, col + 5, res[3], txt)
            sheet.write(row, col + 6, res[4], txt)
            sheet.write(row, col + 7, res[5], txt)
            sheet.write(row, col + 8, 1, txt)
            sheet.write(row, col + 9, res[6], txt)
            sheet.write(row, col + 10, res[7], txt)
            row += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
