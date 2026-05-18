from datetime import datetime, timedelta
from datetime import datetime
from dateutil.parser import parse
import xlrd
import tempfile
import binascii
from odoo import fields, models
from odoo.exceptions import UserError


class AssetImport(models.TransientModel):
    _name = 'asset.import'
    _description = 'Asset import'

    file = fields.Binary(string='File', required=True)

    def action_import_asset(self):
        """Import asset"""
        try:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            book = xlrd.open_workbook(fp.name)
        except FileNotFoundError:
            raise UserError(
                'No such file or directory found. \n%s.' % self.file_name)
        except xlrd.biffh.XLRDError:
            raise UserError('Only excel files are supported.')
        for sheet in book.sheets():
            try:
                for row in range(sheet.nrows):
                    number = 1
                    if row >= 2:
                        row_values = sheet.row_values(row)
                        if row_values[7]:
                            # if row_values[4] == 'OE':
                            #     print(row_values[7], 'OEEEEE')
                            account = self.env['account.asset'].search([(
                                'alternative_ref', '=', row_values[7])])
                            number = number + 1
                            if not account:
                                if row_values[4] == 'OE':
                                    print(row_values[7], 'OEEEEE')
                                self._create_asset(row_values)
            except IndexError:
                pass

    def action_import_asset_model(self):
        """Importing asset model into odoo"""
        try:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            book = xlrd.open_workbook(fp.name)
        except FileNotFoundError:
            raise UserError(
                'No such file or directory found. \n%s.' % self.file_name)
        except xlrd.biffh.XLRDError:
            raise UserError('Only excel files are supported.')
        for sheet in book.sheets():
            try:
                for row in range(sheet.nrows):
                    if row >= 2:
                        row_values = sheet.row_values(row)
                        self._create_asset_model(row_values)
            except IndexError:
                pass

    def _create_asset_model(self, row_values):
        """Creating Asset Model"""
        asset_model = self.env['account.asset'].sudo().search(
            [('state', '=', 'model'), ('name', '=', row_values[8])], limit=1)
        category = ""
        account_asset_id = ""
        # if row_values[4] == 'BD':
        #     category = 'Building'
        #     account_asset_id = 3466
        #     account_depreciation_id = 3466
        #     account_depreciation_expense_id = 2068
        # if row_values[4] == 'CH':
        #     category = 'Computer Hardware'
        #     account_asset_id = 3458
        #     account_depreciation_id = 3458
        #     account_depreciation_expense_id = 2058
        # if row_values[4] == 'CS':
        #     category = 'Computer Software'
        #     account_asset_id = 3459
        #     account_depreciation_id = 3459
        #     account_depreciation_expense_id = 2060
        # if row_values[4] == 'CE':
        #     category = 'Cleaning Equipment'
        #     account_asset_id = 3464
        #     account_depreciation_id = 3464
        #     account_depreciation_expense_id = 2065
        # if row_values[4] == 'FF':
        #     category = 'Furniture and Fittings'
        #     account_asset_id = 3454
        #     account_depreciation_id = 3454
        #     account_depreciation_expense_id = 2051
        # if row_values[4] == 'OA':
        #     category = 'Office Alterations'
        #     account_asset_id = 3460
        #     account_depreciation_id = 3460
        #     account_depreciation_expense_id = 2061
        #
        # if row_values[4] == 'OE':
        #     category = 'Leased Office Equipment'
        #     account_asset_id = 3416
        #     account_depreciation_id = 3416
        #     account_depreciation_expense_id = 2076
        #
        # if row_values[4] == 'MV':
        #     category = 'Motor Vehicle'
        #     account_asset_id = 3466
        #     account_depreciation_id = 3466
        #     account_depreciation_expense_id = 2068
        #
        # if row_values[4] == 'MV':
        #     category = 'Motor Vehicle'
        #     account_asset_id = 3466
        #     account_depreciation_id = 3466
        #     account_depreciation_expense_id = 2068

        # Not Confirmed accounts
        # if row_values[4] == 'EL':
        #     category = row_values[4]
        #     account_asset_id = 3453
        #     account_depreciation_id = 3453
        #     account_depreciation_expense_id = 2028
        if row_values[4] == 'LD':
            category = 'Land'
            account_asset_id = 3453
            account_depreciation_id = 3453
            account_depreciation_expense_id = 2028
        # if row_values[4] == 'EL':
        #     row_values[4] = 'Leased Office Equipment'
        #     account_asset_id = 3466
        #     account_depreciation_id = 3466
        #     account_depreciation_expense_id = 2068

        asset_category = self.env['asset.category'].search(
            [('name', '=', category)], limit=1)
        if not asset_category:
            asset_category = self.env['asset.category'].create({
                'name': category
            })
        asset_type = self.env['asset.type'].search(
            [('name', '=', row_values[2])], limit=1)
        if not asset_type:
            asset_type = self.env['asset.type'].create({
                'name': row_values[2]
            })
        if not asset_model and account_asset_id:
            if row_values[8]:
                asset_model = self.env['account.asset'].create({
                    'name': row_values[8],
                    'state': 'model',
                    # 'account_asset_id': 1630,
                    'account_asset_id': account_asset_id,
                    # 'account_depreciation_id': 1630,
                        'account_depreciation_id': account_depreciation_id,
                    # 'account_depreciation_expense_id': 205,
                    'account_depreciation_expense_id': account_depreciation_expense_id,
                    'method': 'linear',
                    'asset_type': 'purchase',
                    'method_period': '1',
                    'asset_category_id': asset_category.id,
                    'asset_type_id': asset_type.id,
                    'method_number': int(row_values[11])*12/365 if row_values[11] else 1
                })
        self.env.cr.commit()

    def _create_asset(self, row_values):
        """Create a new asset model"""
        account_asset_id = ""
        asset_model = self.env['account.asset'].sudo().search(
            [('state', '=', 'model'), ('name', '=', row_values[8])], limit=1)
        # if not asset_model and row_values[4] not in ['EL', 'LD', 'M']:
        #     raise UserError("Import the asset model")
        # if row_values[4] == 'FF':
        #     row_values[4] = 'Furniture and Fittings'
        #     account_asset_id = 3454
        #     account_depreciation_id = 3454
        #     account_depreciation_expense_id = 2051
        # if row_values[4] == 'OA':
        #     row_values[4] = 'Office Alterations'
        #     account_asset_id = 3460
        #     account_depreciation_id = 3460
        #     account_depreciation_expense_id = 2061
        # if row_values[4] == 'CE':
        #     row_values[4] = 'Cleaning Equipment'
        #     account_asset_id = 3464
        #     account_depreciation_id = 3464
        #     account_depreciation_expense_id = 2065
        # if row_values[4] == 'M':
        #     row_values[4] = 'Plant and Machinery'
        #     account_asset_id = 3464
        #     account_depreciation_id = 3464
        #     account_depreciation_expense_id = 2065
        #
        # if row_values[4] == 'CS':
        #     row_values[4] = 'Computer Software'
        #     account_asset_id = 3459
        #     account_depreciation_id = 3459
        #     account_depreciation_expense_id = 2060
        # if row_values[4] == 'CH':
        #     row_values[4] = 'Computer Hardware'
        #     account_asset_id = 3458
        #     account_depreciation_id = 3458
        #     account_depreciation_expense_id = 2058
        # if row_values[4] == 'OE':
        #     row_values[4] = 'Office Equipment'
        #     account_asset_id = 3456
        #     account_depreciation_id = 3456
        #     account_depreciation_expense_id = 2056
        #
        if row_values[4] == 'LD':
            row_values[4] = 'Land'
            account_asset_id = 3456
            account_depreciation_id = 3456
            account_depreciation_expense_id = 2056

        # if row_values[4] == 'OE':
        #     row_values[4] = 'Leased Office Equipment'
        #     account_asset_id = 3456
        #     account_depreciation_id = 3456
        #     account_depreciation_expense_id = 2056

        # if row_values[4] == 'BD':
        #     row_values[4] = 'Building'
        #     account_asset_id = 3466
        #     account_depreciation_id = 3466
        #     account_depreciation_expense_id = 2068
        #
        # if row_values[4] == 'EL':
        #     row_values[4] = 'Leased Office Equipment'
        #     account_asset_id = 3466
        #     account_depreciation_id = 3466
        #     account_depreciation_expense_id = 2068

        # Not Confirmed accounts
        # if row_values[4] in ['EL', 'LD', 'M']:
        #     account_asset_id = 3453
        #     account_depreciation_id = 3453
        #     account_depreciation_expense_id = 2028
        asset_category = self.env['asset.category'].search(
            [('name', '=', row_values[4])], limit=1)
        if not asset_category:
            asset_category = self.env['asset.category'].create({
                'name': row_values[4]
            })

        asset_type = self.env['asset.type'].search(
            [('name', '=', row_values[2])], limit=1)
        if not asset_type:
            asset_type = self.env['asset.type'].create({
                'name': row_values[2]
            })
        excel_date = row_values[9]
        if type(excel_date) == str:
            date_object = datetime.strptime(excel_date, '%d/%m/%Y')
            formatted_date = date_object.strftime('%Y-%m-%d')
        else:
            excel_base_date = datetime(1899, 12,
                                       30)  # Excel base date (there's a difference due to Excel bug)

            python_date = excel_base_date + timedelta(days=excel_date)

            formatted_date = python_date.strftime('%Y-%m-%d')
        total_depreciation_2023 = ""
        if row_values[13] == '-':
            total_depreciation_2023 = ""
        elif row_values[13] == '':
            total_depreciation_2023 = ""
        else:
            total_depreciation_2023 = row_values[13]
        total_depreciation_2023 = str(total_depreciation_2023).replace(',', '')
        accumulated_depreciation_2023 = ""
        if row_values[14] == '-':
            accumulated_depreciation_2023 = ""
        elif row_values[14] == '':
            accumulated_depreciation_2023 = ""
        else:
            accumulated_depreciation_2023 = row_values[14]
        accumulated_depreciation_2023 = str(accumulated_depreciation_2023).replace(',', '')
        # location_id = self.env['stock.location'].search(
        #     [('name', '=', row_values[10])],
        #     limit=1)
        if account_asset_id:
            asset = self.env['account.asset'].sudo().create({
            'name': row_values[8],
            'model_id': asset_model.id,
            'account_asset_id': account_asset_id,
            'account_depreciation_id': account_depreciation_id,
            'account_depreciation_expense_id': account_depreciation_expense_id,
            'method': 'linear',
            'method_period': '1',
            'method_number': int(row_values[11])*12/365 if row_values[11] else 1,
            'asset_type': asset_model.asset_type,
            'asset_category_id': asset_category.id,
            'asset_type_id': asset_type.id,
            'alternative_ref': row_values[7],
            'acquisition_date': formatted_date,
            'depreciation_on_days': row_values[11],
            'related_purchase_value': float(str(row_values[12]).replace(',', '')) if row_values[12] != '-' else "",
            'original_value': float(str(row_values[12]).replace(',', '')) if row_values[12] != '-' else "",
            # 'salvage_value': float(str(row_values[14]).replace(',', '')) if row_values[14] != '-' else "",
            'salvage_value': float(str(row_values[32]).replace(',', '')) if row_values[32] != '-' else "",
            'total_depreciation_2022': float(total_depreciation_2023) if total_depreciation_2023 else "",
            'accumulated_depreciation_2022': float(accumulated_depreciation_2023) if accumulated_depreciation_2023 else "",
            'closing_book_value_2022': float(str(row_values[15]).replace(',', '')) if row_values[15] != '-' else "" ,
            'closing_book_value_2023': float(str(row_values[33]).replace(',', '')) if row_values[33] != '-' and row_values[33]else "",
            'accumulated_depreciation_2023': float(str(row_values[32]).replace(',', '')) if row_values[32] != '-' and row_values[32] else "",
            'total_depreciation_2023': float(str(row_values[31]).replace(',', '')) if row_values[31] != '-' and row_values[31] else "",
            'value_residual': float(str(row_values[34]).replace(',', '')) if row_values[34] != '-' else "",
            'w_and_t_per': float(str(row_values[35]).replace(',', '')) if row_values[35] != '-' and row_values[35] != '' else "",
            'current_w_and_t_2022': float(str(row_values[36]).replace(',', '')) if row_values[36] != '-' and row_values[36] != '' else "",
            'closing_accum_w_and_t_2022': float(str(row_values[37]).replace(',', '')) if row_values[37] != '-'  and row_values[37] != ''else "",
            'closing_tax_value_2022': float(str(row_values[38]).replace(',', '')) if row_values[38] != '-'  and row_values[38] != ''else "",
            'current_w_and_t_2023': float(str(row_values[39]).replace(',', '')) if row_values[39] != '-'  and row_values[39] != ''else "",
            'closing_accum_w_and_t_2023': float(str(row_values[40]).replace(',', '')) if row_values[40] != '-'  and row_values[40] != ''else "",
            'closing_tax_value_2023': float(str(row_values[41]).replace(',', '')) if row_values[41] != '-'  and row_values[41] != ''else "",
            })

            # if row_values[19] and row_values[19] != '-':
            #     move_1 = self.env['account.move'].create({
            #         'date': datetime.strptime('01072023', '%d%m%Y').date(),
            #         'ref': asset.name + ': Depreciation',
            #         'asset_id': asset.id,
            #         'line_ids': [
            #             (0, 0, {
            #                 'account_id': asset.account_depreciation_id.id,
            #                 'currency_id': asset.currency_id.id,
            #                 'debit': 0.0,
            #                 'credit': row_values[19],
            #             }),
            #             (0, 0, {
            #                 'account_id': asset.account_depreciation_expense_id.id,
            #                 'currency_id': asset.currency_id.id,
            #                 'debit': row_values[19],
            #                 'credit': 0.0,
            #             })]
            #     })
            # if row_values[20] and row_values[20] != '-':
            #     move_2 = self.env['account.move'].create({
            #         'date': datetime.strptime('01082023', '%d%m%Y').date(),
            #         'ref': asset.name + ': Depreciation',
            #         'asset_id': asset.id,
            #         'line_ids': [(0, 0, {
            #             'account_id': asset.account_depreciation_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': 0.0,
            #             'credit': row_values[20],
            #         }), (0, 0, {
            #             'account_id': asset.account_depreciation_expense_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': row_values[20],
            #             'credit': 0.0,
            #         })]
            #     })
            # if row_values[21] and row_values[21] != '-':
            #     move_3 = self.env['account.move'].create({
            #         'date': datetime.strptime('01092023', '%d%m%Y').date(),
            #         'ref': asset.name + ': Depreciation',
            #         'asset_id': asset.id,
            #         'line_ids': [(0, 0, {
            #             'account_id': asset.account_depreciation_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': 0.0,
            #             'credit': row_values[21],
            #         }), (0, 0, {
            #             'account_id': asset.account_depreciation_expense_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': row_values[21],
            #             'credit': 0.0,
            #         })]
            #     })
            # if row_values[22] and row_values[22] != '-':
            #     move_4 = self.env['account.move'].create({
            #         'date': datetime.strptime('01102023', '%d%m%Y').date(),
            #         'ref': asset.name + ': Depreciation',
            #         'asset_id': asset.id,
            #         'line_ids': [(0, 0, {
            #             'account_id': asset.account_depreciation_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': 0.0,
            #             'credit': row_values[22],
            #         }), (0, 0, {
            #             'account_id': asset.account_depreciation_expense_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': row_values[22],
            #             'credit': 0.0,
            #         })]
            #     })
            # if row_values[23] and row_values[23] != '-':
            #     move_5 = self.env['account.move'].create({
            #         'date': datetime.strptime('01112023', '%d%m%Y').date(),
            #         'ref': asset.name + ': Depreciation',
            #         'asset_id': asset.id,
            #         'line_ids': [(0, 0, {
            #             'account_id': asset.account_depreciation_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': 0.0,
            #             'credit': row_values[23],
            #         }), (0, 0, {
            #             'account_id': asset.account_depreciation_expense_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': row_values[23],
            #             'credit': 0.0,
            #         })]
            #     })
            # if row_values[24] and row_values[24] != '-':
            #     move_6 = self.env['account.move'].create({
            #         'date': datetime.strptime('01122023', '%d%m%Y').date(),
            #         'ref': asset.name + ': Depreciation',
            #         'asset_id': asset.id,
            #         'line_ids': [(0, 0, {
            #             'account_id': asset.account_depreciation_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': 0.0,
            #             'credit': row_values[24],
            #         }), (0, 0, {
            #             'account_id': asset.account_depreciation_expense_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': row_values[24],
            #             'credit': 0.0,
            #         })]
            #     })
            # if row_values[25] and row_values[25] != '-':
            #     move_7 = self.env['account.move'].create({
            #         'date': datetime.strptime('01012024', '%d%m%Y').date(),
            #         'ref': asset.name + ': Depreciation',
            #         'asset_id': asset.id,
            #         'line_ids': [(0, 0, {
            #             'account_id': asset.account_depreciation_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': 0.0,
            #             'credit': row_values[25],
            #         }), (0, 0, {
            #             'account_id': asset.account_depreciation_expense_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': row_values[25],
            #             'credit': 0.0,
            #         })]
            #     })
            # if row_values[26] and row_values[26] != '-':
            #     move_8 = self.env['account.move'].create({
            #         'date': datetime.strptime('01022024', '%d%m%Y').date(),
            #         'ref': asset.name + ': Depreciation',
            #         'asset_id': asset.id,
            #         'line_ids': [(0, 0, {
            #             'account_id': asset.account_depreciation_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': 0.0,
            #             'credit': row_values[26],
            #         }), (0, 0, {
            #             'account_id': asset.account_depreciation_expense_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': row_values[26],
            #             'credit': 0.0,
            #         })]
            #     })
            # if row_values[27] and row_values[27] != '-':
            #     move_9 = self.env['account.move'].create({
            #         'date': datetime.strptime('01032024', '%d%m%Y').date(),
            #         'ref': asset.name + ': Depreciation',
            #         'asset_id': asset.id,
            #         'line_ids': [(0, 0, {
            #             'account_id': asset.account_depreciation_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': 0.0,
            #             'credit': row_values[27],
            #         }), (0, 0, {
            #             'account_id': asset.account_depreciation_expense_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': row_values[27],
            #             'credit': 0.0,
            #         })]
            #     })
            # if row_values[28] and row_values[28] != '-':
            #     move_10 = self.env['account.move'].create({
            #         'date': datetime.strptime('01042024', '%d%m%Y').date(),
            #         'ref': asset.name + ': Depreciation',
            #         'asset_id': asset.id,
            #         'line_ids': [(0, 0, {
            #             'account_id': asset.account_depreciation_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': 0.0,
            #             'credit': row_values[28],
            #         }), (0, 0, {
            #             'account_id': asset.account_depreciation_expense_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': row_values[28],
            #             'credit': 0.0,
            #         })]
            #     })
            # if row_values[29] and row_values[29] != '-':
            #     move_10 = self.env['account.move'].create({
            #         'date': datetime.strptime('01052024', '%d%m%Y').date(),
            #         'ref': asset.name + ': Depreciation',
            #         'asset_id': asset.id,
            #         'line_ids': [(0, 0, {
            #             'account_id': asset.account_depreciation_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': 0.0,
            #             'credit': row_values[29],
            #         }), (0, 0, {
            #             'account_id': asset.account_depreciation_expense_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': row_values[29],
            #             'credit': 0.0,
            #         })]
            #     })
            # if row_values[30] and row_values[30] != '-':
            #     move_10 = self.env['account.move'].create({
            #         'date': datetime.strptime('01062024', '%d%m%Y').date(),
            #         'ref': asset.name + ': Depreciation',
            #         'asset_id': asset.id,
            #         'line_ids': [(0, 0, {
            #             'account_id': asset.account_depreciation_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': 0.0,
            #             'credit': row_values[30],
            #         }), (0, 0, {
            #             'account_id': asset.account_depreciation_expense_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': row_values[30],
            #             'credit': 0.0,
            #         })]
            #     })
            self.env.cr.commit()

    def action_update_location_assets(self, ):
        try:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            book = xlrd.open_workbook(fp.name)
        except FileNotFoundError:
            raise UserError(
                'No such file or directory found. \n%s.' % self.file_name)
        except xlrd.biffh.XLRDError:
            raise UserError('Only excel files are supported.')
        for sheet in book.sheets():
            try:
                for row in range(sheet.nrows):
                    if row >= 2:
                        row_values = sheet.row_values(row)
                        if row_values[7]:
                            alternative_ref = row_values[7]
                            account = self.env['account.asset'].search([(
                                'alternative_ref', '=', alternative_ref)])
                            if account:
                                self._update_location_assets(row_values, account)
            except IndexError:
                pass

    def _update_location_assets(self, row_values, asset):
        """Update the Asset"""
        location = ""
        if row_values[10]:
            if type(row_values[10]) == float:
                location = self.env['asset.verification.job.location'].search([('code', '=', int(row_values[10]))])
            # if type(row_values[10]) == str:
            #     location = self.env['asset.verification.job.location'].search([('name', '=', (row_values[10]))])
            #     if not location:
            #         location = self.env['asset.verification.job.location'].create({'name': row_values[10]})
        if location:
            asset.write({
                'job_location_id': location.id
            })
