from werkzeug import urls
import base64
import io
import xlsxwriter
from werkzeug import urls
from odoo.tools import date_utils
from odoo.tools.safe_eval import json
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class QualityControlInternalReviewFramework(models.Model):
    """Quality control - Internal review framework"""
    _name = 'internal.quality.control'
    _description = "Quality Control - Internal Review Framework"
    _rec_name = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected')], tracking=True,
                             default="preparer", string="State")
    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Upload Internal Audit Review Framework")
    review_attachment_ids = fields.Many2many('ir.attachment', 'review_attachment_rel',
                                      string="Upload Review Documents")
    name = fields.Char(string="Name", required=True,
                               help="Name")
    requirements = fields.Html(string="Requirements", required=True,
                               help="Requirements")
    record_work_done = fields.Html(string="Work done", required=True,
                                   help="Record of work done")
    conclusion = fields.Html(string="Conclusion", required=True,
                             help="Conclusion")
    team_id = fields.Many2one('hr.department', string="Team")
    # role_id = fields.Many2one('audit.role', string="Roles")
    user_id = fields.Many2one('res.users', Tracking=True,
                              string="Manager")
    feedback = fields.Char(string="Feedback", tracking=True)
    internal_quality_control_tracking_ids = fields.One2many('internal.quality.control.tracking', 'internal_quality_control_tracking_id', string='Tracking')
    document_ids = fields.Many2many('ir.attachment',
                                    'documents_attachment_internal_quality_rel',
                                    string="Upload Documents")
    user_ids = fields.Many2many('res.users', string="Users",
                                compute="_compute_user_ids")
    user_preparer_ids = fields.Many2one('res.users',
                                         string="Preparer", tracking=True,
                                         default=lambda self: self.env.user)
    user_reviewer_1_ids = fields.Many2one('res.users',
                                           string="First Reviewer",
                                           tracking=True)
    user_reviewer_2_ids = fields.Many2one('res.users',
                                           string="Second Reviewer",
                                           tracking=True)
    user_approver_ids = fields.Many2one('res.users',
                                         string="Approver", tracking=True)
    sequence_no = fields.Char(string='W/P Reference', readonly=True,
                              copy=False)
    comments = fields.Html(string='Comments')

    @api.depends('team_id')
    def _compute_user_ids(self):
        """Compute User IDs for adding domains"""
        for rec in self:
            user = []
            if rec.team_id:
                user = rec.team_id.employee_ids.mapped('user_id').ids
            rec.user_ids = user

    folder_id = fields.Many2one('documents.document', string="Folder", domain=[('type', '=', 'folder')])
    previous_state = fields.Selection([
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer')])

    @api.model_create_multi
    def create(self, vals_list):
        # Assign sequence numbers for each record
        for vals in vals_list:
            vals['sequence_no'] = self.env['ir.sequence'].next_by_code('internal.quality.control')

        records = super(QualityControlInternalReviewFramework, self).create(vals_list)

        for record, vals in zip(records, vals_list):
            # Ensure folder is created
            if not record.folder_id:
                folder = record._create_folder(record.name)
                record.folder_id = folder.id

            # Sync attachments if present
            if 'attachment_ids' in vals:
                record._sync_documents(vals['attachment_ids'])
            if 'review_attachment_ids' in vals:
                record._sync_documents(vals['review_attachment_ids'])

        return records

    def write(self, vals):
        existing_attachments = self.attachment_ids
        existing_review_attachments = self.review_attachment_ids
        existing_documents = self.document_ids
        res = super(QualityControlInternalReviewFramework, self).write(vals)
        if not self.folder_id:
            folder = self._create_folder(self.name)
            self.folder_id = folder.id
        if 'attachment_ids' in vals:
            new_attachments = self.attachment_ids
            removed_attachments = existing_attachments - new_attachments
            self._sync_documents(vals['attachment_ids'])
            self._remove_documents(removed_attachments.ids)
        if 'review_attachment_ids' in vals:
            removed_review_attachments = self.review_attachment_ids
            removed_attachments = existing_review_attachments - removed_review_attachments
            self._sync_documents(vals['review_attachment_ids'])
            self._remove_documents(removed_attachments.ids)
        if 'document_ids' in vals:
            removed_documents = self.document_ids
            removed_attachments = existing_documents - removed_documents
            self._sync_documents(vals['document_ids'])
            self._remove_documents(removed_attachments.ids)
        return res

    def _create_folder(self, name):
        """Create a folder in documents.folder if it doesn't exist."""
        folder = self.env['documents.document']
        documents_folder_id = self.env.ref('internal_audit_management.documents_internal_review_framework_folder').id
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
            [('attachment_id', 'in', self.review_attachment_ids.ids)]).unlink()
        self.env['documents.document'].sudo().search(
            [('attachment_id', 'in', self.document_ids.ids)]).unlink()
        return super(QualityControlInternalReviewFramework, self).unlink()

    show_button = fields.Boolean(
        string="Show Button",
        compute="_compute_show_button",
        store=False
    )

    @api.depends('document_ids', 'review_attachment_ids', 'attachment_ids')
    def _compute_show_button(self):
        for record in self:
            record.show_button = bool(
                record.document_ids or record.review_attachment_ids or record.attachment_ids
            )

    @api.depends('team_id')
    def _compute_user_ids(self):
        """Compute User IDs for adding domains"""
        for rec in self:
            user = []
            if rec.team_id:
                user = rec.team_id.employee_ids.mapped('user_id').ids
            rec.user_ids = user

    # @api.onchange('user_id')
    # def _onchange_user_id(self):
    #     """Onchange user id"""
    #     self.team_id = self.user_id.team_id.id
        # self.role_id = self.user_id.role_id.id

    @api.constrains('date_to', 'date_from')
    def _check_date(self):
        for record in self:
            if record.date_to and record.date_to < record.date_from:
                raise ValidationError(_('Please add a porper period'))
            if record.audit_id:
                if record.audit_id.annual_plan_id.date_to <= record.date_to:
                    raise ValidationError(_('The end date must be equal '
                                            'or less that the date in '
                                            'annual plan'))
                if record.audit_id.annual_plan_id.date_from >= record.date_from:
                    raise ValidationError(_('The start date must be equal '
                                            'or grater that the date '
                                            'in annual plan'))


    def get_list_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=internal.quality.control&view_type=list' % self.id)
        return Urls

    def action_review(self):
        """method for review"""
        previous_state = self.state
        self.state = 'first_reviewer'
        for record in self:
            self.env['internal.quality.control.tracking'].create({
                'internal_quality_control_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'first_reviewer',
                'comment': 'Reviewed',
                'date': fields.Datetime.now(),
            })
        mail_template = self.env.ref(
            'internal_audit_management.email_template_internal_quality_control_review')
        mail_template.send_mail(self.id, force_send=True)

    def action_approve(self):
        """Method for approve"""
        previous_state = self.state
        self.state = 'approved'
        for record in self:
            self.env['internal.quality.control.tracking'].create({
                'internal_quality_control_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'approved',
                'comment': 'Approved',
                'date': fields.Datetime.now(),
            })
        mail_template = self.env.ref(
            'internal_audit_management.email_template_internal_quality_control_approve')
        mail_template.send_mail(self.id, force_send=True)

    def action_update(self):
        previous_state = self.state
        self.state = self.previous_state
        for record in self:
            self.env['internal.quality.control.tracking'].create({
                'internal_quality_control_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': self.previous_state,
                'comment': 'Updated',
                'date': fields.Datetime.now(),
            })

    def action_2nd_review(self):
        """Second Review"""
        previous_state = self.state
        self.state = 'second_reviewer'
        for record in self:
            self.env['internal.quality.control.tracking'].create({
                'internal_quality_control_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'second_reviewer',
                'comment': 'Second Review',
                'date': fields.Datetime.now(),
            })
        mail_template = self.env.ref(
            'internal_audit_management.email_template_internal_quality_control_review')
        mail_template.send_mail(self.id, force_send=True)

    def action_mark_discrepancy(self):
        """Action refuse the request"""
        previous_state = self.state
        self.state = 'rejected'
        for record in self:
            self.env['internal.quality.control.tracking'].create({
                'internal_quality_control_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'rejected',
                'comment': 'Rejected',
                'date': fields.Datetime.now(),
            })
        mail_template = self.env.ref(
            'internal_audit_management.email_template_internal_quality_control_refuse')
        mail_template.send_mail(self.id, force_send=True)

    def action_send_back_review(self):
        """Action SEND BACK TO REVIEW"""
        return {
            'name': 'Audit Reverts/ Review Notes',
            'type': 'ir.actions.act_window',
            'res_model': 'internal.audit.revert.wizard',
            'context': {
                'default_internal_quality_control_id': self.id
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
        previous_state = self.state
        self.state = 'preparer'
        for record in self:
            self.env['internal.quality.control.tracking'].create({
                'internal_quality_control_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'preparer',
                'comment': 'New',
                'date': fields.Datetime.now(),
            })
        mail_template = self.env.ref(
            'internal_audit_management.email_template_internal_quality_control_new')
        mail_template.send_mail(self.id, force_send=True)

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
                                   'valign': 'vcenter', 'text_wrap': True})
        date = workbook.add_format({'num_format': 'd-m-yyyy'})
        sheet.set_column(1, 11, 12, txt)

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
        sheet.write('B5', "W/P Reference : ", small_head)
        sheet.write('C5', method.sequence_no, txt)
        sheet.write('D5', "Requirements : ", small_head)
        sheet.write('E5', method.requirements, txt)
        sheet.write('F5', "Work Done : ", small_head)
        sheet.write('G5', method.record_work_done, txt)
        sheet.write('H5', "Conclusion : ", small_head)
        sheet.write('I5', method.conclusion, txt)

        sheet.write('B6', "Preparer : ", small_head)
        sheet.write('C6', method.user_preparer_ids.name, txt)
        sheet.write('D6', "First Reviewer : ", small_head)
        sheet.write('E6', method.user_reviewer_1_ids.name, date)
        sheet.write('F6', "Second Reviewer : ", small_head)
        sheet.write('G6', method.user_reviewer_2_ids.name, date)
        sheet.write('H6', "Approver : ", small_head)
        sheet.write('I6', method.user_approver_ids.name, txt)

        reverts = self.env['audit.revert'].search(
            [('res_id', '=', method.id), ('res_model', '=', method._name)])
        if method.feedback:
            sheet.write('B8', 'Revert Comments', small_head)
            sheet.merge_range('C8:G8', method.feedback, txt)
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
                row = + 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

