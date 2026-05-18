import io

import xlsxwriter
import base64
from odoo import api, fields, models
from werkzeug import urls
from odoo.tools import date_utils
from odoo.tools.safe_eval import json
from bs4 import BeautifulSoup

class OtherDocuments(models.Model):
    _name = 'other.documents'
    _description = "Other Documents"
    _rec_name = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([('preparer', 'Preparer'),
                              ('first_reviewer', 'First Reviewer'),
                              ('second_reviewer', 'Second Reviewer'),
                              ('approved', 'Approved'),
                              ('reverted', 'Reverted'),
                              ('rejected', 'Rejected')],
                             default="preparer", string="State", tracking=True)
    name = fields.Char(string="Name", help="Name", tracking=True)
    requirements = fields.Html(string="Requirements", required=True,
                               help="Requirements")
    record_work_done = fields.Html(string="Work done", required=True,
                                   help="Record of work done")
    conclusion = fields.Html(string="Conclusion", required=True,
                             help="Conclusion")
    document_ids = fields.Many2many('ir.attachment',string="Upload Documents")
    user_preparer_ids = fields.Many2one('res.users', required=True,
                                        string="Preparer", tracking=True,
                                        default=lambda self: self.env.user)
    user_reviewer_1_ids = fields.Many2one('res.users', string="First Reviewer",
                                          tracking=True)
    user_reviewer_2_ids = fields.Many2one('res.users',
                                          string="Second Reviewer",
                                          tracking=True)
    user_approver_ids = fields.Many2one('res.users', string="Approver",
                                        tracking=True)
    sequence_no = fields.Char(string='W/P Reference', readonly=True,
                              copy=False)

    previous_state = fields.Selection([
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer')])
    feedback = fields.Char(string="Audit Reverts/ Review Notes", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sequence_code = 'other.documents'
            vals['sequence_no'] = self.env['ir.sequence'].next_by_code(
                sequence_code)
        res = super(OtherDocuments, self).create(vals_list)
        return res
    #
    # @api.model
    # def create(self, vals):
    #     vals['sequence_no'] = self.env['ir.sequence'].next_by_code('other.documents')
    #     res = super(OtherDocuments, self).create(vals)
    #     return res

    def get_form_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url, 'web#id=%s&model=other.documents&view_type=form' % self.id)
        return Urls

    def action_review(self):
        """method for review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_other_review')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'first_reviewer'

    def action_2nd_review(self):
        """Second Review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_other_sec_review')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'second_reviewer'

    def action_approve(self):
        """Method for approve"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_other_approve')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'approved'

    def action_mark_discrepancy(self):
        """Action refuse the request"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_other_rejected')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'rejected'

    def action_send_back_review(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_other_reverted')
        mail_template.send_mail(self.id, force_send=True)
        return {
            'name': 'Audit Reverts/ Review Notes',
            'type': 'ir.actions.act_window',
            'res_model': 'internal.audit.revert.wizard',
            'context': {
                'default_other_documents_id': self.id
            },
            'view_mode': 'form',
            'target': 'new',
        }

    def action_view_records(self):
        """Method for view records"""
        return {
            'name': 'Audit Reverts/ Review Notes',
            'type': 'ir.actions.act_window',
            'res_model': 'audit.revert',
            'domain': [('res_id', '=', self.id), ('res_model', '=', self._name)],
            'view_mode': 'list,form',
            'target': 'current',
        }

    def action_update(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_other_review')
        mail_template.send_mail(self.id, force_send=True)
        self.state = self.previous_state

    def action_send_back_new(self):
        """Action send back to new"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_other_send_bak')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'preparer'

    def action_excel_report(self):
        """Print excel reports"""
        plan = self.id
        data = {
            'model_id': self.id,
            'method': plan
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': self._name,
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Other Documents',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        def clean_html(html_text):
            """Removes HTML tags and returns plain text."""
            if not html_text:
                return "Unknown"
            return BeautifulSoup(html_text, "html.parser").get_text(separator=" ").strip()
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        method = self.env[self._name].browse(int(data['method']))
        cell_format = workbook.add_format({'font_size': '10px', 'align': 'left',
                                   'valign': 'vcenter', 'text_wrap': True})
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px'})
        small_head = workbook.add_format(
            {'align': 'center', 'font_size': '11px'})
        txt = workbook.add_format({'font_size': '10px', 'align': 'center',
                                   'valign': 'vcenter', 'text_wrap': True})
        date = workbook.add_format({'num_format': 'd-m-yyyy'})
        sheet.set_column(1, 11, 12, txt)
        if self.env.company.logo:
            image_data = io.BytesIO(base64.b64decode(self.env.company.logo))
            sheet.insert_image('M3', "image.png", {
                'image_data': image_data,
                'x_scale': 0.5,  # Scale image if needed
                'y_scale': 0.5,
                'positioning': 1  # Move and resize with cells
            })
        mom_requirements = clean_html(
            method.requirements) if method.requirements else ' '
        mom_record_work_done = clean_html(
            method.record_work_done) if method.record_work_done else ' '
        mom_conclusion = clean_html(
            method.conclusion) if method.conclusion else ' '
        sheet.write('H1', "Report Date", txt)
        sheet.write('I1', fields.Date.today(), date)
        sheet.merge_range('E2:L3', 'Other Documents', head)
        sheet.write('D7', "Name : ", small_head)
        sheet.merge_range('E7:F7', method.name, txt)
        sheet.write('D9', "W/P Reference : ", small_head)
        sheet.merge_range('E9:F9', method.sequence_no, txt)
        sheet.write('D11', "Requirements: ", small_head)
        sheet.merge_range('E11:F11', mom_requirements, txt)

        sheet.merge_range('I7:J7', "Preparer : ", small_head)
        sheet.merge_range('K7:L7', method.user_preparer_ids.name, txt)
        sheet.merge_range('I9:J9', "First Reviewer : ", small_head)
        sheet.merge_range('K9:L9', method.user_reviewer_1_ids.name, txt)
        sheet.merge_range('I11:J11', "Second Reviewer : ", small_head)
        sheet.merge_range('K11:L11', method.user_reviewer_2_ids.name, txt)
        sheet.merge_range('I13:J13', "Approver : ", small_head)
        sheet.merge_range('K13:L13', method.user_approver_ids.name, txt)

        sheet.merge_range('D18:E18', "Work Done : ", small_head)
        sheet.merge_range('G18:J20', mom_record_work_done, txt)

        sheet.merge_range('D22:E22', "Conclusion : ", small_head)
        sheet.merge_range('G22:J24', mom_conclusion, txt)

        reverts = self.env['audit.revert'].search(
            [('res_id', '=', method.id), ('res_model', '=', method._name)])
        if method.feedback:
            sheet.write('B24', 'Revert Comments', small_head)
            sheet.merge_range('C24:G24', method.feedback, txt)
        if reverts:
            sheet.write('B26', 'Revert Name', small_head)
            sheet.write('C26', 'Created Date', small_head)
            sheet.write('D26', 'Review Comments', small_head)
            sheet.write('E26', 'Audit Proposal', small_head)
            sheet.write('F26', 'State', small_head)
            row = 26
            col = 1
            for revert in reverts:
                sheet.write(row, col, revert.name, txt)
                sheet.write(row, col + 1, revert.date, date)
                sheet.write(row, col + 2, revert.comments, txt)
                sheet.write(row, col + 3, revert.audit_findings, txt)
                sheet.write(row, col + 4, revert.state, txt)
                row = + 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
