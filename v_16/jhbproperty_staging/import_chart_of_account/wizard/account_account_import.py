import xlrd
import tempfile
import binascii
from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountAccountImport(models.Model):
    """Chart of Account Import Model"""
    _name = 'account.account.import'
    _description = "Import Account"

    file = fields.Binary(string='File', required=True)

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
                    # if sheet.name == 'Table 1':
                    #     if row >= 0:
                    #         row_values = sheet.row_values(row)
                    #         # account = self.env['building'].search(
                    #         #     [('jmc_number', '=', row_values[0])])
                    #         # if not property:
                    #         self._create_account(row_values, 'Table 1')
                    # if sheet.name == 'Table 1 (2)':
                    #     if row >= 0:
                    #         row_values = sheet.row_values(row)
                    #         # property = self.env['building'].search(
                    #         #     [('jmc_number', '=', row_values[0])])
                    #         # if not property:
                    #         self._create_account(row_values, 'Table 1 (2)')
                    # if sheet.name == 'Sheet1':
                    #     if row >= 1:
                    #         row_values = sheet.row_values(row)
                    #         # account = self.env['account.account'].search(
                    #         #     [('code', '=', row_values[0])])
                    #         # if not account:
                    #         self._create_account(row_values, 'Sheet1')
                    # if sheet.name == 'Chart of Accounts':
                    #     # if row >= 2:
                    #     if row >= 1:
                    #         row_values = sheet.row_values(row)
                    #         account = self.env['account.account'].search(
                    #             [('code', '=', row_values[0])])
                    #         # if not account:
                    #         #     self._create_account(row_values, 'Chart of Accounts')
                    #         if not account:
                    #             self.create_account(row_values)
                    # else:
                    if row >= 2:
                        row_values = sheet.row_values(row)
                        account = self.env['account.account'].search(
                            [('code', '=', row_values[0])])
                        # if not account:
                        #     self._create_account(row_values, 'Chart of Accounts')
                        if not account:
                            self.create_account(row_values)
            except IndexError:
                pass

    def _create_account(self, row_values, type):
        """Methode for import the Chart of account"""
        if type == 'Chart of Accounts':
            company = self.env['res.company'].search([('name', '=', 'JPC')])
            account_type = ""
            if row_values[9] == 'Revenue':
                account_type = 'expense_direct_cost'
            if (row_values[9] == 'Employee Related Costs' or
                    row_values[9] == 'General Expenses - Advertising Costs' or
                    row_values[9] == 'General Expenses '
                    or row_values[9] == 'Doubtful debts '
                    or row_values[9] == 'Depreciation and amortisation '
                    or row_values[9] == 'Interest and finance costs ' or
                    row_values[9] == 'General Expenses:  Bank charges ' or
                    row_values[9] == 'General Expenses - Repairs and maintenance '):
                account_type = 'expense'
            elif (row_values[9] == 'Property, plant and equipment - Cost'
                    or row_values[9] == 'Property, plant and equipment - Accumulated Depreciation'):
                account_type = 'asset_non_current'
            elif (row_values[9] == 'Receivables from exchange transactions ' or
                  row_values[9] == 'Receivables from non-exchange transactions '
                  or row_values[9] == 'Cash and cash equivalents '):
                account_type = 'asset_current'
            elif (row_values[9] == 'Payables'
                  or row_values[9] == 'Loans from shareholders '
                  or row_values[9] == 'Payables from exchange transactions'
                  or row_values[9] == 'Provisions '
                  or row_values[9] == 'Current tax payable '):
                account_type = 'liability_current'
            elif ((row_values[9] == 'Accumulated surplus ' or
                  row_values[9] == 'Share capital / contributed capital')
                  or row_values[9] == 'Surplus/Deficit:Trnsfr  from  AS'):
                account_type = 'equity'
            category = self.env['account.category'].search([('name', '=', row_values[2])])
            if not category:
                category = self.env['account.category'].create({
                    'name': row_values[2]
                })
            classification = self.env['account.account.tag'].search([('name', '=', row_values[7])])
            if not classification:
                classification = self.env['account.account.tag'].create({
                    'name': row_values[7]
                })
            if account_type:
                account = self.env['account.account'].create({
                    'name': row_values[1],
                    'code': row_values[0],
                    'account_type': account_type,
                    'company_id': company.id,
                    'category_id': category.id,
                    'vat': row_values[3],
                    'budget_type': row_values[6],
                    'item_code': row_values[8],
                    'tag_ids': [(4, classification.id)],
                    'department_code': row_values[4],
                    'department_description': row_values[5]
                })
        # if type == 'Sheet1':
        #     company = self.env['res.company'].search([('name', '=', 'JPC')])
        #     account_type = ''
        #     if row_values[5] == 'I':
        #         account_type = 'income'
        #     if row_values[5] == 'B':
        #         account_type = 'asset_cash'
        #     if account_type:
        #         account = self.env['account.account'].create({
        #             'name': row_values[1],
        #             'code': row_values[0],
        #             'account_type': account_type,
        #             'company_id': company.id
        #         })
        # if type == 'Table 1 (2)':
        #     company = self.env['res.company'].search([('name', '=', 'Portflolio')])
        #     account_type = ''
        #     if row_values[4] == 'I':
        #         account_type = 'income'
        #     if row_values[4] == 'B':
        #         account_type = 'asset_cash'
        #     if account_type:
        #         account = self.env['account.account'].create({
        #             'name': row_values[1],
        #             'code': row_values[0],
        #             'account_type': account_type,
        #             'company_id': company.id
        #         })

    def create_account(self, row_values):
        """Create a new account for protfolio company"""
        classification = self.env['account.account.tag'].search(
            [('name', '=', row_values[6])])
        if not classification:
            classification = self.env['account.account.tag'].create({
                'name': row_values[6]
            })
        category = self.env['account.category'].search(
            [('name', '=', row_values[2])])
        if not category:
            category = self.env['account.category'].create({
                'name': row_values[2]
            })
        account_type = ''
        if row_values[9] == 'Revenue':
            account_type = 'expense_direct_cost'
        elif row_values[9] in ['Employee Related Costs',
                               'General Expenses - Advertising Costs',
                               'General Expenses', 'Doubtful debts',
                               'Depreciation and amortisation',
                               'Interest and finance costs',
                               'General Expenses: Bank charges',
                               'General Expenses - Repairs and maintenance']:
            account_type = 'expense'
        elif row_values[9] in ['Surplus/Deficit:Trnsfr from AS',
                               'Accumulated surplus',
                               'Share capital / contributed capital']:
            pass
        elif row_values[9] == '':
            pass

        elif (row_values[9] in ['Property, plant and equipment - Cost',
                                'Property, plant and equipment - Accumulated Depreciation']):
            account_type = 'asset_non_current'
        elif row_values[9] in ['Receivables from exchange transactions',
                               'Receivables from non-exchange transactions', 'Cash and cash equivalents']:
            account_type = 'asset_current'
        elif row_values[9] in ['Payables', 'Loans from shareholders',
                               'Payables from exchange transactions',
                               'Provisions', 'Current tax payable']:
            account_type = 'liability_current'
        else:
            raise UserError(_("Please check the asset types"))
        if account_type:
            account = self.env['account.account'].create({
                'name': row_values[1],
                'code': str(row_values[0]).replace('.0', ''),
                'account_type': account_type,
                'category_id': category.id,
                'vat': row_values[3],
                'budget_type': row_values[6],
                'item_code': row_values[8],
                'tag_ids': [(4, classification.id)],
                'department_code': row_values[4],
                'department_description': row_values[5]
            })
