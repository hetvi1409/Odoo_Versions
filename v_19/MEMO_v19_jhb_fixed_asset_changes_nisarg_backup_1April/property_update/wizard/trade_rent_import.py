import xlrd
import tempfile
import binascii
from odoo import fields, models
from odoo.exceptions import UserError
from datetime import datetime


class TradeRentImport(models.TransientModel):
    _name = 'trade.rent.import'
    _description = 'Trade Rent import'

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
                    if row >= 1:
                        row_values = sheet.row_values(row)
                        property = self.env['trade.rent'].search(
                            [('ref', '=', row_values[3])])
                        if not property:
                            self._create_trade(row_values)
            except IndexError:
                pass

    def _create_trade(self, row_values):
        """Create a trade"""
        closing_balance = row_values[11].replace(' ', '')
        if closing_balance == '-':
            closing_balance = 0
        if row_values[5]:
            excel_date = row_values[5]
            lease_exp_date = datetime(*xlrd.xldate_as_tuple(excel_date, 0))
        else:
            lease_exp_date = ''
        total_charges = row_values[10].replace(' ', '')
        if total_charges == '-':
            total_charges = 0.0

        if row_values[7]:
            rentroll = datetime(*xlrd.xldate_as_tuple(row_values[7], 0))
        else:
            rentroll = ''
        self.env['trade.rent'].create({
            'bldg_code': row_values[0],
            'bldg_name': row_values[1],
            'name': row_values[2],
            'ref': row_values[3],
            'ten_name': row_values[4],
            'lease_exp_date': lease_exp_date if lease_exp_date else None,
            'state': row_values[6],
            'rentroll': rentroll if rentroll else None,
            'opening': row_values[8],
            'commercial': row_values[9],
            'total_charges': total_charges,
            'closing_balance': float(closing_balance) if closing_balance != '-' else None,
        })
