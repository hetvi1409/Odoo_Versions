from datetime import date

import xlrd
import tempfile
import binascii
from odoo import fields, models
from odoo.exceptions import UserError

class ImportMaintenance(models.TransientModel):
    _name = 'import.maintenance'
    _description = 'Account Import'

    file = fields.Binary(string='File')

    def action_import_xlsx(self):
        """Import xlsx file to maintenance"""
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
                        if sheet.name == 'Mech and Elect':
                            if row_values[1] != 'Operation Area' and row_values[1]:
                                self.create_uswathi_maintenance(row_values)
                        if sheet.name == 'umngeni LM':
                            if row_values[1] != 'Operation Area' and row_values[1]:
                                self.create_umngeni_maintenance(row_values)
                        if sheet.name == 'IMPENDLE':
                            if row_values[1] != 'Operation Area':
                                if row_values[1] or row_values[2]:
                                    print('2222', row_values,)
                                print('IMPENDLE', 'row_values', sheet.nrows, sheet.ncols)
                                self.create_impendle_maintenance(row_values)
                        if sheet.name not in ['Mech and Elect', 'umngeni LM', 'IMPENDLE']:
                            if row_values[1] != 'Operation Area' and row_values[1]:
                                self.create_maintenance(row_values)
            except IndexError:
                pass

    def create_maintenance(self, row_values):
        """Create maintenance"""
        year_installed = ''
        if type(row_values[8]) == float:
            if row_values[8]:
                dval = int(row_values[8])
                year_installed = date.fromordinal(dval + 693594)
        if type(row_values[8]) == str:
            year_installed = (row_values[8])
        maintenance = self.env['maintenance.request'].create({
            'name': row_values[2],
            'maintenance_type': 'preventive',
            'municipality': row_values[0],
            'operation_area': row_values[1],
            'pump_station': row_values[2],
            'coords': row_values[3],
            'source_of_water': row_values[4],
            'production_borehole': row_values[5],
            'type_pump': row_values[6],
            'no_of_per_station': row_values[7],
            'year_installed': str(year_installed),
            'make_of_pump': row_values[9],
            'flow_rate': row_values[10],
            'residual_head': row_values[11],
            'servicing_frequency': row_values[12],
        })
        if len(row_values) == 14:
            maintenance.pump_stations_per_frequency = row_values[13]

    def create_uswathi_maintenance(self, row_values):
        """Create the maintenance"""
        maintenance = self.env['maintenance.request'].create({
            'name': row_values[2],
            'maintenance_type': 'preventive',
            'municipality': 'uMshwathi LM',
            'operation_area': row_values[1],
            'pump_station': row_values[2],
            'type_pump': row_values[3],
            'no_of_per_station': row_values[4],
            'year_installed': row_values[5],
            'make_of_pump': row_values[6],
            'flow_rate': row_values[7],
            'residual_head': row_values[8],
            'servicing_frequency': row_values[9],
            'major_repairs': row_values[10],
            'comments': row_values[11]
        })

    def create_umngeni_maintenance(self, row_values):
        """Create the maintenance"""
        year_installed = ''
        if type(row_values[8]) == float:
            if row_values[8]:
                dval = int(row_values[8])
                year_installed = date.fromordinal(dval + 693594)
        if type(row_values[8]) == str:
            year_installed = (row_values[8])
        maintenance = self.env['maintenance.request'].create({
            'name': row_values[2],
            'maintenance_type': 'preventive',
            'municipality': 'Umngeni LM',
            'operation_area': row_values[1],
            'pump_station': row_values[2],
            'coords': row_values[3],
            'source_of_water': row_values[4],
            'production_borehole': row_values[5],
            'type_pump': row_values[6],
            'no_of_per_station': row_values[7],
            'year_installed': str(year_installed),
            'make_of_pump': row_values[9],
            'flow_rate': row_values[10],
            'residual_head': row_values[11],
            'production_rate': row_values[12],
            'capacity_of_plant': row_values[13],
            'type_of_treatment': row_values[14],
            'population_served': row_values[15],
            'maintenance_work': row_values[16],
            'major_repairs': row_values[17],
            'comments': row_values[18],
            'servicing_frequency': row_values[19]

        })

    def create_impendle_maintenance(self, row_values):
        """Create maintenance"""
        year_installed = ''
        if type(row_values[8]) == float:
            if row_values[8]:
                dval = int(row_values[8])
                year_installed = date.fromordinal(dval + 693594)
        if type(row_values[8]) == str:
            year_installed = (row_values[8])
        maintenance = self.env['maintenance.request'].create({
            'name': row_values[2],
            'maintenance_type': 'preventive',
            'municipality': row_values[0],
            'operation_area': row_values[1],
            'pump_station': row_values[2],
            'coords': row_values[3],
            'source_of_water': row_values[4],
            'production_borehole': row_values[5],
            'type_pump': row_values[6],
            'no_of_per_station': row_values[7],
            'year_installed': str(year_installed),
            'make_of_pump': row_values[9],
            'flow_rate': row_values[10],
            'residual_head': row_values[11],
            'production_rate': row_values[12],
            'capacity_of_plant': row_values[13],
            'type_of_treatment': row_values[14],
            'population_served': row_values[15],
            'maintenance_work': row_values[16],
            'major_repairs': row_values[17],
            'comments': row_values[18],
            'servicing_frequency': row_values[19]
        })
