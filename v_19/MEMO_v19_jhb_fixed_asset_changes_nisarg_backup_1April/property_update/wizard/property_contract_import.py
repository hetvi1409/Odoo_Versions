import xlrd
import tempfile
import binascii
from odoo import fields, models
from odoo.exceptions import UserError
from datetime import datetime
import xlrd


class PropertyContractImport(models.TransientModel):
    _name = 'property.contract.import'
    _description = 'Property Contract import'

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
                lease_type = 'portfolio_lease'
                for row in range(sheet.nrows):
                    if row >= 4:
                        row_values = sheet.row_values(row)
                        property_contract = self.env['rental.contract'].search(
                            [('quick_ref', '=', str(row_values[10]))])
                        if not property_contract:
                            self._create_property_contract(row_values, lease_type)
            except IndexError:
                pass

    def action_import_outdoor_xlsx(self):
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
                lease_type = 'outdoor_lease'
                for row in range(sheet.nrows):
                    if row >= 4:
                        row_values = sheet.row_values(row)
                        property_contract = self.env['rental.contract'].search(
                            [('quick_ref', '=', str(row_values[10]))])
                        if not property_contract:
                            self._create_property_contract(row_values, lease_type)
            except IndexError:
                pass

    def action_import_trade_xlsx(self):
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
                lease_type = 'trade_lease'
                for row in range(sheet.nrows):
                    if row >= 1:
                        row_values = sheet.row_values(row)
                        property_contract = self.env['rental.contract'].search(
                            [('quick_ref', '=', str(row_values[10])), ('lease_type', '=', 'trade_lease')])
                        if not property_contract:
                            self._create_property_contract(row_values, lease_type)
            except IndexError:
                pass

    def action_update_xlsx(self):
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
                    if row >= 4:
                        row_values = sheet.row_values(row)
                        property_contract = self.env['rental.contract'].search(
                            [('quick_ref', '=', str(row_values[10]))])
                        if property_contract:
                            self._write_property_contract(row_values, property_contract)
                            # self._create_property_contract(row_values)
            except IndexError:
                pass

    def _create_property_contract(self, row_values, type_lease):
        """Create a property contract"""
        formatted_date_from = ""
        formatted_date_to = ""
        if row_values[16]:
            if type(row_values[16]) == str:
                input_date = row_values[16]
                date_object = datetime.strptime(input_date, "%d/%m/%Y")
                formatted_date_from = date_object.strftime("%Y-%m-%d")
                if formatted_date_from == '211-04-19':
                    formatted_date_from = '2011-04-19'
                formatted_date_from = datetime.strptime(formatted_date_from,
                                                        '%Y-%m-%d').date()
            if type(row_values[16]) == float:
                date = float(row_values[16])
                formatted_date_from = datetime(
                    *xlrd.xldate_as_tuple(date, 0)).date()
        commence_date = formatted_date_from
        if row_values[17]:
            if type(row_values[17]) == str:
                input_date = row_values[17]
                date_object = datetime.strptime(input_date, "%d/%m/%Y")
                formatted_date_to = date_object.strftime("%Y-%m-%d")
                formatted_date_to = datetime.strptime(formatted_date_to,
                                                      '%Y-%m-%d').date()
            if type(row_values[17]) == float:
                date = float(row_values[17])
                formatted_date_to = datetime(
                    *xlrd.xldate_as_tuple(date, 0)).date()
        lease_exp_date = formatted_date_to
        if formatted_date_from and formatted_date_to:
            if formatted_date_from > formatted_date_to:
                formatted_date_from, formatted_date_to = formatted_date_to, formatted_date_from
        creditor_region = self.env['creditor.region'].search(
            [('name', '=', row_values[2])])
        if not creditor_region:
            creditor_region = self.env['creditor.region'].create({
                'name': row_values[2]
            })
        if row_values[5]:
            portfolio_manager = self.env['res.partner'].search([('name', '=', row_values[5])], limit=1)
            if not portfolio_manager:
                portfolio_manager = self.env['res.partner'].create({
                    'name': row_values[5],
                    'email': row_values[5],
                })
        if row_values[6]:
            credit_controller = self.env['res.partner'].search([('name', '=', row_values[6])])
            if not credit_controller:
                credit_controller = self.env['res.partner'].create({
                    'name': row_values[6],
                    'email': row_values[6],
                })
        arr_status = self.env['arr.status'].search(
            [('name', '=', row_values[11])])
        if not arr_status:
            arr_status = self.env['arr.status'].create({
                'name': row_values[11]
            })
        lease_type = self.env['lease.type'].search(
            [('name', '=', row_values[12])])
        if not lease_type:
            lease_type = self.env['lease.type'].create({
                'name': row_values[12]
            })
        portfolio_category = self.env['portfolio.category'].search(
            [('name', '=', row_values[13])])
        if not portfolio_category:
            portfolio_category = self.env['portfolio.category'].create({
                'name': row_values[13]
            })
        unit_type = self.env['property.unit.type'].search(
            [('name', '=', row_values[14])])
        if not unit_type:
            unit_type = self.env['property.unit.type'].create({
                'name': row_values[14]
            })
        rentroll_period = ''
        if row_values[18]:
            date = float(row_values[18])
            rentroll_period = datetime(*xlrd.xldate_as_tuple(date, 0)).date()
        property = self.env['building'].search([('jmc_number', '=', row_values[8])])
        if row_values[15] == '*** VACANT ***':
            partner = self.env['res.partner'].browse(1)
        else:
            partner = self.env['res.partner'].search(
                [('name', '=', row_values[15])], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': row_values[15],
                    'is_tenant': True,
                })
        contract = self.env['rental.contract'].create({
            'lease_type': type_lease,
            'date_from':
                formatted_date_from if row_values[
                16] else fields.Date.today(),
            'date_to': formatted_date_to if row_values[
                17] else fields.Date.today(),
            'building': property.id if property.id else None,
            'insurance_fee': 0.0,
            'rental_fee': 0.0,
            'partner_id': partner.id if partner else 1,
            'rental_type': row_values[0],
            'view_group': row_values[1],
            'creditor_region_id': creditor_region.id,
            'bldg_code': str(row_values[3]).split('.')[0],
            'bldg_name': row_values[4],
            'portfolio_manager_id': portfolio_manager.id if row_values[5] else None,
            'credit_controller_id': credit_controller.id if row_values[6] else None,
            'unit_code': row_values[7],
            'jmc_number': row_values[8],
            'prem_no': row_values[9],
            'quick_ref': row_values[10],
            'arr_status_id': arr_status.id,
            'lease_type_id': lease_type.id,
            'portfolio_category_id': portfolio_category.id,
            'unit_type_id': unit_type.id,
            'ten_name': row_values[15] if row_values[15] != '*** VACANT ***' else None,
            'commence_date': commence_date if commence_date else None,
            'lease_exp_date': lease_exp_date if lease_exp_date else None,
            'rentroll_period': rentroll_period if rentroll_period else None,
            'opening_balance': row_values[19],
            'commercial_charges': float(str(row_values[20]).replace(',', '')),
            'deposits': row_values[21],
            'development': float(str(row_values[22]).replace(',', '')),
            'expenditure': row_values[23],
            'recoveries': float(str(row_values[24]).replace(',', '')),
            'social': float(str(row_values[25]).replace(',', '')),
            'vat': row_values[26],
            'advertising_charges': float(str(row_values[27]).replace(',', '')),
            'application_fees': row_values[28],
            'interest': float(str(row_values[29]).replace(',', '')),
            'land_sales': float(str(row_values[30]).replace(',', '')),
            'other_income': row_values[31],
            'residential': row_values[32],
            'servitudes': row_values[33],
            'total_receipts': row_values[34],
            'total_charges': row_values[35],
            'closing_balance': row_values[36]
        })
        self.env.cr.commit()

    def _write_property_contract(self, row_values, contract):
        """if already have contract, update the values"""
        formatted_date_from = ""
        formatted_date_to = ""
        if row_values[16]:
            if type(row_values[16]) == str:
                input_date = row_values[16]
                date_object = datetime.strptime(input_date, "%d/%m/%Y")
                formatted_date_from = date_object.strftime("%Y-%m-%d")
                if formatted_date_from == '211-04-19':
                    formatted_date_from = '2011-04-19'
                formatted_date_from = datetime.strptime(formatted_date_from,
                                                        '%Y-%m-%d').date()
            if type(row_values[16]) == float:
                date = float(row_values[16])
                formatted_date_from = datetime(
                    *xlrd.xldate_as_tuple(date, 0)).date()
        commence_date = formatted_date_from
        if row_values[17]:
            if type(row_values[17]) == str:
                input_date = row_values[17]
                date_object = datetime.strptime(input_date, "%d/%m/%Y")
                formatted_date_to = date_object.strftime("%Y-%m-%d")
                formatted_date_to = datetime.strptime(formatted_date_to,
                                                      '%Y-%m-%d').date()
            if type(row_values[17]) == float:
                date = float(row_values[17])
                formatted_date_to = datetime(
                    *xlrd.xldate_as_tuple(date, 0)).date()
        lease_exp_date = formatted_date_to
        if formatted_date_from and formatted_date_to:
            if formatted_date_from > formatted_date_to:
                formatted_date_from, formatted_date_to = formatted_date_to, formatted_date_from
        creditor_region = self.env['creditor.region'].search(
            [('name', '=', row_values[2])])
        if not creditor_region:
            creditor_region = self.env['creditor.region'].create({
                'name': row_values[2]
            })
        if row_values[5]:
            portfolio_manager = self.env['res.partner'].search(
                [('name', '=', row_values[5])], limit=1)
            if not portfolio_manager:
                portfolio_manager = self.env['res.partner'].create({
                    'name': row_values[5],
                    'email': row_values[5],
                })
        if row_values[6]:
            credit_controller = self.env['res.partner'].search(
                [('name', '=', row_values[6])])
            if not credit_controller:
                credit_controller = self.env['res.partner'].create({
                    'name': row_values[6],
                    'email': row_values[6],
                })
        arr_status = self.env['arr.status'].search(
            [('name', '=', row_values[11])])
        if not arr_status:
            arr_status = self.env['arr.status'].create({
                'name': row_values[11]
            })
        lease_type = self.env['lease.type'].search(
            [('name', '=', row_values[12])])
        if not lease_type:
            lease_type = self.env['lease.type'].create({
                'name': row_values[12]
            })
        portfolio_category = self.env['portfolio.category'].search(
            [('name', '=', row_values[13])])
        if not portfolio_category:
            portfolio_category = self.env['portfolio.category'].create({
                'name': row_values[13]
            })
        unit_type = self.env['property.unit.type'].search(
            [('name', '=', row_values[14])])
        if not unit_type:
            unit_type = self.env['property.unit.type'].create({
                'name': row_values[14]
            })
        rentroll_period = ''
        if row_values[18]:
            date = float(row_values[18])
            rentroll_period = datetime(*xlrd.xldate_as_tuple(date, 0)).date()
        property = self.env['building'].search(
            [('jmc_number', '=', row_values[8])])
        if row_values[15] == '*** VACANT ***':
            partner = self.env['res.partner'].browse(1)
        else:
            partner = self.env['res.partner'].search(
                [('name', '=', row_values[15])], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': row_values[15],
                    'is_tenant': True,
                })
        contract.write({
            'date_from':
                formatted_date_from if row_values[
                    16] else fields.Date.today(),
            'date_to': formatted_date_to if row_values[
                17] else fields.Date.today(),
            'building': property.id if property.id else None,
            'insurance_fee': 0.0,
            'rental_fee': 0.0,
            'partner_id': partner.id if partner else 1,
            'rental_type': row_values[0],
            'view_group': row_values[1],
            'creditor_region_id': creditor_region.id,
            'bldg_code': str(row_values[3]).split('.')[0],
            'bldg_name': row_values[4],
            'portfolio_manager_id': portfolio_manager.id if row_values[
                5] else None,
            'credit_controller_id': credit_controller.id if row_values[
                6] else None,
            'unit_code': row_values[7],
            'jmc_number': row_values[8],
            'prem_no': row_values[9],
            'quick_ref': row_values[10],
            'arr_status_id': arr_status.id,
            'lease_type_id': lease_type.id,
            'portfolio_category_id': portfolio_category.id,
            'unit_type_id': unit_type.id,
            'ten_name': row_values[15] if row_values[
                                              15] != '*** VACANT ***' else None,
            'commence_date': commence_date if commence_date else None,
            'lease_exp_date': lease_exp_date if lease_exp_date else None,
            'rentroll_period': rentroll_period if rentroll_period else None,
            'opening_balance': row_values[19],
            'commercial_charges': float(str(row_values[20]).replace(',', '')),
            'deposits': row_values[21],
            'development': float(str(row_values[22]).replace(',', '')),
            'expenditure': row_values[23],
            'recoveries': float(str(row_values[24]).replace(',', '')),
            'social': float(str(row_values[25]).replace(',', '')),
            'vat': row_values[26],
            'advertising_charges': float(str(row_values[27]).replace(',', '')),
            'application_fees': row_values[28],
            'interest': float(str(row_values[29]).replace(',', '')),
            'land_sales': float(str(row_values[30]).replace(',', '')),
            'other_income': row_values[31],
            'residential': row_values[32],
            'servitudes': row_values[33],
            'total_receipts': row_values[34],
            'total_charges': row_values[35],
            'closing_balance': row_values[36]
        })
        self.env.cr.commit()
