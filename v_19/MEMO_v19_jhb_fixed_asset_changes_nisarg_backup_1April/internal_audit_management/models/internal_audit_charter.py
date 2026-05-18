from werkzeug import urls
from odoo.tools import html2plaintext
import base64
import io
import xlsxwriter
from werkzeug import urls
from odoo.tools import date_utils
from odoo.tools.safe_eval import json
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import html2plaintext


class InternalAuditCharter(models.Model):
    """Internal Audit Charter"""
    _name = 'internal.audit.charter'
    _description = "Internal Audit Charter"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([('in_preparer', 'In Preparer'),
                              ('01_in_progress', 'In Progress'), ('02_changes_requested', 'Changes Requested'),
                              ('03_approved', 'Approved'), ('1_done', 'Done'), ('1_canceled', 'Canceled'),
                              ('04_waiting_normal', 'Waiting')],
                             string='State')
    stages = fields.Selection([
        ('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'),
    ], 'State', default='preparer', copy=False,
        tracking=True)

    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Upload Internal Audit Charter")
    requirements = fields.Html(string="Requirements", required=True,
                               help="Requirements")
    name = fields.Char(string="Name", required=True,
                               help="Name")
    audit_charter_ids = fields.One2many("audit.charter.tracking", 'audit_charter_tracking_id',string="Charter Lines")

    record_work_done = fields.Html(string="Work done", required=False,
                                   help="Record of work done")
    conclusion = fields.Html(string="Conclusion", required=False,
                             help="Conclusion")
    notes = fields.Html(string="Notes", related="note_id.notes")
    note_id = fields.Many2one('audit.charter.note', copy=False, string="Notes")
    team_id = fields.Many2one('hr.department', string="Team")
    project_id = fields.Many2one('project.project', string="Project")

    # role_id = fields.Many2one('audit.role', string="Roles")
    user_id = fields.Many2one('res.users', tracking=True,
                              string="Responsible User")
    user_ids = fields.Many2many('res.users', string="Users",
                                compute="_compute_user_ids")
    internal_audit_charter_tracking_ids = fields.One2many('audit.charter.tracking', 'audit_charter_tracking_id', string='Tracking')
    # comment_ids = fields.One2many('audit.comments', 'audit_charter_id',
    #                               tracking=True, string="Comments")
    document_ids = fields.Many2many('ir.attachment',
                                    'documents_attachment_audit_chatter_rel',
                                    string="Upload Documents")

    user_preparer_ids = fields.Many2one('res.users',
                                         string="Preparer", tracking=True)
    user_reviewer_1_ids = fields.Many2one('res.users',
                                           string="First Reviewer", tracking=True)
    user_reviewer_2_ids = fields.Many2one('res.users',
                                           string="Second Reviewer ", tracking=True)
    user_approver_ids = fields.Many2one('res.users',
                                         string="Approver", tracking=True)
    folder_id = fields.Many2one('documents.document', string="Folder", domain=[('type', '=', 'folder')])
    sequence_no = fields.Char(string='W/P Reference', readonly=True,
                              copy=False)
    previous_state = fields.Selection([
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer')])
    feedback = fields.Char(string="Audit Reverts/ Review Notes", tracking=True)
    is_current_user_approver = fields.Boolean(compute='_compute_is_reviewer', store=False)
    is_current_user_reviewer = fields.Boolean(compute='_compute_is_reviewer', store=False)
    is_current_user_reviewer2 = fields.Boolean(compute='_compute_is_reviewer', store=False)

    @api.depends('user_approver_ids', 'user_reviewer_1_ids', 'user_reviewer_2_ids')
    def _compute_is_reviewer(self):
        current_user = self.env.uid
        for rec in self:
            rec.is_current_user_approver = rec.user_approver_ids.id == current_user
            rec.is_current_user_reviewer = rec.user_reviewer_1_ids.id == current_user
            rec.is_current_user_reviewer2 = rec.user_reviewer_2_ids.id == current_user

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sequence_code = 'internal.audit.charter'
            vals['sequence_no'] = self.env['ir.sequence'].next_by_code(
                sequence_code)
        res = super(InternalAuditCharter, self).create(vals_list)
        for rec in res:
            if not rec.folder_id:
                folder = self._create_folder(rec.name)
                rec.folder_id = folder.id
            if 'attachment_ids' in vals_list:
                rec._sync_documents(vals_list['attachment_ids'])
            if 'document_ids' in vals_list:
                rec._sync_documents(vals_list['document_ids'])
        return res

    # @api.model
    # def create(self, vals):
    #     vals['sequence_no'] = self.env['ir.sequence'].next_by_code('internal.audit.charter')
    #     record = super(InternalAuditCharter, self).create(vals)
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
        res = super(InternalAuditCharter, self).write(vals)
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
            'internal_audit_management.documents_internal_audit_charter_folder').id
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
        return super(InternalAuditCharter, self).unlink()

    @api.depends('team_id')
    def _compute_user_ids(self):
        """Compute User IDs for adding domains"""
        for rec in self:
            if rec.team_id:
                rec.user_ids = rec.team_id.employee_ids.mapped('user_id')
            else:
                rec.user_ids = False


    def action_review(self):
        """First Review"""
        mail_template = self.env.ref('internal_audit_management.email_template_internal_audit_charter_to_review')
        recipient_ids = self.user_reviewer_2_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(body=_('Internal Audit Charter %s was reviewed by %s') % (
            self.name, self.env.user.name))
        self.stages = 'first_reviewer'
        for record in self:
            self.env['audit.charter.tracking'].create({
                'audit_charter_tracking_id': record.id,
                'user_id': self.env.user.id,
                'new_stage_id': 'first_reviewer',
                'comment': 'Created',
                'date': fields.Datetime.now(),
            })

        self.state = '01_in_progress'

    def action_update(self):
        previous_state = self.stages
        self.stages = self.previous_state
        self.state = '01_in_progress'
        for record in self:
            self.env['audit.charter.tracking'].create({
                'audit_charter_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': self.stages,
                'comment': 'Updated',
                'date': fields.Datetime.now(),
            })

    def action_2nd_review(self):
        """Second Review"""
        mail_template = self.env.ref('internal_audit_management.email_template_audit_charter_to_approve')
        recipient_ids = self.user_approver_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('Internal Audit Charter %s was reviewed by %s') % (
                self.name, self.env.user.name))
        previous_state = self.stages
        self.stages = 'second_reviewer'
        for record in self:
            self.env['audit.charter.tracking'].create({
                'audit_charter_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'second_reviewer',
                'comment': 'Second Review',
                'date': fields.Datetime.now(),
            })
        self.state = '01_in_progress'

    def action_approve(self):
        """First Review"""
        mail_template = self.env.ref('internal_audit_management.email_template_audit_charter_to_approve')
        recipient_ids = self.user_id
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('Internal Audit Charter %s was Approved by %s') % (
                self.name, self.env.user.name))
        previous_state = self.stages
        self.stages = 'approved'
        for record in self:
            self.env['audit.charter.tracking'].create({
                'audit_charter_tracking_id': record.id,
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
        mail_template = self.env.ref('internal_audit_management.email_template_audit_charter_to_rejected')
        recipient_ids = self.user_id
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('Internal Audit Charter %s was Rejected by %s') % (
                self.name, self.env.user.name))
        previous_state = self.stages
        self.stages = 'rejected'
        for record in self:
            self.env['audit.charter.tracking'].create({
                'audit_charter_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'rejected',
                'comment': 'Rejected',
                'date': fields.Datetime.now(),
            })

    def action_revert(self):
        previous_state = self.stages
        for record in self:
            self.env['audit.charter.tracking'].create({
                'audit_charter_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'reverted',
                'comment': 'Reverted',
                'date': fields.Datetime.now(),
            })

        return {
            'name': 'Revert',
            'type': 'ir.actions.act_window',
            'res_model': 'internal.audit.charter.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_audit_details_id': self.id,
                'default_name': self.name,
            },
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

    # @api.onchange('user_id')
    # def _onchange_user_id(self):
    #     """Onchange user id"""
    #     self.team_id = self.user_id.team_id.id
        # self.role_id = self.user_id.role_id.id

    # @api.model
    # def create(self, values):
    #     """Updating values to audit request"""
    #     res = super().create(values)
    #     if res.audit_id:
    #         res.audit_id.internal_audit_charter_id = res.id
    #     return res

    def get_list_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=internal.audit.charter&view_type=list' % self.id)
        return Urls

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
                     'report_name': 'Internal Audit Chatter',
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
        sheet.insert_image('M3', "image.png", {
            'image_data': image_data,
            'x_scale': 0.5,  # Scale image if needed
            'y_scale': 0.5,
            'positioning': 1  # Move and resize with cells
        })
        sheet.write('H1', "Report Date", txt)
        sheet.write('I1', fields.Date.today(), date)
        sheet.merge_range('E2:L3', 'Internal Audit Chatter', head)
        sheet.write('D7', "Name : ", small_head)
        sheet.merge_range('E7:F7', method.name, txt)
        sheet.write('D9', "W/P Reference : ", small_head)
        sheet.merge_range('E9:F9', method.sequence_no, txt)
        sheet.write('D11', "Requirements : ", small_head)
        sheet.merge_range('E11:F11', method.requirements, txt)
        sheet.merge_range('D18:E18', "Work Done : ", small_head)
        sheet.merge_range('G18:J20', method.record_work_done, txt)
        sheet.merge_range('D22:E22', "Conclusion : ", small_head)
        sheet.merge_range('G22:J24', method.conclusion, txt)

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
            sheet.write('F27', 'Revert Comments', small_head)
            sheet.merge_range('G27:H27', method.feedback, txt)
        if reverts:
            sheet.write('F29', 'Revert Name', small_head)
            sheet.write('G29', 'Created Date', small_head)
            sheet.write('H29', 'Review Comments', small_head)
            sheet.write('I29', 'Audit Proposal', small_head)
            sheet.write('J29', 'State', small_head)
            row = 29
            col = 5
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

    def action_mark_discrepancy(self):
        """Action refuse the request"""
        self.state = 'refuse'
        mail_template = self.env.ref(
            'internal_audit_system.email_template_internal_audit_charter_refuse')
        mail_template.send_mail(self.id, force_send=True)

    def action_send_back_review(self):
        """Action SEND BACK TO REVIEW"""
        if not self.feedback:
            raise UserError(_('Please add the feedback'))
        self.state = 'review'
        mail_template = self.env.ref(
            'internal_audit_system.email_template_internal_audit_charter_reviewed')
        mail_template.send_mail(self.id, force_send=True)

    def action_send_back_new(self):
        """Action send back to newt"""
        self.state = 'new'
        mail_template = self.env.ref(
            'internal_audit_system.email_template_internal_audit_charter_new')
        mail_template.send_mail(self.id, force_send=True)
        
    def action_create_note(self):
        """Create a note for the audit methodology"""
        return {
            'name': _('Audit Notes'),
            'type': 'ir.actions.act_window',
            'res_model': 'audit.charter.note',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_internal_audit_charter_id': self.id
            }
        }

    def action_edit_note(self):
        """Edit a note for the audit methodology"""
        return {
            'name': _('Audit Notes'),
            'type': 'ir.actions.act_window',
            'res_model': 'audit.charter.note',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.note_id.id,
            'domain': [('internal_audit_charter_id', '=', self.id)],
        }
    

