import datetime
from odoo.tools import date_utils
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
from odoo import fields, models


class ExportAsset(models.TransientModel):
    _name = 'export.asset'
    _description = 'Export Asset'


    asset_ids = fields.Many2many('account.asset', domain="[('state', '!=', 'model')]")

    def print_xlsx(self):
        data = {
            'asset_ids': self.asset_ids.ids,
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'export.asset',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Assets',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format({'font_size': '9px'})
        head = workbook.add_format({'bold': True, 'font_size': '9px'})
        txt = workbook.add_format({'font_size': '9px', })
        sheet.name = 'FAR'
        sheet_infra = workbook.add_worksheet()
        sheet_infra.name = 'FAR INFRASTRUCTURE'
        sheet.write('A1', 'FIXED ASSET REGISTER', head)
        sheet.write('A2', 'ASSET CATEGORY', cell_format)
        sheet.write('B2', 'SUB-CATEGORY', cell_format)
        sheet.write('C2', 'ASSET ID', cell_format)
        sheet.write('D2', 'DESCRIPTION', cell_format)
        sheet.write('E2', 'OFFICE', cell_format)
        sheet.write('F2', 'SERIAL NUMBER', cell_format)
        sheet.write('G2', 'PHYSICAL ADDRESS', cell_format)
        sheet.write('H2', 'SOURCE OF FUNDING', cell_format)
        sheet.write('I2', 'PURCHASE DATE', cell_format)
        sheet.write('J2', 'REVISED/ORIGINAL USEFUL LIFE IN MONTHS', cell_format)
        sheet.write('K2', 'REMAINING USEFUL AS AT 1 JULY 2019 (IN MONTHS)', cell_format)
        sheet.write('L2', 'REMAINING USEFUL AS AT 1 JULY 2020 (IN MONTHS)', cell_format)
        sheet.write('M2', 'ADDITION LIFE GIVEN TO ASSETS IN MONTHS', cell_format)
        sheet.write('N2', 'REMAINING USEFUL AS AT 1 JULY 2020 (IN MONTHS)', cell_format)
        sheet.write('O2', 'REMAINING USEFUL AS AT 1 JULY 2021 (IN MONTHS)', cell_format)
        sheet.write('P2', 'REMAINING USEFUL AS AT 1 JULY 2022 (IN MONTHS)', cell_format)
        sheet.write('Q2', 'OPENING COST', cell_format)
        sheet.write('R2', 'ADDITIONS', cell_format)
        sheet.write('S2', 'ADJUSTMENTS', cell_format)
        sheet.write('T2', 'DISPOSALS', cell_format)
        sheet.write('U2', 'CLOSING COST', cell_format)
        sheet.write('V2', 'ACC DEP OPENING', cell_format)
        sheet.write('W2', 'ADJ ACC DEP', cell_format)
        sheet.write('X2', 'DEPRECIATION JULY 2022', cell_format)
        sheet.write('Y2', 'DEPRECIATION AUG 2022', cell_format)
        sheet.write('Z2', 'DEPRECIATION SEP 2022', cell_format)
        sheet.write('AA2', 'DEPRECIATION OCT 2022', cell_format)
        sheet.write('AB2', 'DEPRECIATION NOV 2022', cell_format)
        sheet.write('AC2', 'DEPRECIATION DEC 2022', cell_format)
        sheet.write('AD2', 'DEPRECIATION JAN 2023', cell_format)
        sheet.write('AE2', 'DEPRECIATION FEB 2023', cell_format)
        sheet.write('AF2', 'DEPRECIATION MAR 2023', cell_format)
        sheet.write('AG2', 'DEPRECIATION APR 2023', cell_format)
        sheet.write('AH2', 'DEPRECIATION MAY 2023', cell_format)
        sheet.write('AI2', 'DEPRECIATION JUN 2023', cell_format)
        sheet.write('AJ2', 'DISPOSALS', cell_format)
        sheet.write('AK2', 'IMPAIRMENTS', cell_format)
        sheet.write('AL2', 'CLOSING ACCUMULATED DEPRECIATION', cell_format)
        sheet.write('AM2', 'OPENING BOOK VALUE 1 July 2022', cell_format)
        sheet.write('AN2', 'CLOSING BOOK VALUE 30 June 2023', cell_format)
        sheet.write('AO2', 'CONDITION', cell_format)
        sheet.write('AP2', 'CUSTODIAN', cell_format)

        sheet_infra.write('A1', 'LOCAL MUNICIPALITY', cell_format)
        sheet_infra.write('B1', 'AREA', cell_format)
        sheet_infra.write('C1', 'ASSET CATEGORY', cell_format)
        sheet_infra.write('D1', 'ASSET TYPE', cell_format)
        sheet_infra.write('E1', 'ASSET DESCRIPTION', cell_format)
        sheet_infra.write('F1', 'COMPONENT', cell_format)
        sheet_infra.write('G1', 'ASSET NO', cell_format)
        sheet_infra.write('H1', 'DATE ACQUIRED', cell_format)
        sheet_infra.write('I1', 'SOURCE OF FUNDING', cell_format)
        sheet_infra.write('J1', 'CONDITIONAL ASSESSMENT', cell_format)
        sheet_infra.write('K1', 'PERSON RESPONSIBLE', cell_format)
        sheet_infra.write('L1', 'Revised Useful Life in Months', cell_format)
        sheet_infra.write('M1', 'Remaining Useful Life 1 July 2017 in months', cell_format)
        sheet_infra.write('N1', 'Remaining Useful Life 1 July 2018 in months', cell_format)
        sheet_infra.write('O1', 'Remaining Useful Life 1 July 2019 in months', cell_format)
        sheet_infra.write('P1', 'Number of months to impair', cell_format)
        sheet_infra.write('Q1', 'Remaining Useful Life 1 July 2020 in months', cell_format)
        sheet_infra.write('R1', 'Remaining Useful Life 1 July 2021 in months', cell_format)
        sheet_infra.write('S1', 'Remaining Useful Life 1 July 2022 in months', cell_format)
        sheet_infra.write('T1', 'OPENING COST', cell_format)
        sheet_infra.write('U1', 'ADDITIONS', cell_format)
        sheet_infra.write('V1', 'REVALUATIONS', cell_format)
        sheet_infra.write('W1', 'DISPOSAL / TRANSFER', cell_format)
        sheet_infra.write('X1', 'CLOSING COST', cell_format)
        sheet_infra.write('Y1', 'ACCUMULATED DEPRECIATION OPENING', cell_format)
        sheet_infra.write('Z1', 'DEPRECIATION for JULY 2022', cell_format)
        sheet_infra.write('AA1', 'DEPRECIATION for AUG 2022', cell_format)
        sheet_infra.write('AB1', 'DEPRECIATION for SEP 2022', cell_format)
        sheet_infra.write('AC1', 'DEPRECIATION for OCT 2022', cell_format)
        sheet_infra.write('AD1', 'DEPRECIATION for NOV 2022', cell_format)
        sheet_infra.write('AE1', 'DEPRECIATION for DEC 2022', cell_format)
        sheet_infra.write('AF1', 'DEPRECIATION for JAN 2023', cell_format)
        sheet_infra.write('AG1', 'DEPRECIATION for FEB 2023', cell_format)
        sheet_infra.write('AH1', 'DEPRECIATION for MAR 2023', cell_format)
        sheet_infra.write('AI1', 'DEPRECIATION for APR 2023', cell_format)
        sheet_infra.write('AJ1', 'DEPRECIATION for MAY 2023', cell_format)
        sheet_infra.write('AK1', 'DEPRECIATION for JUNE 2023', cell_format)
        sheet_infra.write('AL1', 'ADJUSTMENTS', cell_format)
        sheet_infra.write('AM1', 'DISPOSAL / TRANSFER', cell_format)
        sheet_infra.write('AN1', 'IMPAIRMENT', cell_format)
        sheet_infra.write('AO1', 'ACCUMULATED DEPRECIATION CLOSING', cell_format)
        sheet_infra.write('AP1', 'OPENING BOOK VALUE 1 JUL 2022', cell_format)
        sheet_infra.write('AQ1', 'CLOSING BOOK VALUE 30 JUNE 2023', cell_format)
        row = 2
        col = 0
        row_infra = 1
        col_infra = 0
        for rec in data['asset_ids']:
            asset = self.env['account.asset'].browse([rec])
            if asset.type == 'FAR':
                sheet.write(row, col, asset.name, txt)
                sheet.write(row, col + 1, asset.asset_category_id.name)
                sheet.write(row, col + 2, asset.identification_number)
                sheet.write(row, col + 3, asset.description)
                sheet.write(row, col + 4, asset.office)
                sheet.write(row, col + 5, asset.serial_number)
                sheet.write(row, col + 6, asset.physical_street)
                sheet.write(row, col + 7, asset.funding_source)
                sheet.write(row, col + 8, str(asset.acquisition_date))
                sheet.write(row, col + 9, asset.original_useful_life)
                useful_life_ = []
                for useful_life in asset.useful_life_ids:
                    useful_life_.append(useful_life.amount)
                sheet.write(row, col + 10, useful_life_[0])
                sheet.write(row, col + 11, useful_life_[1])
                sheet.write(row, col + 13, useful_life_[2])
                sheet.write(row, col + 14, useful_life_[3])
                sheet.write(row, col + 15, useful_life_[4])
                sheet.write(row, col + 16, asset.opening_cost)
                sheet.write(row, col + 17, asset.addition)
                sheet.write(row, col + 18, asset.adjustment)
                sheet.write(row, col + 19, asset.disposal)
                sheet.write(row, col + 20, asset.closing_cost)
                sheet.write(row, col + 21, asset.acc_dep_opening)
                for depreciation in asset.depreciation_move_ids:
                    if depreciation.date == datetime.date(2022, 7, 1):
                        sheet.write(row, col + 23, depreciation.depreciation_value)
                    if depreciation.date == datetime.date(2022, 8, 1):
                        sheet.write(row, col + 24, depreciation.depreciation_value)
                    if depreciation.date == datetime.date(2022, 9, 1):
                        sheet.write(row, col + 25, depreciation.depreciation_value)
                    if depreciation.date == datetime.date(2022, 10, 1):
                        sheet.write(row, col + 26, depreciation.depreciation_value)
                    if depreciation.date == datetime.date(2022, 11, 1):
                        sheet.write(row, col + 27, depreciation.depreciation_value)
                    if depreciation.date == datetime.date(2022, 12, 1):
                        sheet.write(row, col + 28, depreciation.depreciation_value)
                    if depreciation.date == datetime.date(2022, 12, 1):
                        sheet.write(row, col + 29, depreciation.depreciation_value)
                    if depreciation.date == datetime.date(2023, 1, 1):
                        sheet.write(row, col + 30, depreciation.depreciation_value)
                    if depreciation.date == datetime.date(2023, 2, 1):
                        sheet.write(row, col + 31, depreciation.depreciation_value)
                    if depreciation.date == datetime.date(2023, 3, 1):
                        sheet.write(row, col + 32, depreciation.depreciation_value)
                    if depreciation.date == datetime.date(2023, 4, 1):
                        sheet.write(row, col + 33, depreciation.depreciation_value)
                sheet.write(row, col + 36, asset.impairment_losses)
                sheet.write(row, col + 37, asset.closing_accumulated_depreciation)
                sheet.write(row, col + 38, asset.opening_book_value_july_22)
                sheet.write(row, col + 39, asset.closing_book_value_july_22)
                sheet.write(row, col + 40, asset.condition)
                row += 1
            if asset.type == 'INFRASTRUCTURE':
                sheet_infra.write(row_infra, col_infra, asset.physical_street)
                sheet_infra.write(row_infra, col_infra + 1, asset.physical_street2)
                sheet_infra.write(row_infra, col_infra + 2, asset.asset_category_id.name)
                sheet_infra.write(row_infra, col_infra + 3, asset.name)
                sheet_infra.write(row_infra, col_infra + 4, asset.description)
                sheet_infra.write(row_infra, col_infra + 5, asset.component)
                sheet_infra.write(row_infra, col_infra + 6, asset.identification_number)
                sheet_infra.write(row_infra, col_infra + 7, str(asset.acquisition_date))
                sheet_infra.write(row_infra, col_infra + 8, asset.funding_source)
                sheet_infra.write(row_infra, col_infra + 9, asset.conditional_assessment)
                sheet_infra.write(row_infra, col_infra + 10, asset.custodian)
                sheet_infra.write(row_infra, col_infra + 11, asset.original_useful_life)
                useful_life_ = []
                for useful_life in asset.useful_life_ids:
                    useful_life_.append(useful_life.amount)
                sheet_infra.write(row_infra, col_infra + 12, useful_life_[0])
                sheet_infra.write(row_infra, col_infra + 13, useful_life_[1])
                sheet_infra.write(row_infra, col_infra + 14, useful_life_[2])
                sheet_infra.write(row_infra, col_infra + 16, useful_life_[3])
                sheet_infra.write(row_infra, col_infra + 17, useful_life_[4])
                sheet_infra.write(row_infra, col_infra + 18, useful_life_[5])
                sheet_infra.write(row_infra, col_infra + 15, asset.impair)
                sheet_infra.write(row_infra, col_infra + 19, asset.opening_cost)
                sheet_infra.write(row_infra, col_infra + 20, asset.addition)
                sheet_infra.write(row_infra, col_infra + 21, asset.re_valued_value)
                sheet_infra.write(row_infra, col_infra + 22, asset.disposal)
                sheet_infra.write(row_infra, col_infra + 23, asset.closing_cost)
                sheet_infra.write(row_infra, col_infra + 24, asset.acc_dep_opening)

                for depreciation in asset.depreciation_move_ids:
                    if depreciation.date == datetime.date(2022, 7, 1):
                        sheet_infra.write(row_infra, col_infra + 25, depreciation.depreciation_value)
                    if depreciation.date == datetime.date(2022, 8, 1):
                        sheet_infra.write(row_infra, col_infra + 26, depreciation.depreciation_value)
                    if depreciation.date == datetime.date(2022, 9, 1):
                        sheet_infra.write(row_infra, col_infra + 27, depreciation.depreciation_value)
                    if depreciation.date == datetime.date(2022, 10, 1):
                        sheet_infra.write(row_infra, col_infra + 28, depreciation.depreciation_value)
                    if depreciation.date == datetime.date(2022, 11, 1):
                        sheet_infra.write(row_infra, col_infra + 29, depreciation.depreciation_value)
                    if depreciation.date == datetime.date(2022, 12, 1):
                        sheet_infra.write(row_infra, col_infra + 30, depreciation.depreciation_value)
                    if depreciation.date == datetime.date(2023, 1, 1):
                        sheet_infra.write(row_infra, col_infra + 31, depreciation.depreciation_value)
                    if depreciation.date == datetime.date(2023, 2, 1):
                        sheet_infra.write(row_infra, col_infra + 32, depreciation.depreciation_value)
                    if depreciation.date == datetime.date(2022, 3, 1):
                        sheet_infra.write(row_infra, col_infra + 33, depreciation.depreciation_value)
                sheet_infra.write(row_infra, col_infra + 37, asset.adjustment)
                sheet_infra.write(row_infra, col_infra + 39, asset.impairment_losses)
                sheet_infra.write(row_infra, col_infra + 40, asset.closing_accumulated_depreciation)
                sheet_infra.write(row_infra, col_infra + 41, asset.opening_book_value_july_22)
                sheet_infra.write(row_infra, col_infra + 42, asset.closing_book_value_july_22)
                row_infra += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()