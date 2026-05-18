from odoo.tools.json import json_default
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
from odoo import fields, models, _


class AssetDepreciationReports(models.TransientModel):
    _name = 'asset.depreciation.reports'
    _description = "Asset Depreciation reports"
    """Assets Depreciation reports"""

    to_date = fields.Date(string="To Date", help="To date")
    from_date = fields.Date(string="From Date", help="From date")

    def print_sample_report(self):
        data = {
            'to_date': self.to_date,
            'from_date': self.from_date
        }
        return self.env.ref(
            'asset_reports.action_report_asset_depreciation').report_action(None, data=data)

    def print_sample_depreciated_report(self):
        data = {
            'to_date': self.to_date,
            'from_date': self.from_date
        }
        return self.env.ref(
            'asset_reports.action_report_asset_fully_depreciation').report_action(
            None, data=data)

    def print_xlsx(self):
        data = {
            'to_date': self.to_date,
            'from_date': self.from_date
        }
        return {
            'type': 'ir.actions.report',
            'data': {
                'model': 'asset.depreciation.reports',
                'options': json.dumps(data, default=json_default),
                'output_format': 'xlsx_reports',
                'report_name': 'ASSET DEPRECIATION RUN DETAILS',
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
        sheet.merge_range('C1:K2', _("ASSET DEPRECIATION RUN DETAILS"), head)

        sheet.write('A4', 'Asset Register Item ID', cell_format)
        sheet.write('B4', 'Asset Description', cell_format)
        sheet.write('C4', 'Asset Type', cell_format)
        sheet.write('D4', 'Asset Category', cell_format)
        sheet.write('E4', 'Asset Sub-Category', cell_format)
        sheet.write('F4', 'Asset Class', cell_format)
        # sheet.write('G4', 'Measurement Type', cell_format)
        sheet.write('G4', 'Asset Status', cell_format)
        # sheet.write('I4', 'Financial Status', cell_format)
        sheet.write('H4', 'Asset Condition', cell_format)
        sheet.write('I4', 'Depreciation Method', cell_format)
        sheet.write('J4', 'General Ledger Document Number', cell_format)
        # sheet.write('M4', 'In Service Date', cell_format)
        # sheet.write('N4', 'Scheduled Date', cell_format)
        # sheet.write('O4', 'Transaction Date', cell_format)
        sheet.write('K4', 'Period', cell_format)
        sheet.write('L4', 'Useful Life Month', cell_format)
        sheet.write('M4', 'Useful Life Day', cell_format)
        sheet.write('N4', 'Remaining Useful Life Month', cell_format)
        sheet.write('O4', 'Remaining Useful Life Days', cell_format)
        sheet.write('P4', 'Days From Last Run', cell_format)
        sheet.write('Q4', 'Purchase Amount', cell_format)
        sheet.write('R4', 'Accumulated Depreciation Opening Balance', cell_format)
        sheet.write('S4', 'Accumulated Depreciation Closing Balance', cell_format)
        sheet.write('T4', 'Accumulated Depreciation Current Year', cell_format)
        sheet.write('U4', 'Depreciation Value for this Period', cell_format)
        sheet.write('V4', 'Carrying Value', cell_format)
        # sheet.write('AB4', 'Planning Project (Debit)', cell_format)
        # sheet.write('AC4', 'SCOA Item Code (Debit)', cell_format)
        # sheet.write('AD4', 'Planning Project (Credit)', cell_format)
        # sheet.write('AE4', 'SCOA Item Code (Credit)', cell_format)
        # sheet.write('AF4', 'Approve Status', cell_format)

        sql_query = """SELECT '',  a.name, a.state, '',
                                a.method, a.method_period,
                                a.original_value, move.id, m_move.id                                
                                FROM account_asset AS a
                                LEFT JOIN (
                                    SELECT asset_id, MIN(id) AS min_id
                                    FROM account_move
                                    GROUP BY asset_id
                                ) AS min_move ON min_move.asset_id = a.id
                                LEFT JOIN account_move AS move ON move.id = min_move.min_id
                                LEFT JOIN (
                                    SELECT asset_id, MAX(id) AS max_id
                                    FROM account_move
                                    GROUP BY asset_id
                                ) AS max_move ON max_move.asset_id = a.id
                                LEFT JOIN account_move AS m_move ON m_move.id = max_move.max_id
                                WHERE a.id = '3453'"""
        # a.description, at.name,ac.name, sac.name,a.useful_life_month,a.days_from_last_run,
        #                                a.carrying_amount, a.useful_life_day, a.remaining_useful_life_month,
        #                                 a.remaining_useful_life_day
        # LEFT JOIN asset_category as ac ON ac.id = a.asset_category_id
        # LEFT JOIN asset_type as at ON at.id = a.asset_type_id
        # LEFT JOIN asset_category as sac ON sac.id = a.asset_sub_category_id

        # Adding date conditions into the WHERE clause
        if data['from_date']:
            sql_query += """ AND a.acquisition_date > '%s'""" % data['from_date']

        if data['to_date']:
            sql_query += """ AND a.acquisition_date < '%s'""" % data['to_date']

        # Ensure that ORDER BY comes after all filtering conditions
        # sql_query += " ORDER BY a.asset_type_id;"

        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        row = 4
        col = 0
        for res in result:
            depreciation = self.env['account.move'].browse(int(res[16])).asset_depreciated_value if res[16] else ""
            sheet.write(row, col, res[3], txt)
            sheet.write(row, col + 1, res[1], txt)
            sheet.write(row, col + 2, res[2], txt)
            sheet.write(row, col + 3, res[3], txt)
            sheet.write(row, col + 4, res[4], txt)
            sheet.write(row, col + 5, res[5], txt)
            sheet.write(row, col + 6, res[6], txt)
            sheet.write(row, col + 7, res[7], txt)
            sheet.write(row, col + 8, res[8], txt)
            sheet.write(row, col + 10, 'Months' if res[9] == '1' else 'Year', txt)
            sheet.write(row, col + 11, res[10], txt)
            sheet.write(row, col + 12, res[11], txt)
            sheet.write(row, col + 13, res[12], txt)
            sheet.write(row, col + 14, res[13], txt)
            sheet.write(row, col + 15, res[14], txt)
            sheet.write(row, col + 16, res[15], txt)
            sheet.write(row, col + 17, depreciation, txt)
            sheet.write(row, col + 18,
                        self.env['account.move'].browse(int(res[17])).asset_depreciated_value if res[17] else "", txt)
            sheet.write(row, col + 19, res[18], txt)
            sheet.write(row, col + 20, depreciation, txt)
            sheet.write(row, col + 21, res[19], txt)
            row += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
