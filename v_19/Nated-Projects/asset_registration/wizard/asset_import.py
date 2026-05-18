from datetime import timedelta, datetime
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
                if sheet.name == ' FAR':
                    for row in range(sheet.nrows):
                        if row >= 2:
                            row_values = sheet.row_values(row)
                            account = self.env['account.asset'].search([(
                                'identification_number', '=', row_values[0])])
                            if not account:
                                self._create_asset(row_values)
                if sheet.name == 'FAR INFRASTRUCTURE':
                    for row in range(sheet.nrows):
                        if row >= 2:
                            row_values = sheet.row_values(row)
                            account_asset = self.env[
                                'account.asset'].sudo().search(
                                [('identification_number', '=', row_values[9])])
                            if not account_asset:
                                self._create_asset_infra(row_values)
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
                if sheet.name == ' FAR':
                    for row in range(sheet.nrows):
                        if row >= 1:
                            row_values = sheet.row_values(row)
                            self._create_asset_model(row_values)
                if sheet.name == 'FAR INFRASTRUCTURE':
                    for row in range(sheet.nrows):
                        if row >= 1:
                            row_values = sheet.row_values(row)
                            self._create_asset_model_infra(row_values)
            except IndexError:
                pass
    def _create_asset_model(self, row_values):
        """Creating Asset Model"""
        asset_model = self.env['account.asset'].sudo().search(
            [('state', '=', 'model'), ('name', '=', row_values[3])], limit=1)
        if not asset_model:
            asset_model = self.env['account.asset'].create({
                'name': row_values[3],
                'state': 'model',
                'account_depreciation_id': 21,
                'account_depreciation_expense_id': 94,
                'method': 'linear',
                'asset_type': 'purchase',
                'method_period': '1',
                'type': 'FAR'
            })
    def _create_asset_model_infra(self, row_values):
        asset_model = self.env['account.asset'].sudo().search(
            [('state', '=', 'model'), ('name', '=', row_values[7])], limit=1)

        if not asset_model:
            asset_model = self.env['account.asset'].create({
            'name': row_values[6],
            'state': 'model',
            'account_depreciation_id': 21,
            'account_depreciation_expense_id': 94,
            'method': 'linear',
            'asset_type': 'purchase',
            'method_period': '1',
            'type': 'INFRASTRUCTURE'
            })

    def _create_asset(self, row_values):
        """Create a new asset model"""
        asset_model = self.env['account.asset'].sudo().search(
            [('state', '=', 'model'), ('name', '=', row_values[3])], limit=1)
        if not asset_model:
            raise UserError("Import the asset model")
        asset_type = self.env['asset.category'].search(
            [('name', '=', row_values[1])], limit=1)
        if not asset_type:
            asset_type = self.env['asset.category'].create({
                'name': row_values[1]
            })
        # if not asset_model:
        #     asset_model = self.env['account.asset'].create({
        #         'name': row_values[1],
        #         'state': 'model',
        #         'account_depreciation_id': 2,
        #         'account_depreciation_expense_id': 26,
        #         'method': 'linear',
        #         'asset_type': 'purchase',
        #         'method_period': '1',
        #         'type': 'FAR'
        #     })
        if row_values[21] and row_values[16]:
            original_value = float(str(row_values[16]).replace(',', '')) - \
                            float(str(row_values[21]).replace(',', ''))
        elif not row_values[21] and not row_values[16]:
            original_value = ''
        elif row_values[16] and not row_values[21]:
                original_value = float(str(row_values[16]).replace(',', ''))
        date = row_values[8]
        if type(date) == float:
            base_date = datetime(1900, 1, 1)
            acquisition_date = base_date + timedelta(
                days=date - 2)  # subtract 2 to account for Excel's leap year bug
        elif type(date) == str:
            if date[-3] == '/':
                acquisition_date = datetime.strptime(date, '%Y/%m/%d')
            else:
                acquisition_date = datetime.strptime(date, '%d/%m/%Y')
        # if asset_type.name != 'LAND' and asset_type.name != 'OPPE Heritage Asset':
        asset = self.env['account.asset'].create({
            'name': row_values[1],
            'model_id': asset_model.id,
            'account_depreciation_id': asset_model.account_depreciation_id.id,
            'account_depreciation_expense_id': asset_model.account_depreciation_expense_id.id,
            'method': asset_model.method,
            'original_useful_life': row_values[9] if row_values[9] not in ['Infinite ', 'infinite'] else 0,
            'method_number': int(row_values[15]) if type(row_values[15]) == float else 0,
            'method_period': asset_model.method_period,
            'asset_type': asset_model.asset_type,
            'asset_category_id': asset_type.id,
            'identification_number': row_values[0],
            'description': row_values[3],
            'office': row_values[4],
            'serial_number': row_values[5],
            'physical_street': row_values[6],
            'funding_source': row_values[7],
            'acquisition_date': acquisition_date,
            'life_in_months': row_values[9] if row_values[9] not in ['Infinite ', 'infinite'] else 0,
            'original_value': original_value,
            'opening_cost': float(str(row_values[18]).replace(',', '')) if row_values[18] else "",
            'addition': float(str(row_values[19]).replace(',', '')) if
            row_values[19] else "",
            'disposal': float(str(row_values[21]).replace(',', '')) if
            row_values[21] else "",
            'adjustment': float(str(row_values[20]).replace(',', '')) if
            row_values[20] else "",
            'closing_cost': float(str(row_values[22]).replace(',', '')) if
            row_values[22] else "",
            'acc_dep_opening': float(str(row_values[23]).replace(',', '')) if
            row_values[23] else "",
            'impairment_losses': float(row_values[37].replace(',', '')) if
            row_values[37] else "",
            'closing_accumulated_depreciation': float(
                str(row_values[39]).replace(',', '')) if row_values[39] else "",
            'opening_book_value_july_22': float(
                str(row_values[40]).replace(',', '')) if row_values[40] else "",
            'closing_book_value_july_22': float(
                str(row_values[41]).replace(',', '')) if row_values[41] else "",
            'condition': row_values[42],
            'type': 'FAR',
            'custodian': row_values[43]
        })
        self.env.cr.commit()
        # useful_life_2019 = self.env['asset.useful.life'].create({
            #     'date': datetime.strptime('01072019', '%d%m%Y').date(),
            #     'amount': float(str(row_values[10])) if type(
            #         row_values[10]) == float else "",
            #     'asset_id': asset.id
            # })
            # useful_life_2020 = self.env['asset.useful.life'].create({
            #     'date': datetime.strptime('01072020', '%d%m%Y').date(),
            #     'amount': float(str(row_values[11])) if type(
            #         row_values[11]) == float else "",
            #     'asset_id': asset.id
            # })
            # useful_life_2020 = self.env['asset.useful.life'].create({
            #     'date': datetime.strptime('01072020', '%d%m%Y').date(),
            #     'amount': float(str(row_values[13])) if type(
            #         row_values[13]) == float else "",
            #     'asset_id': asset.id
            # })
            # useful_life_2021 = self.env['asset.useful.life'].create({
            #     'date': datetime.strptime('01072021', '%d%m%Y').date(),
            #     'amount': float(str(row_values[14])) if type(
            #         row_values[14]) == float else "",
            #     'asset_id': asset.id
            # })
            # useful_life_2022 = self.env['asset.useful.life'].create({
            #     'date': datetime.strptime('01072021', '%d%m%Y').date(),
            #     'amount': float(str(row_values[15])) if type(
            #         row_values[15]) == float else "",
            #     'asset_id': asset.id
            # })
            # if row_values[23]:
            #     move_1 = self.env['account.move'].create({
            #     'date': datetime.strptime('01072022', '%d%m%Y').date(),
            #     'ref': asset.name + ': Depreciation',
            #     'asset_id': asset.id,
            #     'line_ids': [
            #         (0, 0, {
            #             'account_id': asset.account_depreciation_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': 0.0,
            #             'credit': row_values[23],
            #         }),
            #         (0, 0, {
            #             'account_id': asset.account_depreciation_expense_id.id,
            #             'currency_id': asset.currency_id.id,
            #             'debit': row_values[23],
            #             'credit': 0.0,
            #         })]
            # })
            # if row_values[24]:
            #     move_2 = self.env['account.move'].create({
            #     'date': datetime.strptime('01082022', '%d%m%Y').date(),
            #     'ref': asset.name + ': Depreciation',
            #     'asset_id': asset.id,
            #     'line_ids': [(0, 0, {
            #         'account_id': asset.account_depreciation_id.id,
            #         'currency_id': asset.currency_id.id,
            #         'debit': 0.0,
            #         'credit': row_values[24],
            #     }), (0, 0, {
            #         'account_id': asset.account_depreciation_expense_id.id,
            #         'currency_id': asset.currency_id.id,
            #         'debit': row_values[24],
            #         'credit': 0.0,
            #     })]
            # })
            # if row_values[25]:
            #     move_3 = self.env['account.move'].create({
            #     'date': datetime.strptime('01092022', '%d%m%Y').date(),
            #     'ref': asset.name + ': Depreciation',
            #     'asset_id': asset.id,
            #     'line_ids': [(0, 0, {
            #         'account_id': asset.account_depreciation_id.id,
            #         'currency_id': asset.currency_id.id,
            #         'debit': 0.0,
            #         'credit': row_values[25],
            #     }), (0, 0, {
            #         'account_id': asset.account_depreciation_expense_id.id,
            #         'currency_id': asset.currency_id.id,
            #         'debit': row_values[25],
            #         'credit': 0.0,
            #     })]
            # })
            # if row_values[26]:
            #     move_4 = self.env['account.move'].create({
            #     'date': datetime.strptime('01102022', '%d%m%Y').date(),
            #     'ref': asset.name + ': Depreciation',
            #     'asset_id': asset.id,
            #     'line_ids': [(0, 0, {
            #         'account_id': asset.account_depreciation_id.id,
            #         'currency_id': asset.currency_id.id,
            #         'debit': 0.0,
            #         'credit': row_values[26],
            #     }), (0, 0, {
            #         'account_id': asset.account_depreciation_expense_id.id,
            #         'currency_id': asset.currency_id.id,
            #         'debit': row_values[26],
            #         'credit': 0.0,
            #     })]
            # })
            # if row_values[27]:
            #     move_5 = self.env['account.move'].create({
            #     'date': datetime.strptime('01112022', '%d%m%Y').date(),
            #     'ref': asset.name + ': Depreciation',
            #     'asset_id': asset.id,
            #     'line_ids': [(0, 0, {
            #         'account_id': asset.account_depreciation_id.id,
            #         'currency_id': asset.currency_id.id,
            #         'debit': 0.0,
            #         'credit': row_values[27],
            #     }), (0, 0, {
            #         'account_id': asset.account_depreciation_expense_id.id,
            #         'currency_id': asset.currency_id.id,
            #         'debit': row_values[27],
            #         'credit': 0.0,
            #     })]
            # })
            # if row_values[28]:
            #     move_6 = self.env['account.move'].create({
            #     'date': datetime.strptime('01122022', '%d%m%Y').date(),
            #     'ref': asset.name + ': Depreciation',
            #     'asset_id': asset.id,
            #     'line_ids': [(0, 0, {
            #         'account_id': asset.account_depreciation_id.id,
            #         'currency_id': asset.currency_id.id,
            #         'debit': 0.0,
            #         'credit': row_values[28],
            #     }), (0, 0, {
            #         'account_id': asset.account_depreciation_expense_id.id,
            #         'currency_id': asset.currency_id.id,
            #         'debit': row_values[28],
            #         'credit': 0.0,
            #     })]
            # })
            # if row_values[29]:
            #     move_7 = self.env['account.move'].create({
            #     'date': datetime.strptime('01012023', '%d%m%Y').date(),
            #     'ref': asset.name + ': Depreciation',
            #     'asset_id': asset.id,
            #     'line_ids': [(0, 0, {
            #         'account_id': asset.account_depreciation_id.id,
            #         'currency_id': asset.currency_id.id,
            #         'debit': 0.0,
            #         'credit': row_values[29],
            #     }), (0, 0, {
            #         'account_id': asset.account_depreciation_expense_id.id,
            #         'currency_id': asset.currency_id.id,
            #         'debit': row_values[29],
            #         'credit': 0.0,
            #     })]
            # })
            # if row_values[30]:
            #     move_8 = self.env['account.move'].create({
            #     'date': datetime.strptime('01032023', '%d%m%Y').date(),
            #     'ref': asset.name + ': Depreciation',
            #     'asset_id': asset.id,
            #     'line_ids': [(0, 0, {
            #         'account_id': asset.account_depreciation_id.id,
            #         'currency_id': asset.currency_id.id,
            #         'debit': 0.0,
            #         'credit': row_values[30],
            #     }), (0, 0, {
            #         'account_id': asset.account_depreciation_expense_id.id,
            #         'currency_id': asset.currency_id.id,
            #         'debit': row_values[30],
            #         'credit': 0.0,
            #     })]
            # })
            # if row_values[31]:
            #     move_9 = self.env['account.move'].create({
            #     'date': datetime.strptime('01032023', '%d%m%Y').date(),
            #     'ref': asset.name + ': Depreciation',
            #     'asset_id': asset.id,
            #     'line_ids': [(0, 0, {
            #         'account_id': asset.account_depreciation_id.id,
            #         'currency_id': asset.currency_id.id,
            #         'debit': 0.0,
            #         'credit': row_values[31],
            #     }), (0, 0, {
            #         'account_id': asset.account_depreciation_expense_id.id,
            #         'currency_id': asset.currency_id.id,
            #         'debit': row_values[31],
            #         'credit': 0.0,
            #     })]
            # })
            # if row_values[32]:
            #     move_10 = self.env['account.move'].create({
            #     'date': datetime.strptime('01042023', '%d%m%Y').date(),
            #     'ref': asset.name + ': Depreciation',
            #     'asset_id': asset.id,
            #     'line_ids': [(0, 0, {
            #         'account_id': asset.account_depreciation_id.id,
            #         'currency_id': asset.currency_id.id,
            #         'debit': 0.0,
            #         'credit': row_values[32],
            #     }), (0, 0, {
            #         'account_id': asset.account_depreciation_expense_id.id,
            #         'currency_id': asset.currency_id.id,
            #         'debit': row_values[32],
            #         'credit': 0.0,
            #     })]
            # })
            # # move = self.env['account.move'].create({
            # #     'date': datetime.strptime('01042023', '%d%m%Y').date(),
            # #     'ref': asset.name + ': Depreciation',
            # #     'asset_id': asset.id,
            # #     'line_ids': [(0, 0, {
            # #             'account_id': asset.account_depreciation_id.id,
            # #             'currency_id': asset.currency_id.id,
            # #             'debit': 0.0,
            # #             'credit': row_values[33],
            # #         }), (0, 0, {
            # #             'account_id': asset.account_depreciation_expense_id.id,
            # #             'currency_id': asset.currency_id.id,
            # #             'debit': row_values[33],
            # #             'credit': 0.0,
            # #         })]
            # # })
            # # asset.total_depreciation_entries_count = 10


    def _create_asset_infra(self, row_values):
        """Create a new asset model"""
        asset_model = self.env['account.asset'].sudo().search(
            [('state', '=', 'model'), ('name', '=', row_values[6])], limit=1)
        asset_type = self.env['asset.category'].search(
            [('name', '=', row_values[5])], limit=1)
        if not asset_type:
            asset_type = self.env['asset.category'].create({
                'name': row_values[5]
            })
        # if not asset_model:
        #     asset_model = self.env['account.asset'].create({
        #     'name': row_values[4],
        #     'state': 'model',
        #     'account_depreciation_id': 2,
        #     'account_depreciation_expense_id': 26,
        #     'method': 'linear',
        #     'asset_type': 'purchase',
        #     'method_period': '1',
        #     'type': 'INFRASTRUCTURE'
        # })
        date = row_values[10]
        if type(date) == float:
            base_date = datetime(1900, 1, 1)
            acquisition_date = base_date + timedelta(
                days=date - 2)  # subtract 2 to account for Excel's leap year bug
        elif type(date) == str:
            if date[-3] == '/':
                acquisition_date = datetime.strptime(date, '%Y/%m/%d')
            else:
                acquisition_date = datetime.strptime(date, '%d/%m/%Y')
        # try:
        #     acquisition_date = datetime.strptime(
        #         str(row_values[7]).replace('/', ''), '%d%m%Y').date()
        # except ValueError:
        #     acquisition_date = fields.Date.today()
        if row_values[29]:
            orginal_value = float(str(row_values[24]).replace(',', '')) - \
                            float(str(row_values[29]).replace(',', ''))
        else:
            orginal_value = float(str(row_values[24]).replace(',', '')) if row_values[24] else 0
        print('assse')
        asset = self.env['account.asset'].create({
            'name': row_values[6],
            'model_id': asset_model.id,
            'account_depreciation_id': asset_model.account_depreciation_id.id,
            'account_depreciation_expense_id': asset_model.account_depreciation_expense_id.id,
            'method': asset_model.method,
            'method_number': row_values[18],
            'method_period': asset_model.method_period,
            'asset_type': asset_model.asset_type,
            'asset_category_id': asset_type.id,
            'physical_street': row_values[0],
            'physical_street2': row_values[1],
            'description': row_values[7],
            'component': row_values[8],
            'identification_number': row_values[9],
            'acquisition_date': acquisition_date,
            'funding_source': row_values[11],
            'conditional_assessment': row_values[12],
            'custodian': row_values[13],
            'original_useful_life': row_values[14],
            'original_value': orginal_value,
            'impair': row_values[18],
            'opening_cost': float(str(row_values[24]).replace(',', '')) if
            row_values[24] else "",
            'addition': float(str(row_values[25]).replace(',', '')) if
            row_values[25] else "",
            're_valued_value': float(row_values[26].replace(',', '')) if
            row_values[26] else "",
            'disposal': float(row_values[27].replace(',', '')) if row_values[
                27] else "",
            'closing_cost': float(str(row_values[28]).replace(',', '')) if
            row_values[28] else "",
            'acc_dep_opening': float(str(row_values[29]).replace(',', '')) if
            row_values[29] else "",
            'adjustment': float(row_values[42].replace(',', '')) if row_values[
                42] else "",
            'impairment_losses': float(row_values[44].replace(',', '')) if
            row_values[44] else "",
            'closing_accumulated_depreciation': float(
                str(row_values[45]).replace(',', '')) if row_values[45] else "",
            'opening_book_value_july_22': float(
                str(row_values[46]).replace(',', '')) if row_values[46] else "",
            'closing_book_value_july_22': float(
                str(row_values[47]).replace(',', '')) if row_values[47] else "",
            'type': 'INFRASTRUCTURE',

        })
        print('fdsfg')
        self.env.cr.commit()
        # useful_life_2017 = self.env['asset.useful.life'].create({
        #     'date': datetime.strptime('01072017', '%d%m%Y').date(),
        #     'amount': row_values[12],
        #     'asset_id': asset.id
        # })
        # useful_life_2018 = self.env['asset.useful.life'].create({
        #     'date': datetime.strptime('01072018', '%d%m%Y').date(),
        #     'amount': row_values[13],
        #     'asset_id': asset.id
        # })
        # useful_life_2019 = self.env['asset.useful.life'].create({
        #     'date': datetime.strptime('01072019', '%d%m%Y').date(),
        #     'amount': row_values[14],
        #     'asset_id': asset.id
        # })
        # useful_life_2020 = self.env['asset.useful.life'].create({
        #     'date': datetime.strptime('01072020', '%d%m%Y').date(),
        #     'amount': row_values[16],
        #     'asset_id': asset.id
        # })
        # useful_life_2021 = self.env['asset.useful.life'].create({
        #     'date': datetime.strptime('01072021', '%d%m%Y').date(),
        #     'amount': row_values[17],
        #     'asset_id': asset.id
        # })
        # useful_life_2022 = self.env['asset.useful.life'].create({
        #     'date': datetime.strptime('01072021', '%d%m%Y').date(),
        #     'amount': row_values[18],
        #     'asset_id': asset.id
        # })
        # move = self.env['account.move'].create({
        #     'date': datetime.strptime('01072022', '%d%m%Y').date(),
        #     'ref': asset.name + ': Depreciation',
        #     'asset_id': asset.id,
        #     'line_ids': [
        #         (0, 0, {
        #             'account_id': asset.account_depreciation_id.id,
        #             'currency_id': asset.currency_id.id,
        #             'debit': 0.0,
        #             'credit': float(str(row_values[25]).replace(',', '')) if
        #             row_values[25] else "",
        #         }),
        #         (0, 0, {
        #             'account_id': asset.account_depreciation_expense_id.id,
        #             'currency_id': asset.currency_id.id,
        #             'debit': float(str(row_values[25]).replace(',', '')) if
        #             row_values[25] else "",
        #             'credit': 0.0,
        #         })]
        # })
        # move = self.env['account.move'].create({
        #     'date': datetime.strptime('01082022', '%d%m%Y').date(),
        #     'ref': asset.name + ': Depreciation',
        #     'asset_id': asset.id,
        #     'line_ids': [
        #         (0, 0, {
        #             'account_id': asset.account_depreciation_id.id,
        #             'currency_id': asset.currency_id.id,
        #             'debit': 0.0,
        #             'credit': float(str(row_values[26]).replace(',', '')) if
        #             row_values[26] else "",
        #         }),
        #         (0, 0, {
        #             'account_id': asset.account_depreciation_expense_id.id,
        #             'currency_id': asset.currency_id.id,
        #             'debit': float(str(row_values[26]).replace(',', '')) if
        #             row_values[26] else "",
        #             'credit': 0.0,
        #         })]
        # })
        # move = self.env['account.move'].create({
        #     'date': datetime.strptime('01092022', '%d%m%Y').date(),
        #     'ref': asset.name + ': Depreciation',
        #     'asset_id': asset.id,
        #     'line_ids': [
        #         (0, 0, {
        #             'account_id': asset.account_depreciation_id.id,
        #             'currency_id': asset.currency_id.id,
        #             'debit': 0.0,
        #             'credit': float(str(row_values[27]).replace(',', '')) if
        #             row_values[27] else "",
        #         }),
        #         (0, 0, {
        #             'account_id': asset.account_depreciation_expense_id.id,
        #             'currency_id': asset.currency_id.id,
        #             'debit': float(str(row_values[27]).replace(',', '')) if
        #             row_values[27] else "",
        #             'credit': 0.0,
        #         })]
        # })
        # move = self.env['account.move'].create({
        #     'date': datetime.strptime('01102022', '%d%m%Y').date(),
        #     'ref': asset.name + ': Depreciation',
        #     'asset_id': asset.id,
        #     'line_ids': [
        #         (0, 0, {
        #             'account_id': asset.account_depreciation_id.id,
        #             'currency_id': asset.currency_id.id,
        #             'debit': 0.0,
        #             'credit': float(str(row_values[28]).replace(',', '')) if
        #             row_values[28] else "",
        #         }),
        #         (0, 0, {
        #             'account_id': asset.account_depreciation_expense_id.id,
        #             'currency_id': asset.currency_id.id,
        #             'debit': float(str(row_values[28]).replace(',', '')) if
        #             row_values[28] else "",
        #             'credit': 0.0,
        #         })]
        # })
        # move = self.env['account.move'].create({
        #     'date': datetime.strptime('01112022', '%d%m%Y').date(),
        #     'ref': asset.name + ': Depreciation',
        #     'asset_id': asset.id,
        #     'line_ids': [
        #         (0, 0, {
        #             'account_id': asset.account_depreciation_id.id,
        #             'currency_id': asset.currency_id.id,
        #             'debit': 0.0,
        #             'credit': float(str(row_values[29]).replace(',', '')) if
        #             row_values[29] else "",
        #         }),
        #         (0, 0, {
        #             'account_id': asset.account_depreciation_expense_id.id,
        #             'currency_id': asset.currency_id.id,
        #             'debit': float(str(row_values[29]).replace(',', '')) if
        #             row_values[29] else "",
        #             'credit': 0.0,
        #         })]
        # })
        # move = self.env['account.move'].create({
        #     'date': datetime.strptime('01122022', '%d%m%Y').date(),
        #     'ref': asset.name + ': Depreciation',
        #     'asset_id': asset.id,
        #     'line_ids': [
        #         (0, 0, {
        #             'account_id': asset.account_depreciation_id.id,
        #             'currency_id': asset.currency_id.id,
        #             'debit': 0.0,
        #             'credit': float(str(row_values[30]).replace(',', '')) if
        #             row_values[30] else "",
        #         }),
        #         (0, 0, {
        #             'account_id': asset.account_depreciation_expense_id.id,
        #             'currency_id': asset.currency_id.id,
        #             'debit': float(str(row_values[30]).replace(',', '')) if
        #             row_values[30] else "",
        #             'credit': 0.0,
        #         })]
        # })
        # move = self.env['account.move'].create({
        #     'date': datetime.strptime('01012023', '%d%m%Y').date(),
        #     'ref': asset.name + ': Depreciation',
        #     'asset_id': asset.id,
        #     'line_ids': [
        #         (0, 0, {
        #             'account_id': asset.account_depreciation_id.id,
        #             'currency_id': asset.currency_id.id,
        #             'debit': 0.0,
        #             'credit': float(str(row_values[31]).replace(',', '')) if
        #             row_values[31] else "",
        #         }),
        #         (0, 0, {
        #             'account_id': asset.account_depreciation_expense_id.id,
        #             'currency_id': asset.currency_id.id,
        #             'debit': float(str(row_values[31]).replace(',', '')) if
        #             row_values[31] else "",
        #             'credit': 0.0,
        #         })]
        # })
        # move = self.env['account.move'].create({
        #     'date': datetime.strptime('01022023', '%d%m%Y').date(),
        #     'ref': asset.name + ': Depreciation',
        #     'asset_id': asset.id,
        #     'line_ids': [
        #         (0, 0, {
        #             'account_id': asset.account_depreciation_id.id,
        #             'currency_id': asset.currency_id.id,
        #             'debit': 0.0,
        #             'credit': float(str(row_values[32]).replace(',', '')) if
        #             row_values[32] else "",
        #         }),
        #         (0, 0, {
        #             'account_id': asset.account_depreciation_expense_id.id,
        #             'currency_id': asset.currency_id.id,
        #             'debit': float(str(row_values[32]).replace(',', '')) if
        #             row_values[32] else "",
        #             'credit': 0.0,
        #         })]
        # })
        # move = self.env['account.move'].create({
        #     'date': datetime.strptime('01032023', '%d%m%Y').date(),
        #     'ref': asset.name + ': Depreciation',
        #     'asset_id': asset.id,
        #     'line_ids': [
        #         (0, 0, {
        #             'account_id': asset.account_depreciation_id.id,
        #             'currency_id': asset.currency_id.id,
        #             'debit': 0.0,
        #             'credit': float(str(row_values[33]).replace(',', '')) if
        #             row_values[33] else "",
        #         }),
        #         (0, 0, {
        #             'account_id': asset.account_depreciation_expense_id.id,
        #             'currency_id': asset.currency_id.id,
        #             'debit': float(str(row_values[33]).replace(',', '')) if
        #             row_values[33] else "",
        #             'credit': 0.0,
        #         })]
        # })
