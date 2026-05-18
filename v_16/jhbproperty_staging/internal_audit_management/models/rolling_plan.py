import base64
import io

import xlsxwriter

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from werkzeug import urls

from odoo.tools import date_utils
from odoo.tools.safe_eval import json
from datetime import date
from odoo.tools import json_default


class RollingPlans(models.Model):
    _name = 'rolling.plan'
    _description = "Internal Audit Rolling Plan"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'rec_name'

    rec_name = fields.Char('Name', compute="_compute_name")
    plan_id = fields.Many2one('internal.audit.plan', string="Plan")
    name = fields.Char(string='Name', required=True, tracking=True)
    sequence_no = fields.Char(string='ARP Number', readonly=True, copy=False,)
    category_id = fields.Many2one('audit.assignment.category',
                                  string='Category', tracking=True)
    department_ids = fields.Many2many('hr.department', string='Department',
                                    tracking=True)
    department_id = fields.Many2one('hr.department', string='Department',
                                    tracking=True)
    user_ids = fields.Many2many('res.users', string="Users",
                                compute="_compute_user_ids")
    period = fields.Char(string="Period", related='plan_id.period')
    year_ids = fields.Many2many('arp.year', string="Years", related='plan_id.year_ids')
    arp_year_id = fields.Many2one('arp.year', string='Year', tracking=True,)
    start_date = fields.Date(string='Planned Date')
    date_end = fields.Date(string="End Date")
    team_id = fields.Many2one('hr.department', string='Team',)
    team_members_ids = fields.Many2many('hr.employee', string="Team Members",)
    risk_priority_rating = fields.Selection([('low', 'Low'),
                                             ('low-medium', 'Low Medium'),
                                             ('medium', 'Medium'),
                                             ('medium-high', 'Medium High'),
                                             ('high', 'High')],
                                            string="Risk Priority Rating",
                                            tracking=True,
                                            default='low', required=True)
    # q1_allocated_time = fields.Float(string="Q1 Allocated Time")
    # q2_allocated_time = fields.Float(string="Q2 Allocated Time")
    # q3_allocated_time = fields.Float(string="Q3 Allocated Time")
    # q4_allocated_time = fields.Float(string="Q4 Allocated Time")
    # allocated_hours = fields.Float(string="Allocated Hours")
    description = fields.Text(string="Description")
    stages = fields.Selection([
        ('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'),
    ], 'State', default='preparer', tracking=True)
    state = fields.Selection([('in_preparer', 'In Preparer'),
                              ('01_in_progress', 'In Progress'),
                              ('02_changes_requested', 'Changes Requested'),
                              ('03_approved', 'Approved'), ('1_done', 'Done'),
                              ('1_canceled', 'Canceled'),
                              ('04_waiting_normal', 'Waiting')],
                             string='State')
    user_preparer_ids = fields.Many2one('res.users',
                                         string="Preparer", tracking=True, default=lambda self: self.env.user)
    user_reviewer_1_ids = fields.Many2one('res.users',
                                           string="First Reviewer",
                                           tracking=True, )
    user_reviewer_2_ids = fields.Many2one('res.users',string="Second Reviewer",
                                           tracking=True, )
    user_approver_ids = fields.Many2one('res.users',
                                         string="Approver", tracking=True, )
    operational_plan_ids = fields.One2many('operational.plan', 'rolling_plan_id', string='Internal Audit Operational Plan')
    rolling_plan_tracking = fields.One2many('rolling.plan.tracking','rolling_tracking_id', string='Tracking')
    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Upload Internal Audit Plan")
    project_ids = fields.One2many('project.project', 'internal_audit_1_year_id', string="Projects")
    folder_id = fields.Many2one('documents.folder', string="Folder")

    feedback = fields.Char(string="Audit Reverts/ Review Notes", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        # Assign sequence numbers for each record
        for vals in vals_list:
            vals['sequence_no'] = self.env['ir.sequence'].next_by_code('rolling.plan')

        records = super(RollingPlans, self).create(vals_list)

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
        res = super(RollingPlans, self).write(vals)
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
            'internal_audit_management.documents_arp_1_folder').id
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
            'view_mode': 'kanban,tree,form',
            'context': {'default_res_model': self._name,
                        'default_res_id': self.id},
        }

    def _remove_documents(self, attachment_ids):
        """Remove documents linked to detached attachments."""
        Document = self.env['documents.document']
        documents_to_remove = Document.search(
            [('attachment_id', 'in', attachment_ids)])
        documents_to_remove.unlink()

    def unlink(self):
        self.env['documents.document'].sudo().search([('attachment_id', 'in', self.attachment_ids.ids)]).unlink()
        return super(RollingPlans, self).unlink()

    @api.depends('name', 'arp_year_id')
    def _compute_name(self):
        for rec in self:
            name = ""
            if rec.name:
                name += rec.name
            if rec.arp_year_id:
                name += ' (' + rec.arp_year_id.name + ') '
            rec.rec_name = name

    def get_form_url(self):
        """Method to generate the URL to the form view of the current rolling plan record."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        action = self.env.ref('internal_audit_management.action_internal_audit_rolling_plan',
                              raise_if_not_found=False)
        action_id = action.id if action else 0
        url = urls.url_join(
            base_url,
            'web#id=%s&action=%s&model=rolling.plan&view_type=form' % (
            self.id, action_id)
        )
        return url

    @api.onchange('year_ids', 'plan_id', 'arp_year_id')
    def _onchange_year_plan(self):
        """Updating the periods based on the plan"""
        if self.plan_id.date_from:
            year = self.plan_id.date_from.year
            year_string_1 = str(year) + ' - ' + str(year + 1)
            year_string_2 = str(year + 1) + ' - ' + str(year + 2)
            year_string_3 = str(year + 2) + ' - ' + str(year + 3)
            if self.arp_year_id.name == year_string_1:
                self.start_date = self.plan_id.date_from
                self.date_end = self.plan_id.date_from + relativedelta(
                    years=1) + relativedelta(days=-1)
            if self.arp_year_id.name == year_string_2:
                self.start_date = self.plan_id.date_from + relativedelta(
                    years=1)
                self.date_end = self.plan_id.date_from + relativedelta(
                    years=2) + relativedelta(days=-1)
            if self.arp_year_id.name == year_string_3:
                self.start_date = self.plan_id.date_from + relativedelta(
                    years=2)
                self.date_end = self.plan_id.date_from + relativedelta(
                    years=3) + relativedelta(days=-1)

    @api.onchange('plan_id')
    def _onchange_plan_id(self):
        """Auto-populate some fields based on the plan"""
        if self.plan_id:
            self.user_preparer_ids = self.plan_id.user_preparer_ids.id
            self.user_reviewer_1_ids = self.plan_id.user_reviewer_1_ids.id
            self.user_reviewer_2_ids = self.plan_id.user_reviewer_2_ids.id
            self.user_approver_ids = self.plan_id.user_approver_ids.id

    @api.depends('department_ids')
    def _compute_user_ids(self):
        """Compute User IDs for adding domains"""
        for rec in self:
            user = []
            if rec.department_ids:
                user = rec.department_ids.employee_ids.mapped('user_id')
            rec.user_ids = user

    # @api.onchange('allocated_hours', 'q1_allocated_time', 'q2_allocated_time',
    #               'q3_allocated_time', 'q4_allocated_time')
    # def _onchange_allocated_hours(self):
    #     """Allocated Hours calculation"""
    #     for rec in self:
    #         rec.allocated_hours = self.q1_allocated_time + self.q2_allocated_time + self.q3_allocated_time + self.q4_allocated_time

    @api.onchange('start_date', 'date_end')
    def _onchange_planned_date(self):
        if self.plan_id:
            if self.start_date:
                self.date_end = self.start_date + relativedelta(years=1) + relativedelta(days=-1)
        else:
            if not self.date_end and self.start_date:
                self.start_date = False
            elif not self.start_date and self.date_end:
                self.date_end = False

    @api.constrains('start_date', 'date_end')
    def _constraints_date_start_date(self):
        for record in self:
            if record.plan_id:
                if record.start_date and record.plan_id.date_from > record.start_date:
                    raise ValidationError(_(
                        'Please add a proper period for the ARP %s. Period should be between %s and %s. Check the ARP for 3 Year plan Period %s.' % (
                            record.name, record.plan_id.date_from,
                            record.plan_id.date_to, record.plan_id.name)))
                if record.date_end and record.plan_id.date_to < record.date_end:
                    raise ValidationError(
                        _('Please add a proper period for ARP the %s. Period should be inbetween %s and %s. Check the ARP for 3 Year plan Period %s.' % (
                            record.name, record.plan_id.date_from,
                            record.plan_id.date_to, record.plan_id.name)))

    # @api.constrains('q1_allocated_time', 'q2_allocated_time', 'q3_allocated_time', 'q4_allocated_time')
    # def _constraints_allocated_time(self):
    #     """Allocated Time Can't be 0"""
    #     allocated_time = ""
    #     if self.q1_allocated_time == 0:
    #         allocated_time = "Q1"
    #     if self.q2_allocated_time == 0:
    #         allocated_time = allocated_time + ' , Q2' if allocated_time else 'Q2'
    #     if self.q3_allocated_time == 0:
    #         allocated_time = allocated_time + ' , Q3' if allocated_time else 'Q3'
    #     if self.q4_allocated_time == 0:
    #         allocated_time = allocated_time + ' , Q4' if allocated_time else 'Q4'
    #     if (self.q1_allocated_time == 0 and self.q2_allocated_time == 0 and
    #          self.q3_allocated_time == 0 and self.q4_allocated_time == 0):
    #         if allocated_time:
    #             raise ValidationError(_('Please add %s Allocated Time for the %s') % (allocated_time, self.name))

    def action_review(self):
        """First Review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_rolling_plan_to_review')
        recipient_ids = self.user_reviewer_2_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Rolling Plan %s was reviewed by %s') % (
                self.name, self.env.user.name))
        previous_stage = self.stages
        self.stages = 'first_reviewer'
        self.rolling_plan_tracking.create({
            'rolling_tracking_id': self.id,
            'comment': "First Review",
            'previous': previous_stage,
            'new_state': self.stages,
            'user_id': self.env.user.id,
        })
        self.state = '01_in_progress'

    def action_2nd_review(self):
        """Second Review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_rolling_plan_to_approve')
        recipient_ids = self.user_approver_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Rolling Plan %s was reviewed by %s') % (
                self.name, self.env.user.name))
        self.stages = 'second_reviewer'
        self.rolling_plan_tracking.create({
            'rolling_tracking_id': self.id,
            'comment': "Second Review",
            'previous': "First Review",
            'new_state': self.stages,
            'user_id': self.env.user.id,
        })
        self.state = '01_in_progress'

    def action_approve(self):
        """First Review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_rolling_plan_to_approve')
        recipient_ids = self.user_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Rolling Plan %s was Approved by %s') % (
                self.name, self.env.user.name))
        self.stages = 'approved'
        self.rolling_plan_tracking.create({
            'rolling_tracking_id': self.id,
            'comment': "Approved",
            'previous': "Second Review",
            'new_state': self.stages,
            'user_id': self.env.user.id,
        })
        self.state = '03_approved'

    def action_reject(self):
        """First Review"""
        self.state = '1_canceled'
        mail_template = self.env.ref(
            'internal_audit_management.email_template_rolling_plan_to_rejected')
        recipient_ids = self.user_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Rolling Plan %s was Rejected by %s') % (
                self.name, self.env.user.name))
        previous_stage = self.stages
        self.stages = 'rejected'
        self.rolling_plan_tracking.create({
            'rolling_tracking_id': self.id,
            'comment': "Rejected",
            'previous': previous_stage,
            'new_state': self.stages,
            'user_id': self.env.user.id,
        })

    def action_update(self):
        self.stages = 'first_reviewer'
        self.rolling_plan_tracking.create({
            'rolling_tracking_id': self.id,
            'comment': "Updated",
            'previous': "Reverted",
            'new_state': self.stages,
            'user_id': self.env.user.id,
        })

    def action_revert(self):
        previous_stage = self.stages
        # self.stages = 'reverted'
        self.rolling_plan_tracking.create({
            'rolling_tracking_id': self.id,
            'comment': "Reverted",
            'previous': previous_stage,
            'new_state': self.stages,
            'user_id': self.env.user.id,
        })
        return {
            'name': 'Revert Procedure',
            'type': 'ir.actions.act_window',
            'res_model': 'rolling.revert.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_rolling_plan_detail_id': self.id,
                'default_rolling_plan': self.name,
            },
        }

    def action_view_records(self):
        """Method for view records"""
        return {
            'name': 'Audit Reverts/ Review Notes',
            'type': 'ir.actions.act_window',
            'res_model': 'audit.revert',
            'domain': [('res_id', '=', self.id), ('res_model', '=', self._name)],
            'view_mode': 'tree,form',
            'target': 'current',
        }

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
                                   'valign': 'vcenter', 'text_wrap': True })
        date = workbook.add_format({'num_format': 'd-m-yyyy'})
        sheet.set_column(1, 11, 15, txt)

        # image_data = io.BytesIO(base64.b64decode(self.env.company.logo))
        # image_data = base64.b64decode(self.env.company.logo)

        image_data = ""
        if self.env.company.logo:
            image_data = io.BytesIO(base64.b64decode(self.env.company.logo))
        sheet.insert_image('H2', "image.png", {
            'image_data': image_data,
            'x_scale': 0.5,  # Scale image if needed
            'y_scale': 0.5,
            'positioning': 1  # Move and resize with cells
        })
        sheet.write('H1', "Report Date" , txt)
        sheet.write('I1', fields.Date.today(), date)

        sheet.merge_range('B2:G3', method.name, head)
        sheet.write('B5', "ARP Number : ", small_head)
        sheet.write('C5', method.sequence_no, txt)
        sheet.write('D5', "Plan : ", small_head)
        sheet.write('E5', method.plan_id.name, txt)
        sheet.write('F5', "State : ", small_head)
        sheet.write('G5', method.stages, txt)
        sheet.write('H5', "Category : ", small_head)
        sheet.write('I5', method.category_id.name, txt)

        sheet.write('B6', "Department : ", small_head)
        sheet.write('C6', ", ".join(user.name for user in method.department_ids), txt)
        sheet.write('D6', "Risk Priority Rating: ", small_head)
        sheet.write('E6', method.risk_priority_rating, txt)
        sheet.write('F6', "Start Date : ", small_head) 
        sheet.write('G6', method.start_date, date)
        sheet.write('H6', "End Date: ", small_head)
        sheet.write('I6', method.date_end, txt)
        
        sheet.write('B7', "Year: ", small_head)
        sheet.write('C7', method.arp_year_id.name, txt)
        sheet.write('D7', "Period: ", small_head)
        sheet.write('E7', method.period, txt)
        sheet.write('F7', "Preparer : ", small_head) 
        sheet.write('G7', method.user_preparer_ids.name, txt)
        
        sheet.write('B8', "First Reviewer: ", small_head)
        sheet.write('C8', method.user_reviewer_1_ids.name, txt)
        sheet.write('D8', "Second Reviewer: ", small_head)
        sheet.write('E8', method.user_reviewer_2_ids.name, txt)
        sheet.write('F8', "Approver : ", small_head)
        sheet.write('G8', method.user_approver_ids.name, txt)


        row = 10
        col = 1

        if method.operational_plan_ids:
            sheet.write(row, col, 'ARP Number', small_head)
            sheet.write(row, col + 1, 'ARP Name', small_head)
            sheet.write(row, col + 2, 'AOP Name', small_head)
            sheet.write(row, col + 3, 'Internal Audit Rolling Plan 3', small_head)
            sheet.write(row, col + 4, 'Project Number', small_head)
            sheet.write(row, col + 5, 'Motivation/Link', small_head)
            sheet.write(row, col + 6, 'Scope Of Work', small_head)
            sheet.write(row, col + 7, 'Type Of Audit', small_head)
            sheet.write(row, col + 8, 'Department', small_head)
            sheet.write(row, col + 9, 'Risk Description', small_head)
            sheet.write(row, col + 10, 'Risk Priority Rating', small_head)
            sheet.write(row, col + 11, 'Start Date', small_head)
            sheet.write(row, col + 12, 'End Date', small_head)
            row += 1
            for line in method.operational_plan_ids:
                sheet.write(row, col, line.sequence_number, txt)
                sheet.write(row, col + 1, line.rolling_plan_id.name, txt)
                sheet.write(row, col + 2, line.plan_id.name, txt)
                sheet.write(row, col + 3, line.project_number, txt)
                sheet.write(row, col + 4, line.name, txt)
                sheet.write(row, col + 5, line.description, txt)
                sheet.write(row, col + 6, line.scope_of_work, txt)
                sheet.write(row, col + 7, line.assurance_consulting, txt)
                sheet.write(row, col + 8, ", ".join(user.name for user in line.department_ids), txt)
                sheet.write(row, col + 9, line.risk_priority_rating, txt)
                sheet.write(row, col + 10, line.risk_description, txt)
                sheet.write(row, col + 11, line.start_date, txt)
                sheet.write(row, col + 12, line.date_end, txt)
                row += 1
        row += 1
        reverts = self.env['audit.revert'].search([('res_id', '=', method.id), ('res_model', '=', method._name)])
        if method.feedback:
            sheet.write(row, col, 'Revert Comments', small_head)
            sheet.write(row, col + 1, method.feedback, txt)
            row += 1
        row += 1
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
                row =+ 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

    def action_print_word(self):
        self.ensure_one()

        from docx import Document
        from odoo.tools import format_date
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
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as logo_tmp:
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
        title = doc.add_heading('Internal Audit Rolling Plan 1 Year', level=1)
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
        table = doc.add_table(rows=1, cols=12)
        table.style = 'Table Grid'

        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'ARP Number'
        hdr_cells[1].text = 'ARP Name'
        hdr_cells[2].text = 'AOP Name'
        hdr_cells[3].text = 'Internal Audit Rolling Plan 3 Years'
        hdr_cells[4].text = 'Project Number'
        hdr_cells[5].text = 'Motivation/Link to Description'
        hdr_cells[6].text = 'Scope of Work'
        hdr_cells[7].text = 'Type of Audit'
        hdr_cells[8].text = 'Risk Priority Rating'
        hdr_cells[9].text = 'Risk Department'
        hdr_cells[10].text = 'Start Date'
        hdr_cells[11].text = 'End Date'

        for line in self.operational_plan_ids:
            row = table.add_row().cells
            row[0].text = line.sequence_number or ''
            row[1].text = line.rolling_plan_id.name or ''
            row[2].text = line.name or ''
            row[3].text = line.plan_id.name or ''
            row[4].text = line.project_number or ''
            row[5].text = line.description or ''
            row[6].text = line.scope_of_work or ''
            row[7].text = line.assurance_consulting or ''
            row[8].text = line.risk_priority_rating or ''
            row[9].text = line.risk_description or ''
            row[10].text = format_date(self.env,
                                       line.start_date) if line.start_date else ''
            row[11].text = format_date(self.env,
                                       line.date_end) if line.date_end else ''

        # === SAVE TEMP DOCX ===
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            doc.save(tmp.name)
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            docx_binary = base64.b64encode(f.read())

        os.unlink(tmp_path)

        # === ATTACHMENT ===
        attachment = self.env['ir.attachment'].create({
            'name': 'ARP_1_Year_Report.docx',
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
        pdf_content, _ = self.env['ir.actions.report'].sudo()._render_qweb_pdf("internal_audit_management.internal_rolling_plan_report_action", res_ids=self.ids)
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


class RollingPlanTracking(models.Model):
    _name = "rolling.plan.tracking"
    _description = "Rolling Plan Tracking"

    rolling_tracking_id = fields.Many2one('rolling.plan', string='Tracking')
    user_id = fields.Many2one('res.users',string='User')
    previous = fields.Char(string='Previous')
    new_state = fields.Char(string='New')
    comment = fields.Char(string='Comment')
    date_updated = fields.Date(string='Date', default=fields.Datetime.now)


