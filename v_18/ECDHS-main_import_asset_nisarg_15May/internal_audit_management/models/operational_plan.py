from dateutil.relativedelta import relativedelta
from odoo.tools.json import json_default
from odoo import api, fields, models,_
from werkzeug import urls
import base64
import io
import xlsxwriter
from odoo.tools import date_utils
from odoo.tools.safe_eval import json
from datetime import date



class OperationalPlan(models.Model):
    _name = 'operational.plan'
    _description = "Internal Audit Operational Plan"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    rolling_plan_id = fields.Many2one('rolling.plan',
                                      string='Internal Audit Rolling Plan: 1 Year',
                                      ondelete='cascade')
    plan_id = fields.Many2one('internal.audit.plan',
                              string="Internal Audit Rolling Plan: 3 Year")
    sequence_number = fields.Char(string="ARP Number", related="rolling_plan_id.sequence_no")
    user_id = fields.Many2one('res.users', string="Manager Responsible",
                              default=lambda self: self.env.user)
    # period = fields.Selection(
    #     [('first', 'Q1'), ('second', 'Q2'),
    #      ('third', 'Q3'), ('fourth', 'Q4')],
    #     string="Period", required=True, default='first',
    #     help="Period of the AOP (e.g., 2024, 2025).")
    q1_allocated_time = fields.Float(string="Q1 Allocated Time",
                                     )
    q2_allocated_time = fields.Float(string="Q2 Allocated Time",)
    q3_allocated_time = fields.Float(string="Q3 Allocated Time",)
    q4_allocated_time = fields.Float(string="Q4 Allocated Time",)
    check_allocated_time = fields.Float(string="Check Allocated Time",
                                        compute="_compute_check_allocated_time",
                                        store=True)
    assurance_consulting = fields.Selection([('Assurance', 'Assurance'),
                                             ('Consulting', 'Consulting'),('limited_assurance', 'Limited Assurance'),('limited_consulting', 'Limited Consulting')],
                                            string="Type of audit")
    # partner_id = fields.Many2one('res.company', string='Municipality',related="plan_id.company_id")
    department_ids = fields.Many2many('hr.department',
                                    string="Department",
                                    help="Reference to the department being audited",)
    entity_type_id = fields.Many2one('entity.type', string='Section', )
    scope_of_work = fields.Text(string="Scope of Work",
                                help="Detailed scope of the audit work")
    team_member_ids = fields.Many2many('hr.employee', string='Team Members',
                                       compute="_compute_user_ids")
    # user_time_estimation_ids = fields.One2many('audit.time.estimation',
    #                                            'operation_plan_id',
    #                                            string="Audit Time Estimation")
    start_date = fields.Date(string='Planned Date')
    date_end = fields.Date(string="End Date")
    description = fields.Text(string='Motivation/Link to Description')
    user_ids = fields.Many2many('res.users', string="Users", compute="_compute_user_ids")
    tag_ids = fields.Many2many('project.tags', string='Tags')
    user_preparer_ids = fields.Many2one('res.users',
                                         string="Preparer", tracking=True)
    user_reviewer_1_ids = fields.Many2one('res.users',
                                           string="First Reviewer",
                                           tracking=True)
    user_reviewer_2_ids = fields.Many2one('res.users',
                                           string="Second Reviewer",tracking=True)
    user_approver_ids = fields.Many2one('res.users',
                                         string="Approver", tracking=True)
    stages = fields.Selection([
        ('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'),
    ], 'State', default='preparer', tracking=True, copy=False)
    state = fields.Selection([('in_preparer', 'In Preparer'),
                              ('01_in_progress', 'In Progress'),
                              ('02_changes_requested', 'Changes Requested'),
                              ('03_approved', 'Approved'), ('1_done', 'Done'),
                              ('1_canceled', 'Canceled'),
                              ('04_waiting_normal', 'Waiting')],
                             string='State')
    # timesheet_ids = fields.One2many('account.analytic.line', 'operational_plan_timesheet_id',
    #                                 string="Timesheet")
    operational_plan_tracking_ids = fields.One2many(
        'operational.plan.tracking', 'operational_plan_tracking_id',
        string='Tracking')
    project_ids = fields.One2many('project.project', 'aop_id', string='Project')
    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Upload Internal Audit Plan")
    folder_id = fields.Many2one('documents.document', string="Folder", domain=[('type', '=', 'folder')])
    feedback = fields.Char(string="Audit Reverts/ Review Notes", tracking=True)

    risk_priority_rating = fields.Selection([('low', 'Low'),
                                             ('low-medium', 'Low Medium'),
                                             ('medium', 'Medium'),
                                             ('medium-high', 'Medium High'),
                                             ('high', 'High')],
                                            string="Risk Priority Rating",
                                            tracking=True,)
    risk_description = fields.Char(string="Risk Description")
    project_number = fields.Char(string="Project Number")

    @api.model_create_multi
    def create(self, vals_list):
        records = super(OperationalPlan, self).create(vals_list)
        for record, vals in zip(records, vals_list):
            # Ensure folder is created
            if not record.folder_id:
                folder = record._create_folder(record.name)
                record.folder_id = folder.id
            # Sync documents if any
            if 'attachment_ids' in vals:
                record._sync_documents(vals['attachment_ids'])
        return records

    def write(self, vals):
        existing_attachments = self.attachment_ids
        res = super(OperationalPlan, self).write(vals)
        if not self.folder_id:
            folder = self._create_folder(self.name)
            self.folder_id = folder.id
        if 'attachment_ids' in vals:
            new_attachments = self.attachment_ids
            removed_attachments = existing_attachments - new_attachments
            self._sync_documents(vals['attachment_ids'])
            self._remove_documents(removed_attachments.ids)
        return res

    def _create_folder(self, name):
        """Create a folder in documents.folder if it doesn't exist."""
        folder = self.env['documents.document']
        documents_folder_id = self.env.ref(
            'internal_audit_management.documents_aop_folder').id
        folder = folder.search([('name', '=', name), ('type', '=', 'folder'),
                                ('folder_id', '=', documents_folder_id)],
                               limit=1)
        if not folder:
            folder = folder.create({'name': name,
                                    'type': 'folder',
                                    'folder_id': documents_folder_id})
        return folder

    def _sync_documents(self, attachment_ids):
        """Synchronize attachments with documents.document."""
        document = self.env['documents.document']
        if attachment_ids:
            for attachment_id in attachment_ids:
                attachment = self.env['ir.attachment'].browse(
                    attachment_id[1])
                if not document.search([('attachment_id', '=', attachment.id)]):
                    document.create({
                        'name': attachment.name,
                        'attachment_id': attachment.id,
                        'folder_id': self.folder_id.id if self.folder_id else
                        self.env['documents.folder'].search([], limit=1).id,
                    })

    def action_view_documents(self):
        self.ensure_one()
        return {
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'name': _("%(name)s's Documents", name=self.name),
            'domain': [
                ('res_model', '=', self._name), ('res_id', '=', self.id),
            ],
            'target': 'new',
            'view_mode': 'kanban,list,form',
            'context': {'default_res_model': self._name,
                        'default_res_id': self.id},
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

    def _remove_documents(self, attachment_ids):
        """Remove documents linked to detached attachments."""
        Document = self.env['documents.document']
        documents_to_remove = Document.search(
            [('attachment_id', 'in', attachment_ids)])
        documents_to_remove.unlink()

    def unlink(self):
        self.env['documents.document'].sudo().search([('attachment_id', 'in', self.attachment_ids.ids)]).unlink()
        return super(OperationalPlan, self).unlink()

    @api.depends('department_ids')
    def _compute_user_ids(self):
        """Compute User IDs for adding domains"""
        for rec in self:
            user = []
            members = []
            if rec.department_ids:
                user = rec.department_ids.employee_ids.mapped('user_id').ids
                members = rec.department_ids.mapped('employee_ids').ids
            rec.user_ids = user
            rec.team_member_ids = members

    @api.onchange('rolling_plan_id')
    def _onchange_rolling_plan(self):
        """Auto-populating some fields based on the ARP"""
        if self.rolling_plan_id:
            self.plan_id = self.rolling_plan_id.plan_id.id
            self.department_ids = self.rolling_plan_id.department_ids
            self.user_preparer_ids = self.rolling_plan_id.user_preparer_ids.id
            self.user_reviewer_1_ids = self.rolling_plan_id.user_reviewer_1_ids.id
            self.user_reviewer_2_ids = self.rolling_plan_id.user_reviewer_2_ids.id
            self.user_approver_ids = self.rolling_plan_id.user_approver_ids.id

    @api.onchange('start_date')
    def _onchange_start_date(self):
        """Update end date based on start date"""
        if self.start_date:
            self.date_end = self.start_date + relativedelta(
                months=3) + relativedelta(days=-1)

    def get_form_url(self):
        """Method to generate the URL to the form view of the current operational plan record."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        action = self.env.ref('internal_audit_management.action_internal_audit_operational_plan',
                              raise_if_not_found=False)
        action_id = action.id if action else 0
        url = urls.url_join(
            base_url,
            'web#id=%s&action=%s&model=operational.plan&view_type=form' % (
            self.id, action_id)
        )
        return url

    def action_review(self):
        """First Review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_operational_plan_to_review')
        recipient_ids = self.user_reviewer_2_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Operational Plan %s was reviewed by %s') % (
                self.name, self.env.user.name))
        self.state = '01_in_progress'
        self.stages = 'first_reviewer'
        for record in self:
            self.env['operational.plan.tracking'].create({
                'operational_plan_tracking_id': record.id,
                'user_id': self.env.user.id,
                'new_stage_id': 'first_reviewer',
                'comment': 'Created',
                'date': fields.Datetime.now(),
            })

    def action_2nd_review(self):
        """Second Review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_operational_plan_to_approve')
        recipient_ids = self.user_approver_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Operational Plan %s was reviewed by %s') % (
                self.name, self.env.user.name))
        previous_state = self.stages
        self.stages = 'second_reviewer'
        for record in self:
            self.env['operational.plan.tracking'].create({
                'operational_plan_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'second_reviewer',
                'comment': 'Second Review',
                'date': fields.Datetime.now(),
            })
        self.state = '01_in_progress'

    def action_approve(self):
        """First Review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_operational_plan_to_approve')
        recipient_ids = self.user_id
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Operational Plan %s was Approved by %s') % (
                self.name, self.env.user.name))
        previous_state = self.stages
        self.stages = 'approved'
        for record in self:
            self.env['operational.plan.tracking'].create({
                'operational_plan_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'approved',
                'comment': 'Approved',
                'date': fields.Datetime.now(),
            })
        self.state = '03_approved'

    def action_reject(self):
        """First Review"""
        self.state = '1_canceled'
        mail_template = self.env.ref(
            'internal_audit_management.email_template_operational_plan_to_rejected')
        recipient_ids = self.user_id
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Operational Plan %s was Rejected by %s') % (
                self.name, self.env.user.name))
        previous_state = self.stages
        self.stages = 'rejected'
        for record in self:
            self.env['operational.plan.tracking'].create({
                'operational_plan_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'rejected',
                'comment': 'Rejected',
                'date': fields.Datetime.now(),
            })

    def action_revert(self):
        return {
            'name': 'Revert Procedure',
            'type': 'ir.actions.act_window',
            'res_model': 'operational.revert.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_operational_plan_detail_id': self.id,
                'default_operational_plan': self.name,
            },
        }
    def action_update(self):
        """Action send back to newt"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_operational_plan_to_review')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.stages
        self.stages = 'first_reviewer'
        for record in self:
            self.env['operational.plan.tracking'].create({
                'operational_plan_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'first_reviewer',
                'comment': 'Updated',
                'date': fields.Datetime.now(),
            })


    @api.depends('q1_allocated_time', 'q2_allocated_time', 'q3_allocated_time', 'q4_allocated_time')
    def _compute_check_allocated_time(self):
        """Compute check allocated Time"""
        for rec in self:
            check_allocated_time = 0
            check_allocated_time = rec.q1_allocated_time + rec.q2_allocated_time + rec.q3_allocated_time + rec.q4_allocated_time
            rec.check_allocated_time = check_allocated_time


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
                                           default=json_default),
                     'output_format': 'xlsx',
                     'report_name': 'ARP 3 Year',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
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

        # image_data = io.BytesIO(base64.b64decode(self.env.company.logo))
        image_data = ""
        if self.env.company.logo:
            image_data = io.BytesIO(base64.b64decode(self.env.company.logo))
        sheet.insert_image('H2', "image.png", {
            'image_data': image_data,
            'x_scale': 0.5,  # Scale image if needed
            'y_scale': 0.5,
            'positioning': 1  # Move and resize with cells
        })
        sheet.write('H1', "Report Date", txt)
        sheet.write('I1', fields.Date.today(), date)

        sheet.merge_range('B2:G3', method.name, head)

        sheet.write('B5', "Internal Audit Rolling Plan: 3 Year:", small_head)
        sheet.write('C5', method.plan_id.name, txt)
        sheet.write('D5', "Internal Audit Rolling Plan: 1 Year : ", small_head)
        sheet.write('E5', method.rolling_plan_id.name, txt)
        sheet.write('F5', "ARP Number : ", small_head)
        sheet.write('G5', method.sequence_number, txt)


        sheet.write('B6', "First Reviewer : ", small_head)
        sheet.write('C6', method.user_reviewer_1_ids.name, date)
        sheet.write('D6', "Second Reviewer : ", small_head)
        sheet.write('E6', method.user_reviewer_2_ids.name, date)
        sheet.write('F6', "Approver : ", small_head)
        sheet.write('G6', method.user_approver_ids.name, txt)

        row = 7
        col = 1
        if method.project_ids:
            sheet.write(row, col, 'Project Name', small_head)
            sheet.write(row, col + 1, 'Internal Audit Rolling Plan: 3', small_head)
            sheet.write(row, col + 2, 'Internal Audit Rolling Plan: 1', small_head)
            sheet.write(row, col + 3, 'ARP Number', small_head)
            sheet.write(row, col + 4, 'Scope Of Work', small_head)
            sheet.write(row, col + 5, 'Q1 Allocation Time', small_head)
            sheet.write(row, col + 6, 'Q2 Allocation Time', small_head)
            sheet.write(row, col + 7, 'Q3 Allocation Time', small_head)
            sheet.write(row, col + 8, 'Q4 Allocation Time', small_head)
            sheet.write(row, col + 9, 'Team', small_head)
            row += 1
            for rec in method.project_ids:
                sheet.write(row, col, rec.name, txt)
                sheet.write(row, col + 1, rec.plan_id.name, txt)
                sheet.write(row, col + 2, rec.internal_audit_1_year_id.name, txt)
                sheet.write(row, col + 3, rec.sequence_number, txt)
                sheet.write(row, col + 4, rec.scope_of_work, txt)
                sheet.write(row, col + 5, rec.q1_allocated_time, txt)
                sheet.write(row, col + 6, rec.q2_allocated_time, txt)
                sheet.write(row, col + 7, rec.q3_allocated_time, txt)
                sheet.write(row, col + 8, rec.q4_allocated_time, txt)
                sheet.write(row, col + 9, rec.department_id.name, txt)
                row += 1
            row += 1

        reverts = self.env['audit.revert'].search(
            [('res_id', '=', method.id), ('res_model', '=', method._name)])
        if method.feedback:

            sheet.write(row, col, 'Revert Comments', small_head)
            sheet.write(row, col + 1, method.feedback, txt)
            row += 2
        if reverts:
            sheet.write(row, col, 'Revert Name', small_head)
            sheet.write(row, col + 1, 'Created Date', small_head)
            sheet.write(row, col + 2, 'Review Comments', small_head)
            sheet.write(row, col + 3, 'Audit Proposal', small_head)
            sheet.write(row, col + 4, 'State', small_head)
            row += 1
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

    def action_print_word(self):
        self.ensure_one()

        from docx import Document
        from docx.shared import Pt, Inches
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        import tempfile
        import base64
        import os

        # Create document
        doc = Document()
        section = doc.sections[0]
        header = section.header

        # Clear default empty paragraph
        header.paragraphs[0].clear()

        p_date = header.add_paragraph()
        p_date.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p_date.add_run(date.today().strftime("%d %B %Y"))
        run.font.size = Pt(9)

        p_logo = header.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        if self.env.company.logo:
            logo_data = base64.b64decode(self.env.company.logo)
            with tempfile.NamedTemporaryFile(delete=False,
                                             suffix=".png") as logo_tmp:
                logo_tmp.write(logo_data)
                logo_path = logo_tmp.name

            run = p_logo.add_run()
            run.add_picture(logo_path, width=Inches(1.2))
            os.unlink(logo_path)

        p_name = header.add_paragraph()
        p_name.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p_name.add_run(self.env.company.name or "")
        run.bold = True
        run.font.size = Pt(11)

        # === TITLE ===
        title = doc.add_heading('Internal Audit Operational Plan', level=1)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # === META INFO ===
        # p = doc.add_paragraph()
        # p.add_run("Company: ").bold = True
        # p.add_run(self.company_id.name or "")

        p = doc.add_paragraph()
        p.add_run("Period: ").bold = True
        p.add_run(self.name or "")

        doc.add_paragraph("")  # spacing

        # === TABLE EXAMPLE ===
        table = doc.add_table(rows=1, cols=15)
        table.style = 'Table Grid'

        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Name'
        hdr_cells[1].text = 'Plan'
        hdr_cells[2].text = 'ARP 3 Year Plan'
        hdr_cells[3].text = 'ARP 1 Year Plan'
        hdr_cells[4].text = 'ARP Number'
        hdr_cells[5].text = 'Audit Type'
        hdr_cells[6].text = 'Scope of Work'
        hdr_cells[7].text = 'Q1 Allocation Time'
        hdr_cells[8].text = 'Q2 Allocation Time'
        hdr_cells[9].text = 'Q3 Allocation Time'
        hdr_cells[10].text = 'Q4 Allocation Time'
        hdr_cells[11].text = 'Team'
        hdr_cells[12].text = 'Project Manager'
        hdr_cells[13].text = 'Start Date'
        hdr_cells[14].text = 'End Date'

        for line in self.project_ids:
            row = table.add_row().cells
            row[0].text = line.name or ''
            row[1].text = line.plan_id.name if line.plan_id else ""
            row[2].text = line.internal_audit_3_years.name if line.internal_audit_3_years else ""
            row[3].text = line.internal_audit_1_year_id.name if line.internal_audit_1_year_id else ""
            row[4].text = line.sequence_number if line.sequence_number else ""
            row[5].text = line.audit_type if line.audit_type else ""
            row[6].text = line.scope_of_work if line.scope_of_work else ""
            row[7].text = str(line.q1_allocated_time)
            row[8].text = str(line.q2_allocated_time)
            row[9].text = str(line.q3_allocated_time)
            row[10].text = str(line.q4_allocated_time)
            row[11].text = line.department_id.name if line.department_id else ""
            row[12].text = line.user_id.name if line.user_id else ""
            row[13].text = str(line.date_start)
            row[14].text = str(line.date)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            doc.save(tmp.name)
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            docx_binary = base64.b64encode(f.read())

        os.unlink(tmp_path)

        # === ATTACHMENT ===
        attachment = self.env['ir.attachment'].create({
            'name': 'AOP_Report.docx',
            'type': 'binary',
            'datas': docx_binary,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': (
                'application/vnd.openxmlformats-officedocument.'
                'wordprocessingml.document'
            ),
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }


    sign_request_id = fields.Many2one('sign.template', string="Sign Request")

    def action_send_sign(self):
        """Send for sign"""
        self.ensure_one()

        # 1️⃣ Get Report
        # report = self.env.ref('internal_audit_management.internal_audit_rolling_plan_report_action')

        # pdf_content, _ = report._render_qweb_pdf(self.id)
        pdf_content, _ = self.env['ir.actions.report'].sudo()._render_qweb_pdf("internal_audit_management.operational_plan_report", res_ids=self.ids)
        # 2️⃣ Create Attachment
        attachment = self.env['ir.attachment'].create({
            'name': f'{self.name}_for_sign.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })

        # 3️⃣ Create Sign Template from Attachment
        sign_template = self.env['sign.template'].create({
                'name': f'Sign Template - {self.name}',
                'attachment_id': attachment.id,
        })

        # 4️⃣ Create Sign Request
        print(self.reviewer_id.partner_id.id)
        vals =[]
        for item in sign_template.sign_item_ids:
            vals.append((0, 0, {
                'partner_id': self.reviewer_id.partner_id.id,
                'role_id': item.responsible_id.id,
            }),)
        # sign_request = self.env['sign.request'].create({
        #     'template_id': sign_template.id,
        #     'reference': self.name,
        #     # 'request_item_ids': vals
        #     'request_item_ids': [Command.create({
        #         'partner_id': self.reviewer_id.partner_id.id,
        #         'role_id': self.env.ref('sign.sign_item_role_customer').id,
        #     })],
        # })
        #
        # # 5️⃣ Save Request to Record
        self.sign_request_id = sign_template.id

    def view_signed_document(self):
        return self.sign_request_id.go_to_custom_template()

class AuditTimeEstimation(models.Model):
    _name = 'audit.time.estimation'
    _description = "Audit Time Estimation"

    user_id = fields.Many2one('res.users', string="Assignee", required=False)
    user_ids = fields.Many2many('res.users', compute='_compute_user_ids')
    allocated_time = fields.Float(string="Estimated", required=True)
    remaining_hours = fields.Float(string="Remaining Hours",
                                   compute="_compute_remaining_hours")
    hours_spent = fields.Float(string="Hours Spent",
                               compute="_compute_remaining_hours")
    operation_plan_id = fields.Many2one('operational.plan', string="Task")

    @api.depends('operation_plan_id')
    def _compute_user_ids(self):
        for rec in self:
            user = rec.operation_plan_id.department_ids.employee_ids.mapped('user_id').ids
            rec.user_ids = user

    @api.depends('allocated_time', 'remaining_hours')
    def _compute_remaining_hours(self):
        """Compute remaining hours"""
        for rec in self:
            remaining_hours = 0
            hours_spent = 0
            # unit_amounts = rec.operation_plan_id.timesheet_ids.filtered(
            #     lambda t: t.employee_id == rec.user_id.employee_id).mapped(
            #     'unit_amount')
            # remaining_hours = rec.allocated_time - sum(unit_amounts)
            # hours_spent = sum(unit_amounts)
            rec.remaining_hours = remaining_hours
            rec.hours_spent = hours_spent

class OperationalPlanTracking(models.Model):
    _name = 'operational.plan.tracking'
    _description = 'Operational Plan Tracking'

    operational_plan_tracking_id = fields.Many2one('operational.plan', string='Operational Plan')
    user_id = fields.Many2one('res.users', string='User')
    previous_stage_id = fields.Selection([
        ('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'),],
                             default="preparer", string="Previous Stage")
    new_stage_id = fields.Selection([
        ('new', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'),],
                                 default="preparer", string="New Stage")
    comment = fields.Text(string='Comment')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
