# -*- coding: utf-8 -*-
# Powered by Mindphin.
# © 2024 Mindphin. (<https://www.mindphin.com>).

from odoo.http import request
import time
from odoo import api, _, http
from odoo.exceptions import UserError
from odoo.addons.portal.controllers.portal import CustomerPortal
import base64
from datetime import datetime, date
import secrets


class PortalStatement(CustomerPortal):

    @http.route(['/my/customer/statement'], type='http', auth="public", website=True)
    def portal_my_customer_statement(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        today = date.today()
        if not date_begin:
            date_begin = date(today.year, 1, 1)
        else:
            date_begin = date_begin.strftime('%Y-%m-%d')
        if not date_end:
            date_end = date(today.year, 12, 31)
        else:
            date_end = date_end.strftime('%Y-%m-%d')
        journals = request.env['account.journal'].sudo().search([]).ids
        data = {'form': {'id': 6,
                         'date_from': str(date_begin),
                         'date_to': str(date_end),
                         'journal_ids': journals,
                         'target_move': 'posted',
                         'company_id': [request.env.company.id],
                         'used_context':
                         {'journal_ids': journals,
                          'state': 'posted',
                          'date_from': str(date_begin),
                          'date_to': str(date_end),
                          'strict_range': True,
                          'company_id': request.env.company.id,
                          'lang': 'en_US'
                          },
                         'result_selection': '',
                         'partner_ids': [request.env.user.partner_id.id],
                         'reconciled': False,
                         'amount_currency': False
                         },
                'report_type': 'pdf'
                }
        values = self._get_report_values(data=data)
        if values:
            credit_sum = sum(line['credit'] for line in values['lines']) + values['initial_balance']['credit']
            debit_sum = sum(line['debit'] for line in values['lines']) + values['initial_balance']['debit']
            balance_sum = debit_sum - credit_sum
            values.update({'sum_balance': {'credit_sum': credit_sum,
                                           'debit_sum': debit_sum,
                                           'balance_sum': balance_sum,
                                           }})
        return request.render("md_portal_customer_statement.portal_my_customer_statement", values)

    @http.route('/my/portal/customer/statement', type="json", auth="public")
    def portal_my_customer_statement_date(self, date_begin, date_end, print_report, **kw):
        today = date.today()
        value = {}
        if not date_begin:
            date_begin = date(today.year, 1, 1)
        else:
            date_begin = datetime.strptime(date_begin, '%d/%m/%Y').date()
            date_begin = date_begin.strftime('%Y-%m-%d')
        if not date_end:
            date_end = date(today.year, 12, 31)
        else:
            date_end = datetime.strptime(date_end, '%d/%m/%Y').date()
            date_end = date_end.strftime('%Y-%m-%d')
        journals = request.env['account.journal'].sudo().search([]).ids
        data = {'form': {'id': 6,
                         'date_from': str(date_begin),
                         'date_to': str(date_end),
                         'journal_ids': journals,
                         'target_move': 'posted',
                         'company_id': [request.env.company.id],
                         'used_context':
                         {'journal_ids': journals,
                          'state': 'posted',
                          'date_from': str(date_begin),
                          'date_to': str(date_end),
                          'strict_range': True,
                          'company_id': request.env.company.id,
                          'lang': 'en_US'
                          },
                         'result_selection': '',
                         'partner_ids': [request.env.user.partner_id.id],
                         'reconciled': False,
                         'amount_currency': False
                         },
                'report_type': 'pdf'
                }
        values = self._get_report_values(data=data)
        if values:
            credit_sum = sum(line['credit'] for line in values['lines']) + values['initial_balance']['credit']
            debit_sum = sum(line['debit'] for line in values['lines']) + values['initial_balance']['debit']
            balance_sum = debit_sum - credit_sum
            values.update({'sum_balance': {'credit_sum': credit_sum,
                                           'debit_sum': debit_sum,
                                           'balance_sum': balance_sum,
                                           }})
        if print_report:
            report = request.env['ir.actions.report'].sudo()._render_qweb_pdf('md_portal_customer_statement.md_report_partnerledger', 1, data=values)
            filename = "Statement_report" + '.pdf'
            attachment = request.env['ir.attachment'].sudo().create({'name': filename,
                                                                     'type': 'binary',
                                                                     'datas': base64.b64encode(report[0]),
                                                                     'res_model': 'res.partner',
                                                                     'res_id': request.env.user.partner_id.id,
                                                                     'mimetype': 'application/x-pdf'
                                                                     })

            attachment.access_token = secrets.token_urlsafe(32)
            return {'attachmentID': attachment.id, 'access_token': attachment.access_token}
        else:
            value['updated_statement_report'] = request.env['ir.ui.view'].sudo()._render_template("md_portal_customer_statement.portal_statement_lines", values)
            return value

    def _lines(self, data, partner):
        full_account = []
        currency = request.env['res.currency']
        query_get_data = request.env['account.move.line'].sudo().with_context(data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        query = """
            SELECT "account_move_line".id, "account_move_line".date, j.code, acc.name->>'en_US' as a_name, "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit, "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code
            FROM """ + query_get_data[0] + """
            LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
            LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
            LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
            LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
            WHERE "account_move_line".partner_id = %s
                AND m.state IN %s
                AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + """
                ORDER BY "account_move_line".date"""
        request.env.cr.execute(query, tuple(params))
        res = request.env.cr.dictfetchall()
        sums = self.get_initialbalance(data=data, partner=partner)['balance']
        # lang = request.env['res.lang']
        # lang_id = lang.sudo()._lang_get(lang_code)
        # date_format = lang_id.date_format
        for r in res:
            r['date'] = r['date']
            r['displayed_name'] = '-'.join(
                r[field_name] for field_name in ('move_name', 'ref', 'name')
                if r[field_name] not in (None, '', '/')
            )
            sums += r['debit'] - r['credit']
            r['progress'] = sums
            r['currency_id'] = currency.sudo().browse(r.get('currency_id'))
            full_account.append(r)
        return full_account

    def get_initialbalance(self, partner, data):
        init_data = data
        init_data['form']['used_context'].update({'initial_bal': True})
        if 'date_to' in init_data['form']['used_context'].keys():
            init_data['form']['used_context'].pop('date_to')
        query_get_data = request.env['account.move.line'].sudo().with_context(init_data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if init_data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        params = [partner.id, tuple(init_data['computed']['move_state']), tuple(init_data['computed']['account_ids'])] + query_get_data[2]
        query = """
            SELECT "account_move_line".id, "account_move_line".date, j.code, acc.name->>'en_US' as a_name, "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit, "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code
            FROM """ + query_get_data[0] + """
            LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
            LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
            LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
            LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
            WHERE "account_move_line".partner_id = %s
                AND m.state IN %s
                AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + """
                ORDER BY "account_move_line".date"""
        request.env.cr.execute(query, tuple(params))
        res = request.env.cr.dictfetchall()
        credit_sum = sum(line['credit'] for line in res)
        debit_sum = sum(line['debit'] for line in res)
        balance_sum = debit_sum - credit_sum
        return {
            'debit': debit_sum,
            'credit': credit_sum,
            'balance': balance_sum,
        }

    @api.model
    def _get_report_values(self, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        data['computed'] = {}

        obj_partner = request.env['res.partner']
        query_get_data = request.env['account.move.line'].sudo().with_context(data['form'].get('used_context', {}))._query_get()
        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = data['form'].get('result_selection', 'customer')
        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['liability_payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['asset_receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['asset_receivable', 'liability_payable']

        request.env.cr.execute("""
            SELECT a.id
            FROM account_account a
            WHERE a.account_type IN %s
            AND NOT a.deprecated""", (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in request.env.cr.fetchall()]
        params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        query = """
            SELECT DISTINCT "account_move_line".partner_id
            FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
            WHERE "account_move_line".partner_id IS NOT NULL
                AND "account_move_line".account_id = account.id
                AND am.id = "account_move_line".move_id
                AND am.state IN %s
                AND "account_move_line".account_id IN %s
                AND NOT account.deprecated
                AND """ + query_get_data[1]
        request.env.cr.execute(query, tuple(params))
        if data['form']['partner_ids']:
            partner_ids = data['form']['partner_ids']
        else:
            partner_ids = [res['partner_id'] for res in
                           request.env.cr.dictfetchall()]
        partners = obj_partner.sudo().browse(partner_ids)
        partners = sorted(partners, key=lambda x: (x.ref or '', x.name or ''))
        return {
            'doc_ids': partner_ids,
            'doc_model': request.env['res.partner'],
            'data': data,
            'partner': request.env['res.partner'].sudo().browse(data['form']['partner_ids']),
            'docs': partners,
            'date_from': data['form']['date_from'],
            'date_to': data['form']['date_to'],
            'time': time,
            'lines': self._lines(data=data, partner=request.env['res.partner'].sudo().browse(data['form']['partner_ids'])),
            'initial_balance': self.get_initialbalance(data=data, partner=request.env['res.partner'].sudo().browse(data['form']['partner_ids']))
        }
