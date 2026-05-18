from odoo import  models
from odoo.tools import date_utils
import io
import json

try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter

class OutdoorAdvertisement(models.Model):
    """Outdoor advertisement"""
    _inherit = 'outdoor.advertisement'

    def export_outdoor(self):
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
                     'report_name': 'Outdoor Advertisement Register',
                     },
            'report_type': 'xlsx_reports',
        }

    def get_xlsx_report(self, data, response):
        data = tuple(data)
        if len(data) == 1:
            data = str(data).replace(',', '')
        else:
            data = str(data)
        sql_query = """select outdoor.ref, outdoor.address, outdoor.erf, township.name, outdoor.format, region.name,
                    outdoor.ward, zoning.name, owner.name, outdoor.jmc_number
                    from outdoor_advertisement as outdoor
                    LEFT JOIN township_township as township ON township.id = outdoor.township_id
                    LEFT JOIN regions as region ON region.id = outdoor.region_id
                    LEFT JOIN property_zoning as zoning ON zoning.id = outdoor.zoning_id
                    LEFT JOIN res_partner as owner ON owner.id = outdoor.owned_id
                    Where outdoor.id in %s""" % (data)
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
        sheet.write('A1', 'Reference', head)
        sheet.write('B1', 'Site Location/Address', head)
        sheet.write('C1', 'Erf Details', head)
        sheet.write('D1', 'Township', head)
        sheet.write('E1', 'Format', head)
        sheet.write('F1', 'Region', head)
        sheet.write('G1', 'Ward', head)
        sheet.write('H1', 'Zoning', head)
        sheet.write('I1', 'Owned', head)
        sheet.write('J1', 'JMC Number', head)
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
            # sheet.write(row, col + 10, rec[10], txt)
            # sheet.write(row, col + 11, rec[11], txt)
            # sheet.write(row, col + 12, rec[12], txt)
            # sheet.write(row, col + 13, rec[13], txt)
            # sheet.write(row, col + 14, rec[14], txt)
            row += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

