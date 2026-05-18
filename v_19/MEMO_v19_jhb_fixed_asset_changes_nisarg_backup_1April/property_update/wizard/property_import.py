import xlrd
import tempfile
import binascii
from odoo import fields, models
from odoo.exceptions import UserError


class PropertyImport(models.TransientModel):
    _name = 'property.import'
    _description = 'Property import'

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
                        property = self.env['building'].search(
                            [('jmc_number', '=', row_values[0])])
                        if not property:
                            self._create_property(row_values)
                        else:
                            self._write_property(row_values, property)
            except IndexError:
                pass

    def _create_property(self, row_values):
        condition = ''
        if row_values[3] == '1 - Very Good':
            condition = 'very_good'
        if row_values[3] == '2 - Good':
            condition = 'good'
        if row_values[3] == '3 - Fair':
            condition = 'fair'
        if row_values[3] == '4 - Poor':
            condition = 'poor'
        if row_values[3] == '5 - Very Poor':
            condition = 'very_poor'
        region = self.env['regions'].search([('name', '=', row_values[4])])
        if not region:
            region = self.env['regions'].create({
                'name': row_values[4]
            })
        zoning = self.env['property.zoning'].search(
            [('name', '=', row_values[6])], limit=1)
        if not zoning:
            zoning = self.env['property.zoning'].create({
                'name': row_values[6]
            })
        department = self.env['property.department'].search([('name', '=', row_values[10])])
        if not department:
            department = self.env['property.department'].create({
                'name': row_values[10]
            })
        category = self.env['property.category'].search([('name', '=', row_values[13])])
        if not category:
            category = self.env['property.category'].create({
                'name': row_values[13]
            })
        category_amp = self.env['property.category.amp'].search([('name', '=', row_values[11])])
        amp = row_values[11].split(' - ')
        if not category_amp:
            category_amp = self.env['property.category.amp'].create({
                'name': row_values[11],
                'category_name': amp[-1],
                'category_id': category.id
            })
        price = ""
        if row_values[15] != '-' or row_values[15] != '':
            price_per_m = str(row_values[15]).split('R')
            price = price_per_m[-1].replace(',', '')
        if price == '-':
            price = 0.0
        self.env['building'].create({
            'name': row_values[1],
            'jmc_number': row_values[0],
            'address': row_values[2],
            'property_condition': condition,
            'region_id': region.id,
            'ward': row_values[5],
            'zoning_id': zoning.id,
            'latitude': row_values[7],
            'longitude': row_values[8],
            'sg_id': row_values[9],
            'department_id': department.id,
            'category_id': category.id,
            'category_amp_id': category_amp.id,
            'current_use': row_values[12],
            'pricing': float(price),
            'history_amount': float(price),
        })
        self.env.cr.commit()

    def _write_property(self, row_values, property):
        condition = ''
        if row_values[3] == '1 - Very Good':
            condition = 'very_good'
        if row_values[3] == '2 - Good':
            condition = 'good'
        if row_values[3] == '3 - Fair':
            condition = 'fair'
        if row_values[3] == '4 - Poor':
            condition = 'poor'
        if row_values[3] == '5 - Very Poor':
            condition = 'very_poor'
        region = self.env['regions'].search([('name', '=', row_values[4])])
        if not region:
            region = self.env['regions'].create({
                'name': row_values[4]
            })
        zoning = self.env['property.zoning'].search(
            [('name', '=', row_values[6])], limit=1)
        if not zoning:
            zoning = self.env['property.zoning'].create({
                'name': row_values[6]
            })
        department = self.env['property.department'].search([('name', '=', row_values[10])])
        if not department:
            department = self.env['property.department'].create({
                'name': row_values[10]
            })
        category = self.env['property.category'].search([('name', '=', row_values[13])])
        if not category:
            category = self.env['property.category'].create({
                'name': row_values[13]
            })
        category_amp = self.env['property.category.amp'].search([('name', '=', row_values[11])])
        amp = row_values[11].split(' - ')
        if not category_amp:
            category_amp = self.env['property.category.amp'].create({
                'name': row_values[11],
                'category_name': amp[-1],
                'category_id': category.id
            })
        price = ""
        if row_values[15] != '-' or row_values[15] != '':
            price_per_m = str(row_values[15]).split('R')
            price = price_per_m[-1].replace(',', '')
        if price == '-':
            price = 0.0
        property.write({
            'name': row_values[1],
            'jmc_number': row_values[0],
            'address': row_values[2],
            'property_condition': condition,
            'region_id': region.id,
            'ward': row_values[5],
            'zoning_id': zoning.id,
            'latitude': row_values[7],
            'longitude': row_values[8],
            'sg_id': row_values[9],
            'department_id': department.id,
            'category_id': category.id,
            'category_amp_id': category_amp.id,
            'current_use': row_values[12],
            'pricing': float(price),
            'history_amount': float(price),
        })
        self.env.cr.commit()
