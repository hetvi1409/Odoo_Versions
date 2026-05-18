from odoo import  models
from odoo.tools import date_utils
import io
import json

try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter

class AccountAsset(models.Model):
    _inherit = 'account.asset'

    def export_property(self):
        """Export Property"""
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        data = self._context.get('active_ids')
        return {
            'type': 'ir.actions.report',
            'data': {'model': self._name,
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx_reports',
                     'report_name': 'Asset Register Export',
                     },
            'report_type': 'xlsx_reports',
        }

    def get_xlsx_report(self, data, response):
        """Print Excel"""
        data = tuple(data)

        if len(data) == 1:
            data = str(data).replace(',', '')
        else:
            data = str(data)
        sql_query = """Select company.name as company_name, category.name as category, 
                    asset.alternative_ref, asset.name, asset.acquisition_date,
                    asset.depreciation_on_days, asset.original_value, 
                    asset.total_depreciation_2022, asset.accumulated_depreciation_2022,
                    asset.closing_book_value_2022, asset.total_depreciation_2022,
                    asset.closing_book_value_2023, asset.total_depreciation_2023, asset.w_and_t_per,
                    asset.current_w_and_t_2022, asset.closing_accum_w_and_t_2022,
                    asset.closing_tax_value_2022, asset.current_w_and_t_2023, 
                    asset.closing_accum_w_and_t_2023, asset.closing_tax_value_2023, location.name
                    From account_asset as asset
                    LEFT JOIN asset_category as category on category.id = asset.asset_category_id
                    LEFT JOIN asset_verification_job_location as location on location.id = asset.job_location_id
                    LEFT JOIN res_company as company on company.id = asset.company_id
                        Where asset.id in %s""" % (data)
        self.env.cr.execute(sql_query, )
        result = self.env.cr.fetchall()
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format(
            {'font_size': '12px', 'align': 'center'})
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '12px'})
        txt = workbook.add_format({'font_size': '10px', 'align': 'center'})
        sheet.write('A1', 'Company', head)
        sheet.write('B1', 'Company Name', head)
        sheet.write('C1', 'Type', head)
        sheet.write('D1', 'Class', head)
        sheet.write('E1', 'Category', head)
        sheet.write('F1', 'Sub Category', head)
        sheet.write('H1', 'Asset', head)
        sheet.write('H1', 'Alternate Ref', head)
        sheet.write('I1', 'Description', head)
        sheet.write('J1', 'Acq. Date', head)
        sheet.write('K1', 'Location', head)
        sheet.write('L1', 'Depreciation Days', head)
        sheet.write('M1', 'Purchase Price', head)
        sheet.write('N1', 'Total Depreciation 2024', head)
        sheet.write('O1', 'Accumulated Depreciation 2024', head)
        sheet.write('P1', 'Closing Book Value 2024', head)
        sheet.write('Q1', '01/07/2024', head)
        sheet.write('R1', '01/08/2024', head)
        sheet.write('S1', '01/09/2024', head)
        sheet.write('T1', '01/10/2024', head)
        sheet.write('U1', '01/11/2024', head)
        sheet.write('V1', '01/12/2024', head)
        sheet.write('W1', '01/01/2025', head)
        sheet.write('X1', '01/02/2025', head)
        sheet.write('Y1', '01/03/2025', head)
        sheet.write('Y1', '01/03/2025', head)
        sheet.write('Z1', '01/04/2025', head)
        sheet.write('AA1', '01/05/2025', head)
        sheet.write('AB1', '01/06/2025', head)
        sheet.write('AC1', 'Total Depreciation 2025', head)

        sheet.write('AD1', 'Accumulated Depreciation 2025', head)
        sheet.write('AE1', 'Closing Book Value 2025', head)
        sheet.write('AF1', 'Residual Value', head)
        sheet.write('AG1', 'W&T %', head)
        sheet.write('AH1', 'Current W&T 2024', head)
        sheet.write('AI1', 'Closing Accum. W&T 2024', head)
        sheet.write('AJ1', 'Closing Tax Value 2024', head)
        sheet.write('AK1', 'Current W&T 2024', head)
        sheet.write('AL1', 'Closing Accum. W&T 2025', head)
        sheet.write('AM1', 'Closing Tax Value 2025', head)
        row = 1
        col = 0
        format2 = workbook.add_format({'num_format': 'dd/mm/yy'})
        percent_fmt = workbook.add_format({'num_format': '0.00%'})

        for rec in result:
            sheet.write(row, col, '200', txt)
            sheet.write(row, col + 1, rec[0], txt)
            sheet.write(row, col + 2, '', txt)
            sheet.write(row, col + 3, rec[1], txt)
            sheet.write(row, col + 4, rec[1], txt)
            sheet.write(row, col + 5, rec[1], txt)
            sheet.write(row, col + 6, '', txt)
            sheet.write(row, col + 7, rec[2], txt)
            sheet.write(row, col + 8, rec[3], txt)
            sheet.write(row, col + 9, rec[4], format2)
            sheet.write(row, col + 10, rec[20], txt)
            sheet.write(row, col + 11, rec[5], txt)
            sheet.write(row, col + 12, rec[6], txt)
            sheet.write(row, col + 13, rec[7], txt)
            sheet.write(row, col + 14, rec[8], txt)
            sheet.write(row, col + 15, rec[9], txt)
            sheet.write(row, col + 16, '', txt)
            sheet.write(row, col + 17, '', txt)
            sheet.write(row, col + 18, '', txt)
            sheet.write(row, col + 19, '', txt)
            sheet.write(row, col + 20, '', txt)
            sheet.write(row, col + 21, '', txt)
            sheet.write(row, col + 22, '', txt)
            sheet.write(row, col + 23, '', txt)
            sheet.write(row, col + 24, '', txt)
            sheet.write(row, col + 25, '', txt)
            sheet.write(row, col + 26, '', txt)
            sheet.write(row, col + 27, '', txt)
            sheet.write(row, col + 28, rec[10], txt)

            sheet.write(row, col + 29, rec[11], txt)
            sheet.write(row, col + 30, rec[12], txt)
            sheet.write(row, col + 31, '1', txt)
            sheet.write(row, col + 32, rec[13], percent_fmt)
            sheet.write(row, col + 33, rec[14], txt)
            sheet.write(row, col + 34, rec[15], txt)
            sheet.write(row, col + 35, rec[16],txt)
            sheet.write(row, col + 36, rec[17],txt)
            sheet.write(row, col + 37, rec[18],txt)
            sheet.write(row, col + 38, rec[19],txt)
            row += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
