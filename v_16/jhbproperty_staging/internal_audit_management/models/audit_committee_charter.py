import io

import xlsxwriter
import base64
from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import html2plaintext
from odoo.tools import date_utils
from odoo.tools.safe_eval import json
from bs4 import BeautifulSoup


class AuditCommitteeCharter(models.Model):
    """Audit Committee Charter"""
    _name = 'audit.committee.charter'
    _description = "Audit Committee Charter"
    _rec_name = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    project_id = fields.Many2one('project.project', string="Project")

    state = fields.Selection([('in_preparer', 'In Preparer'),
                              ('01_in_progress', 'In Progress'), ('02_changes_requested', 'Changes Requested'),
                              ('03_approved', 'Approved'), ('1_done', 'Done'), ('1_canceled', 'Canceled'),
                              ('04_waiting_normal', 'Waiting')],
                             string='State')
    stages = fields.Selection([('draft','Draft'),
        ('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], 'State', default='draft', tracking=True, copy=False)
    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Upload Audit Committee Charter")
    requirements = fields.Html(string="Requirements", required=True,
                               help="Requirements")
    name = fields.Char(string="Name", required=True,
                               help="Name")
    record_work_done = fields.Html(string="Work done", required=False,
                                   help="Record of work done")
    conclusion = fields.Html(string="Conclusion", required=False,
                             help="Conclusion")
    user_ids = fields.Many2many('res.users', string="Users",
                                compute="_compute_user_ids")
    notes = fields.Html(string="Notes", related="note_id.notes")
    note_id = fields.Many2one('committee.charter.note', copy=False, string="Notes")
    # audit_id = fields.Many2one('audit.request', string="Audit")
    team_id = fields.Many2one('hr.department', string="Team")
    # role_id = fields.Many2one('audit.role', string="Roles")

    user_id = fields.Many2one('res.users', tracking=True,
                              string="Responsible User")
    feedback = fields.Char(string="Feedback", tracking=True)
    audit_committee_charter_tracking_ids = fields.One2many('audit.committee.charter.tracking', 'audit_committee_charter_tracking_id', string='Tracking')
    # comment_ids = fields.One2many('audit.comments', 'committee_charter_id',
    #                               tracking=True, string="Comments")
    document_ids = fields.Many2many('ir.attachment',
                                    'documents_attachment_committee_chatter_rel',
                                    string="Upload Documents")
    user_preparer_ids = fields.Many2one('res.users',
                                         string="Preparer", tracking=True)
    user_reviewer_1_ids = fields.Many2one('res.users',
                                           string="First Reviewer", tracking=True)
    user_reviewer_2_ids = fields.Many2one('res.users',
                                           string="Second Reviewer", tracking=True)
    user_approver_ids = fields.Many2one('res.users',
                                         string="Approver", tracking=True)
    internal_audit_committee_charter_tracking_ids = fields.One2many('audit.committee.charter.tracking', 'audit_committee_charter_tracking_id', string='Tracking')
    folder_id = fields.Many2one('documents.folder', string="Folder")
    sequence_no = fields.Char(string='W/P Reference', readonly=True,
                              copy=False)
    previous_state = fields.Selection([
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer')])

    @api.model_create_multi
    def create(self, vals_list):
        # Assign sequence numbers for each record
        for vals in vals_list:
            vals['sequence_no'] = self.env['ir.sequence'].next_by_code('internal.audit.charter')

        records = super(AuditCommitteeCharter, self).create(vals_list)

        for record, vals in zip(records, vals_list):
            # Create folder if it doesn't exist
            if not record.folder_id:
                folder = record._create_folder(record.name)
                record.folder_id = folder.id

            # Sync attachments if provided
            if 'attachment_ids' in vals:
                record._sync_documents(vals['attachment_ids'])
            if 'document_ids' in vals:
                record._sync_documents(vals['document_ids'])

        return records

    def write(self, vals):
        existing_attachments = self.attachment_ids
        existing_documents = self.document_ids
        res = super(AuditCommitteeCharter, self).write(vals)
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
        """Create a folder in documents.folder if it doesn't exist."""
        folder = self.env['documents.document']
        documents_folder_id = self.env.ref(
            'internal_audit_management.documents_internal_audit_committee_charter_folder').id
        folder = folder.search([('name', '=', name),
                                ('type', '=', 'folder'),
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
        self.env['documents.document'].sudo().search(
            [('attachment_id', 'in', self.attachment_ids.ids)]).unlink()
        self.env['documents.document'].sudo().search(
            [('attachment_id', 'in', self.document_ids.ids)]).unlink()
        return super(AuditCommitteeCharter, self).unlink()

    @api.depends('team_id')
    def _compute_user_ids(self):
        """Compute User IDs for adding domains"""
        for rec in self:
            if rec.team_id:
                rec.user_ids = rec.team_id.employee_ids.mapped('user_id')
            else:
                rec.user_ids = False

    def action_2nd_review(self):
        """Second Review"""
        mail_template = self.env.ref('internal_audit_management.email_template_audit_committee_charter_to_approve')
        recipient_ids = self.user_approver_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('Audit Committee Charter %s was reviewed by %s') % (
                self.name, self.env.user.name))
        previous_state = self.stages
        self.stages = 'second_reviewer'
        for record in self:
            self.env['audit.committee.charter.tracking'].create({
                'audit_committee_charter_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'second_reviewer',
                'comment': 'Second Review',
                'date': fields.Datetime.now(),
            })
        self.state = '01_in_progress'

    def action_revert_comment(self):
        return {
            'name': 'Audit Reverts/ Review Notes',
            'type': 'ir.actions.act_window',
            'res_model': 'internal.audit.revert.wizard',
            'context': {
                'default_audit_committee_charter_id': self.id
            },
            'view_mode': 'form',
            'target': 'new',
        }

    def action_revert(self):
        if not self.feedback:
            raise UserError(_('Please add the Audit Reverts/ Review Notes'))
        previous_state = self.stages
        self.previous_state = previous_state
        res_user_id = ""
        if self.stages == 'first_reviewer':
            res_user_id = self.user_reviewer_1_ids
        if self.stages == 'second_reviewer':
            res_user_id = self.user_reviewer_2_ids
        if self.stages in ['first_reviewer', 'second_reviewer']:
            self.env['audit.revert'].create({
                'res_id': self.id,
                'res_model': self._name,
                'comments': self.feedback,
                'user_id': self.env.uid,
                'record_state': self.stages,
                'reference_type': 'audit_committee_charter',
                'res_user_id': res_user_id.id if res_user_id else None,
            })
            self.stages = 'reverted'
            self.state = '02_changes_requested'
        else:
            self.state = '01_in_progress'
            self.stages = 'preparer'
        for record in self:
            self.env['audit.committee.charter.tracking'].create({
                'audit_committee_charter_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'reverted',
                'comment': 'Reverted',
                'date': fields.Datetime.now(),
            })

    def action_update(self):
        previous_state = self.stages
        self.stages = self.previous_state
        self.state = '01_in_progress'
        for record in self:
            self.env['audit.committee.charter.tracking'].create({
                'audit_committee_charter_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'first_reviewer',
                'comment': 'Updated',
                'date': fields.Datetime.now(),
            })

    def action_reject(self):
        """First Review"""
        self.state = '1_canceled'
        mail_template = self.env.ref('internal_audit_management.email_template_audit_committee_charter_to_rejected')
        recipient_ids = self.user_id
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('Audit Committee Charter %s was Rejected by %s') % (
                self.name, self.env.user.name))
        previous_state = self.stages
        self.stages = 'rejected'
        for record in self:
            self.env['audit.committee.charter.tracking'].create({
                'audit_committee_charter_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'rejected',
                'comment': 'Rejected',
                'date': fields.Datetime.now(),
            })

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

    def get_list_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=audit.committee.charter&view_type=list' % self.id)
        return Urls


    def action_review(self):
        """First Review"""
        mail_template = self.env.ref('internal_audit_management.email_template_internal_audit_committee_charter_to_review')
        recipient_ids = self.user_reviewer_2_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(body=_('Audit Committee Charter %s was reviewed by %s') % (
            self.name, self.env.user.name))
        self.stages = 'preparer'
        for record in self:
            self.env['audit.committee.charter.tracking'].create({
                'audit_committee_charter_tracking_id': record.id,
                'user_id': self.env.user.id,
                'new_stage_id': 'preparer',
                'comment': 'Created',
                'date': fields.Datetime.now(),
            })

        self.state = '01_in_progress'

    # def action_review(self):
    #     """method for review"""
    #     if not self.comment_ids:
    #         raise UserError(_("Please add the comments"))
    #     self.state = 'review'
    #     mail_template = self.env.ref(
    #         'internal_audit_system.email_template_audit_committee_charter_review')
    #     mail_template.send_mail(self.id, force_send=True)

    def action_approve(self):
        """Method for approve"""
        if not self.attachment_ids:
            raise UserError(_("Please Attach the documents"))
        self.state = '03_approved'
        mail_template = self.env.ref(
            'internal_audit_management.email_template_audit_committee_charter_to_approve')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.stages
        for record in self:
            self.env['audit.committee.charter.tracking'].create({
                'audit_committee_charter_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'first_reviewer',
                'comment': 'Updated',
                'date': fields.Datetime.now(),
            })
        self.stages = 'approved'

    def action_mark_discrepancy(self):
        """Action refuse the request"""
        self.state = 'refuse'
        mail_template = self.env.ref(
            'internal_audit_management.email_template_audit_committee_charter_refuse')
        mail_template.send_mail(self.id, force_send=True)

    def action_send_back_review(self):
        """Action SEND BACK TO REVIEW"""
        if not self.feedback:
            raise UserError(_('Please add the feedback'))
        self.state = 'review'
        mail_template = self.env.ref(
            'internal_audit_system.email_template_audit_committee_charter_reviewed')
        mail_template.send_mail(self.id, force_send=True)

    def action_send_back_new(self):
        """Action send back to newt"""
        self.state = 'new'
        mail_template = self.env.ref(
            'internal_audit_system.email_template_audit_committee_charter_new')
        mail_template.send_mail(self.id, force_send=True)
    

    def action_create_note(self):
        """Create a note for the audit methodology"""
        return {
            'name': _('Audit Notes'),
            'type': 'ir.actions.act_window',
            'res_model': 'committee.charter.note',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_audit_committee_charter_id': self.id
            }
        }

    def action_edit_note(self):
        """Edit a note for the audit methodology"""
        return {
            'name': _('Audit Notes'),
            'type': 'ir.actions.act_window',
            'res_model': 'committee.charter.note',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.note_id.id,
            'domain': [('audit_committee_charter_id', '=', self.id)],
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
                     'report_name': 'Audit Committee Chatter',
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
        sheet.merge_range('E2:L3', 'Audit Committee Chatter', head)
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


class InternalAuditCharterNote(models.Model):
    """Audit Methodology Note"""
    _name = 'committee.charter.note'
    _description = 'Audit Committee Charter Template'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    notes = fields.Html(string="Notes")
    audit_committee_charter_id = fields.Many2one('audit.committee.charter',
                                                string="Audit Committee Charter",
                                                required=True)
    state = fields.Selection(
        [('new', 'New'), ('review', 'Review'), ('refuse', 'Refuse'),
         ('approve', 'Approve')], tracking=True,
        default="new", string="State")
    approver_id = fields.Many2one('res.users', string="Approver", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        """Updating values to audit request"""
        records_vals = []
        for values in vals_list:
            if values.get('notes'):
                # Generating name from first line of the description
                text = html2plaintext(values['notes'])
                name = text.strip().replace('*', '').partition("\n")[0]
                values['name'] = (name[:97] + '...') if len(name) > 100 else name
            else:
                values['name'] = _('Untitled Note')
            records_vals.append(values)
        res = super().create(records_vals)
        for rec in res:
            if rec.audit_committee_charter_id:
                rec.audit_committee_charter_id.note_id = rec.id
        return res

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

    # def action_review(self):
    #     """method for review"""
    #     self.state = 'review'
    #
    # def action_approve(self):
    #     """Method for approve"""
    #     self.state = 'approve'
    #     self.approver_id = self.env.uid

    def action_mark_discrepancy(self):
        """Action refuse the request"""
        self.state = 'refuse'

    def action_send_back_review(self):
        """Action SEND BACK TO REVIEW"""
        self.state = 'review'

    def action_send_back_new(self):
        """Action send back to newt"""
        self.state = 'new'
