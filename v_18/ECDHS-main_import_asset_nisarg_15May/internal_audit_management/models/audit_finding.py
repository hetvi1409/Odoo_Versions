from odoo import api, fields, models,_
from werkzeug import urls
import base64

import io
import json
import xlsxwriter
from odoo.tools import date_utils
from bs4 import BeautifulSoup




class AuditFinding(models.Model):
    """Communicate Audit Finding"""
    _name = "audit.finding"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Audit Finding"
    _rec_name = 'finding_name'

    stages = fields.Selection([('draft','Draft'),
        ('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'),
        ('find_raised', 'Finding Raised'),
        ('find_response', 'Finding Responded to'),
        ('find_conclude', 'Finding concluded'),
    ], 'State', default='draft', tracking=True, copy=False)
    finding_number = fields.Char(string='Audit Name')
    state = fields.Selection([ ('in_preparer', 'In Preparer'),
        ('01_in_progress', 'In Progress'), ('02_changes_requested', 'Changes Requested'),
        ('03_approved', 'Approved'), ('1_done', 'Done'), ('1_canceled', 'Canceled'), ('04_waiting_normal', 'Waiting'),  ('05_find_rase', 'Finding Raised'), ('06_mgmt_respond', 'Management Respond'), ('07_auditor_conclusion', 'Auditor Conclusion')],
        string='State')
    audit_requirement = fields.Html(string="Audit Requirement", required=True)
    audit_finding = fields.Html(string="Audit Finding",required=True)
    impact = fields.Html(string="Impact")
    internal_control_deficiency = fields.Html(
        string="Internal Control Deficiency")
    recommendation = fields.Html(string="Recommendation")
    management_response = fields.Char(string="Management Response")
    finding_name = fields.Char(string="Name",required=True)
    upload_document_name = fields.Char(string="Name")
    position_id = fields.Many2one('hr.job', string="Position")
    department_id = fields.Many2one('hr.department', string="Department",required=True)
    head_department_id = fields.Many2one('res.users',
                                         string="Head of Department",required=True)
    user_id = fields.Many2one('res.users')
    user_ids = fields.Many2many('res.users', string="Users",
                                compute="_compute_user_ids")
    finding_date = fields.Date(string="Date")
    project_id = fields.Many2one('project.project', string="Project")
    task_id = fields.Many2one('project.task',domain="[('project_id','=',project_id)]",string="Task")

    auditor_conclusion = fields.Char(string="Auditor’s Conclusion")
    is_finding_resolved = fields.Selection([('resolved', 'Resolved'),
                                            ('not_resolved', 'Not Resolved'),
                                            ('partially_resolved',
                                             'Partially Resolved')])
    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Attachment",tracking=True)
    document_ids = fields.Many2many('ir.attachment','doc_attach_rel',string="Documents")
    user_preparer_ids = fields.Many2one('res.users',
                                           string="Preparer", tracking=True)
    user_reviewer_1_ids = fields.Many2one('res.users',
                                           string="First Reviewer", tracking=True)
    user_reviewer_2_ids = fields.Many2one('res.users',
                                           string="Second Reviewer ", tracking=True)
    user_approver_ids = fields.Many2one('res.users', string="Approver", tracking=True)
    manager_approval = fields.Selection([('agree', 'Agree'), ('disagree', 'Disagree')],tracking=True)
    classification =  fields.Selection([('positive', 'Positive'), ('housekeeping', 'Housekeeping'), ('significant', 'Significant'), ('critical', 'Critical')],tracking=True)
    audit_finding_tracking_ids = fields.One2many(
        'audit.finding.tracking', 'audit_finding_tracking_id',
        string='Tracking')
    name_user = fields.Many2one('res.users',string='Name')
    feedback = fields.Char(string="Audit Reverts/ Review Notes", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('task_id') and self.env.context.get('default_task_id'):
                vals['task_id'] = self.env.context.get('default_task_id')
            if not vals.get('project_id') and self.env.context.get('default_project_id'):
                vals['project_id'] = self.env.context.get('default_project_id')
        return super().create(vals_list)

    @api.depends('department_id')
    def _compute_user_ids(self):
        """Compute User IDs for adding domains"""
        for rec in self:
            user = []
            if rec.department_id:
                user = rec.department_id.employee_ids.mapped('user_id').ids
            rec.user_ids = user

    def get_list_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=audit.finding&view_type=form' % self.id   )

        return Urls


    def action_review(self):
        """First Review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_audit_findings_to_review')
        recipient_ids = self.user_reviewer_1_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(body=_('The Audit Findings %s was reviewed by %s') % (
            self.finding_name, self.user_reviewer_1_ids.name))
        self.stages = 'preparer'
        for record in self:
            self.env['audit.finding.tracking'].create({
                'audit_finding_tracking_id': record.id,
                'user_id': self.env.user.id,
                'new_stage_id': 'first_reviewer',
                'comment': 'Created',
                'date': fields.Datetime.now(),
            })

        self.state = '01_in_progress'

    def action_update(self):
        previous_state = self.stages
        self.stages = 'preparer'
        for record in self:
            self.env['audit.finding.tracking'].create({
                'audit_finding_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'first_reviewer',
                'comment': 'Updated',
                'date': fields.Datetime.now(),
            })

    def action_sent_manager(self):
        previous_state = self.stages
        mail_template = self.env.ref(
            'internal_audit_management.email_template_audit_findings_to_mngr')
        recipient_ids = self.head_department_id
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Audit Findings %s was reviewed by %s') % (
                self.finding_name, self.head_department_id.name))
        self.stages = 'find_response'
        for record in self:
            self.env['audit.finding.tracking'].create({
                'audit_finding_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'find_response',
                'comment': 'Sent to Manager',
                'date': fields.Datetime.now(),
            })

    def action_sent_auditor(self):
        previous_state = self.stages
        mail_template = self.env.ref(
            'internal_audit_management.email_template_audit_findings_to_auditor')
        recipient_ids = self.user_preparer_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Audit Findings %s was reviewed by %s') % (
                self.finding_name, self.user_preparer_ids.name))
        self.stages = 'find_conclude'
        for record in self:
            self.env['audit.finding.tracking'].create({
                'audit_finding_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'find_conclude',
                'comment': 'Sent to Auditor',
                'date': fields.Datetime.now(),
            })

    def action_2nd_review(self):
        """Second Review"""
        mail_template = self.env.ref('internal_audit_management.email_template_audit_findings_to_sec_review')
        recipient_ids = self.user_reviewer_2_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Audit Findings %s was reviewed by %s') % (
                self.audit_finding, self.user_reviewer_2_ids.name))
        previous_state = self.stages
        self.stages = 'second_reviewer'
        for record in self:
            self.env['audit.finding.tracking'].create({
                'audit_finding_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'second_reviewer',
                'comment': 'Second Review',
                'date': fields.Datetime.now(),
            })
        self.state = '01_in_progress'

    def action_approve(self):
        """First Review"""
        mail_template = self.env.ref('internal_audit_management.email_template_audit_findings_to_approve')
        recipient_ids = self.user_approver_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Audit Findings %s was Approved by %s') % (
                self.audit_finding, self.user_approver_ids.name))
        previous_state = self.stages
        self.stages = 'approved'
        for record in self:
            self.env['audit.finding.tracking'].create({
                'audit_finding_tracking_id': record.id,
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
        mail_template = self.env.ref('internal_audit_management.email_template_audit_findings_to_rejected')
        recipient_ids = self.user_id
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Audit Findings %s was Rejected by %s') % (
                self.audit_finding, self.env.user.name))
        previous_state = self.stages
        self.stages = 'rejected'
        for record in self:
            self.env['audit.finding.tracking'].create({
                'audit_finding_tracking_id': record.id,
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
            'res_model': 'audit.revert.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_audit_details': self.id,
                'default_audit_findings': self.audit_finding,
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

    def action_excel_findings_report(self):
        plan = self.id
        data = {
            'model_id': self.id,
            'plan': plan
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': self._name,
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Audit Finding Report',
                     },
            'report_type': 'xlsx',
        }

    # def get_xlsx_report(self, data, response):
    #     print("{kjhgffed")

    def get_xlsx_report(self, data, response):
        def clean_html(html_text):
            """Removes HTML tags and returns plain text."""
            if not html_text:
                return "Unknown"
            return BeautifulSoup(html_text, "html.parser").get_text(separator=" ").strip()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Audit Finding Report")

        # Formatting
        head_format = workbook.add_format({'align': 'center', 'bold': True, 'font_size': 20})
        sub_head_format = workbook.add_format({'align': 'center', 'bold': True, 'font_size': 11})
        text_format = workbook.add_format({'align': 'left', 'font_size': 10, 'text_wrap': True})
        date_format = workbook.add_format({'num_format': 'd-m-yyyy', 'align': 'center'})

        # Set Column Widths and Row Heights
        sheet.set_column('A:A', 5)  # Adjust for logo
        sheet.set_column('B:C', 15)
        sheet.set_column('J:K', 12)
        sheet.set_row(0, 40)  # Increase row height for logo

        # Insert Company Logo (Left Side, Bigger & Correctly Aligned)
        company_logo = self.env.company.logo
        if company_logo:
            try:
                image_data = io.BytesIO(base64.b64decode(company_logo))
                sheet.insert_image('A1', "image.png", {
                    'image_data': image_data,
                    'x_scale': 1.5,  # Increase size
                    'y_scale': 1.5,
                    'positioning': 1  # Move and resize with cells
                })
            except Exception:
                sheet.write('A1', "Logo Error", text_format)  # Error placeholder

        # Merge Title in Center
        sheet.merge_range('D1:J1', "Audit Finding Report", head_format)

        # Insert Report Date (Top Right)
        sheet.write('K1', "Report Date:", text_format)
        sheet.write('L1', fields.Date.today(), date_format)

        # Table Headers
        headers = ["Project", "Task", "Audit Requirement","Audit Finding","Impact","Internal Control Deficiency","Name","Position","Department",'HOD',"Reverts"]
        for col, header in enumerate(headers, start=1):
            sheet.write(6, col, header, sub_head_format)  # Shift down for proper spacing

        # Fetch Data
        plan = self.env[self._name].browse(int(data.get('plan', 0)))
        max_length = len("Audit Requirement")  # Start with header length
        max_length_audit_finding = len("Audit Finding")  # Start with header length
        max_length_impact = len("Impact")  # Start with header length
        max_length_audit_control = len("Internal Control Deficiency")  # Start with header length

        if plan.exists():
            row = 8
            sheet.write(row, 1, plan.project_id.name if plan.project_id else "N/A", text_format)
            sheet.write(row, 2, plan.task_id.name if plan.task_id else "Unknown", text_format)
            sheet.write(row, 7, plan.name_user.name if plan.name_user else "Unknown", text_format)
            sheet.write(row, 8, plan.position_id.name if plan.position_id else "Unknown", text_format)
            sheet.write(row, 9, plan.department_id.name if plan.department_id else "Unknown", text_format)
            sheet.write(row, 10, plan.head_department_id.name if plan.head_department_id else "Unknown", text_format)
            sheet.write(row, 11, plan.feedback if plan.feedback else "Unknown", text_format)

            audit_text = clean_html(plan.audit_requirement) if plan.audit_requirement else "Unknown"
            audit_finding_text = clean_html(plan.audit_finding) if plan.audit_finding else "Unknown"
            audit_impact_text = clean_html(plan.impact) if plan.impact else "Unknown"
            audit_internal_control_text = clean_html(plan.internal_control_deficiency) if plan.internal_control_deficiency else "Unknown"
            max_length = max(max_length, len(audit_text))  # Update max length dynamically
            max_length_audit_finding = max(max_length_audit_finding, len(audit_finding_text))  # Update max length dynamically
            max_length_audit_impact = max(max_length_impact, len(audit_impact_text))  # Update max length dynamically
            max_length_audit_internal_control = max(max_length_audit_control, len(audit_internal_control_text))  # Update max length dynamically

            sheet.write(row, 3, audit_text, text_format)  # Write cleaned text
            sheet.write(row, 4, audit_finding_text, text_format)  # Write cleaned text
            sheet.write(row, 5, audit_impact_text, text_format)  # Write cleaned text
            sheet.write(row, 6, audit_internal_control_text, text_format)  # Write cleaned text

            # Adjust row height for better readability
            sheet.set_row(row, 20 + (max_length // 20) * 5)  # Increase row height based on text length
            sheet.set_row(row, 20 + (max_length_audit_finding // 20) * 5)  # Increase row height based on text length
            sheet.set_row(row, 20 + (max_length_audit_impact // 20) * 5)  # Increase row height based on text length
            sheet.set_row(row, 20 + (max_length_audit_internal_control // 20) * 5)  # Increase row height based on text length

        else:
            sheet.write(8, 1, "No Data Found", text_format)

        # Dynamically set column width for "Audit Requirement"
        column_width = min(max_length * 1.2, 100)  # Apply a reasonable max width
        sheet.set_column('D:D', column_width)
        column_width = min(max_length * 1.2, 100)  # Apply a reasonable max width
        sheet.set_column('E:E', column_width)
        column_width = min(max_length * 1.2, 100)  # Apply a reasonable max width
        sheet.set_column('F:F', column_width)
        column_width = min(max_length * 1.2, 100)  # Apply a reasonable max width
        sheet.set_column('G:G', column_width)
        # Set dynamically calculated width

        # Finalize Workbook
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()


class AuditPosition(models.Model):
    """Audit Position"""
    _name = 'audit.position'
    _description = 'Audit Position'

    name = fields.Char(string="Name", required=True)


class AuditRole(models.Model):
    """Audit Team"""
    _name = 'audit.role'
    _description = "Audit Role"

    name = fields.Char(string="Role", required=True)
    type = fields.Selection([('Preparer', 'Preparer'), ('Reviewer_1', 'Reviewer 1'),
                             ('Reviewer_2', 'Reviewer 2'),
                             ('Approver', 'Approver')], required=True)

class AuditFindingTracking(models.Model):
    _name = 'audit.finding.tracking'
    _description = 'Audit Finding Tracking'

    audit_finding_tracking_id = fields.Many2one('audit.finding', string='Audit Finding')
    user_id = fields.Many2one('res.users', string='User')
    previous_stage_id = fields.Selection([
        ('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'),
        ('find_raised', 'Finding Raised'),
        ('find_response', 'Finding Responded to'),
        ('find_conclude', 'Finding concluded'),
    ], default="preparer", string="Previous Stage")
    new_stage_id = fields.Selection([
        ('new', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'),
        ('find_raised', 'Finding Raised'),
        ('find_response', 'Finding Responded to'),
        ('find_conclude', 'Finding concluded'),
    ],default="preparer", string="New Stage")
    comment = fields.Text(string='Comment')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)



