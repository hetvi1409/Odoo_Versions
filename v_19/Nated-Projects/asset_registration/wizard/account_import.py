import xlrd
import tempfile
import binascii
from odoo import fields, models
from odoo.exceptions import UserError

class AccountImport(models.TransientModel):
    _name = 'account.import'
    _description = 'Account Import'

    file = fields.Binary(string='File')

    def action_import_xlsx(self):
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
                    if row >= 0:
                        row_values = sheet.row_values(row)
                        account = self.env['account.account'].search([('code', '=', row_values[0])])
                        if not account:
                            self._create_account(row_values)
            except IndexError:
                pass
    def _create_account(self, row_values):
        if row_values[0] == 'AccountNumber':
            pass
        else:
            account_number_list = row_values[0].split('/')
            # account_number = account_number_list[0][1:].replace('-', '') + \
            #                  account_number_list[1][2:] + \
            #                  account_number_list[2][1:] + \
            #                  account_number_list[3][1:] + \
            #                  account_number_list[4][1:] + \
            #                  account_number_list[5]

            self.env['account.account'].create({
                'code': row_values[0],
                'name': row_values[1],
                'account_type': 'asset_non_current',
                'project': row_values[2],
                'project_scoa_account': row_values[3],
                'item': row_values[4],
                'item_scoa_account': row_values[5],
                'fund': row_values[6],
                'fund_scoa_account': row_values[7],
                'function': row_values[8],
                'function_scoa_account': row_values[9],
                'region': row_values[10],
                'region_scoa_account': row_values[11],
                'cost': row_values[12],
                'cost_scoa_account': row_values[13],
                'msc': row_values[13]
            })