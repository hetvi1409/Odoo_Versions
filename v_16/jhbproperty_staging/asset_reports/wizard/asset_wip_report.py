from odoo.tools import date_utils
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
from odoo import fields, models, _


class AssetWipReport(models.TransientModel):
    _name = 'asset.wip.reports'
    _description = "Asset wip reports"
    """Assets wip reports"""

    to_date = fields.Date(string="To Date", help="To date")
    from_date = fields.Date(string="From Date", help="From date")

    def print_xlsx(self):
        data = {
            'to_date': self.to_date,
            'from_date': self.from_date
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'asset.wip.reports',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx_reports',
                     'report_name': 'Assets Wip',
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
        sheet.merge_range('C1:J2', _("Asset Wip Detail"), head)

        sheet.write('A4', 'Contract ID', cell_format)
        sheet.write('B4', 'Financial Year', cell_format)
        sheet.write('C4', 'Processing Month', cell_format)
        sheet.write('D4', 'Planned Start Date', cell_format)
        sheet.write('E4', 'Planned End Date', cell_format)
        sheet.write('F4', 'Contract Registration  Number', cell_format)
        sheet.write('G4', 'Contract Description', cell_format)
        sheet.write('H4', 'Contract Value', cell_format)
        sheet.write('I4', 'Contract Balance', cell_format)
        sheet.write('J4', 'Actual Expenditure', cell_format)
        sheet.write('K4', 'Invoice No', cell_format)
        sheet.write('L4', 'Invoice Amount', cell_format)
        sheet.write('M4', 'Credit Note No', cell_format)
        sheet.write('N4', 'Credit Note Amount', cell_format)
        sheet.write('O4', 'Debit Note No', cell_format)
        sheet.write('P4', 'Debit Note Amount', cell_format)
        sheet.write('Q4', 'Paid Amount', cell_format)
        sheet.write('R4', 'Balance Outstanding for Payment', cell_format)
        sheet.write('S4', 'Payment Certificate Number', cell_format)
        sheet.write('T4', 'Payment Certificate Amount', cell_format)
        sheet.write('U4', 'Project Completed', cell_format)
        sql_query = """SELECT a.identification_number, a.description, 
                    a.acquisition_date, a.asset_barcode, a.condition, 
                    a.useful_life_month, a.deed_number, ownership.name, 
                    department.name, division.name, a.physical_city,
                    a.physical_street, a.building, a.room_number, 
                    a.physical_street2, a.comments, a.date_verification, 
                    partner.name
                    FROM account_asset AS a
                    LEFT JOIN asset_transfer_ownership as ownership ON ownership.id = a.ownership_id
                    LEFT JOIN asset_transfer_department as department ON department.id = a.department_id
                    LEFT JOIN asset_transfer_division as division ON division.id = a.division_id
                    LEFT JOIN res_users as usr ON usr.id = a.asset_verification_user_id
                    LEFT JOIN res_partner as partner ON partner.id = usr.partner_id
                    WHERE a.state != 'model' 
                     ORDER BY a.asset_type_id"""
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
        format = workbook.add_format({'num_format': 'd-m-yyyy'})
        # for res in result:
        #     row += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
