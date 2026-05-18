import xlrd
import tempfile
import binascii
from odoo import fields, models
from odoo.exceptions import UserError

class ImportProjectTask(models.Model):
    _name = 'import.project.task'
    _description = 'Import a Project Task'
    """Import a Project Task"""

    project_id = fields.Many2one('project.project', readonly=True)
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
                        if row >= 2:
                            if sheet.name == 'WIP Schedule':
                                row_values = sheet.row_values(row)
                                if row_values[3]:
                                    task = self.env['project.task'].search(
                                        [('name', '=', row_values[0])])
                                    if not task:
                                        self.env['project.task'].create({
                                            'name': row_values[0],
                                            'location': row_values[3],
                                            'payments': row_values[4],
                                            'addition': row_values[5] if row_values[5] != ' ' and row_values[5] != '' else None,
                                            'retention_paid': row_values[6] if row_values[6] != ' ' and row_values[6] != ''  else None,
                                            'accumulated_payment': row_values[7],
                                            'retention': row_values[8],
                                            'retention_held': row_values[9],
                                            'retention_reserved': row_values[10],
                                            'total_retention_held': row_values[11],
                                            'retention_added': row_values[12],
                                            'completed_project': row_values[13],
                                            'value_work': row_values[14],
                                            # 'as_per_tb': row_values[16],
                                            # 'IA01952': row_values[17],
                                            # 'rts': row_values[18],
                                            # 'total': row_values[19]
                                        })
                except IndexError:
                    pass

