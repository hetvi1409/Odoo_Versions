from odoo.tools.json import json_default
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
from odoo import fields, models, _


class AssetRegisterReports(models.TransientModel):
    _name = 'asset.register.report'
    _description = "Asset Register reports"
    """Assets register reports"""

    to_date = fields.Date(string="To Date", help="To date")
    from_date = fields.Date(string="From Date", help="From date")

    def print_xlsx(self):
        data = {
            'to_date': self.to_date,
            'from_date': self.from_date
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'asset.register.report',
                     'options': json.dumps(data,
                                           default=json_default),
                     'output_format': 'xlsx_reports',
                     'report_name': 'Assets Register Reports',
                     },
            'report_type': 'xlsx_reports',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format({'font_size': 12, 'align': 'center'})
        head = workbook.add_format({'font_size': 18, 'align': 'center', 'color': '#00008B', 'bold': True})
        txt = workbook.add_format({'font_size': 12, })
        sheet.merge_range('C1:H2', _("Asset Analysis of Financial Year"), head)
        sheet.merge_range('BM4:CB4', _('COST'), cell_format)
        sheet.merge_range('CC4:CI4', _('Accumulated Depreciation'), cell_format)
        sheet.merge_range('CJ4:CP4', _('Accumulated Impairment'), cell_format)
        sheet.write('A5', 'Financial Year', cell_format)
        sheet.write('B5', 'Asset Register Item ID', cell_format)
        sheet.write('C5', 'Municipal Asset  Register ID', cell_format)
        sheet.write('D5', 'Parent Asset Register Item ID', cell_format)
        sheet.write('E5', 'Main Asset Description', cell_format)
        sheet.write('F5', 'Main Asset ID', cell_format)
        sheet.write('G5', 'Asset Description', cell_format)
        sheet.write('H5', 'Old Bar Code', cell_format)
        sheet.write('I5', 'Barcode', cell_format)
        sheet.write('J5', 'Image Ref', cell_format)
        sheet.write('K5', 'Asset Type', cell_format)
        sheet.write('L5', 'Asset Category', cell_format)
        sheet.write('M5', 'Asset Sub Category', cell_format)
        sheet.write('N5', 'Asset Class', cell_format)
        sheet.write('O5', 'CIDMS Sub Component Type', cell_format)
        sheet.write('P5', 'CIDMS Component Type', cell_format)
        sheet.write('Q5', 'CIDMS Accounting Group', cell_format)
        sheet.write('R5', 'CIDMS Sub Accounting Group', cell_format)
        sheet.write('S5', 'CIDMS Asset Group Type', cell_format)
        sheet.write('T5', 'CIDMS Asset Type', cell_format)
        sheet.write('U5', 'Cash/Non Cash Generating Unit', cell_format)
        sheet.write('V5', 'Measurement Type', cell_format)
        sheet.write('W5', 'Asset Status', cell_format)
        sheet.write('X5', 'Financial Status', cell_format)
        sheet.write('Y5', 'Take On Date', cell_format)
        sheet.write('Z5', 'Acquisition Date', cell_format)
        sheet.write('AA5', 'Date of Refurbishment/Improvement', cell_format)
        sheet.write('AB5', 'Nature Of Addition', cell_format)
        sheet.write('AC5', 'Infrastructure/Non Infrastructure', cell_format)
        sheet.write('AD5', 'Cost Of Addition', cell_format)
        sheet.write('AE5', 'In Service Date', cell_format)
        sheet.write('AF5', 'Disposal Date', cell_format)
        sheet.write('AG5', 'Reason for Disposal', cell_format)
        sheet.write('AH5', 'Impairment Date', cell_format)
        sheet.write('AI5', 'Date Modified', cell_format)
        sheet.write('AJ5', 'Verified Date', cell_format)
        sheet.write('AK5', 'Verification Done By', cell_format)
        sheet.write('AL5', 'Year Constructed', cell_format)
        sheet.write('AM5', 'Commisioning Date', cell_format)
        sheet.write('AN5', 'Construction Material', cell_format)
        sheet.write('AO5', 'Forecast Replacement Year', cell_format)
        sheet.write('AP5', 'Asset Condition', cell_format)
        sheet.write('AQ5', 'Insurance Cover', cell_format)
        sheet.write('AR5', 'Insurance Policy No', cell_format)
        sheet.write('AS5', 'Warranty', cell_format)
        sheet.write('AT5', 'Current Replacement Cost CRC', cell_format)
        sheet.write('AU5', 'Depreciated Replacement Cost DRC', cell_format)
        sheet.write('AV5', 'Annualised Maintenance % CRC', cell_format)
        sheet.write('AW5', 'Annual Maintenance Budget Forecast Amount', cell_format)
        sheet.write('AX5', 'Depreciation Method', cell_format)
        sheet.write('AY5', 'Useful Life Month Component', cell_format)
        sheet.write('AZ5', 'Useful Life Year Component', cell_format)
        sheet.write('BA5', 'Useful Life Days Component', cell_format)
        sheet.write('BB5', 'Revised Useful Life Year Component', cell_format)
        sheet.write('BC5', 'Revised Useful Life Month Component', cell_format)
        sheet.write('BD5', 'Revised Useful Life Days Component', cell_format)
        sheet.write('BE5', 'Remaining Useful Life Year Component', cell_format)
        sheet.write('BF5', 'Remaining Useful Life Month Component', cell_format)
        sheet.write('BG5', 'Remaining Useful Life days Component', cell_format)
        sheet.write('BH5', 'Remaining Useful Life(RUL) At Take On', cell_format)
        sheet.write('BI5', 'Remaining Useful Life(RUL) At Take On', cell_format)
        sheet.write('BJ5', 'Revised Remaining Useful Life Year Component', cell_format)
        sheet.write('BK5', 'Revised Remaining Useful Life Month Component', cell_format)
        sheet.write('BL5', 'Revised Remaining Useful Life Days Component', cell_format)

        sheet.write('BM5', 'Opening Balance', cell_format)
        sheet.write('BN5', 'Correction of Error', cell_format)
        sheet.write('BO5', 'Restated Opening Balance', cell_format)
        sheet.write('BP5', 'Acquisitions', cell_format)
        sheet.write('BQ5', 'Residual Value', cell_format)
        sheet.write('BR5', 'Revised Residual Value', cell_format)
        sheet.write('BS5', 'Decommisioning, Restoration and Similar Liabilities', cell_format)
        sheet.write('BT5', 'Work In Progress Amount', cell_format)
        sheet.write('BU5', 'Refurbishment / Improvement Amount', cell_format)
        sheet.write('BV5', 'Change in Accounting Estimate', cell_format)
        sheet.write('BW5', 'Revaluation Value', cell_format)
        sheet.write('BX5', 'Fair Value Adjustment', cell_format)
        sheet.write('BY5', 'Transfer Received', cell_format)
        sheet.write('BZ5', 'Transfer Made', cell_format)
        sheet.write('CA5', 'Disposal Value', cell_format)
        sheet.write('CB5', 'Closing Balance', cell_format)

        sheet.write('CC5', 'Opening Balance', cell_format)
        sheet.write('CD5', 'Other Changes', cell_format)
        sheet.write('CE5', 'Restated Opening Balance', cell_format)
        sheet.write('CF5', 'Accumulated Depreciation', cell_format)
        sheet.write('CG5', 'Disposal', cell_format)
        sheet.write('CH5', 'Transfer', cell_format)
        sheet.write('CI5', 'Closing Balance', cell_format)

        sheet.write('CJ5', 'Opening Balance', cell_format)
        sheet.write('CK5', 'Other Changes', cell_format)
        sheet.write('CL5', 'Restated Opening Balance', cell_format)
        sheet.write('CM5', 'Impairment', cell_format)
        sheet.write('CN5', 'Reversal of Impairment Loss', cell_format)
        sheet.write('CO5', 'Transfers', cell_format)
        sheet.write('CP5', 'Accumulated Impairment Closing Balance', cell_format)

        sheet.write('CQ5', 'Carrying Amount', cell_format)
        sheet.write('CR5', 'Comments', cell_format)
        sheet.write('CS5', 'Donor ID /Registration Number / Parastatal Code', cell_format)
        sheet.write('CT5', 'Donor Name / Company Name / Parastatal Name', cell_format)
        sheet.write('CU5', 'Date Donated', cell_format)
        sheet.write('CV5', 'UoM', cell_format)
        sheet.write('CW5', 'Dim1', cell_format)
        sheet.write('CX5', 'Dim2', cell_format)
        sheet.write('CY5', 'Dim3', cell_format)
        sheet.write('CZ5', 'Dimension Quantity', cell_format)
        sheet.write('DA5', 'Quantity', cell_format)
        sheet.write('DB5', 'Diameter', cell_format)
        sheet.write('DC5', 'Capacity', cell_format)
        sheet.write('DD5', 'SG Key', cell_format)
        sheet.write('DE5', 'Deed Number', cell_format)
        sheet.write('DF5', 'Erf/Farm Number', cell_format)
        sheet.write('DG5', 'Erf Size M2', cell_format)
        sheet.write('DH5', 'Portion Number', cell_format)
        sheet.write('DI5', 'Make', cell_format)
        sheet.write('DJ5', 'Model', cell_format)
        sheet.write('DK5', 'Unit Number', cell_format)
        sheet.write('DL5', 'Registration Number', cell_format)
        sheet.write('DM5', 'Serial Number', cell_format)
        sheet.write('DN5', 'Custodian Name', cell_format)
        sheet.write('DO5', 'Custodian ID Number', cell_format)
        sheet.write('DP5', 'Basic Municipal Services', cell_format)
        sheet.write('DQ5', 'Criticality Grade', cell_format)
        sheet.write('DR5', 'Performance Grade', cell_format)
        sheet.write('DS5', 'Utilisation Grade', cell_format)
        sheet.write('DT5', 'Infrastructure Health Grade', cell_format)
        sheet.write("DU5", 'Consequence Of Failure', cell_format)
        sheet.write('DV5', 'Risk', cell_format)
        sheet.write('DW5', 'Asset Ownership', cell_format)
        sheet.write('DX5', 'Department', cell_format)
        sheet.write('DY5', 'Division', cell_format)
        sheet.write('DZ5', 'Town', cell_format)
        sheet.write('EA5', 'Street Address', cell_format)
        sheet.write('EB5', 'Building', cell_format)
        sheet.write('EC5', 'Ward', cell_format)
        sheet.write('ED5', 'Zoning', cell_format)
        sheet.write('EE5', 'Floor Description', cell_format)
        sheet.write('EF5', 'Room Number', cell_format)
        sheet.write('EG5', 'Suburb', cell_format)
        sheet.write('EH5', 'Well Known Text (WKT)', cell_format)
        sheet.write('EI5', 'GIS ID', cell_format)
        sheet.write('EJ5', 'Latitude', cell_format)
        sheet.write('EK5', 'Longitude', cell_format)
        sheet.write('EL5', 'Funding Source Amount', cell_format)
        sheet.write('EM5', 'Funding Source Number', cell_format)
        sheet.write('EN5', 'Funding Type', cell_format)

        sql_query = """SELECT '', a.name, a.state, a.acquisition_date, 
                            a.disposal_date, '', '', 
                            a.write_date, '', '', a.method, 
                            '', a.original_value - (COALESCE(a.salvage_value, 0)) - COALESCE(a.already_depreciated_amount_import, 0) - 
                            (SELECT COALESCE(SUM(depreciation_value), 0) FROM account_move as move where move.asset_id = a.id and move.state='posted'),
                            '', '', 
                            '', '', '', 
                            '', '', '', '',
                            '', '', '', 
                            '', '','','','','','','','','',''
                            FROM account_asset AS a
                            WHERE a.state != 'model'"""

        # LEFT JOIN asset_category AS ac ON ac.id = a.asset_category_id
        # LEFT JOIN asset_type AS at ON at.id = a.asset_type_id
        # LEFT JOIN asset_category as sac ON sac.id = a.asset_sub_category_id

        # Add date conditions
        if data['from_date']:
            sql_query += """ AND a.acquisition_date > '%s'""" % data['from_date']

        if data['to_date']:
            sql_query += """ AND a.acquisition_date < '%s'""" % data['to_date']

        # Correct ORDER BY
        # sql_query += " ORDER BY a.asset_type_id;"

        format = workbook.add_format({'num_format': 'd-m-yyyy'})
        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        row = 5
        col = 0
        for res in result:
            sheet.write(row, col + 1, res[0], txt)
            sheet.write(row, col + 3, res[1], txt)
            sheet.write(row, col + 4, res[2], txt)
            sheet.write(row, col + 5, res[3], txt)
            sheet.write(row, col + 6, res[4], txt)
            sheet.write(row, col + 7, res[5], txt)
            sheet.write(row, col + 8, res[6], txt)
            sheet.write(row, col + 10, res[7], txt)
            sheet.write(row, col + 11, res[8], txt)
            sheet.write(row, col + 12, res[9], txt)
            sheet.write(row, col + 13, res[10], txt)
            sheet.write(row, col + 13, res[10], txt)
            sheet.write(row, col + 22, res[11], txt)
            sheet.write(row, col + 25, res[12], format)
            sheet.write(row, col + 31, res[13], format)
            sheet.write(row, col + 32, res[14], txt)
            sheet.write(row, col + 33, res[15], format)
            sheet.write(row, col + 34, res[16], format)
            sheet.write(row, col + 41, res[17], txt)
            sheet.write(row, col + 43, res[18], txt)
            sheet.write(row, col + 49, res[19], txt)
            sheet.write(row, col + 64, res[20], txt)
            sheet.write(row, col + 68, res[21], txt)
            sheet.write(row, col + 74, res[22], txt)
            sheet.write(row, col + 75, res[23], txt)
            sheet.write(row, col + 83, res[24], txt)
            sheet.write(row, col + 84, res[25], txt)
            sheet.write(row, col + 85, res[26], txt)
            sheet.write(row, col + 90, res[27], txt)
            sheet.write(row, col + 92, res[28], txt)
            sheet.write(row, col + 94, res[29], txt)
            sheet.write(row, col + 104, 1, txt)
            sheet.write(row, col + 108, res[30], txt)
            sheet.write(row, col + 116, res[31], txt)
            sheet.write(row, col + 117, res[32], txt)
            sheet.write(row, col + 129, res[33], txt)
            sheet.write(row, col + 130, res[34], txt)
            sheet.write(row, col + 131, res[35], txt)
            row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