class InternalAuditCharterNote(models.Model):
    """Audit Methodology Note"""
    _name = 'audit.charter.note'
    _description = 'Internal Audit Charter Template'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    notes = fields.Html(string="Notes")
    internal_audit_charter_id = fields.Many2one('internal.audit.charter', string="Internal Audit Charter", required=True)
    state = fields.Selection([('new', 'New'), ('review', 'Review'), ('refuse', 'Refuse'),
                              ('approve', 'Approve')], tracking=True,
                             default="new", string="State")
    approver_id = fields.Many2one('res.users', string="Approver", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals['notes']:
                text = html2plaintext(vals['notes'])
                name = text.strip().replace('*', '').partition("\n")[0]
                vals['name'] = (name[:97] + '...') if len(
                    name) > 100 else name
            else:
                vals['name'] = _('Untitled Note')

        res = super().create(vals_list)
        for rec in res:
            if rec.internal_audit_charter_id:
                rec.internal_audit_charter_id.note_id = rec.id
        return res

    # @api.model
    # def create(self, values):
    #     """Updating values to audit request"""
    #     if values.get('notes'):
    #         # Generating name from first line of the description
    #         text = html2plaintext(values['notes'])
    #         name = text.strip().replace('*', '').partition("\n")[0]
    #         values['name'] = (name[:97] + '...') if len(name) > 100 else name
    #     else:
    #         values['name'] = _('Untitled Note')
    #     res = super().create(values)
    #     if res.internal_audit_charter_id:
    #         res.internal_audit_charter_id.note_id = res.id
    #     return res

    def write(self, values):
        if values.get('notes'):
            # Generating name from first line of the description
            text = html2plaintext(values['notes'])
            name = text.strip().replace('*', '').partition("\n")[0]
            values['name'] = (name[:97] + '...') if len(name) > 100 else name
        else:
            values['name'] = _('Untitled Note')
        res = super().write(values)
        return res

    def action_review(self):
        """method for review"""
        self.state = 'review'

    def action_approve(self):
        """Method for approve"""
        self.state = 'approve'
        self.approver_id = self.env.uid

    def action_mark_discrepancy(self):
        """Action refuse the request"""
        self.state = 'refuse'

    def action_send_back_review(self):
        """Action SEND BACK TO REVIEW"""
        self.state = 'review'

    def action_send_back_new(self):
        """Action send back to newt"""
        self.state = 'new'
