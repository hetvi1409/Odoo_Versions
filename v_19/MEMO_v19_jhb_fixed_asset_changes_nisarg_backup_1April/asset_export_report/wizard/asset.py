from datetime import datetime, timedelta
from datetime import datetime
from dateutil.parser import parse
import xlrd
import tempfile
import binascii
from odoo import fields, models
from odoo.exceptions import UserError


class AssetImport(models.TransientModel):
    _inherit = 'asset.import'

    def action_update_assets(self, ):
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
                    if row >= 2 and sheet.name == 'All':
                        row_values = sheet.row_values(row)
                        if row_values[7]:
                            alternative_ref = row_values[7].replace('JPC', '')
                            account = self.env['account.asset'].search([(
                                'alternative_ref', '=', alternative_ref)])
                            if account:
                                self._update_assets(row_values, account)
            except IndexError:
                pass

    def _update_assets(self, row_values, asset):
        """Update the Asset"""
        asset.write({
            'total_depreciation_2022': float(str(row_values[13]).replace(',', '')) if row_values[13] != '-' and row_values[13] else "",
            'accumulated_depreciation_2022': float(str(row_values[14]).replace(',', '')) if row_values[14] != '-' and row_values[14] else "",
            'closing_book_value_2022': float(str(row_values[15]).replace(',', '')) if row_values[15] != '-' and row_values[15] else "",
            'total_depreciation_2023': float(str(row_values[31]).replace(',', '')) if row_values[31] != '-' and row_values[31] else "",
            'accumulated_depreciation_2023': float(str(row_values[32]).replace(',', '')) if row_values[32] != '-' and row_values[32] else "",
            'closing_book_value_2023': float(str(row_values[33]).replace(',', '')) if row_values[33] != '-' and row_values[33]else "",
            'closing_accum_w_and_t_2022': float(str(row_values[37]).replace(',', '')) if row_values[37] != '-' and row_values[37]else "",
            'closing_accum_w_and_t_2023': float(str(row_values[40]).replace(',', '')) if row_values[40] != '-' and row_values[40]else "",
        })
