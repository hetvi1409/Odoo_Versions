from odoo.tools.json import json_default
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
from odoo import fields, models, _


class AssetVerificationReport(models.TransientModel):
    _name = 'asset.verification.reports'
    _description = "Asset verification reports"
    """Assets verification reports"""

    to_date = fields.Date(string="To Date", help="To date")
    from_date = fields.Date(string="From Date", help="From date")

    def print_xlsx(self):
        data = {
            'to_date': self.to_date,
            'from_date': self.from_date
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'asset.verification.reports',
                     'options': json.dumps(data,
                                           default=json_default),
                     'output_format': 'xlsx_reports',
                     'report_name': 'Assets Verification',
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
        sheet.merge_range('C1:J2', _("Asset Verification Detail"), head)

        sheet.write('A4', 'Asset Register Item ID', cell_format)
        sheet.write('B4', 'Asset Description', cell_format)
        sheet.write('C4', 'Asset Class', cell_format)
        sheet.write('D4', 'Acquisition Date', cell_format)
        sheet.write('E4', 'In Service Date', cell_format)
        sheet.write('F4', 'Barcode', cell_format)
        sheet.write('G4', 'Image Ref', cell_format)
        sheet.write('H4', 'Financial Status', cell_format)
        sheet.write('I4', 'Asset Condition', cell_format)
        sheet.write('J4', 'Useful Life Month Component', cell_format)
        sheet.write('K4', 'Useful Life Year Component', cell_format)
        sheet.write('L4', 'Remaining Useful Life Month', cell_format)
        sheet.write('M4', 'Remaining Useful Life Year', cell_format)
        sheet.write('N4', 'Quantity', cell_format)
        sheet.write('O4', 'SG Key', cell_format)
        sheet.write('P4', 'Deed Number', cell_format)
        sheet.write('Q4', 'Erf / Farm Number', cell_format)
        sheet.write('R4', 'Erf Size M2', cell_format)
        sheet.write('S4', 'Portion Number', cell_format)
        sheet.write('T4', 'Unit Number', cell_format)
        # sheet.write('U4', 'Unit Number', cell_format)
        sheet.write('U4', 'Custodian ID Number / Passport Number', cell_format)
        sheet.write('V4', 'Asset Ownership', cell_format)
        sheet.write('W4', 'Department', cell_format)
        sheet.write('X4', 'Division', cell_format)
        sheet.write('Y4', 'Town', cell_format)
        sheet.write('Z4', 'Street Address', cell_format)
        sheet.write('AA4', 'Building', cell_format)
        sheet.write('AB4', 'Ward', cell_format)
        sheet.write('AC4', 'Zoning', cell_format)
        sheet.write('AD4', 'Floor Description', cell_format)
        sheet.write('AE4', 'Room Number', cell_format)
        sheet.write('AF4', 'Suburb', cell_format)
        sheet.write('AG4', 'Well Know Text (WKT)', cell_format)
        sheet.write('AH4', 'GIS ID', cell_format)
        sheet.write('AI4', 'Latitude', cell_format)
        sheet.write('AJ4', 'Longitude', cell_format)
        sheet.write('AK4', 'Verify Status', cell_format)
        sheet.write('AL4', 'Verification Date', cell_format)
        sheet.write('AM4', 'Verified By', cell_format)

        sql_query = """SELECT '', '', 
                    a.acquisition_date, '', '', 
                   '', '', '', 
                    '', '','',
                    '', '', '', 
                    '', '', '', 
                    ''
                    FROM account_asset AS a
                    WHERE a.state != 'model' 
                     """
        # ORDER BY a.asset_type_id
        # LEFT JOIN res_partner as partner ON partner.id = usr.partner_id
        # LEFT JOIN res_users as usr ON usr.id = a.asset_verification_user_id
        # LEFT JOIN asset_transfer_ownership as ownership ON ownership.id = a.ownership_id
        # LEFT JOIN asset_transfer_department as department ON department.id = a.department_id
        # LEFT JOIN asset_transfer_division as division ON division.id = a.division_id
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
        for res in result:
            sheet.write(row, col, res[0], txt)
            sheet.write(row, col + 1, res[1], txt)
            sheet.write(row, col + 3, res[2], format)
            sheet.write(row, col + 5, res[3], txt)
            sheet.write(row, col + 8, res[4], txt)
            sheet.write(row, col + 9, res[5],)
            sheet.write(row, col + 13, 1, txt)
            sheet.write(row, col + 15, res[6], txt)
            sheet.write(row, col + 21, res[7], txt)
            sheet.write(row, col + 22, res[8], txt)
            sheet.write(row, col + 23, res[9], txt)
            sheet.write(row, col + 24, res[10], txt)
            sheet.write(row, col + 25, res[11], txt)
            sheet.write(row, col + 26, res[12], txt)
            sheet.write(row, col + 30, res[13], txt)
            sheet.write(row, col + 31, res[14], txt)
            sheet.write(row, col + 36, res[15], txt)
            sheet.write(row, col + 37, res[16], format)
            sheet.write(row, col + 38, res[17], format)
            row += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
