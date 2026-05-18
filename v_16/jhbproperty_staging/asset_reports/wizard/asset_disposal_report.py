from odoo.tools import date_utils
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
from odoo import fields, models, _


class AssetDisposalReports(models.TransientModel):
    _name = 'asset.disposal.reports'
    _description = "Asset disposal reports"
    """Assets disposal reports"""

    to_date = fields.Date(string="To Date", help="To date")
    from_date = fields.Date(string="From Date", help="From date")

    def print_sample_report(self):
        data = {
            'to_date': self.to_date,
            'from_date': self.from_date
        }
        return self.env.ref(
            'asset_reports.action_report_asset_disposal').report_action(None, data=data)

    def print_xlsx(self):
        data = {
            'to_date': self.to_date,
            'from_date': self.from_date
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'asset.disposal.reports',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx_reports',
                     'report_name': 'Assets Disposal Reports',
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
        sheet.merge_range('A1:P3', _("Asset Disposal"), head)

        sheet.write('A5', 'Asset Register Item ID', cell_format)
        sheet.write('B5', 'Asset Description', cell_format)
        sheet.write('C5', 'Asset Class', cell_format)
        sheet.write('D5', 'Acquisition Date', cell_format)
        sheet.write('E5', 'In Service Date', cell_format)
        sheet.write('F5', 'Disposal Date', cell_format)
        sheet.write('G5', 'Disposal Method', cell_format)
        sheet.write('H5', 'Disposal Reason', cell_format)
        sheet.write('I5', 'Barcode', cell_format)
        sheet.write('J5', 'Financial Status', cell_format)
        sheet.write('K5', 'Asset Condition', cell_format)
        sheet.write('L5', 'Useful Life Year Component', cell_format)
        sheet.write('M5', 'Remaining Useful Life Month Component', cell_format)
        sheet.write('N5', 'Quantity', cell_format)
        sheet.write('O5', 'Department', cell_format)
        sheet.write('P5', 'Division', cell_format)
        sheet.write('Q5', 'SGKey', cell_format)
        sheet.write('R5', 'Deed Number', cell_format)
        sheet.write('S5', 'Erf Number', cell_format)
        sheet.write('T5', 'Erf Size', cell_format)
        sheet.write('U5', 'Portion Number', cell_format)
        sheet.write('V5', 'Unit Number', cell_format)
        sheet.write('W5', 'Custodian Name', cell_format)
        sheet.write('X5', 'Custodian Id Number /  Passport Number', cell_format)
        sheet.write('Y5', 'Asset Ownership', cell_format)
        sheet.write('Z5', 'Town', cell_format)
        sheet.write('AA5', 'Street', cell_format)
        sheet.write('AB5', 'Building', cell_format)
        sheet.write('AC5', 'Ward', cell_format)
        sheet.write('AD5', 'Zoning', cell_format)
        sheet.write('AE5', 'Room Number', cell_format)
        sheet.write('AF5', 'Suburb', cell_format)
        sheet.write('AG5', 'Well Know Text (WKT)', cell_format)
        sheet.write('AH5', 'GIS ID', cell_format)
        sheet.write('AI5', 'Latitude', cell_format)
        sheet.write('AJ5', 'Longitude', cell_format)
        sheet.write('AK5', 'Purchase Amount / Cost', cell_format)
        sheet.write('AL5', 'Accumulated Depreciation Closing Balance', cell_format)
        sheet.write('AM5', 'Accumulated Impairment Closing Balance', cell_format)
        sheet.write('AN5', 'Amount Realised', cell_format)
        sheet.write('AO5', 'Profit/Loss On Disposal', cell_format)
        sql_query = """SELECT a.identification_number, a.name, a.description, a.disposal_reason, a.acquisition_date, p.name, a.state
                FROM account_asset AS a
                JOIN res_users AS u ON u.id = a.create_uid
 JOIN res_partner as p ON p.id = u.partner_id
                WHERE
                a.state != 'model'"""
        if data['from_date']:
            sql_query = sql_query + """ AND a.acquisition_date > '%s'""" % (
                data['from_date'])
        if data['to_date']:
            sql_query = sql_query + """ AND a.acquisition_date < '%s'""" % (
                data['to_date'])
        format = workbook.add_format({'num_format': 'd-m-yyyy'})
        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        row = 5
        col = 0
        format4 = workbook.add_format({'num_format': 'd-m-yyyy'})
        for res in result:
            sheet.write(row, col, res[0], txt)
            sheet.write(row, col + 1, res[1], txt)
            sheet.write(row, col + 3, res[2], format)
            sheet.write(row, col + 5, res[3], format)
            sheet.write(row, col + 6, res[4], txt)
            sheet.write(row, col + 7, res[5], txt)
            sheet.write(row, col + 8, res[6], txt)
            sheet.write(row, col + 10, res[7], txt)
            sheet.write(row, col + 13, 1, txt)
            sheet.write(row, col + 14, res[8], txt)
            sheet.write(row, col + 15, res[9], txt)
            sheet.write(row, col + 17, res[10], txt)
            sheet.write(row, col + 22, res[11], txt)
            sheet.write(row, col + 24, res[12], txt)
            sheet.write(row, col + 25, res[13], txt)
            sheet.write(row, col + 26, res[14], txt)
            sheet.write(row, col + 27, res[15], txt)
            sheet.write(row, col + 30, res[16], txt)
            row += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
