import base64
import io
import xlsxwriter
from werkzeug import urls
from odoo.tools import date_utils
from odoo.tools.safe_eval import json
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from bs4 import BeautifulSoup


class FinancialStatementsPerformanceReport(models.Model):
    """Financial Statements And Performance Report"""
    _name = 'financial.statement'
    _description = "Financial Statements And Performance Report"
    _rec_name = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([('draft','Draft'),('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected')],
                             default="draft", string="State")
    attachment_ids = fields.Many2many('ir.attachment',
                            string="Upload Annual Financial Statements")
    interim_attachment_ids = fields.Many2many('ir.attachment',
                                                  'interim_attachment_rel',
                                      string="Upload Interim Financial Statements")
    performance_attachment_ids = fields.Many2many('ir.attachment',
                                                  'performance_attachment_rel',
                                      string="Upload Performance Planning Documents")
    name = fields.Char(string="Name", help="Name")
    requirements = fields.Html(string="Requirements", required=True,
                               help="Requirements")
    record_work_done = fields.Html(string="Work done", required=True,
                                   help="Record of work done")
    conclusion = fields.Html(string="Conclusion", required=True,
                             help="Conclusion")
    # audit_id = fields.Many2one('audit.request', string="Audit")
    team_id = fields.Many2one('hr.department', string="Team")
    # role_id = fields.Many2one('audit.role', string="Roles")
    user_id = fields.Many2one('res.users', tracking=True,
                              string="Responsible User")
    financial_statement_tracking_ids = fields.One2many('financial.statement.tracking', 'financial_statement_tracking_id', string='Tracking')
    # comment_ids = fields.One2many('audit.comments', 'financial_statement_id',
    #                               tracking=True, string="Comments")
    document_ids = fields.Many2many('ir.attachment', 'documents_attachment_rel', string="Upload Documents")
    user_ids = fields.Many2many('res.users', string="Users",
                                compute="_compute_user_ids")
    user_preparer_ids = fields.Many2one('res.users',required=True,
                                         string="Preparer", tracking=True,
                                         default=lambda self: self.env.user)
    user_reviewer_1_ids = fields.Many2one('res.users',string="First Reviewer",
                                           tracking=True)
    user_reviewer_2_ids = fields.Many2one('res.users', string="Second Reviewer",
                                           tracking=True)
    user_approver_ids = fields.Many2one('res.users', string="Approver", tracking=True)
    sequence_no = fields.Char(string='W/P Reference', readonly=True,
                              copy=False)
    previous_state = fields.Selection([
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer')])
    feedback = fields.Char(string="Audit Reverts/ Review Notes", tracking=True)

    @api.depends('team_id')
    def _compute_user_ids(self):
        """Compute User IDs for adding domains"""
        for rec in self:
            user = []
            if rec.team_id:
                user = rec.team_id.employee_ids.mapped('user_id').ids
            rec.user_ids = user

    def create(self, vals):
        # Create the record
        vals['sequence_no'] = self.env['ir.sequence'].next_by_code('financial.statement')
        record = super(FinancialStatementsPerformanceReport, self).create(vals)
        # Automatically create a document record
        record._create_document_records()
        return record

    def write(self, vals):
        # Update the record
        res = super(FinancialStatementsPerformanceReport, self).write(vals)
        # Automatically create a document record
        self._create_document_records()
        return res

    def _create_document_records(self):
        document = self.env['documents.document']
        for record in self:
            for attachment in record.document_ids:
                document.create({
                    'name': attachment.name,
                    'attachment_id': attachment.id,
                    'folder_id': 1,
                    # Specify the folder ID or logic to determine the correct folder
                    'owner_id': self.env.user.id,
                    # Optional: assign the current user as the owner
                })


    def get_list_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=financial.statement&view_type=list' % self.id)
        return Urls

    def action_review(self):
        """method for review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_financial_statement_review')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.state
        # Concatenate all comments into a single string
        # comments = "\n".join(self.comment_ids.mapped('name'))
        self.state = 'preparer'
        for record in self:
            # Add a new line in the tracking
            self.env['financial.statement.tracking'].create({
                'financial_statement_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': record.state,
                'comment': 'First Review',
                'date': fields.Datetime.now(),
            })

    def action_update(self):
        previous_state = self.state
        self.state = self.previous_state
        for record in self:
            self.env['financial.statement.tracking'].create({
                'financial_statement_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': record.state,
                'comment': 'Updated',
                'date': fields.Datetime.now(),
            })

    def action_2nd_review(self):
        """Second Review"""
        previous_state = self.state
        self.state = 'second_reviewer'
        for record in self:
            self.env['financial.statement.tracking'].create({
                'financial_statement_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': record.state,
                'comment': 'Second Review',
                'date': fields.Datetime.now(),
            })
        mail_template = self.env.ref(
            'internal_audit_management.email_template_financial_statement_reviewed')
        mail_template.send_mail(self.id, force_send=True)

    def action_approve(self):
        """Method for approve"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_financial_statement_approve')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.state
        self.state = 'approved'
        for record in self:
            # Add a new line in the tracking
            self.env['financial.statement.tracking'].create({
                'financial_statement_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': record.state,
                'comment': 'Approved',
                'date': fields.Datetime.now(),
            })

    def action_mark_discrepancy(self):
        """Action refuse the request"""
        # self.state = 'refuse'
        mail_template = self.env.ref(
            'internal_audit_management.email_template_financial_statement_refuse')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.state
        self.state = 'rejected'
        for record in self:
            # Add a new line in the tracking
            self.env['financial.statement.tracking'].create({
                'financial_statement_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'rejected',
                'comment': 'Rejected',
                'date': fields.Datetime.now(),
            })

    def action_send_back_review(self):
        """Action SEND BACK TO REVIEW"""
        return {
            'name': 'Audit Reverts/ Review Notes',
            'type': 'ir.actions.act_window',
            'res_model': 'internal.audit.revert.wizard',
            'context': {
                'default_financial_statement_id': self.id
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

    def action_send_back_new(self):
        """Action send back to newt"""
        # self.state = 'new'
        mail_template = self.env.ref(
            'internal_audit_management.email_template_financial_statement_new')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.state
        self.state = 'preparer'
        for record in self:
            # Add a new line in the tracking
            self.env['financial.statement.tracking'].create({
                'financial_statement_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': record.state,
                'comment': 'New',
                'date': fields.Datetime.now(),
            })

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
                     'report_name': 'Audit Standards',
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
        cell_format = workbook.add_format(
            {'font_size': '12px', 'align': 'center'})
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
        sheet.merge_range('E2:L3', method.name, head)
        sheet.write('D9', "W/P Reference : ", small_head)
        sheet.merge_range('E9:F9', method.sequence_no, txt)
        sheet.write('D11', "Requirements : ", small_head)
        sheet.merge_range('E11:F11', mom_requirements, txt)
        sheet.merge_range('D18:E18', "Work Done : ", small_head)
        sheet.merge_range('G18:J20', mom_record_work_done, txt)
        sheet.merge_range('D22:E22', "Conclusion : ", small_head)
        sheet.merge_range('G22:J24', mom_conclusion, txt)

        sheet.merge_range('I7:J7', "Preparer : ", small_head)
        sheet.merge_range('K7:L7', method.user_preparer_ids.name, txt)
        sheet.merge_range('I9:J9', "First Reviewer : ", small_head)
        sheet.merge_range('K9:L9', method.user_reviewer_1_ids.name, txt)
        sheet.merge_range('I11:J11', "Second Reviewer : ", small_head)
        sheet.merge_range('K11:L11', method.user_reviewer_2_ids.name, txt)
        sheet.merge_range('I13:J13', "Approver : ", small_head)
        sheet.merge_range('K13:L13', method.user_approver_ids.name, txt)

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
