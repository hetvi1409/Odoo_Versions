import base64
import io
import json
import xlsxwriter
from odoo.tools import date_utils
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from datetime import datetime, date


class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

    state = fields.Selection(selection_add=[
        ('waiting_finance_manager_approval',
         'Waiting Finance Manager Approval'),
        ('finance_manager_approved',
         'Finance Manager Approved'),
        ('finance_manager_rejected',
         'Finance Manager Rejected'),
        ('ceo_approved',
         'CEO Approved'),
        ('cancel',)],
        ondelete={
            'waiting_finance_manager_approval': 'cascade',
            'finance_manager_approved': 'cascade',
            'finance_manager_rejected': 'cascade',
            'ceo_approved': 'cascade'
        })
    reason_for_reject = fields.Text('Reason for Rejection')

    def request_finance_approve_budget(self):
        """
        Department user sent request to finance manager for the approval
        """
        self.write({'state': 'waiting_finance_manager_approval'})

    def action_finance_manager_approve(self):
        self.write({'state': 'finance_manager_approved'})

    def ceo_approve_budget(self):
        self.write({'state': 'ceo_approved'})

    def action_finance_manager_reject(self):
        self.ensure_one()
        if not self.reason_for_reject:
            raise ValidationError(
                _('Please add the Reason for Rejection'))
        # Here you can add custom logic to handle the rejection, such as sending notifications or updating records.
        # You should also set the state to 'finance_manager_rejected' and add the reason for rejection.
        self.write({
            'state': 'finance_manager_rejected',
            'reason_for_reject': "Your Reason for Rejection"
            # You can replace with the actual reason
        })

    def budget_capture(self):
        today = datetime.now()
        if today.month == 10 and today.day == 15:  # Assuming mid-October is on the 15th day
            # Code to send your notification here
            mail_content = _('Hello, it is mid-October!')
            main_content = {
                'subject': _('Mid-October Notification'),
                'body_html': mail_content,
            }
            mail_id = self.env['mail.mail'].sudo().create(main_content)
            mail_id.mail_message_id.body = mail_content
            mail_id.sudo().send()

    def export_budget_line(self):
        # self._check_dates(self.start_date, self.end_date)
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['form'] = self.read()[0]
        # datas = self
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return {
            'type': 'ir.actions.report',
            'data': {
                'model': 'crossovered.budget',
                'options': json.dumps(datas,
                                      default=date_utils.json_default),
                'output_format': 'budget_xlsx',
                'report_name': 'BUDGET '
            },
            'report_type': 'budget_xlsx',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet("")
        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True,
             'top': True,
             'align': 'center', 'bold': True})
        format3 = workbook.add_format(
            {'bottom': True, 'top': True, 'font_size': 12})
        font_size_8 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True,
             'font_size': 8})
        justify = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True,
             'font_size': 12})
        format3.set_align('center')
        font_size_8.set_align('center')
        justify.set_align('justify')
        format1.set_align('center')
        boldc = workbook.add_format({'bold': True, 'align': 'center'})
        boldl = workbook.add_format({
            'font_size': 12,
            'bottom': True,
            'right': True,
            'left': True,
            'top': True,
            'align': 'center',
            'bold': True,
            'bg_color': '#D3D3D3'  # Grey background color
        })
        # boldl = workbook.add_format({'bold': True, 'align': 'left'})
        left = workbook.add_format({'align': 'left'})
        worksheet.merge_range('A2:I2', 'BUDGET REPORT', boldc)

        row = 6
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 30)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 30)
        worksheet.set_column('H:H', 30)
        worksheet.write('A%s' % row, 'Core Entity', boldl)
        worksheet.write('B%s' % row, 'Dept No', boldl)
        worksheet.write('C%s' % row, 'Dept Description', boldl)
        worksheet.write('D%s' % row, 'Cost Center No', boldl)
        worksheet.write('E%s' % row, 'Cost Center Description', boldl)
        worksheet.write('F%s' % row, 'Item No', boldl)
        worksheet.write('G%s' % row, 'Type Item Description', boldl)
        worksheet.write('H%s' % row, 'mSCOA Rev and Exp Category', boldl)
        new_row = 7
        for rec in self.browse(data['ids']):
            worksheet.write('A%s' % new_row,
                            rec.user_id.name if rec.user_id.name else '')
            # worksheet.write('B%s' % new_row,
            #                 rec.user_id if rec.user_id else '')
            # worksheet.write('C%s' % new_row,
            #                 rec.user_id if rec.user_id else '')
            # worksheet.write('D%s' % new_row, rec.user_id if rec.user_id else '')
            # worksheet.write('E%s' % new_row,
            #                 rec.user_id if rec.user_id else '')
            # worksheet.write('F%s' % new_row, rec.user_id if rec.user_id else '')
            # worksheet.write('G%s' % new_row, rec.user_id if rec.user_id else '')
            # worksheet.write('H%s' % new_row,
            #                 rec.user_id if rec.user_id else '')
            new_row += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

    def send_mail_export_budget_line(self):
        report = self.env.ref(
            'budget_update.action_report_send_sample_xlsx')

        for rec in self:
            data_record = base64.b64encode(
                self.env['ir.actions.report'].sudo()._render_xlsx(report,
                                                                  [rec.id],
                                                                  data=None)[0]
            )
            ir_values = {
                'name': 'Sample Excel',
                'type': 'binary',
                'datas': data_record,
                'store_fname': data_record,
                'mimetype': 'application/vnd.ms-excel',
            }
            attachment = self.env['ir.attachment'].sudo().create(ir_values)
            if attachment:
                email_template = self.env.ref(
                    'budget_update.budget_email_template')
                if rec.user_id.partner_id.email:
                    email = rec.user_id.partner_id.email
                else:
                    email = 'admin@example.com'
                if email_template and email:
                    email_values = {
                        'email_to': email,
                        'email_cc': False,
                        'scheduled_date': False,
                        'recipient_ids': [],
                        'partner_ids': [],
                        'auto_delete': True,
                    }
                    email_template.attachment_ids = [(4, attachment.id)]
                    email_template.with_context(partner=rec.user_id.partner_id,
                                                inv=rec).send_mail(
                        rec.id, email_values=email_values, force_send=True)
                    email_template.attachment_ids = [(5, 0, 0)]


