import base64
import io
import json
import xlsxwriter
from odoo.tools import date_utils
from odoo.exceptions import UserError
from odoo import api, fields, models, _
from datetime import datetime, date

class ReportCustomerInvoiceXlsx(models.AbstractModel):
    _name = 'report.budget_managment_update.report_budget_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Report Customer Invoice Xlsx'

    def generate_xlsx_report(self, workbook, data, objs):
        sheet = workbook.add_worksheet('Report')
        head_format = workbook.add_format({
            'align': 'center',
            'bold': True,
            'font_size': '10px'
        })
        sheet.write(0, 2, 'PRODUCT', head_format)
        sheet.write(0, 3, 'PRODUCT DESCRIPTION', head_format)
        sheet.write(0, 7, 'ORDER #', head_format)
        sheet.write(0, 8, 'CUSTOMER', head_format)
        sheet.write(0, 11, 'UNITS ORDERED', head_format)
        sheet.write(0, 12, 'UNITS SHIPPED', head_format)
        sheet.write(0, 15, 'DELIVERY DATE', head_format)
        sheet.write(0, 16, 'NOTES', head_format)
        sheet.write(0, 20, 'INVOICE DATE', head_format)
        sheet.write(0, 21, 'INVOICE #', head_format)


    # def generate_xlsx_report(self, workbook, data, objs):
    #     output = io.BytesIO()
    #     workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    #     worksheet = workbook.add_worksheet("")
    #     format1 = workbook.add_format(
    #         {'font_size': 14, 'bottom': True, 'right': True, 'left': True,
    #          'top': True,
    #          'align': 'center', 'bold': True})
    #     format3 = workbook.add_format(
    #         {'bottom': True, 'top': True, 'font_size': 12})
    #     font_size_8 = workbook.add_format(
    #         {'bottom': True, 'top': True, 'right': True, 'left': True,
    #          'font_size': 8})
    #     justify = workbook.add_format(
    #         {'bottom': True, 'top': True, 'right': True, 'left': True,
    #          'font_size': 12})
    #     format3.set_align('center')
    #     font_size_8.set_align('center')
    #     justify.set_align('justify')
    #     format1.set_align('center')
    #     boldc = workbook.add_format({'bold': True, 'align': 'center'})
    #     boldl = workbook.add_format({
    #         'font_size': 12,
    #         'bottom': True,
    #         'right': True,
    #         'left': True,
    #         'top': True,
    #         'align': 'center',
    #         'bold': True,
    #         'bg_color': '#D3D3D3'  # Grey background color
    #     })
    #     # boldl = workbook.add_format({'bold': True, 'align': 'left'})
    #     left = workbook.add_format({'align': 'left'})
    #     worksheet.merge_range('A2:I2', 'BUDGET REPORT', boldc)
    #
    #     row = 6
    #     worksheet.set_column('A:A', 20)
    #     worksheet.set_column('B:B', 20)
    #     worksheet.set_column('C:C', 30)
    #     worksheet.set_column('D:D', 20)
    #     worksheet.set_column('E:E', 30)
    #     worksheet.set_column('F:F', 15)
    #     worksheet.set_column('G:G', 30)
    #     worksheet.set_column('H:H', 30)
    #     worksheet.write('A%s' % row, 'Core Entity', boldl)
    #     worksheet.write('B%s' % row, 'Dept No', boldl)
    #     worksheet.write('C%s' % row, 'Dept Description', boldl)
    #     worksheet.write('D%s' % row, 'Cost Center No', boldl)
    #     worksheet.write('E%s' % row, 'Cost Center Description', boldl)
    #     worksheet.write('F%s' % row, 'Item No', boldl)
    #     worksheet.write('G%s' % row, 'Type Item Description', boldl)
    #     worksheet.write('H%s' % row, 'mSCOA Rev and Exp Category', boldl)
    #     new_row = 7
    #     for rec in self.browse(data['ids']):
    #         worksheet.write('A%s' % new_row,
    #                         rec.user_id.name if rec.user_id.name else '')
    #         # worksheet.write('B%s' % new_row,
    #         #                 rec.user_id if rec.user_id else '')
    #         # worksheet.write('C%s' % new_row,
    #         #                 rec.user_id if rec.user_id else '')
    #         # worksheet.write('D%s' % new_row, rec.user_id if rec.user_id else '')
    #         # worksheet.write('E%s' % new_row,
    #         #                 rec.user_id if rec.user_id else '')
    #         # worksheet.write('F%s' % new_row, rec.user_id if rec.user_id else '')
    #         # worksheet.write('G%s' % new_row, rec.user_id if rec.user_id else '')
    #         # worksheet.write('H%s' % new_row,
    #         #                 rec.user_id if rec.user_id else '')
    #         new_row += 1
    #     workbook.close()
    #     output.seek(0)
    #     response.stream.write(output.read())
    #     output.close()
