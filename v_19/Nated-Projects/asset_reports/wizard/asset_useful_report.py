from odoo.tools import date_utils
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
from odoo import fields, models, _


class AssetUSeFulReports(models.TransientModel):
    _name = 'asset.useful.reports'
    _description = "Asset Useful life reports"
    """Assets Useful reports"""

    to_date = fields.Date(string="To Date", help="To date")
    from_date = fields.Date(string="From Date", help="From date")

    def print_xlsx(self):
        data = {
            'to_date': self.to_date,
            'from_date': self.from_date
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'asset.useful.reports',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Assets Useful Life',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format({'font_size': 12, 'align': 'center'})
        head = workbook.add_format({'font_size': 18, 'align': 'center', 'color': '#00008B', 'bold': True})
        txt = workbook.add_format({'font_size': '9px', })
        sheet.merge_range('C1:H2', _("Asset Useful life"), head)

        sheet.write('A5', 'Asset Register ID', cell_format)
        sheet.write('B5', 'Description', cell_format)
        sheet.write('C5', 'Asset Class Description', cell_format)
        sheet.write('D5', 'Asset Category Description', cell_format)
        sheet.write('E5', 'Purchase Amount', cell_format)
        sheet.write('F5', 'Useful Life Month Component', cell_format)
        sheet.write('G5', 'Barcode', cell_format)
        sheet.write('H5', 'Remaining Useful Life', cell_format)
        sheet.write('I5', 'Room Desc', cell_format)
        sheet.write('J5', 'Department Desc', cell_format)
        sheet.write('K5', 'Accumulated Depreciation Opening Balance', cell_format)
        sheet.write('L5', 'Replacement Value', cell_format)
        sheet.write('M5', 'Revaluation Amount', cell_format)
        sheet.write("N5", 'Impairment Amount Current Year', cell_format)
        sheet.write("O5", 'Market Value', cell_format)
        sheet.write("P5", 'Ready For Use', cell_format)
        sheet.write("Q5", 'Asset Type Desc', cell_format)
        sheet.write("R5", 'Serial Number', cell_format)
        sheet.write("S5", 'Asset Sub Category Description', cell_format)
        sheet.write("T5", 'Residual Value', cell_format)
        sheet.write("U5", "Date Of Disposal", cell_format)
        sheet.write("V5", 'Method Of Disposal', cell_format)
        sheet.write("W5", 'Disposal Amount Cost', cell_format)
        sheet.write("X5", 'Condition Rating Desc', cell_format)
        sheet.write("Y5", 'Municipal Classification', cell_format)
        sheet.write("Z5", 'Acquisition Date', cell_format)

        sql_query = """SELECT a.identification_number, a.description, ac.name,
                        a.original_value, a.component, a.asset_barcode,
                        aul.remaining_useful_life, at.name, a.acc_dep_opening,
                        a.re_valued_value, a.impairment, at.name,
                        a.serial_number, a.id, a.disposal_date, 
                        a.direct_disposal_amount, a.acquisition_date, 
                        ac.description, a.room_number, a.replacement_value, 
                        a.market_value, a.ready_for_use, 
                        a.sub_category_description, a.method_disposal,
                        a.direct_disposal_amount, a.condition_asset
                        FROM account_asset AS a
                        LEFT JOIN asset_category AS ac ON ac.id = a.asset_category_id
                        LEFT JOIN asset_type AS at ON at.id = a.asset_type_id
                        LEFT JOIN (
                            SELECT *, ROW_NUMBER() OVER (PARTITION BY asset_id ORDER BY id DESC) AS rn
                                   FROM
                            asset_useful_life
                            WHERE
                            date <= '%s') AS aul ON aul.asset_id = a.id AND aul.rn = 1
                            WHERE
                            a.state != 'model'""" % fields.Date.today()
        if data['from_date']:
            sql_query = sql_query + """ AND a.acquisition_date > '%s'""" % (
            data['from_date'])
        if data['to_date']:
            sql_query = sql_query + """ AND a.acquisition_date < '%s'""" % (
            data['to_date'])
        format4 = workbook.add_format({'num_format': 'd-m-yyyy'})
        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        row = 5
        col = 0
        for res in result:
            sheet.write(row, col, res[0], txt)
            sheet.write(row, col + 1, res[1], txt)
            sheet.write(row, col + 2, res[2], txt)
            sheet.write(row, col + 3, res[17], txt)
            sheet.write(row, col + 4, res[3], txt)
            sheet.write(row, col + 5, res[4], txt)
            sheet.write(row, col + 6, res[5], txt)
            sheet.write(row, col + 7, res[6], txt)
            sheet.write(row, col + 8, res[18], txt)
            sheet.write(row, col + 9, res[7], txt)
            sheet.write(row, col + 10, res[8], txt)
            sheet.write(row, col + 11, res[19], txt)
            sheet.write(row, col + 12, res[9], txt)
            sheet.write(row, col + 13, res[10], txt)
            sheet.write(row, col + 14, res[20], txt)
            sheet.write(row, col + 15, res[21], txt)
            sheet.write(row, col + 16, res[11], txt)
            sheet.write(row, col + 17, res[12], txt)
            sheet.write(row, col + 18, res[22], txt)
            sheet.write(row, col + 19, self.env['account.asset'].browse(int(res[13])).value_residual, txt)
            sheet.write(row, col + 20, res[14], txt)
            sheet.write(row, col + 21, res[23], txt)
            sheet.write(row, col + 22, res[15], txt)
            sheet.write(row, col + 23, res[24], txt)
            sheet.write(row, col + 24, res[25], txt)
            sheet.write(row, col + 25, res[16], format4)

            row += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
