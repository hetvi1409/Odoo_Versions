from odoo.tools import date_utils
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
from odoo import fields, models,_


class AssetTransferReport(models.TransientModel):
    _name = 'asset.transfer.reports'
    _description = "Asset Transfer reports"
    """Assets transfer reports"""

    to_date = fields.Date(string="To Date", help="To date")
    from_date = fields.Date(string="From Date", help="From date")

    def print_xlsx(self):
        data = {
            'to_date': self.to_date,
            'from_date': self.from_date
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'asset.transfer.reports',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Assets Transfer',
                     },
            'report_type': 'xlsx',
        }
    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        # workbook.autofit()
        cell_format = workbook.add_format({'font_size': 12, 'align': 'center'})
        head = workbook.add_format({'font_size': 18, 'align': 'center', 'color': '#00008B', 'bold': True})
        txt = workbook.add_format({'font_size': '9px', })
        sheet.merge_range('E1:H2', _(" Asset Transfer Detail"), head)

        sheet.write('A4', 'Asset Register Item ID', cell_format)
        sheet.write('B4', 'Asset Description', cell_format)
        sheet.write('C4', 'Barcode', cell_format)
        sheet.write('D4', 'Asset Class', cell_format)
        sheet.write('E4', 'Transfer From Department', cell_format)
        sheet.write('F4', 'Transfer From Division', cell_format)
        sheet.write('G4', 'Transfer From Asset Ownership', cell_format)
        sheet.write('H4', 'Transfer From Custodian Name', cell_format)
        sheet.write('I4', 'Transfer From Custodian ID Number', cell_format)
        sheet.write('J4', 'Transfer To New Department', cell_format)
        sheet.write('K4', 'Transfer To New Division', cell_format)
        sheet.write('L4', 'Transfer To New Asset Ownership', cell_format)
        sheet.write('M4', 'Transfer To New Custodian Name', cell_format)
        sheet.write('N4', 'Transfer To New Custodian ID Number', cell_format)
        sheet.write('O4', 'Town', cell_format)
        sheet.write('P4', 'Suburb', cell_format)
        sheet.write('Q4', 'Street Address', cell_format)
        sheet.write('R4', 'Building', cell_format)
        sheet.write('S4', 'Floor Description', cell_format)
        sheet.write('T4', 'Room Number', cell_format)
        sheet.write('U4', 'Carrying Amount', cell_format)
        sheet.write('V4', 'Transfer Date', cell_format)

        sql_query = """SELECT a.identification_number, a.description, 
                        a.asset_barcode, a.name, atd.name, atdiv.name, ato.name,
                        a.transfer_from_custodian_name,
                        a.transfer_from_custodian_id_number, atnd.name, 
                        atndiv.name, atno.name, 
                        a.transfer_to_new_custodian_name, 
                        a.transfer_to_new_custodian_id_number, a.physical_city, 
                        a.physical_street, a.physical_street2, a.building,
                        a.room_number, a.carrying_amount
                        FROM account_asset AS a
                        LEFT JOIN asset_transfer_department as atd ON atd.id = a.transfer_department_id
                        LEFT JOIN asset_transfer_division as atdiv ON atdiv.id = a.transfer_division_id
                        LEFT JOIN asset_transfer_ownership as ato ON ato.id = a.transfer_ownership_id
                        LEFT JOIN asset_transfer_department as atnd on atnd.id = a.transfer_new_department_id
                        LEFT JOIN asset_transfer_division as atndiv ON atndiv.id = a.transfer_new_division_id
                        LEFT JOIN asset_transfer_ownership as atno ON atno.id = a.transfer_new_ownership_id
                        WHERE a.state != 'model' """
        if data['from_date']:
            sql_query = sql_query + """ AND a.acquisition_date > '%s'""" % (
            data['from_date'])
        if data['to_date']:
            sql_query = sql_query + """ AND a.acquisition_date < '%s'""" % (
            data['to_date'])
        sql_query = sql_query + """ 
                        ORDER BY a.transfer_department_id"""
        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        row = 4
        col = 0
        for res in result:
            sheet.write(row, col, res[0], txt)
            sheet.write(row, col + 1, res[1], txt)
            sheet.write(row, col + 2, res[2], txt)
            sheet.write(row, col + 3, res[3], txt)
            sheet.write(row, col + 4, res[4], txt)
            sheet.write(row, col + 5, res[5], txt)
            sheet.write(row, col + 6, res[6], txt)
            sheet.write(row, col + 7, res[7], txt)
            sheet.write(row, col + 8, res[8], txt)
            sheet.write(row, col + 9, res[9], txt)
            sheet.write(row, col + 10, res[10], txt)
            sheet.write(row, col + 11, res[11], txt)
            sheet.write(row, col + 12, res[12], txt)
            sheet.write(row, col + 13, res[13], txt)
            sheet.write(row, col + 14, res[14], txt)
            sheet.write(row, col + 15, res[15], txt)
            sheet.write(row, col + 16, res[16], txt)
            sheet.write(row, col + 17, res[17], txt)
            # sheet.write(row, col + 18, res[7], txt)
            sheet.write(row, col + 19, res[18], txt)
            sheet.write(row, col + 20, res[19], txt)
            # sheet.write(row, col + 21, res[9], txt)
            # sheet.write(row, col + 21, res[22], txt)
            row += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
