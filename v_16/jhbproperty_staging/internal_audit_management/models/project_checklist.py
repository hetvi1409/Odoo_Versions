import io

import xlsxwriter
import base64
from werkzeug import urls
from odoo import api, fields, models,_
from odoo.exceptions import UserError
from odoo.tools import date_utils
from odoo.tools.safe_eval import json



class ProjectChecklist(models.Model):

    _name = "project.checklist"
    _rec_name = "project_title"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    project_id = fields.Many2one('project.project', string='Project')
    project_title = fields.Char(string='Title', related='project_id.name', readonly=False)
    project = fields.Char(string='Project #',related='project_id.project_number')
    state = fields.Selection([('preparer', 'Preparer'),
                              ('first_reviewer', 'First Reviewer'),
                              ('second_reviewer', 'Reviewer'),
                              ('approver', ''),
                              ('approved', 'Approved'),
                              ('reverted', 'Reverted'),
                              ('rejected', 'Rejected')], tracking=True,
                             default="preparer", string="State")
    user_preparer_ids = fields.Many2one('res.users',
                                        string="Preparer")
    user_reviewer_1_ids = fields.Many2one('res.users', string="First Reviewer")
    user_reviewer_2_ids = fields.Many2one('res.users',
                                          string="Second Reviewer")
    user_approver_ids = fields.Many2one('res.users', string="Approver")
    planing_checklist_ids = fields.Many2many('plan.checklist',string='Planing', default=lambda self: self._get_default_lines())
    preliminary_survey_ids = fields.Many2many('preliminary.survey',string='Preliminary Survey', default=lambda self: self._get_default_preliminary())
    field_work_ids = fields.Many2many('field.work',string='Field Work', default=lambda self: self._get_default_work_phase())
    final_phase_ids = fields.Many2many('final.phase',string='Final Phase', default=lambda self: self._get_default_final_phase())
    auditor_in_charge = fields.Many2one('res.users')
    auditor_manager = fields.Many2one('res.users')
    feedback = fields.Char(string="Audit Reverts/ Review Notes", tracking=True)
    previous_state = fields.Selection([
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer')])
    document_ids = fields.Many2many('ir.attachment', string="Documents")
    project_task_id = fields.Many2one('project.task',string='Project Task')

    @api.model
    def _get_default_lines(self):
        return [
            (0, 0, {'description': 'Prepare project assignment form'}),
            (0, 0, {'description': "Review previous audit report, audit customer's replies, and working papers."}),
            (0, 0, {'description': "Prepare summary of prior audit findings and note corrective set forth in audit customer's replies."}),
            (0, 0, {'description': "Review Post-Audit Review Form. (C‑20)."}),
            (0, 0, {'description': "Establish initial audit objectives and scope."}),
        ]

    @api.model
    def _get_default_preliminary(self):
        return [
            (0, 0, {'description': "Conduct an opening conference to discuss audit customer's concerns and revise initial audit objectives as appropriate."}),
            (0, 0, {
                'description': "Familiarize yourself with departmental objectives, how they are attained, how they are monitored, and how results are determined."}),
            (0, 0, {
                'description': "Familiarize yourself with the activities carried out by the department and review the system of control provided over those activities."}),
            (0, 0, {'description': "Obtain copies of written procedures and, if necessary, update them. If there are no written procedures, document the practices followed in the working papers. (refer to the system description)"}),
            (0, 0,
             {'description': "Observe and document the operation (flow of information and reports)."}),
            (0, 0,
             {
                 'description': "Obtain general background information (number of documents handled and source of funding, number of employees, etc.). – refer to preliminary survey under budget analysis and staffing."}),
            (0, 0,
             {
                 'description': "Identify any bank account numbers relevant to the department."}),
            (0, 0,
             {
                 'description': "Draw preliminary conclusion as to adequacy of the system of control and effectiveness of the operation."}),
            (0, 0,
             {
                 'description': "List areas of risk."}),
            (0, 0,
             {
                 'description': "Revise initial audit objectives and scope."}),
            (0, 0,
             {
                 'description': "Prepare audit program."}),
            (0, 0,
             {
                 'description': "Obtain Supervisor's approval of preliminary survey and audit program."}),
        ]

    @api.model
    def _get_default_work_phase(self):
        return [
            (0, 0, {'description': 'Perform and document the reviews and tests set forth in the audit program and analyze results.'}),
            (0, 0, {
                'description': "Be alert for opportunities for cost reduction and system improvements."}),
            (0, 0, {
                'description': "Review and document status of prior audit findings."}),
            (0, 0, {'description': "Prepare summary of findings, review with client and record management comments and corrective actions planned or taken."}),
        ]

    @api.model
    def _get_default_final_phase(self):
        return [
            (0, 0, {'description': 'Review working papers for compliance with the items listed on the Audit Work Paper Review Checklist(C-14.1).'}),
            (0, 0, {
                'description': "Obtain supervisor's approval of work papers."}),
            (0, 0, {
                'description': "Prepare report draft and review with supervisor."}),
            (0, 0, {'description': "Obtain approval for audit customer's review."}),
            (0, 0,
             {'description': "Review the report draft with audit customer."}),
            (0, 0,
             {'description': "Modify report draft, if necessary, review revised draft with supervisor and obtain approval for final editing."}),
            (0, 0,
             {'description': "Proof read and reference final report."}),
            (0, 0,
             {'description': "Complete the Project Time Record."}),
            (0, 0,
             {'description': "Prepare a Post-Audit Review Form."}),
            (0, 0,
             {'description': "Prepare Audit Customer Survey form and distribute to audit customer."}),
        ]

    def get_form_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=project.checklist&view_type=form' % self.id)
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
                     'report_name': 'Project Checklist',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
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
        sheet.write('H1', "Report Date", txt)
        sheet.write('I1', fields.Date.today(), date)
        sheet.merge_range('E2:L3', 'PROJECT CHECKLIST AND AUDIT CONSIDERATIONS', head)
        sheet.write('D7', "Title : ", small_head)
        sheet.merge_range('E7:F7', method.project_title, txt)
        sheet.write('D9', "Project : ", small_head)
        sheet.merge_range('E9:F9', method.project_id.name, txt)
        sheet.write('D11', "Project #: ", small_head)

        sheet.merge_range('I7:J7', "Preparer : ", small_head)
        sheet.merge_range('K7:L7', method.user_preparer_ids.name, txt)
        sheet.merge_range('I9:J9', "First Reviewer : ", small_head)
        sheet.merge_range('K9:L9', method.user_reviewer_1_ids.name, txt)
        sheet.merge_range('I11:J11', "Second Reviewer : ", small_head)
        sheet.merge_range('K11:L11', method.user_reviewer_2_ids.name, txt)
        sheet.merge_range('I13:J13', "Approver : ", small_head)
        sheet.merge_range('K13:L13', method.user_approver_ids.name, txt)
        plans = method.planing_checklist_ids
        if plans:
            sheet.merge_range('D20:H20', 'Planning: ', small_head)
            sheet.write('K20', 'Date', small_head)
            sheet.write('L20', 'Initials', small_head)
            row = 22
            col = 3
            for plan in plans:
                sheet.merge_range(row, col, row, col + 6, plan.description, cell_format)
                sheet.write(row, col + 7, plan.plan_date if plan.plan_date else ' ', date)
                sheet.write(row, col + 8, plan.initials, txt)
                row += 1

        prelim = method.preliminary_survey_ids
        if prelim:
            sheet.merge_range('D34:H34', 'Preliminary Survey: ', small_head)
            sheet.write('K34', 'Date', small_head)
            sheet.write('L34', 'Initials', small_head)
            row = 34
            col = 3
            for pre in prelim:
                sheet.merge_range(row, col, row, col + 6, pre.description,
                                  cell_format)
                sheet.write(row, col + 7, pre.plan_date if pre.plan_date else ' ', date)
                sheet.write(row, col + 8, pre.initials, txt)
                row += 1

        field_work = method.field_work_ids
        if field_work:
            sheet.merge_range('D54:H54', 'FIELD WORK PHASE: ', small_head)
            sheet.write('K54', 'Date', small_head)
            sheet.write('L54', 'Initials', small_head)
            row = 54
            col = 3
            for fw in field_work:
                sheet.merge_range(row, col, row, col + 6, fw.description,
                                  cell_format)
                sheet.write(row, col + 7, fw.plan_date if fw.plan_date else ' ', date)
                sheet.write(row, col + 8, fw.initials, txt)
                row += 1

        final = method.final_phase_ids
        if final:
            sheet.merge_range('D67:H67', 'FINAL PHASE: ', small_head)
            sheet.write('K67', 'Date', small_head)
            sheet.write('L67', 'Initials', small_head)
            row = 67
            col = 3
            for fin in final:
                sheet.merge_range(row, col, row, col + 6, fin.description,
                                  cell_format)
                sheet.write(row, col + 7, fin.plan_date if fin.plan_date else ' ', date)
                sheet.write(row, col + 8, fin.initials, txt)
                row += 1

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

    def action_review(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_project_checklist')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'first_reviewer'

    def action_2nd_review(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_project_checklist_sec')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'second_reviewer'

    def action_send_approver(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_project_check_approve')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'approver'

    def action_revert(self):
        return {
            'name': 'Audit Reverts/ Review Notes',
            'type': 'ir.actions.act_window',
            'res_model': 'internal.audit.revert.wizard',
            'context': {
                'default_project_checklist_id': self.id
            },
            'view_mode': 'form',
            'target': 'new',
        }

    def action_reject(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_project_checklist_reject')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'rejected'

    def action_approve(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_project_checklist_approve')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'approved'

    def action_update(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_project_checklist_update')
        mail_template.send_mail(self.id, force_send=True)
        self.state = self.previous_state

    def action_print_project_checklist(self):
        self.ensure_one()
        data = {
            'model_id': self.id,
        }
        return self.env.ref(
            'internal_audit_management.action_print_project_checklist'
        ).report_action(self, data=data)

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


class PlanningChecklist(models.Model):

    _name = "plan.checklist"
    _rec_name = "description"

    description = fields.Char(string='Description')
    plan_date = fields.Date(string='Date')
    initials = fields.Char(string='Initials')

class PreliminarySurvey(models.Model):

    _name = "preliminary.survey"
    _rec_name = "description"

    description = fields.Char(string='Description')
    plan_date = fields.Date(string='Date')
    initials = fields.Char(string='Initials')

class FieldWork(models.Model):

    _name = "field.work"
    _rec_name = "description"

    description = fields.Char(string='Description')
    plan_date = fields.Date(string='Date')
    initials = fields.Char(string='Initials')

class FinalPhase(models.Model):

    _name = "final.phase"
    _rec_name = "description"

    description = fields.Char(string='Description')
    plan_date = fields.Date(string='Date')
    initials = fields.Char(string='Initials')

