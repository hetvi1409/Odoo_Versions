from odoo.tools import date_utils
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
from odoo import fields, models, _


class AssetInsuranceReports(models.TransientModel):
    _name = 'asset.insurance.reports'
    _description = "Asset insurance reports"
    """Assets insurance reports"""

    to_date = fields.Date(string="To Date", help="To date")
    from_date = fields.Date(string="From Date", help="From date")

    def print_xlsx(self):
        data = {
            'to_date': self.to_date,
            'from_date': self.from_date
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'asset.insurance.reports',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Assets Insurance Reports',
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
        sheet.merge_range('A1:P3', _("Asset Insurance Detail"), head)

        sheet.write('A5', 'Asset Register ID', cell_format)
        sheet.write('B5', 'Description', cell_format)
        sheet.write('C5', 'Asset Class Description', cell_format)
        sheet.write('D5', 'Asset Category Description', cell_format)
        sheet.write('E5', 'Purchase Amount', cell_format)
        sheet.write('F5', 'Book Value', cell_format)
        sheet.write('G5', 'Insured Value', cell_format)
        sheet.write('H5', 'Difference', cell_format)
        sheet.write('I5', 'Policy Number', cell_format)
        sheet.write('J5', 'Premium Monthly', cell_format)
        sheet.write('K5', 'Premium Annual', cell_format)
        sheet.write('L5', 'Insured Period', cell_format)
        sheet.write('M5', 'Claim Date', cell_format)
        sheet.write('N5', 'Ref No', cell_format)
        sheet.write('O5', 'Claimed Amount', cell_format)
        sheet.write('P5', 'Insurance Claim Status', cell_format)
        sql_query = """SELECT a.identification_number, a.description, ac.name,
                                a.original_value, a.book_value, a.insured_value,
                                a.policy_number, a.premium_monthly, a.premium_annually,
                                a.insured_period, a.claim_date
                                FROM account_asset AS a
                                LEFT JOIN asset_category AS ac ON ac.id = a.asset_category_id
                                LEFT JOIN asset_type AS at ON at.id = a.asset_type_id
                                WHERE a.state != 'model'"""

        # Add date conditions to the WHERE clause
        if data['from_date']:
            sql_query += """ AND a.acquisition_date > '%s'""" % data['from_date']

        if data['to_date']:
            sql_query += """ AND a.acquisition_date < '%s'""" % data['to_date']

        # Add the ORDER BY clause after all conditions
        sql_query += " ORDER BY a.insured_value;"
        format4 = workbook.add_format({'num_format': 'd-m-yyyy'})
        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        row = 5
        col = 0
        format4 = workbook.add_format({'num_format': 'd-m-yyyy'})
        for res in result:
            sheet.write(row, col, res[0], txt)
            sheet.write(row, col + 1, res[1], txt)
            sheet.write(row, col + 3, res[2], txt)
            sheet.write(row, col + 4, res[3], txt)
            sheet.write(row, col + 5, res[4], txt)
            sheet.write(row, col + 6, res[5], txt)
            sheet.write(row, col + 8, res[6], txt)
            sheet.write(row, col + 9, res[7], txt)
            sheet.write(row, col + 10, res[8], txt)
            sheet.write(row, col + 11, res[9], txt)
            sheet.write(row, col + 12, res[10], format4)
            row += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
