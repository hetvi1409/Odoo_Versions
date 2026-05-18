from odoo import  models
from odoo.tools import date_utils
import io
import json

try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter

class Property(models.Model):
    _inherit = 'building'

    def export_property(self):
        """Export the property"""
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        data = self._context.get('active_ids')
        return {
            'type': 'ir.actions.report',
            'data': {'model': self._name,
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx_reports',
                     'report_name': 'Property Asset Register',
                     },
            'report_type': 'xlsx_reports',
        }

    def get_xlsx_report(self, data, response):
        data = tuple(data)

        if len(data) == 1:
            data = str(data).replace(',', '')
        else:
            data = str(data)
        sql_query = """select build.jmc_number, build.name, build.address, build.property_condition,
                    region.name, build.ward, zoning.name, build.latitude, build.longitude, build.sg_id,
                    department.name, amp.name, build.current_use, category.name, build.history_amount
                    from building as build
                    LEFT JOIN regions as region ON region.id = build.region_id
                    LEFT JOIN property_zoning as zoning ON zoning.id = build.zoning_id
                    LEFT JOIN property_department as department ON department.id = build.department_id
                    LEFT JOIN property_category_amp as amp ON amp.id = build.category_amp_id
                    LEFT JOIN property_category as category ON category.id = build.category_id
                    Where build.id in %s""" % (data)
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
        sheet.write('A1', 'Asset Number', head)
        sheet.write('B1', 'Asset Desc', head)
        sheet.write('C1', 'Location', head)
        sheet.write('D1', 'Condition of Property', head)
        sheet.write('E1', 'Region', head)
        sheet.write('F1', 'Ward', head)
        sheet.write('G1', 'Zoning', head)
        sheet.write('H1', 'Coordinates latitude', head)
        sheet.write('I1', 'Coordinates longitude', head)
        sheet.write('J1', 'SG ID', head)
        sheet.write('K1', 'User Department', head)
        sheet.write('L1', 'Category - AMP', head)
        sheet.write('M1', 'Current Use', head)
        sheet.write('N1', 'Main Category', head)
        sheet.write('O1', 'Historical Book Value', head)
        row = 1
        col = 0
        for rec in result:
            sheet.write(row, col, rec[0], txt)
            sheet.write(row, col + 1, rec[1], txt)
            sheet.write(row, col + 2, rec[2], txt)
            sheet.write(row, col + 3, rec[3], txt)
            sheet.write(row, col + 4, rec[4], txt)
            sheet.write(row, col + 5, rec[5], txt)
            sheet.write(row, col + 6, rec[6], txt)
            sheet.write(row, col + 7, rec[7], txt)
            sheet.write(row, col + 8, rec[8], txt)
            sheet.write(row, col + 9, rec[9], txt)
            sheet.write(row, col + 10, rec[10], txt)
            sheet.write(row, col + 11, rec[11], txt)
            sheet.write(row, col + 12, rec[12], txt)
            sheet.write(row, col + 13, rec[13], txt)
            sheet.write(row, col + 14, rec[14], txt)
            row += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
