from odoo import models, fields, api
from werkzeug import urls
from datetime import datetime, timedelta
import io
import json
from odoo.tools import json_default
import xlsxwriter


class FuelCardTransaction(models.Model):
    _name = 'fuel.card.transaction'
    _description = 'Fuel Card Transaction'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Transaction Reference')
    card_id = fields.Many2one('fuel.card',
                              string='Fuel Card being issue/returned')
    driver_id = fields.Many2one('hr.employee',
                                string='Driver receiving/returning the card')
    vehicle_id = fields.Many2one('fleet.vehicle',
                                 string='Vehicle assigned(optional)')
    date_issued = fields.Datetime(string='Date and Time issue')
    issued_by_id = fields.Many2one('res.users',
                                   string='User who issued the card')
    date_returned = fields.Datetime('Date and time of return')
    returned_to_id = fields.Many2one('res.users',
                                     string='User who received the returned card')
    status = fields.Selection([('issued', 'Issued'), ('returned', 'Returned')])
    notes = fields.Html(string='Additional notes')

    def get_form_fuel_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=fuel.card.transaction&view_type=form' % self.id)
        return Urls

    def send_mail(self):
        overdue_threshold = datetime.now() - timedelta(days=7)
        overdue_cards = self.search([
            ('status', '=', 'issued'),
            ('date_issued', '<=', overdue_threshold),
            ('date_returned', '=', False)
        ])
        fleet_managers = self.env.ref('fuel_card_register.group_fleet_manager',
                                      raise_if_not_found=False)
        if fleet_managers and fleet_managers.users:
            mail_template = self.env.ref(
                'fuel_card_register.mail_template_fuel_card').with_context(
                lang=self.env.user.lang)
            for rec in overdue_cards:
                for user in fleet_managers.users:
                    mail_template.with_context(
                        lang=user.lang,
                        user=user,
                        overdue_card=rec
                    ).send_mail(rec.id, force_send=True)

    @api.onchange('date_issued', 'date_returned')
    def _onchange_status(self):
        if self.date_returned:
            self.status = 'returned'
        elif self.date_issued:
            self.status = 'issued'
        else:
            self.status = False

    def action_download_report(self):
        data = { }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'fuel.card.transaction',
                     'options': json.dumps(data,
                                           default=json_default),
                     'output_format': 'xlsx_reports',
                     'report_name': 'Issued Fuel Card Report',
                     },
            'report_type': 'xlsx_reports',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format(
            {'font_size': '12px', 'align': 'center'})
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px'})
        datetime_format = workbook.add_format(
                    {'num_format': 'yyyy-mm-dd hh:mm:ss'})
        wrap_format = workbook.add_format({'text_wrap': True})
        txt = workbook.add_format({'font_size': '10px', 'align': 'center'})
        transactions = self.search([('status', '=', 'issued')])
        sheet.merge_range('B2:I3', 'Issued Fuel Cards', head)
        headers = [
            'Transaction Reference',
            'Fuel Card',
            'Driver',
            'Vehicle',
            'Date Issued',
            'Issued By',
            'Date Returned',
            'Returned To',
            'Status',
            'Notes',
        ]
        for col_num, header in enumerate(headers):
            sheet.write(8, col_num, header, cell_format)
        for row_num, txn in enumerate(transactions, start=9):
            sheet.write(row_num, 0, txn.name or '')
            sheet.write(row_num, 1, txn.card_id.name or '')
            sheet.write(row_num, 2, txn.driver_id.name or '')
            sheet.write(row_num, 3, txn.vehicle_id.name or '')
            if txn.date_issued:
                sheet.write_datetime(row_num, 4, txn.date_issued,
                                     datetime_format)
            else:
                sheet.write(row_num, 4, '')
            sheet.write(row_num, 5, txn.issued_by_id.name or '', txt)
            if txn.date_returned:
                sheet.write_datetime(row_num, 6, txn.date_returned,
                                     datetime_format)
            else:
                sheet.write(row_num, 6, '')
            sheet.write(row_num, 7, txn.returned_to_id.name or '', txt)
            sheet.write(row_num, 8,
                        dict(txn._fields['status'].selection).get(
                            txn.status, '') or '', txt)
            sheet.write(row_num, 9, txn.notes or '', wrap_format)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()