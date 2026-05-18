from odoo import models, fields, _
import requests

import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# from Crypto.Cipher import AES
# from Crypto.Util.Padding import pad
# from Crypto.Random import get_random_bytes
import base64


class SageAssetIntegration(models.Model):
    """Methode for Sage Integration"""
    _name = """asset.sage.integration"""

    encrypt_password = fields.Boolean(string="Encrypt Password")
    user_password = fields.Char('userPassword')
    participant_reference = fields.Char('participantReference')
    private_key = fields.Char('privateKey')
    type = fields.Selection([('account', 'Account'),
                             ('transaction', 'Transaction'),
                             ('acquisitions', 'Acquisitions')],
                            string="Type", required=True, default='account')
    name = fields.Char(string="Name")
    username = fields.Char(string="Username", required=True, default='Odoo')
    password = fields.Char(string="Password", required=True,
                           default="EDIM5eER23++7rnpKvyEk+8pFFU/BkS5HLRkH5oJ0dM=", )
    # default='EDIM5eER23++7rnpKvyEk+6y0yix0DLo1i6hw+xbCw=')
    scoaVersionId = fields.Integer(string="scoaVersionId")
    date_from = fields.Date(string="transactionDateFrom")
    date_to = fields.Date(string="transactionDateTo")
    account = fields.Char(string="Account")

    def action_get_general_ledger(self):
        """Action test general ledger"""
        url = "http://169.254.1.2:83"

        payload = {}
        # headers = {
        #     'username': 'Odoo',
        #     'password': 'J75R4O9q/ur7mm58yl+WTou7jm43wlH3fDG/wZJSvk4='
        # }
        headers = {
            'username': self.username,
            'password': self.password
        }

        if self.type == 'account':
            url = url + '/api/accounts'
            if self.scoaVersionId:
                url = url + '?scoaVersionId=' + str(self.scoaVersionId)
                _logger.info("hi.....")
            else:
                url = url + '?scoaVersionId='

            _logger.info('URL: %s', url)
            try:
                response = requests.request("GET", url, headers=headers,
                                            data=payload)

                res = response.json()

                if response.status_code == 200:
                    _logger.info('response', response)
                    res = response.json()
                    for rec in res['response']:
                        account_type = ''
                        if rec['accountTypeID'] in [14, 15, 18, 19, 24, 28]:
                            account_type = 'asset_non_current'
                        account = self.env['account.account'].search([('code', '=',  rec['account'])])
                        if account_type and not account:
                            _logger.info(rec)
                            account_vals = {
                                'code': rec['account'],
                                'name': rec['accountDescription'],
                                'account_type': account_type,
                                'account_link': rec["accountLink"],
                                'account_master': rec["accountMaster"],
                                'extension_id_account': rec[
                                    "accountExtensionID"],
                                'account_extension': rec["accountExtAccount"],
                                'account_extension_link': rec[
                                    "accountExtAccountlink"],
                                'project_code': rec["projectCode"],
                                'project_description': rec[
                                    "projectDescription"],
                                'project_long_code': rec["projectLongCode"],
                                'project_guid_code': rec["projectGuidCode"],
                                'project_soca_account': rec[
                                    "projectSCOAAccount"],
                                'item_code': rec["itemCode"],
                                'item_description': rec["itemDescription"],
                                'item_long_code': rec["itemLongCode"],
                                'item_guid_code': rec["itemGuidCode"],
                                'item_soca_account': rec["itemSCOAAccount"],
                                'fund_code': rec["fundCode"],
                                'fund_description': rec["fundDescription"],
                                'fund_long_code': rec["fundLongCode"],
                                'fund_guid_code': rec["fundGuidCode"],
                                'fund_soca_account': rec["fundSCOAAccount"],
                                'function_code': rec["functionCode"],
                                'function_description': rec[
                                    "functionDescription"],
                                'function_long_code': rec["functionLongCode"],
                                'function_guid_code': rec["functionGuidCode"],
                                'function_soca_account': rec[
                                    "functionSCOAAccount"],
                                'region_code': rec["regionCode"],
                                'region_description': rec["regionDescription"],
                                'region_long_code': rec["regionLongCode"],
                                'region_guid_code': rec["regionGuidCode"],
                                'region_soca_account': rec["regionSCOAAccount"],
                                'costing_code': rec["costingCode"],
                                'costing_description': rec[
                                    "costingDescription"],
                                'costing_long_code': rec["costingLongCode"],
                                'costing_guid_code': rec["costingGuidCode"],
                                'costing_soca_account': rec[
                                    "costingSCOAAccount"],
                                'msc_code': rec["mscCode"],
                                'msc_description': rec["mscDescription"],
                                'scoa_version_id': rec["scoaVersionID"],

                            }
                            _logger.info('account_vals: %s', account_vals)
                            account = self.env['account.account'].create(
                                account_vals)
                            self.env.cr.commit()
                            _logger.info('account: %s', account)
                        else:
                            _logger.info(f"AccountTypeID {rec['accountTypeID']}")
            except Exception as e:
                raise UserError(f"Error {e}")
        if self.type == 'transaction':
            url = url + '/api/gltransactions'
            if self.date_from:
                url = url + '?transactionDateFrom=' + str(
                    self.date_from.year) + '-' + str(
                    self.date_from.month) + '-' + str(self.date_from.day)
            if self.date_to:
                url = url + '&transactionDateTo=' + str(
                    self.date_to.year) + '-' + str(
                    self.date_to.month) + '-' + str(self.date_to.day)
            if self.account:
                url = url + '?transactionAccount=' + str(self.account)
            # else:
            #    url = url + '?transactionAccount='
            # url = 'http://169.254.1.2:83/api/gltransactions?transactionDateFrom=2024-01-01&transactionDateTo=2024-07-31'
            _logger.info('URL: %s', url)
            try:
                response = requests.request("GET", url, headers=headers,
                                            data=payload)

                _logger.info('response: %s', response)
                _logger.info('response status: %s', response.__dict__)
                _logger.info('response status type: %s', type(response.status_code))
                if response.status_code == 200:
                    _logger.info("200, Status")
                    res = response.json()
                    _logger.info("200, Status", res['response'])
                    account_type_ids = [item["reference"] for item in res['response']]
                    _logger.info('account_type_ids: %s', account_type_ids)
                    unique_sorted = sorted(account_type_ids)
                    _logger.info('unique_sorted: %s', unique_sorted)

                    for rec in res['response']:
                        _logger.info(rec)
                        move = self.env['account.move'].search(
                            [('ref', '=', rec['reference'])])
                        if not move:
                            move = self.env['account.move'].sudo().create({
                                'move_type': 'entry',
                                'ref': rec['reference'],
                            })

                        _logger.info('move: %s', move)
                        journal_values = {
                            'name': rec['description'],
                            'debit': rec['debit'],
                            'sage_unique_identifier': rec['id'],
                            'date': rec['transactionDate'],
                            'credit': rec['credit'],
                            'balance': rec['amount'],
                            'audit_number': rec['accountNumber'],
                            'account_id': self.env['account.account'].search(
                                [('name', '=', rec['accountNumber'])], limit=1).id if
                            self.env['account.account'].search(
                                [('name', '=', rec['accountNumber'])], limit=1) else 1,
                            'move_id': move.id,
                        }
                        move_line = self.env['account.move.line'].sudo().create(journal_values)
                        _logger.info('move_line: %s', move_line)
                # _logger.info('response json: %s', response.json())
                res = response.json()
                # _logger.info('response status: %s',
                #             res['response'][0]['status'])
                # _logger.info('response statusDescription: %s',
                #             res['response'][0]['statusDescription'])
            except Exception as e:
                _logger.info('Exception df', e)
                raise UserError(e)
        if self.type == 'acquisitions':
            url = url + '/api/acquisitions'
            if self.date_from:
                url = url + '?transactionDateFrom=' + str(self.date_from)
            if self.date_to:
                url = url + '?transactionDateTo=' + str(self.date_to)
            # if self.account:
            url = url + '?Account=' + str(self.account)

            _logger.info('URL: %s', url)
            data = [{
                "id": 209857,
                "invoiceDate": "2024-06-03T00:00:00",
                "invoiceNumber": "GRV28238",
                "orderNumber": "uMDM03536",
                "supplierAccount": "FIR0013",
                "supplierName": "FIRST TECHNOLOGY KWAZULU NATAL",
                "accountNumber": "C0003-1/IA06193/F0002/X046/R0395/001/CORP",
                "accountDescription": "DC22_BS_Assets_Computer Equipment/Acquisitions/Transfer from Operational"
                                      "Revenue/Administrative and Corporate Support/Administrative or Head Office/Default/CORPORATE SERVICES",
                "itemFullDescription": "Assets:Non-current Assets:Property, Plant and Equipment:Cost Model:Computer Equipment:In-"
                                       "use:Cost:Acquisitions",
                "itemsDescription": 'null',
                "glAccountId": 19835,
                "totalAmountExcl": 716704.95,
                "totalTaxAmount": 107505.74,
                "totalAmountIncl": 824210.69
            },
                {
                    "id": 210055,
                    "invoiceDate": "2024-06-10T00:00:00",
                    "invoiceNumber": "GRV28220",
                    "orderNumber": "uMDM03566",
                    "supplierAccount": "PKV002",
                    "supplierName": "P.K Valves cc",
                    "accountNumber": "C0061-22/IA06433/F0002/X147/R0396/001/TECH",
                    "accountDescription": "Distribution-22/Acquisitions/Transfer from Operational Revenue/Water Storage/Whole of the District/Default/Technical Services",
                    "itemFullDescription": "Assets:Non-current Assets:Property, Plant and Equipment:Cost Model:Water Supply "
                                           "Infrastructure:Distribution:Cost:Acquisitions",
                    "itemsDescription": 'null',
                    "glAccountId": 8797,
                    "totalAmountExcl": 126750,
                    "totalTaxAmount": 19012.5,
                    "totalAmountIncl": 145762.5
                }]
            # for rec in data:
            #     partner = self.env['res.partner'].search([('name', '=', rec['supplierName'])])
            #     if not partner:
            #         partner = self.env['res.partner'].create({
            #             'name': rec['supplierName'],
            #         })
            #     move = self.env['account.move'].search(
            #         [('ref', '=', rec['invoiceNumber']),
            #          ('move_type', '=', 'out_invoice')])
            #     if not move:
            #         move = self.env['account.move'].sudo().create({
            #             'move_type': 'out_invoice',
            #             'ref': rec['invoiceNumber'],
            #             'invoice_date': rec['invoiceDate'],
            #             'partner_id': partner.id
            #         })
            #         print(move.journal_id.default_account_id, 'default')
            #     print(move.read(), 'move')
            #     percentage = (rec["totalTaxAmount"] / rec['totalAmountExcl']) * 100
            #     print(percentage, round(percentage, 2))
            #     tax = self.env['account.tax'].search([('amount', '=', percentage), ('type_tax_use', '=', 'sale')])
            #     if not tax:
            #         tax = self.env['account.tax'].create({
            #             'amount': percentage,
            #             'type_tax_use': 'sale',
            #             'name': "Tax %s" % str(percentage),
            #         })
            #     journal = self.env['account.move.line'].search([('sage_unique_identifier', '=', rec['id'])])
            #     if not journal:
            #         journal_values = {
            #             'name': rec['itemFullDescription'],
            #             'price_unit': rec['totalAmountExcl'],
            #             'sage_unique_identifier': rec['id'],
            #             'price_subtotal': rec['totalAmountIncl'],
            #             'tax_ids': tax.ids,
            #             'account_id': self.env['account.account'].search(
            #                 [('account_link', '=', rec['glAccountId'])],
            #                 limit=1).id if
            #             self.env['account.account'].search(
            #                 [('account_link', '=', rec['glAccountId'])],
            #                 limit=1) else 1,
            #             'move_id': move.id,
            #         }
            #         print(journal_values, 'safas')
            #         self.env['account.move.line'].sudo().create(journal_values)
            try:
                response = requests.request("GET", url, headers=headers,
                                            data=payload)

                _logger.info('response: %s', response)
                _logger.info('response text: %s', response.text)
                _logger.info('response acqusition json: %s', response.__dict__)
                res = response.json()
                _logger.info('response status: %s',
                             res['response'][0]['status'])
                _logger.info('response statusDescription: %s',
                             res['response'][0]['statusDescription'])
                if res['response'][0]['status'] == 'Error':
                    raise UserError(res['response'][0]['statusDescription'])
                if response.status_code == 200:
                    for rec in response.json():
                        partner = self.env['res.partner'].search(
                            [('name', '=', rec['supplierName'])])
                        if not partner:
                            partner = self.env['res.partner'].create({
                                'name': rec['supplierName'],
                            })

                        _logger.info('Partner details: %s', partner)
                        move = self.env['account.move'].search(
                            [('ref', '=', rec['invoiceNumber']),
                             ('move_type', '=', 'out_invoice')])
                        if not move:
                            move = self.env['account.move'].sudo().create({
                                'move_type': 'out_invoice',
                                'ref': rec['invoiceNumber'],
                                'invoice_date': rec['invoiceDate'],
                                'partner_id': partner.id
                            })
                        _logger.info('Journal Entry details: %s', move)
                        percentage = (rec["totalTaxAmount"] / rec[
                            'totalAmountExcl']) * 100
                        tax = self.env['account.tax'].search(
                            [('amount', '=', percentage),
                             ('type_tax_use', '=', 'sale')])
                        if not tax:
                            tax = self.env['account.tax'].create({
                                'amount': percentage,
                                'type_tax_use': 'sale',
                                'name': "Tax %s" % str(percentage),
                            })
                        journal = self.env['account.move.line'].search(
                            [('sage_unique_identifier', '=', rec['id'])])
                        if not journal:
                            journal_values = {
                                'name': rec['itemFullDescription'],
                                'price_unit': rec['totalAmountExcl'],
                                'sage_unique_identifier': rec['id'],
                                'price_subtotal': rec['totalAmountIncl'],
                                'tax_ids': tax.ids,
                                'account_id': self.env[
                                    'account.account'].search(
                                    [('account_link', '=', rec['glAccountId'])],
                                    limit=1).id if
                                self.env['account.account'].search(
                                    [('account_link', '=', rec['glAccountId'])],
                                    limit=1) else 1,
                                'move_id': move.id,
                            }
                            line = self.env['account.move.line'].sudo().create(
                                journal_values)
                            _logger.info('Journal Item details: %s', line)
                raise UserError(response.text)
            except Exception as e:
                raise UserError(e)

    # def action_get_password(self):
    #     """get password"""
    #     user_password = "examplePassword"
    #     participant_reference = "exampleReference"
    #     private_key = "examplePrivateKey"
    #
    #     encrypted = self.encrypt_pass(user_password, participant_reference,
    #                                   private_key)
    #     print(f"Encrypted: {encrypted}")
    #
    #     _logger.info('encrypted', encrypted)
    #     self.password = encrypted
    #
    # def encrypt_pass(self, user_password, participant_reference, private_key):
    #     # Ensure the private key is exactly 16 bytes (128 bits)
    #     key = private_key.encode('utf-8')
    #     if len(key) > 16:
    #         key = key[:16]
    #     elif len(key) < 16:
    #         key = key.ljust(16, b'\0')
    #
    #     # Create a new AES cipher with CBC mode
    #     cipher = AES.new(key, AES.MODE_CBC)
    #
    #     # Prepare the data to be encrypted
    #     plaintext = (user_password + '|' + participant_reference).encode(
    #         'utf-8')
    #     padded_plaintext = pad(plaintext, AES.block_size)
    #
    #     # Encrypt the data
    #     ciphertext = cipher.encrypt(padded_plaintext)
    #
    #     # Combine IV and ciphertext for transmission
    #     encrypted_data = cipher.iv + ciphertext
    #
    #     # Encode to Base64 for transmission
    #     return base64.b64encode(encrypted_data).decode('utf-8')
    #
