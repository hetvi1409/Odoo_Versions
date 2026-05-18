import xlrd
import tempfile
import binascii
from odoo import fields, models
from odoo.exceptions import UserError


class OutdoorAdvertisementImport(models.TransientModel):
    _name = 'outdoor.advertisement.import'
    _description = 'Outdoor Advertisement import'

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
                    row_values = sheet.row_values(row)
                    # if sheet.name == 'Number Of Sites':
                    #     if row >= 1:
                    #         company = self.env['res.partner'].search(
                    #             [('name', '=', row_values[1]), ('company_type', '=', 'company')])
                    #         if not company:
                    #             company = self.env['res.partner'].create({
                    #                 'name': row_values[1],
                    #                 'company_type': 'company'
                    #             })
                    if sheet.name == 'JPC - Primedia':
                        if row >= 2:
                            if row_values[2] != '':
                                company = self.env['res.partner'].search(
                                    [('name', '=', 'Primedia'),
                                     ('company_type', '=', 'company')])
                                if not company:
                                    company = self.env['res.partner'].create({
                                        'name': 'Primedia',
                                        'company_type': 'company'
                                    })
                                Primedia = self.env[
                                    'outdoor.advertisement'].search(
                                    [('sequence', '=', row_values[0]),
                                     ('company_id', '=', company.id)])
                                if not Primedia:
                                    self._create_outdoor_advertisement(row_values)
                    if sheet.name == 'JCdecaux':
                        if row >= 2:
                            company = self.env['res.partner'].search(
                                [('name', '=', 'Jc Decaux'),
                                     ('company_type', '=', 'company')])
                            if not company:
                                company = self.env['res.partner'].create({
                                    'name': 'Jc Decaux',
                                    'company_type': 'company'
                                })
                            JcDecaux = self.env[
                                'outdoor.advertisement'].search(
                                [('sequence', '=', row_values[0]),
                                 ('company_id', '=', company.id)])
                            if not JcDecaux:
                                self._create_outdoor_advertisement_JCdecaux(row_values)
                    # if sheet.name == 'Kena Media':
                    #     if row >= 1:
                    #         if row_values[0]:
                    #             company = self.env['res.company'].search(
                    #                 [('name', '=', 'Kena Media')])
                    #             kena = self.env[
                    #                 'outdoor.advertisement'].search(
                    #                 [('sequence', '=', row_values[0]),
                    #                  ('company_id', '=', company.id)])
                    #             if not kena:
                    #                 self._create_outdoor_advertisement_Kena(row_values)
                    if sheet.name == 'Rishile':
                        if row >= 1:
                            company = self.env['res.partner'].search(
                                [('name', '=', 'Rishile '),
                                ('company_type', '=', 'company')])
                            if not company:
                                company = self.env['res.partner'].create({
                                    'name': 'Rishile',
                                    'company_type': 'company'
                                })
                            Rishile = self.env[
                                'outdoor.advertisement'].search(
                                [('sequence', '=', row_values[0]),
                                 ('company_id', '=', company.id)])
                            if not Rishile:
                                self._create_outdoor_advertisement_Rishile(
                                    row_values)
                    if sheet.name == 'Media Genious':
                        if row >= 1:
                            company = self.env['res.partner'].search(
                                [('name', '=', 'Media genious '),
                                ('company_type', '=', 'company')])
                            if not company:
                                company = self.env['res.partner'].create({
                                    'name': 'Media genious ',
                                    'company_type': 'company'
                                })
                            Media = self.env[
                                'outdoor.advertisement'].search(
                                [('sequence', '=', row_values[0]),
                                 ('company_id', '=', company.id)])
                            if not Media:
                                self._create_outdoor_advertisement_Media(
                                    row_values)
                    if sheet.name == 'New Era Outdoor':
                        if row >= 1:
                            company = self.env['res.partner'].search(
                                [('name', '=', 'New Era Outdoor'),
                                ('company_type', '=', 'company')])
                            if not company:
                                company = self.env['res.partner'].create({
                                    'name': 'New Era Outdoor',
                                    'company_type': 'company'
                                })
                            Era = self.env[
                                'outdoor.advertisement'].search(
                                [('sequence', '=', row_values[0]),
                                 ('company_id', '=', company.id)])
                            if not Era:
                                self._create_outdoor_advertisement_New_Era_Outdoor(
                                    row_values)
                    # if sheet.name == 'Frontseat':
                    #     if row >= 1 and row <= 28:
                    #         if row_values[0] != '':
                    #             company = self.env['res.company'].search(
                    #                 [('name', '=', 'Frontseat One')])
                    #             Frontseat = self.env[
                    #                 'outdoor.advertisement'].search(
                    #                 [('sequence', '=', row_values[0]),
                    #                  ('company_id', '=', company.id)])
                    #             if not Frontseat:
                    #                 self._create_outdoor_advertisement_Frontseat(
                    #                     row_values)
                    if sheet.name == 'Movie Magic':
                        if row >= 1:
                            company = self.env['res.partner'].search(
                                [('name', '=', 'Movie magic'),
                                ('company_type', '=', 'company')])
                            if not company:
                                company = self.env['res.partner'].create({
                                    'name': 'Movie magic',
                                    'company_type': 'company'
                                })
                            Movie = self.env[
                                'outdoor.advertisement'].search(
                                [('company_id', '=', company.id)])
                            if not Movie:
                                self._create_outdoor_advertisement_Movie(row_values)
                    if sheet.name == 'Karabo Media':
                        if row >= 1:
                            company = self.env['res.partner'].search(
                                [('name', '=', 'Karabo Media'),
                                 ('company_type', '=', 'company')])
                            if not company:
                                company = self.env['res.partner'].create({
                                    'name': 'Karabo Media',
                                    'company_type': 'company'
                                })
                            if not company:
                                company = self.env['res.partner'].create(
                                    {
                                        'name': 'Karabo Media',
                                        'company_type': 'company',
                                    })
                            Karabo = self.env[
                                'outdoor.advertisement'].search(
                                [('sequence', '=', row_values[0]),
                                 ('company_id', '=', company.id)])
                            if not Karabo:
                                self._create_outdoor_advertisement_Karabo(
                                    row_values)
                    if sheet.name == 'Ad outpost':
                        if row >= 1:
                            company = self.env['res.partner'].search(
                                [('name', '=', 'Ad outpost'),
                                 ('company_type', '=', 'company')], limit=1)
                            if not company:
                                company = self.env['res.partner'].create(
                                    {
                                        'name': 'Ad outpost',
                                        'company_type': 'company',
                                    })
                            if row_values[2] != '':
                                Ad = self.env[
                                    'outdoor.advertisement'].search(
                                    [('sequence', '=', row_values[0]),
                                     ('company_id', '=', company.id)])
                                if not Ad:
                                    self._create_outdoor_advertisement_Ad(
                                        row_values)
                    if sheet.name == 'Frontrow':
                        if row >=1:
                            if row_values[0] != '':
                                company = self.env['res.partner'].search(
                                    [('name', '=', 'Frontrow'),
                                     ('company_type', '=', 'company')])
                                if not company:
                                    company = self.env['res.partner'].create(
                                        {
                                            'name': 'Frontrow',
                                            'company_type': 'company',
                                        })
                                Frontrow = self.env[
                                    'outdoor.advertisement'].search(
                                    [('sequence', '=', row_values[0]),
                                     ('company_id', '=', company.id)])
                                if not Frontrow:

                                    self._create_outdoor_advertisement_Frontrow(
                                        row_values)
                    if sheet.name == 'Alive Advertising':
                        if row >=1:
                            company = self.env['res.partner'].search(
                                [('name', '=', 'Alive Advertising'),
                                 ('company_type', '=', 'company')])
                            if not company:
                                company = self.env['res.partner'].create(
                                    {
                                        'name': 'Frontrow',
                                        'company_type': 'company',
                                    })
                            Alive = self.env[
                                'outdoor.advertisement'].search(
                                [('sequence', '=', row_values[0]),
                                 ('company_id', '=', company.id)])
                            if not Alive:
                                self._create_outdoor_advertisement_Alive(
                                    row_values)
                    if sheet.name == 'Outsmart':
                        if row >=1:
                            company = self.env['res.partner'].search(
                                [('name', '=', 'Outsmart Network Provantage'),
                                 ('company_type', '=', 'company')])
                            if not company:
                                company = self.env['res.partner'].create(
                                    {
                                        'name': 'Outsmart Network Provantage',
                                        'company_type': 'company',
                                    })
                            Outsmart = self.env[
                                'outdoor.advertisement'].search(
                                [('sequence', '=', row_values[0]),
                                 ('company_id', '=', company.id)])
                            if not Outsmart:
                                self._create_outdoor_advertisement_Outsmart(
                                    row_values)
                    if sheet.name == 'Meraka Media ':
                        if row >=1:
                            if row_values[0] != '':
                                company = self.env['res.partner'].search(
                                    [('name', '=', 'Mereka Media'),
                                 ('company_type', '=', 'company')])
                            if not company:
                                company = self.env['res.partner'].create(
                                    {
                                        'name': 'Mereka Media',
                                        'company_type': 'company',
                                    })
                            Mereka = self.env[
                                'outdoor.advertisement'].search(
                                [('sequence', '=', row_values[0]),
                                 ('company_id', '=', company.id)])
                            if not Mereka:
                                self._create_outdoor_advertisement_Mereka(
                                    row_values)
            except IndexError:
                pass

    def _create_outdoor_advertisement(self, row_values):
        """Create outdoor advertisement"""
        township = self.env['township.township'].search(
            [('name', '=', row_values[3])])
        if not township:
            township = self.env['township.township'].create(
                {'name': row_values[3]})
        region = self.env['regions'].search([('name', '=', row_values[5])])
        if not region:
            region = self.env['regions'].create({
                'name': row_values[5]
            })

        if row_values[7] == 'No Zoning' or row_values[7] == 'No zoning' or \
                row_values[7] == 'Null':
            zoning = ""
        else:
            zoning = self.env['property.zoning'].search(
                [('name', '=', row_values[7])], limit=1)
            if not zoning:
                zoning = self.env['property.zoning'].create({
                    'name': row_values[7]
                })
        owen = self.env['res.partner'].search(
            [('name', '=', row_values[8])], limit=1)
        if not owen:
            owen = self.env['res.partner'].create({
                'name': row_values[8]
            })
        company = self.env['res.partner'].search(
            [('name', '=', 'Primedia'),
             ('company_type', '=', 'company')])
        outdoor = self.env['outdoor.advertisement'].create({
            'address': row_values[1],
            'erf': row_values[2],
            'township_id': township.id,
            'format': row_values[4],
            'region_id': region.id,
            'ward': row_values[6],
            'zoning_id': zoning.id if zoning else None,
            'owned_id': owen.id,
            'jmc_number': row_values[9] if row_values[9] != 'No JMC' else None,
            # 'start_date': row_values[10] if row_values[10] else None,
            # 'end_date': row_values[11] if row_values[11] else None,
            # 'day_notice': row_values[12],
            # 'rental': row_values[13],
            # 'renewal': row_values[14],
            'company_id': company.id,
            'sequence': row_values[0]
        })
        self.env.cr.commit()

    def _create_outdoor_advertisement_JCdecaux(self, row_values):
        """Create outdoor advertisement"""
        township = self.env['township.township'].search(
            [('name', '=', row_values[4])])
        if not township:
            township = self.env['township.township'].create(
                {'name': row_values[4]})
        region = self.env['regions'].search([('name', '=', row_values[6])])
        if not region:
            region = self.env['regions'].create({
                'name': row_values[6]
            })
        if row_values[8] == 'No Zoning' or row_values[8] == 'No zoning' or \
                row_values[8] == 'Null' or row_values[8] == 'No Zooning':
            zoning = ""
        else:
            zoning = self.env['property.zoning'].search(
                [('name', '=', row_values[8])], limit=1)
            if not zoning:
                zoning = self.env['property.zoning'].create({
                    'name': row_values[8]
                })
        owen = self.env['res.partner'].search(
            [('name', '=', row_values[9])], limit=1)
        if not owen:
            owen = self.env['res.partner'].create({
                'name': row_values[9]
            })
        company = self.env['res.partner'].search(
            [('name', '=', 'Jc Decaux'), ('company_type', '=', 'company')])
        self.env['outdoor.advertisement'].create({
            'sequence': row_values[0],
            'ref': row_values[1],
            'address': row_values[2],
            'erf': row_values[3],
            'township_id': township.id,
            # 'format': row_values[5],
            'region_id': region.id,
            'ward': row_values[7],
            'zoning_id': zoning.id if zoning else None,
            'owned_id': owen.id,
            'jmc_number': row_values[10] if row_values[10] != 'No JMC' else None,
            # 'start_date': row_values[11] if row_values[11] else None,
            # 'end_date': row_values[12] if row_values[12] else None,
            # 'day_notice': row_values[13],
            # 'rental': row_values[14],
            # 'renewal': row_values[15],
            'company_id': company.id,
        })
        self.env.cr.commit()

    def _create_outdoor_advertisement_Kena(self, row_values):
        """Create outdoor advertisement"""
        company = self.env['res.company'].search([('name', '=', 'Kena Media')])
        township = self.env['township.township'].search(
            [('name', '=', row_values[3])])
        if not township:
            township = self.env['township.township'].create(
                {'name': row_values[3]})
        region = self.env['regions'].search([('name', '=', row_values[6])])
        if not region:
            region = self.env['regions'].create({
                'name': row_values[6]
            })
        if row_values[8] == 'No Zoning' or row_values[8] == 'No zoning' or \
                row_values[8] == 'Null' or row_values[8] == 'No Zooning':
            zoning = ""
        else:
            zoning = self.env['property.zoning'].search(
                [('name', '=', row_values[8])], limit=1)
            if not zoning:
                zoning = self.env['property.zoning'].create({
                    'name': row_values[8]
                })
        owen = self.env['res.partner'].search(
            [('name', '=', row_values[10])], limit=1)
        if not owen:
            owen = self.env['res.partner'].create({
                'name': row_values[10]
            })
        self.env['outdoor.advertisement'].create({
            'sequence': row_values[0],
            'no_of_structure': row_values[1],
            'format': row_values[2],
            'township_id': township.id,
            'address': row_values[4],
            'erf': row_values[5],
            'region_id': region.id,
            'ward': row_values[7],
            'zoning_id': zoning.id if zoning else None,
            'jmc_number': row_values[9] if row_values[9] != 'No JMC' else None,
            'owned_id': owen.id,
            'start_date': row_values[11] if row_values[11] else None,
            'end_date': row_values[12] if row_values[12] else None,
            'day_notice': row_values[13],
            'rental': row_values[14],
            'renewal': row_values[15],
            'company_id': company.id,
        })

    def _create_outdoor_advertisement_Rishile(self, row_values):
        """Create outdoor advertisement"""
        company = self.env['res.partner'].search( [
            ('name', '=', 'Rishile '), ('company_type', '=', 'company')])
        region = self.env['regions'].search([('name', '=', row_values[5])])
        if not region:
            region = self.env['regions'].create({
                'name': row_values[5]
            })
        if row_values[6] == 'No Zoning' or row_values[6] == 'No zoning' or \
                row_values[6] == 'Null' or row_values[6] == 'No Zooning':
            zoning = ""
        else:
            zoning = self.env['property.zoning'].search(
                [('name', '=', row_values[6])], limit=1)
            if not zoning:
                zoning = self.env['property.zoning'].create({
                    'name': row_values[6]
                })
        if not region:
            region = self.env['regions'].create({
                'name': row_values[5]
            })
        owen = self.env['res.partner'].search(
            [('name', '=', row_values[8])], limit=1)
        if not owen:
            owen = self.env['res.partner'].create({
                'name': row_values[8]
            })
        self.env['outdoor.advertisement'].create({
            'sequence': row_values[0],
            'ref': row_values[1],
            'erf': row_values[2],
            'surbub': row_values[3],
            'ward': row_values[4],
            'region_id': region.id,
            'zoning_id': zoning.id if zoning else None,
            'jmc_number': row_values[7] if row_values[7] != 'No JMC' else None,
            'owned_id': owen.id,
            # 'start_date': row_values[9] if row_values[9] else None,
            # 'end_date': row_values[10] if row_values[10] else None,
            # 'day_notice': row_values[11],
            # 'rental': row_values[12],
            # 'renewal': row_values[13],
            'company_id': company.id,
        })
        self.env.cr.commit()

    def _create_outdoor_advertisement_Media(self, row_values):
        """Create outdoor advertisement"""
        company = self.env['res.partner'].search(
            [('name', '=', 'Media genious '),
             ('company_type', '=', 'company')])
        region = self.env['regions'].search([('name', '=', row_values[5])])
        if not region:
            region = self.env['regions'].create({
                'name': row_values[5]
            })
        if row_values[6] == 'No Zoning' or row_values[6] == 'No zoning' or \
                row_values[6] == 'Null' or row_values[6] == 'No Zooning':
            zoning = ""
        else:
            zoning = self.env['property.zoning'].search(
                [('name', '=', row_values[6])], limit=1)
            if not zoning:
                zoning = self.env['property.zoning'].create({
                    'name': row_values[6]
                })
        owen = self.env['res.partner'].search(
            [('name', '=', row_values[8])], limit=1)
        if not owen:
            owen = self.env['res.partner'].create({
                'name': row_values[8]
            })
        self.env['outdoor.advertisement'].create({
            'sequence': row_values[0],
            'ref': row_values[1],
            'erf': row_values[2],
            'surbub': row_values[3],
            'ward': row_values[4],
            'region_id': region.id,
            'zoning_id': zoning.id if zoning else None,
            'jmc_number': row_values[7] if row_values[7] != 'No JMC' else None,
            'owned_id': owen.id,
            # 'start_date': row_values[9] if row_values[9] else None,
            # 'end_date': row_values[10] if row_values[10] else None,
            # 'day_notice': row_values[11],
            # 'rental': row_values[12],
            # 'renewal': row_values[13],
            'company_id': company.id,
        })
        self.env.cr.commit()

    def _create_outdoor_advertisement_New_Era_Outdoor(self, row_values):
        """Create outdoor advertisement"""
        company = self.env['res.partner'].search(
            [('name', '=', 'New Era Outdoor'),
                                ('company_type', '=', 'company')])
        region = self.env['regions'].search([('name', '=', row_values[6])])
        if not region:
            region = self.env['regions'].create({
                'name': row_values[6]
            })
        if row_values[7] == 'No Zoning' or row_values[7] == 'No zoning' or \
                row_values[7] == 'Null' or row_values[7] == 'No Zooning':
            zoning = ""
        else:
            zoning = self.env['property.zoning'].search(
                [('name', '=', row_values[7])], limit=1)
            if not zoning:
                zoning = self.env['property.zoning'].create({
                    'name': row_values[7]
                })
        owen = self.env['res.partner'].search(
            [('name', '=', row_values[9])], limit=1)
        if not owen:
            owen = self.env['res.partner'].create({
                'name': row_values[9]
            })
        self.env['outdoor.advertisement'].create({
            'sequence': row_values[0],
            'ref': row_values[1],
            'address': row_values[2],
            'erf': row_values[3],
            'surbub': row_values[4],
            'ward': row_values[5],
            'region_id': region.id,
            'zoning_id': zoning.id if zoning else None,
            'jmc_number': row_values[8] if row_values[8] != 'No JMC' else None,
            'owned_id': owen.id,
            # 'start_date': row_values[10] if row_values[10] else None,
            # 'end_date': row_values[11] if row_values[11] else None,
            # 'day_notice': row_values[12],
            # 'rental': row_values[13],
            # 'renewal': row_values[14],
            'company_id': company.id,
        })
        self.env.cr.commit()

    def _create_outdoor_advertisement_Frontseat(self, row_values):
        """Create a new outdoor advertisement"""
        region = self.env['regions'].search([('name', '=', row_values[5])])
        if not region:
            region = self.env['regions'].create({
                'name': row_values[5]
            })
        if row_values[7] == 'No Zoning' or row_values[7] == 'No zoning' or \
                row_values[7] == 'Null' or row_values[7] == 'No Zooning':
            zoning = ""
        else:
            zoning = self.env['property.zoning'].search(
                [('name', '=', row_values[7])], limit=1)
            if not zoning:
                zoning = self.env['property.zoning'].create({
                    'name': row_values[7]
                })
        owen = self.env['res.partner'].search(
            [('name', '=', row_values[9])], limit=1)
        if not owen:
            owen = self.env['res.partner'].create({
                'name': row_values[9]
            })
        company = self.env['res.company'].search(
            [('name', '=', 'Frontseat One')])
        self.env['outdoor.advertisement'].create({
            'sequence': row_values[0],
            'ref': row_values[1],
            'address': row_values[2],
            'erf': row_values[3],
            'surbub': row_values[4],
            'region_id': region.id,
            'ward': row_values[6],
            'jmc_number': row_values[8] if row_values[8] != 'No JMC' else None,
            'owned_id': owen.id,
            'zoning_id': zoning.id if zoning else None,
            'start_date': row_values[10] if row_values[10] else None,
            'end_date': row_values[11] if row_values[11] else None,
            'day_notice': row_values[12],
            'rental': row_values[13],
            'renewal': row_values[14],
            'company_id': company.id,
        })

    def _create_outdoor_advertisement_Movie(self, row_values):
        """Create outdoor advertisement"""
        company = self.env['res.partner'].search(
            [('name', '=', 'Movie magic'),
             ('company_type', '=', 'company')])
        region = self.env['regions'].search([('name', '=', row_values[5])])
        if not region:
            region = self.env['regions'].create({
                'name': row_values[5]
            })
        if row_values[6] == 'No Zoning' or row_values[6] == 'No zoning' or \
                row_values[6] == 'Null' or row_values[6] == 'No Zooning':
            zoning = ""
        else:
            zoning = self.env['property.zoning'].search(
                [('name', '=', row_values[6])], limit=1)
            if not zoning:
                zoning = self.env['property.zoning'].create({
                    'name': row_values[6]
                })
        owen = self.env['res.partner'].search(
            [('name', '=', row_values[8])], limit=1)
        if not owen:
            owen = self.env['res.partner'].create({
                'name': row_values[8]
            })
        self.env['outdoor.advertisement'].create({
            'ref': row_values[0],
            'address': row_values[1],
            'erf': row_values[2],
            'surbub': row_values[3],
            'ward': row_values[4],
            'region_id': region.id,
            'zoning_id': zoning.id if zoning else None,
            'owned_id': owen.id,
            'jmc_number': row_values[7] if row_values[7] != 'No JMC' else None,
            # 'start_date': row_values[9] if row_values[9] else None,
            # 'end_date': row_values[10] if row_values[10] else None,
            # 'day_notice': row_values[11],
            # 'rental': row_values[12],
            # 'renewal': row_values[13],
            'company_id': company.id,
        })
        self.env.cr.commit()

    def _create_outdoor_advertisement_Karabo(self, row_values):
        """Create outdoor advertisement"""
        company = self.env['res.partner'].search(
            [('name', '=', 'Karabo Media'),
             ('company_type', '=', 'company')])
        region = self.env['regions'].search([('name', '=', row_values[5])])
        if not region:
            region = self.env['regions'].create({
                'name': row_values[5]
            })
        if row_values[7] == 'No Zoning' or row_values[7] == 'No zoning' or \
                row_values[7] == 'Null' or row_values[7] == 'No Zooning':
            zoning = ""
        else:
            zoning = self.env['property.zoning'].search(
                [('name', '=', row_values[7])], limit=1)
            if not zoning:
                zoning = self.env['property.zoning'].create({
                    'name': row_values[7]
                })
        owen = self.env['res.partner'].search(
            [('name', '=', row_values[9])], limit=1)
        if not owen:
            owen = self.env['res.partner'].create({
                'name': row_values[9]
            })
        self.env['outdoor.advertisement'].create({
            'sequence': row_values[0],
            'ref': row_values[1],
            'address': row_values[2],
            'erf': row_values[3],
            'surbub': row_values[4],
            'region_id': region.id,
            'ward': row_values[6],
            'zoning_id': zoning.id if zoning else None,
            'jmc_number': row_values[8]  if row_values[8] != 'No JMC' else None,
            'owned_id': owen.id,
            # 'start_date': row_values[10] if row_values[10] else None,
            # 'end_date': row_values[11] if row_values[11] else None,
            # 'day_notice': row_values[12],
            # 'rental': row_values[13],
            # 'renewal': row_values[14],
            'company_id': company.id,
        })
        self.env.cr.commit()

    def _create_outdoor_advertisement_Ad(self, row_values):
        """Create a new outdoor advertisement"""
        region = self.env['regions'].search([('name', '=', row_values[5])])
        if not region:
            region = self.env['regions'].create({
                'name': row_values[5]
            })
        if row_values[7] == 'No Zoning' or row_values[7] == 'No zoning' or \
                row_values[7] == 'Null' or row_values[7] == 'No Zooning':
            zoning = ""
        else:
            zoning = self.env['property.zoning'].search(
                [('name', '=', row_values[7])], limit=1)
            if not zoning:
                zoning = self.env['property.zoning'].create({
                    'name': row_values[7]
                })
        owen = self.env['res.partner'].search(
            [('name', '=', row_values[9])], limit=1)
        if not owen:
            owen = self.env['res.partner'].create({
                'name': row_values[9]
            })
        company = self.env['res.partner'].search(
            [('name', '=', 'Ad outpost'),
             ('company_type', '=', 'company')], limit=1)
        self.env['outdoor.advertisement'].create({
            'sequence': row_values[0],
            'ref': row_values[1],
            'address': row_values[2],
            'erf': row_values[3],
            'surbub': row_values[4],
            'region_id': region.id,
            'ward': row_values[6],
            'zoning_id': zoning.id if zoning else None,
            'jmc_number': row_values[8] if row_values[8] != 'No JMC' else None,
            'owned_id': owen.id,
            # 'start_date': row_values[10] if row_values[10] else None,
            # 'end_date': row_values[11] if row_values[11] else None,
            # 'day_notice': row_values[12],
            # 'rental': row_values[13],
            # 'renewal': row_values[14],
            'company_id': company.id,
        })
        self.env.cr.commit()

    def _create_outdoor_advertisement_Frontrow(self, row_values):
        """Create a new outdoor advertisement"""
        company = self.env['res.partner'].search(
            [('name', '=', 'Frontrow'),
             ('company_type', '=', 'company')])
        region = self.env['regions'].search([('name', '=', row_values[5])])
        if not region:
            region = self.env['regions'].create({
                'name': row_values[5]
            })
        if row_values[6] == 'No Zoning' or row_values[6] == 'No zoning' or \
                row_values[6] == 'Null' or row_values[6] == 'No Zooning':
            zoning = ""
        else:
            zoning = self.env['property.zoning'].search(
                [('name', '=', row_values[6])], limit=1)
            if not zoning:
                zoning = self.env['property.zoning'].create({
                    'name': row_values[6]
                })
        owen = self.env['res.partner'].search(
            [('name', '=', row_values[8])], limit=1)
        if not owen:
            owen = self.env['res.partner'].create({
                'name': row_values[8]
            })
        outdoor = self.env['outdoor.advertisement'].create({
            'sequence': row_values[0],
            'facility': row_values[1],
            'erf': row_values[2],
            'surbub': row_values[3],
            'ward': row_values[4],
            'region_id': region.id,
            'zoning_id': zoning.id if zoning else None,
            'jmc_number': row_values[7] if row_values[7] != 'No JMC' else None,
            'owned_id': owen.id,
            # 'start_date': row_values[9] if row_values[9] else None,
            # 'end_date': row_values[10] if row_values[10] else None,
            # 'day_notice': row_values[11],
            # 'rental': row_values[12],
            # 'renewal': row_values[13],
            'company_id': company.id,
        })
        self.env.cr.commit()

    def _create_outdoor_advertisement_Alive(self, row_values):
        company = self.env['res.partner'].search(
            [('name', '=', 'Alive Advertising'),
             ('company_type', '=', 'company')])
        region = self.env['regions'].search([('name', '=', row_values[6])])
        if not region:
            region = self.env['regions'].create({
                'name': row_values[6]
            })
        if row_values[7] == 'No Zoning' or row_values[7] == 'No zoning' or \
                row_values[7] == 'Null' or row_values[7] == 'No Zooning':
            zoning = ""
        else:
            zoning = self.env['property.zoning'].search(
                [('name', '=', row_values[7])], limit=1)
            if not zoning:
                zoning = self.env['property.zoning'].create({
                    'name': row_values[7]
                })
        owen = self.env['res.partner'].search(
            [('name', '=', row_values[9])], limit=1)
        if not owen:
            owen = self.env['res.partner'].create({
                'name': row_values[9]
            })
        self.env['outdoor.advertisement'].create({
            'sequence': row_values[0],
            'ref': row_values[1],
            'address': row_values[2],
            'erf': row_values[3],
            'surbub': row_values[4],
            'ward': row_values[5],
            'region_id': region.id,
            'zoning_id': zoning.id if zoning else None,
            'jmc_number': row_values[8] if row_values[8] != 'No JMC' else None,
            'owned_id': owen.id,
            # 'start_date': row_values[11] if row_values[11] else None,
            # 'end_date': row_values[12] if row_values[12] else None,
            # 'day_notice': row_values[13],
            # 'rental': row_values[14],
            # 'renewal': row_values[15],
            'company_id': company.id,
        })
        self.env.cr.commit()

    def _create_outdoor_advertisement_Outsmart(self, row_values):
        """Create outdoor advertisement"""
        region = self.env['regions'].search([('name', '=', row_values[6])])
        if not region:
            region = self.env['regions'].create({
                'name': row_values[6]
            })
        if row_values[7] == 'No Zoning' or row_values[7] == 'No zoning' or \
                row_values[7] == 'Null' or row_values[7] == 'No Zooning':
            zoning = ""
        else:
            zoning = self.env['property.zoning'].search(
                [('name', '=', row_values[7])], limit=1)
            if not zoning:
                zoning = self.env['property.zoning'].create({
                    'name': row_values[7]
                })
        owen = self.env['res.partner'].search(
            [('name', '=', row_values[9])], limit=1)
        if not owen:
            owen = self.env['res.partner'].create({
                'name': row_values[9]
            })
        company = self.env['res.partner'].search(
            [('name', '=', 'Outsmart Network Provantage'),
             ('company_type', '=', 'company')])
        self.env['outdoor.advertisement'].create({
            'sequence': row_values[0],
            'facility': row_values[1],
            'address': row_values[2],
            'erf': row_values[3],
            'surbub': row_values[4],
            'ward': row_values[5],
            'region_id': region.id,
            'zoning_id': zoning.id if zoning else None,
            'jmc_number': row_values[8] if row_values[8] != 'No JMC' else None,
            'owned_id': owen.id,
            # 'start_date': row_values[10] if row_values[10] else None,
            # 'end_date': row_values[11] if row_values[11] else None,
            # 'day_notice': row_values[12],
            # 'rental': row_values[13],
            # 'renewal': row_values[14],
            'company_id': company.id,
        })
        self.env.cr.commit()

    def _create_outdoor_advertisement_Mereka(self, row_values):
        """Create outdoor advertisement"""
        company = self.env['res.partner'].search(
            [('name', '=', 'Mereka Media'),
         ('company_type', '=', 'company')])
        township = self.env['township.township'].search(
            [('name', '=', row_values[4])])
        if not township:
            township = self.env['township.township'].create(
                {'name': row_values[4]})
        region = self.env['regions'].search([('name', '=', row_values[5])])
        if not region:
            region = self.env['regions'].create({
                'name': row_values[5]
            })
        if row_values[7] == 'No Zoning' or row_values[7] == 'No zoning' or \
                row_values[7] == 'Null' or row_values[7] == 'No Zooning':
            zoning = ""
        else:
            zoning = self.env['property.zoning'].search(
                [('name', '=', row_values[7])], limit=1)
            if not zoning:
                zoning = self.env['property.zoning'].create({
                    'name': row_values[7]
                })
        owen = self.env['res.partner'].search(
            [('name', '=', row_values[8])], limit=1)
        if not owen:
            owen = self.env['res.partner'].create({
                'name': row_values[8]
            })
        outdoor = self.env['outdoor.advertisement'].create({
            'sequence': row_values[0],
            'ref': row_values[1],
            'address': row_values[2],
            'erf': row_values[3],
            'township_id': township.id,
            'region_id': region.id,
            'ward': row_values[6],
            'zoning_id': zoning.id if zoning else None,
            'owned_id': owen.id,
            'jmc_number': row_values[9] if row_values[9] != 'No JMC' else None,
            # 'start_date': row_values[10] if row_values[10] else None,
            # 'end_date': row_values[11] if row_values[11] else None,
            # 'day_notice': row_values[12],
            # 'rental': row_values[13],
            # 'renewal': row_values[14],
            'company_id': company.id,
        })
        self.env.cr.commit()
