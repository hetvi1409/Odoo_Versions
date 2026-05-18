import base64

from werkzeug import urls
import io
import json
import xlsxwriter
from odoo.tools import date_utils
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class InternalAuditMethodology(models.Model):
    """Internal Audit Plan"""
    _name = 'internal.audit.method'
    _description = "Internal Audit Method"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    state = fields.Selection([('preparer', 'Preparer'),
                              ('first_reviewer', 'First Reviewer'),
                              ('second_reviewer', 'Second Reviewer'),
                              ('approved', 'Approved'),
                              ('reverted', 'Reverted'),
                              ('rejected', 'Rejected')],
                             default="preparer", string="State")
    date_from = fields.Date(string="From Date", required=True)
    date_to = fields.Date(string="To Date", required=True)
    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Upload Internal Audit Methodology")
    team_id = fields.Many2one('hr.department', string="Team", required=True)
    user_ids = fields.Many2many('res.users', string="Users",
                                compute="_compute_user_ids")
    user_preparer_ids = fields.Many2one('res.users',
                                         required=True,
                                         string="Preparer", tracking=True,
                                         default=lambda self: self.env.user)
    user_reviewer_1_ids = fields.Many2one('res.users',
                                           string="First Reviewer",
                                           tracking=True,
                                           domain="[('id', 'in', user_ids)]")
    user_reviewer_2_ids = fields.Many2one('res.users',
                                           string="Second Reviewer",
                                           tracking=True,
                                           domain="[('id', 'in', user_ids)]")
    user_approver_ids = fields.Many2one('res.users',
                                         string="Approver", tracking=True,
                                         domain="[('id', 'in', user_ids)]")
    document_ids = fields.Many2many('ir.attachment',
                                    'doc_attachment_audit_mgmt_rel',
                                    string="Upload Documents")
    methodology_tracking_ids = fields.One2many(
        'methodology.tracking', 'methodology_tracking_id',
        string='Tracking')

    folder_id = fields.Many2one('documents.document', string="Folder",domain=[('type', '=', 'folder')])
    sequence_no = fields.Char('Sequence Number')
    previous_state = fields.Selection([
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer')])
    feedback = fields.Char(string="Audit Reverts/ Review Notes", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sequence_code = 'internal.audit.method'
            vals['sequence_no'] = self.env['ir.sequence'].next_by_code(
                sequence_code)
        res = super(InternalAuditMethodology, self).create(vals_list)
        for record in res:
            if not self.folder_id:
                folder = self._create_folder(record.name)
                record.folder_id = folder.id
            if 'attachment_ids' in vals_list:
                self._sync_documents(vals_list['attachment_ids'])
            if 'document_ids' in vals_list:
                self._sync_documents(vals_list['document_ids'])
        return res

    # @api.model
    # def create(self, vals):
    #     vals['sequence_no'] = self.env['ir.sequence'].next_by_code('internal.audit.method')
    #     record = super(InternalAuditMethodology, self).create(vals)
    #     if not self.folder_id:
    #         folder = self._create_folder(record.name)
    #         record.folder_id = folder.id
    #     if 'attachment_ids' in vals:
    #         self._sync_documents(vals['attachment_ids'])
    #     if 'document_ids' in vals:
    #         self._sync_documents(vals['document_ids'])
    #     return record

    def write(self, vals):
        existing_attachments = self.attachment_ids
        existing_documents = self.document_ids
        res = super(InternalAuditMethodology, self).write(vals)
        if not self.folder_id:
            folder = self._create_folder(self.name)
            self.folder_id = folder.id
        if 'attachment_ids' in vals:
            new_attachments = self.attachment_ids
            removed_attachments = existing_attachments - new_attachments
            self._sync_documents(vals['attachment_ids'])
            self._remove_documents(removed_attachments.ids)
        if 'document_ids' in vals:
            new_documents = self.document_ids
            removed_attachments = existing_documents - new_documents
            self._sync_documents(vals['document_ids'])
            self._remove_documents(removed_attachments.ids)
        return res

    def _create_folder(self, name):
        """Create a folder in documents.document if it doesn't exist."""
        folder = self.env['documents.document']
        documents_folder_id = self.env.ref(
            'internal_audit_management.documents_audit_methodology_folder').id
        folder = folder.search([('name', '=', name),
                                ('folder_id', '=', documents_folder_id)],
                               limit=1)
        if not folder:
            folder = folder.create({'name': name,
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
                        self.env['documents.document'].search([('type', '=', 'folder')], limit=1).id,
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

    def _remove_documents(self, attachment_ids):
        """Remove documents linked to detached attachments."""
        Document = self.env['documents.document']
        documents_to_remove = Document.search(
            [('attachment_id', 'in', attachment_ids)])
        documents_to_remove.unlink()

    def unlink(self):
        self.env['documents.document'].sudo().search(
            [('attachment_id', 'in', self.attachment_ids.ids)]).unlink()
        self.env['documents.document'].sudo().search(
            [('attachment_id', 'in', self.document_ids.ids)]).unlink()
        return super(InternalAuditMethodology, self).unlink()

    @api.depends('team_id')
    def _compute_user_ids(self):
        """Compute User IDs for adding domains"""
        for rec in self:
            user = []
            if rec.team_id:
                user = rec.team_id.employee_ids.mapped('user_id').ids
            rec.user_ids = user

    def get_list_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=internal.audit.method&view_type=list' % self.id)
        return Urls

    def action_review(self):
        """method for review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_methodology_review')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.state
        self.state = 'first_reviewer'
        for record in self:
            # Add a new line in the tracking
            self.env['methodology.tracking'].create({
                'methodology_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': record.state,
                'comment': 'First Review',
                'date': fields.Datetime.now(),
            })

    def action_2nd_review(self):
        """Second Review"""
        previous_state = self.state
        self.state = 'second_reviewer'
        for record in self:
            self.env['methodology.tracking'].create({
                'methodology_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': record.state,
                'comment': 'Second Review',
                'date': fields.Datetime.now(),
            })
        mail_template = self.env.ref(
            'internal_audit_management.email_template_methodology_second_review')
        mail_template.send_mail(self.id, force_send=True)

    def action_approve(self):
        """Method for approve"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_methodology_approved')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.state
        self.state = 'approved'
        for record in self:
            # Add a new line in the tracking
            self.env['methodology.tracking'].create({
                'methodology_tracking_id': record.id,
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
            'internal_audit_management.email_template_methodology_refused')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.state
        self.state = 'rejected'
        for record in self:
            # Add a new line in the tracking
            self.env['methodology.tracking'].create({
                'methodology_tracking_id': record.id,
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
                'default_audit_method_id': self.id
            },
            'view_mode': 'form',
            'target': 'new',
        }

    def action_update(self):
        previous_state = self.state
        self.state = 'first_reviewer'
        self.feedback = ""
        self.state = self.previous_state
        for record in self:
            self.env['methodology.tracking'].create({
                'methodology_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': record.state,
                'comment': 'Updated',
                'date': fields.Datetime.now(),
            })

    def action_send_back_new(self):
        """Action send back to newt"""
        # self.state = 'new'
        mail_template = self.env.ref(
            'internal_audit_management.email_template_methodology_review')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.state
        self.state = 'preparer'
        for record in self:
            # Add a new line in the tracking
            self.env['methodology.tracking'].create({
                'methodology_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': record.state,
                'comment': 'New',
                'date': fields.Datetime.now(),
            })

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
        sheet.set_column(1, 11, 12, txt)

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
        sheet.write('B5', "Sequence No : ", small_head)
        sheet.write('C5', method.sequence_no, txt)
        sheet.write('D5', "Team : ", small_head)
        sheet.write('E5', method.team_id.name, txt)
        sheet.write('F5', "State : ", small_head)
        sheet.write('G5', method.state, txt)

        sheet.write('B6', "Start Date : ", small_head)
        sheet.write('C6', method.date_from, date)
        sheet.write('D6', "End Date : ", small_head)
        sheet.write('E6', method.date_to, date)
        sheet.write('F6', "Preparer : ", small_head)
        sheet.write('G6', method.user_preparer_ids.name, txt)

        sheet.write('B7', "First Reviewer : ", small_head)
        sheet.write('C7', method.user_reviewer_1_ids.name, date)
        sheet.write('D7', "Second Reviewer : ", small_head)
        sheet.write('E7', method.user_reviewer_2_ids.name, date)
        sheet.write('F7', "Approver : ", small_head)
        sheet.write('G7', method.user_approver_ids.name, txt)

        reverts = self.env['audit.revert'].search([('res_id', '=', method.id), ('res_model', '=', method._name)])
        if method.feedback:
            sheet.write('B8', 'Revert Comments', small_head)
            sheet.merge_range('C8:G38', method.feedback, txt)
        if reverts:

            sheet.write('B10', 'Revert Name', small_head)
            sheet.write('C10', 'Created Date', small_head)
            sheet.write('D10', 'Review Comments', small_head)
            sheet.write('E10', 'Audit Proposal', small_head)
            sheet.write('F10', 'State', small_head)
            row = 10
            col = 1
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


class MethodologyTracking(models.Model):
    _name = 'methodology.tracking'
    _description = 'Methodology Tracking'

    methodology_tracking_id = fields.Many2one('internal.audit.method', string='Audit Methodology Tracking')
    user_id = fields.Many2one('res.users', string='User')
    previous_stage_id = fields.Selection([('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected')],
                             default="preparer", string="Previous Stage")
    new_stage_id = fields.Selection([('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected')],
                                 default="preparer", string="New Stage")
    comment = fields.Text(string='Comment')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
