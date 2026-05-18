from odoo.tools import date_utils
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
from odoo import fields, models, _


class AssetUSeFulReports(models.TransientModel):
    _name = 'asset.report'
    _description = "Asset reports"
    """Assets reports"""

    to_date = fields.Date(string="To Date", help="To date")
    from_date = fields.Date(string="From Date", help="From date")

    def print_xlsx(self):
        data = {
            'to_date': self.to_date,
            'from_date': self.from_date
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'asset.report',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Assets Reports',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format({'font_size': 12, 'align': 'center'})
        head = workbook.add_format({'font_size': 18, 'align': 'center', 'color': '#00008B', 'bold': True})
        txt = workbook.add_format({'font_size': '9px', })
        sheet.merge_range('C1:H2', _("Asset Analysis of Financial Year"), head)
        sheet.merge_range('A4:F4', " ",)
        sheet.merge_range('G4:V4', "Cost", cell_format)
        sheet.merge_range('W4:AC4', 'Accumulated Depreciation/Amortisation', cell_format)
        sheet.merge_range('AD4:AK4', 'Accumulated Impairment', cell_format)
        sheet.write('A5', 'Financial Year', cell_format)
        sheet.write('B5', 'Asset Type', cell_format)
        sheet.write('C5', 'Asset Category', cell_format)
        sheet.write('D5', 'Asset Sub Category', cell_format)
        sheet.write('E5', 'Measurement Type', cell_format)
        sheet.write('F5', 'Asset Status', cell_format)
        sheet.write('G5', 'Opening Balance', cell_format)
        sheet.write('H5', 'Aquisitions', cell_format)
        sheet.write('I5', 'Revaluations', cell_format)
        sheet.write('J5', 'Decommission, Restoration and Similar Liabilities', cell_format)
        sheet.write('K5', 'Prior Year Adjustments', cell_format)
        sheet.write('L5', 'Change in Accounting Policy', cell_format)
        sheet.write('M5', 'Disposals', cell_format)
        sheet.write("N5", 'Transfer Received', cell_format)
        sheet.write("O5", 'Transfer Made', cell_format)
        sheet.write("P5", 'Fair Value Adjustments', cell_format)
        sheet.write("Q5", 'Transfer to/from', cell_format)
        sheet.write("R5", 'Other Changes Changes not specifically listed', cell_format)
        sheet.write("S5", 'Sales Biological Assets Classified as held for Sale', cell_format)
        sheet.write("T5", 'Decrease Due To Harvest', cell_format)
        sheet.write("U5", "Entity Combination", cell_format)
        sheet.write("V5", 'Closing Balance', cell_format)
        sheet.write("W5", 'Opening Balance', cell_format)
        sheet.write("X5", 'Other Changes Changes not specifically listed', cell_format)
        sheet.write("Y5", 'Current Depreciation', cell_format)
        sheet.write("Z5", 'Disposals Transfers Out', cell_format)
        sheet.write("AA5", 'Disposals', cell_format)
        sheet.write("AB5", 'Transfers', cell_format)
        sheet.write("AC5", 'Closing Balance', cell_format)
        sheet.write("AD5", 'Opening Balance', cell_format)
        sheet.write("AE5", 'Current Impairment', cell_format)
        sheet.write("AF5", 'Reversal of Impairment', cell_format)
        sheet.write("AG5", 'Disposals/ Transfers Out', cell_format)
        sheet.write("AH5", 'Disposals', cell_format)
        sheet.write("AI5", 'Transfers Made', cell_format)
        sheet.write("AJ5", 'Changes not specifically listed', cell_format)
        sheet.write("AK5", 'Closing Balance', cell_format)
        sheet.write("AL5", "Carrying Value", cell_format)

        sql_query = """SELECT at.name, ac.name, a.state, a.opening_cost,
                    a.acquisition_date, a.disposal, 
                    a.fair_value_less_cost_to_sell, a.closing_cost, 
                    am.depreciation_value, a.transfer, a.carrying_amount,
                    sac.name
                    FROM account_asset AS a
                    LEFT JOIN asset_category AS ac ON ac.id = a.asset_category_id
                    LEFT JOIN asset_type AS at ON at.id = a.asset_type_id
                    LEFT JOIN asset_category as sac ON sac.id = a.asset_sub_category_id
                    LEFT JOIN (
                        SELECT * 
                        FROM account_move 
                        WHERE date <= '2023-08-01' 
                        ORDER BY date DESC
                        Limit 1
                    ) as am ON am.asset_id = a.id
                    WHERE a.state != 'model'"""
        if data['from_date']:
            sql_query = sql_query + """ AND a.acquisition_date > '%s'""" % (
            data['from_date'])
        if data['to_date']:
            sql_query = sql_query + """ AND a.acquisition_date < '%s'""" % (
            data['to_date'])
        sql_query = sql_query + """ 
                    ORDER BY a.asset_type_id"""
        format4 = workbook.add_format({'num_format': 'd-m-yyyy'})
        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        row = 5
        col = 0
        for res in result:
            sheet.write(row, col + 1, res[0], txt)
            sheet.write(row, col + 2, res[1], txt)
            sheet.write(row, col + 3, res[11], txt)
            sheet.write(row, col + 5, res[2], txt)
            sheet.write(row, col + 6, res[3], txt)
            sheet.write(row, col + 7, res[4], format4)
            sheet.write(row, col + 12, res[5], txt)
            sheet.write(row, col + 15, res[6], txt)
            sheet.write(row, col + 21, res[7], txt)
            sheet.write(row, col + 22, res[3], txt)
            sheet.write(row, col + 24, res[8], txt)
            sheet.write(row, col + 26, res[5], txt)
            sheet.write(row, col + 27, res[9], txt)
            sheet.write(row, col + 28, res[7], txt)
            sheet.write(row, col + 29, res[3], txt)
            sheet.write(row, col + 33, res[5], txt)
            sheet.write(row, col + 36, res[7], txt)
            sheet.write(row, col + 37, res[10], txt)

            row += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
