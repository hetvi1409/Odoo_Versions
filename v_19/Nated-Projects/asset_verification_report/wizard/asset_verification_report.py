import time
import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.tools import float_is_zero
from odoo.tools import date_utils
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter


class AssetVerificationReport(models.TransientModel):
    _name = 'asset.verification.reports'
    _description = "Asset verification reports"
    """Assets verification reports"""

    to_date = fields.Date(string="To Date", help="To date")
    from_date = fields.Date(string="From Date", help="From date")

    def print_xlsx(self):
        datas = {
            'to_date': self.to_date,
            'from_date': self.from_date
        }

        return {
            'type': 'ir.actions.report',
            'data': {
                'model': 'asset.verification.reports',
                'output_format': 'xlsx_asset',
                'options': json.dumps(
                    datas, default=date_utils.json_default),
                'report_name': 'Assets Verification'
            },
            'report_type': 'xlsx_asset',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet("")
        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True,
             'top': True, 'align': 'center', 'bold': True})
        format3 = workbook.add_format(
            {'bottom': True, 'top': True, 'font_size': 12})
        font_size_8 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True,
             'font_size': 8})
        justify = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True,
             'font_size': 12})
        format3.set_align('center')
        font_size_8.set_align('center')
        justify.set_align('justify')
        format1.set_align('center')
        boldc = workbook.add_format({'bold': True, 'align': 'center'})
        boldl = workbook.add_format({
            'font_size': 12,
            'bottom': True,
            'right': True,
            'left': True,
            'top': True,
            'align': 'center',
            'bold': True,
            'bg_color': '#D3D3D3'  # Grey background color
        })
        left = workbook.add_format({'align': 'left'})
        worksheet.merge_range('A2:I2', 'VERIFICATION', boldc)

        row = 6
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 20)
        worksheet.write('A%s' % row, 'Alternative Ref', boldl)
        worksheet.write('B%s' % row, 'Description', boldl)
        worksheet.write('C%s' % row, 'Location', boldl)
        worksheet.write('D%s' % row, 'Verified', boldl)

        sql_query = """
            SELECT a.location_id, a.description, a.alternative_ref,
                   a.is_verified, a.acquisition_date
            FROM account_asset AS a
        """

        # query_params = []
        #
        # if data['from_date']:
        #     sql_query += " AND a.acquisition_date >= %s"
        #     query_params.append(data['from_date'])
        #
        # if data['to_date']:
        #     sql_query += " AND a.acquisition_date <= %s"
        #     query_params.append(data['to_date'])

        self.env.cr.execute(sql_query)
        result = self.env.cr.dictfetchall()

        new_row = 7

        for rec in result:
            worksheet.write('A%s' % new_row, rec['alternative_ref'])
            worksheet.write('B%s' % new_row, rec['description'])
            worksheet.write('C%s' % new_row, rec['location_id'])
            worksheet.write('D%s' % new_row, 'Verified' if rec['is_verified'] else '')
            new_row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
