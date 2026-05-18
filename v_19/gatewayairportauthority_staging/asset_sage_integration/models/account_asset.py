import re
import json
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import requests
from collections import defaultdict
import logging
_logger = logging.getLogger(__name__)


class AccountAccount(models.Model):
    _inherit = 'account.asset'

    sage_id = fields.Many2one('sage.response', string="Sage Response")
    sage_account_account_id = fields.Many2one('account.account', string="Sage Account")
    sage_depreciation_account_id = fields.Many2one('account.account', string="Depreciation Account")
    sage_accumulated_depreciation_account_id = fields.Many2one('account.account', string="Accumulated Depreciation Account")
    sage_expense_account_id = fields.Many2one('account.account', string="Expense Account")
    sage_cost_account_id = fields.Many2one('account.account', string="Asset Cost Account")
    all_asset_count = fields.Integer(string="Asset Count", compute="_compute_asset_count")

    def _compute_asset_count(self):
        for rec in self:
            rec.all_asset_count = self.env['account.asset'].search_count([('state', '!=', 'model'), ('model_id', '=', rec.id)])

    def action_view_asset(self):
        """View Asset"""
        asset = self.env['account.asset'].search(
            [('state', '!=', 'model'), ('model_id', '=', self.id)])
        action = {
            'name': _('Assets'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.asset',
            'context': {'create': False},
        }
        if len(asset) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': asset.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', asset.ids)],
            })
        return action

    def action_post_transaction(self):
        """Post Transaction"""
        headers = {
                'username': 'Odoo',
                'password': 'EDIM5eER23++7rnpKvyEk+8pFFU/BkS5HLRkH5oJ0dM=',
                "Content-Type": "application/json"
        }
        asset = self.env['account.asset'].search(
            [('state', '=', 'open'), ('model_id', '=', self.id)])
        move_line = self.env['account.move.line']
        GLTransaction = []
        for rec in asset:
            depreciation = rec.depreciation_move_ids
            for line in depreciation:
                if line.state == "posted":
                    move_line = move_line + line.line_ids
        ref_date = set(move_line.mapped('date'))
        for date in ref_date:
            same_date_lines = move_line.filtered(lambda l: l.date == date)
            accounts = set(same_date_lines.mapped('account_id'))
            for account in accounts:
                for same_date_line in same_date_lines:
                    if same_date_line.account_id == account:
                        if same_date_line.debit:
                            matching_lines = [tx for tx in GLTransaction if
                                          tx["AccountID"] == account.name and tx['dTxDate'] == date and tx['fDebit'] != 0]
                            if matching_lines:
                                matching_lines[0]['fDebit'] =+ same_date_line.debit
                            else:
                                data = {
                                'Description': same_date_line.name,
                                'Reference': "ODOO-" + str(date.month) + "-"+  str(same_date_line.move_id.id) + "-DR",
                                "fDebit": same_date_line.debit,
                                'fCredit': 0,
                                "AccountID": account.name,
                                "iProjectID": 0,
                                "dTxDate": str(date) + "T00:00:00",
                                # "UniqueID":"7783"
                                # "UniqueID": str(date.day) + str(date.month)+ str(date.year) + str(same_date_line.id)
                                "UniqueID": str(date.day).zfill(2) + str(
                                        date.month).zfill(2) + str(
                                        date.year) + str(same_date_line.id)
                            }
                                GLTransaction.append(data)
                        if same_date_line.credit:
                            matching_lines = [tx for tx in GLTransaction if
                                          tx["AccountID"] == account.name and tx['dTxDate'] == date and tx['fCredit'] != 0]
                            if matching_lines:
                                matching_lines[0]['fCredit'] =+ same_date_line.credit
                            else:
                                data = {
                                    'Description': same_date_line.name,
                                    'Reference': "ODOO-" + str(date.month) + "-"+  str(same_date_line.move_id.id) + "-CR",
                                    "fDebit": 0,
                                    'fCredit': same_date_line.credit,
                                    "AccountID": account.name,
                                    "iProjectID": 0,
                                    "dTxDate": str(date) + "T00:00:00",
                                    # "UniqueID":"7783"
                                    "UniqueID": str(date.day).zfill(2) + str(
                                                                            date.month).zfill(2) + str(
                                                                            date.year) + str(same_date_line.id)
                                }
                                GLTransaction.append(data)

        _logger.info("GLTransaction %s" % GLTransaction)
        payload = json.dumps({
            "data": [
                {
                    "AccountID": 3034,
                    "Reference": "JNLOdoo-52860",
                    "Description": "Sample Description",
                    "fDebit": 100000,
                    "fCredit": 0,
                    "TaxAmount": 0,
                    "iProjectID": 0,
                    "dTxDate": "2025-09-10T00:00:00",
                    "UniqueID": 72026
                },
                {
                    "AccountID": 3035,
                    "Reference": "JNLOdoo-55250",
                    "Description": "Another Description",
                    "fDebit": 0,
                    "fCredit": 100000,
                    "TaxAmount": 0,
                    "iProjectID": 0,
                    "dTxDate": "2025-09-10T00:00:00",
                    "UniqueID": 72225
                }
            ]
        })

        payload = json.dumps({
            'data': GLTransaction
        })
        _logger.info("payload %s" % payload)
        self.message_post( body=_('Payload: %s ') % (payload, ))
        url = "http://169.254.1.2:83/api/gltransactions"
        response = requests.post(url, headers=headers, data=payload)
        self.message_post( body=_('Response: %s') % (response.__dict__, ))
        # response = requests.request("POST", url, headers=headers, data=payload)

        # _logger.info("response %s %s" % (response, response.__dict__))
        # _logger.info("response %s %s" % (response, response.text))
        # [{'Account': 'Expenses', 'Reference': 'Asset - 5 Years: Depreciation',
        #   'fDebit': 400.0, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0,
        #   'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'},
        #  {'Account': 'Current Assets',
        #   'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 0,
        #   'fCredit': 400.0, 'AccountID': False, 'iProjectID': 0,
        #   'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'},
        #  {'Account': 'Expenses', 'Reference': 'Asset - 5 Years: Depreciation',
        #   'fDebit': 386.67, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0,
        #   'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'},
        #  {'Account': 'Current Assets',
        #   'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 0,
        #   'fCredit': 386.67, 'AccountID': False, 'iProjectID': 0,
        #   'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'}]
        # GLTransaction

        # [{'Account': 'Expenses', 'Reference': 'Asset - 5 Years: Depreciation',
        #   'fDebit': 386.67, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0,
        #   'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'},
        #  {'Account': 'Current Assets',
        #   'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 0,
        #   'fCredit': 386.67, 'AccountID': False, 'iProjectID': 0,
        #   'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'}]
        # GLTransaction
        # [{'Account': 'Expenses', 'Reference': 'Asset - 5 Years: Depreciation',
        #   'fDebit': 386.67, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0,
        #   'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'},
        #  {'Account': 'Current Assets',
        #   'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 0,
        #   'fCredit': 386.67, 'AccountID': False, 'iProjectID': 0,
        #   'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'}]
        # GLTransaction
        #
        # [{'Account': 'Expenses', 'Reference': 'Asset - 5 Years: Depreciation',
        #   'fDebit': 386.67, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0,
        #   'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'},
        #  {'Account': 'Current Assets',
        #   'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 0,
        #   'fCredit': 386.67, 'AccountID': False, 'iProjectID': 0,
        #   'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'}]
        # GLTransaction
        #
        # data = [{'Account': 'Expenses', 'Reference': 'Asset - 5 Years: Depreciation',
        #   'fDebit': 400.0, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0,
        #   'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'},
        #  {'Account': 'Current Assets',
        #   'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 0,
        #   'fCredit': 400.0, 'AccountID': False, 'iProjectID': 0,
        #   'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'}]
        #
        # data =[{'Account': 'Current Assets', 'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 0, 'fCredit': 386.67, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'},
        #        {'Account': 'Current Assets', 'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 0, 'fCredit': 386.67, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'},
        #        {'Account': 'Expenses', 'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 386.67, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'},
        #        {'Account': 'Expenses', 'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 386.67, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'},
        #        {'Account': 'Expenses', 'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 386.67, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'},
        #        {'Account': 'Expenses', 'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 386.67, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'},
        #        {'Account': 'Expenses', 'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 386.67, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'},
        #        {'Account': 'Expenses', 'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 386.67, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'}]

    def action_post_transaction_asset(self):
        """Asset - Post Transaction API"""
        headers = {
            'username': 'Odoo',
            'password': 'EDIM5eER23++7rnpKvyEk+8pFFU/BkS5HLRkH5oJ0dM=',
            "Content-Type": "application/json"
        }
        move_line = self.env['account.move.line']
        depreciation = self.depreciation_move_ids
        GLTransaction = []
        for line in depreciation:
            if line.state == "posted":
                move_line = move_line + line.line_ids
        print(move_line, 'move_line')
        ref_date = set(move_line.mapped('date'))
        print(ref_date)
        for date in ref_date:
            print(date)
            same_date_lines = move_line.filtered(lambda l: l.date == date)
            accounts = set(same_date_lines.mapped('account_id'))
            for account in accounts:
                for same_date_line in same_date_lines:
                    if same_date_line.account_id == account:
                        if same_date_line.debit:
                            matching_lines = [tx for tx in GLTransaction if
                                          tx["AccountID"] == account.name and tx['dTxDate'] == date and tx['fDebit'] != 0]
                            print(matching_lines)
                            if matching_lines:
                                print(matching_lines[0]['fDebit'])
                                matching_lines[0]['fDebit'] =+ same_date_line.debit
                            else:
                                data = {
                                'Description': same_date_line.name,
                                'Reference': "ODOO-" + str(date.month) + "-"+  str(same_date_line.move_id.id) + "-DR",
                                "fDebit": same_date_line.debit,
                                'fCredit': 0,
                                "AccountID": account.account_link,
                                "iProjectID": 0,
                                "dTxDate": str(date) + "T00:00:00",
                                # "UniqueID":"7783"
                                "UniqueID": str(date.day) + str(date.month)+ str(date.year) + str(same_date_line.id)
                            }
                                GLTransaction.append(data)
                        if same_date_line.credit:
                            matching_lines = [tx for tx in GLTransaction if
                                          tx["AccountID"] == account.name and tx['dTxDate'] == date and tx['fCredit'] != 0]
                            if matching_lines:
                                matching_lines[0]['fCredit'] =+ same_date_line.credit
                            else:
                                data = {
                                    'Description': same_date_line.name,
                                    'Reference': "ODOO-" + str(date.month) + "-"+  str(same_date_line.move_id.id) + "-CR",
                                    "fDebit": 0,
                                    'fCredit': same_date_line.credit,
                                    "AccountID": account.account_link,
                                    "iProjectID": 0,
                                    "dTxDate": str(date) + "T00:00:00",
                                    # "UniqueID":"7783"
                                "UniqueID": str(date.day) + str(date.month)+ str(date.year) + str(same_date_line.id)
                                }
                                GLTransaction.append(data)
        print(GLTransaction, 'GLTransaction')
        _logger.info("hi.....")
        _logger.info("GLTransaction %s" % GLTransaction)

        payload = json.dumps({
            'data': GLTransaction
        })
        print(payload)

        self.message_post( body=_('Payload: %s') % (payload, ))
        url = "http://169.254.1.2:83/api/gltransactions"
        response = requests.request("POST", url, headers=headers, data=payload)
        self.message_post( body=_('Response: %s') % (response.__dict__, ))
        _logger.info("response %s %s" % (response, response.__dict__))
        # [{'Account': 'Expenses',
        #   'Reference': 'Asset - 5 Years (copy): Depreciation', 'fDebit': 400.0,
        #   'fCredit': 0, 'AccountID': False, 'iProjectID': 0,
        #   'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'},
        #  {'Account': 'Current Assets',
        #   'Reference': 'Asset - 5 Years (copy): Depreciation', 'fDebit': 0,
        #   'fCredit': 400.0, 'AccountID': False, 'iProjectID': 0,
        #   'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'},
        #  {'Account': 'Expenses',
        #   'Reference': 'Asset - 5 Years (copy): Depreciation', 'fDebit': 386.67,
        #   'fCredit': 0, 'AccountID': False, 'iProjectID': 0,
        #   'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'},
        #  {'Account': 'Current Assets',
        #   'Reference': 'Asset - 5 Years (copy): Depreciation', 'fDebit': 0,
        #   'fCredit': 386.67, 'AccountID': False, 'iProjectID': 0,
        #   'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'}]
        # GLTransaction

    # data = [{'Account': 'Current Assets', 'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 0, 'fCredit': 100.0, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'},
    #         {'Account': 'Current Assets', 'Reference': 'Asset - 5 Years (copy): Depreciation', 'fDebit': 0, 'fCredit': 400.0, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'},
    #         {'Account': 'Expenses', 'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 100.0, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'},
    #         {'Account': 'Expenses', 'Reference': 'Asset - 5 Years (copy): Depreciation', 'fDebit': 400.0, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'},
    #         {'Account': 'Current Assets', 'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 0, 'fCredit': 26.67, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'},
    #         {'Account': 'Current Assets', 'Reference': 'Asset - 5 Years (copy): Depreciation', 'fDebit': 0, 'fCredit': 386.67, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'},
    #         {'Account': 'Expenses', 'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 26.67, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'},
    #         {'Account': 'Expenses', 'Reference': 'Asset - 5 Years (copy): Depreciation', 'fDebit': 386.67, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'}] GLTransaction
    # data = [
    #     {'Account': 'Expenses', 'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 100.0, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'},
    #     {'Account': 'Expenses', 'Reference': 'Asset - 5 Years (copy): Depreciation', 'fDebit': 400.0, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'},
    #     {'Account': 'Current Assets', 'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 0, 'fCredit': 100.0, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'},
    #     {'Account': 'Current Assets', 'Reference': 'Asset - 5 Years (copy): Depreciation', 'fDebit': 0, 'fCredit': 400.0, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 7, 31), 'UniqueID': '7783'},
    #     {'Account': 'Expenses', 'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 26.67, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'},
    #     {'Account': 'Expenses', 'Reference': 'Asset - 5 Years (copy): Depreciation', 'fDebit': 386.67, 'fCredit': 0, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'},
    #     {'Account': 'Current Assets', 'Reference': 'Asset - 5 Years: Depreciation', 'fDebit': 0, 'fCredit': 26.67, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'},
    #     {'Account': 'Current Assets', 'Reference': 'Asset - 5 Years (copy): Depreciation', 'fDebit': 0, 'fCredit': 386.67, 'AccountID': False, 'iProjectID': 0, 'dTxDate': datetime.date(2025, 6, 30), 'UniqueID': '7783'}] GLTransaction

