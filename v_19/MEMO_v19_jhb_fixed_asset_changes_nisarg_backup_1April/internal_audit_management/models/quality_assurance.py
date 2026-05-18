import io

import xlsxwriter
import base64
from werkzeug import urls
from odoo import api, fields, models,_
from odoo.exceptions import UserError
from odoo.tools import date_utils
from odoo.tools.safe_eval import json


class QualityAssurance(models.Model):
    _name = "quality.assurance"
    _rec_name = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    general_note = fields.Html(string='General Note')
    name = fields.Many2one('project.project',string='Name')
    subject = fields.Char(string='Subject',related='name.name')
    assurance_number = fields.Char(string='Assurance Number')
    period_start = fields.Date()
    period_end = fields.Date()
    conclusion = fields.Html(string='Conclusion')
    prepared_by = fields.Many2one('res.users')
    reviewed_by = fields.Many2one('res.users')
    state = fields.Selection([('preparer', 'Preparer'),
                              ('first_reviewer', 'First Reviewer'),
                              ('second_reviewer', 'Second Reviewer'),
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
    planing_admin_ids = fields.Many2many('plan.administration',
                                             string='Planning and Administration', default=lambda
            self: self._get_default_pa_lines())
    field_work_phase = fields.Many2many('field.phase', string='Fieldwork phase',default=lambda
            self: self._get_default_fp_lines())
    reporting_phase = fields.Many2many('reporting.phase', string='Reporting phase',default=lambda
            self: self._get_default_rp_lines())
    general = fields.Many2many('general.phase', string='General',default=lambda
            self: self._get_default_general_lines())

    feedback = fields.Char(string="Audit Reverts/ Review Notes", tracking=True)
    previous_state = fields.Selection([
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer')])
    document_ids = fields.Many2many('ir.attachment', string="Documents")

    @api.model
    def _get_default_pa_lines(self):
        return [
            (0, 0, {'requirement': "Was the standard notification letter issued?"}),
            (0, 0, {
                'requirement': "Was annual audit plan developed for the audit?"}),
            (0, 0, {
                'requirement': "Was previous audits, AG's reports considered? (High-level overview)"}),
            (0, 0, {'requirement': "Was entry/engagement meeting documented and a copy submitted to the auditee?"}),
            (0, 0,
             {'requirement': "Was the standard engagement letter issued timeously (Check against the date of the audit programme), signed and/or acknowledged and a copy of the letter retained on the file? "}),
            (0, 0,
             {'requirement': "Did the Engagement letter include the following details: - objectives and scope of work, - Estimated hours, communication channels & methods. (Contents of the engagement letter)"}),
            (0, 0,
             {'requirement': "Was declaration of independence signed?"}),
            (0, 0,
             {'requirement': "Was a preliminary survey questionnaire prepared?"}),
            (0, 0,
             {'requirement': "Was the risks that is relevant to the activity under review assessed and documented? (Risk and control matrix)"}),
            (0, 0,
             {'requirement': "Was the system description documented, approved by auditee, compared to a relevant control framework and key controls documented? (departmental policy/framework/SOP)"}),
            (0, 0,
             {'requirement': "Was the system description verified and where risks (exceptions) are identified reported appropriately? (walkthrough)"}),
            (0, 0,
             {'requirement': "Was an analytical review done? (Only practical from Q2  audits onwards and depends on the type of the audit)"}),
            (0, 0,
             {'requirement': "Have the audit programmes been approved prior to the execution phase and are any adjustments approved promptly? "}),
            (0, 0,
             {'requirement': "Does the audit programme address all the identified risks? (Content of the system description and Risk & Control Matrix)"}),
            (0, 0,
             {
                 'requirement': "Does the audit program cover the objectives and scope indicated in the engagement letter? (Compare the AP and engagement letter)"}),
            (0, 0,
             {
                 'requirement': "Was there a project breakdown and budget?  (No std doc - but should reflect budgeted hrs and stages of the audit)"}),
            (0, 0,
             {
                 'requirement': "Are audit staff available that have the degree of technical training and proficiency required to perform the audit? (skills and experience doc completed)"}),
        ]

    @api.model
    def _get_default_fp_lines(self):
        return [
            (0, 0,{'requirement': "Was an adequate sample selected for testing? (Check WPs for type of sample)"}),
            (0, 0,{'requirement': "Were all the audit working papers and audit programmes properly completed and concluded on? (Ref #4 for audit programme. Check WP's for conclusion)"}),
            (0, 0,{'requirement': "Does the working paper contain the required information? (the source of the documentation, direction of testing, population size, sample size tested and sample method used)"}),
            (0, 0,{'requirement': "Have the audit finding been documented in the required format (All tabs to be completed)?"}),
            (0, 0,{'requirement': "Have the audit findings been discussed with the client? (check minutes of consultation meetings with clients/exit minutes of meeting)"}),
            (0, 0,{'requirement': "Is the audit programme referenced to the relevant work papers?"}),
            (0, 0,{'requirement': "Was adequate documentation collected from the auditee? (Check exceptions vs evidence)"}),
        ]

    @api.model
    def _get_default_rp_lines(self):
        return [
            (0, 0, {
                'requirement': "Have all queries been raised during the audit? (Refer to exception report)"}),
            (0, 0, {
                'requirement': "Are all the findings properly substantiated?"}),
            (0, 0, {
                'requirement': "Has the draft report been prepared according to the required format?"}),
            (0, 0, {
                'requirement': "Does the Audit Report comply with the reporting standards?"}),
            (0, 0, {
                'requirement': "Did the Audit Report present the background, purpose, scope, results of the audit and, where appropriate expression of an opinion?"}),
            (0, 0, {
                'requirement': "If there has been a deviation from the objectives and scope identified in the engagement letter, have the reasons been documented and reported? (Check engagement letter vs AP)"}),
            (0, 0, {
                'requirement': "Has agreed action plans been included in the report?"}),
            (0, 0, {
                'requirement': "Are the reports accurate, objective, clear, concise, constructive, impartion, complete and timely? "}),
            (0, 0, {
                'requirement': "Has the draft report been issued within two weeks after the finalisation of the audit? (Check date of exit meeting vs date of report report issue)"}),
            (0, 0, {
                'requirement': "Has the draft report been discussed with the client and comments obtained within two weeks? (Check time phrames as per the engagement letter)"}),
            (0, 0, {
                'requirement': "Has the final report been submitted to Senior Managers within a week after receipt of the comments? (Manager to Senior Manager)"}),
            (0, 0, {
                'requirement': "Has the final report been issued within two weeks after submission to Senior Managers? (Senior Manager to client)"}),
            (0, 0, {
                'requirement': "Has an exit interview meeting been held with the Client? (Minutes and attendance register)"}),
            (0, 0, {
                'requirement': "Were evaluation forms from clients received and filed? (Check client satisfaction survey)"}),
            (0, 0, {
                'requirement': "Is a distribution list included and was it appropriate?"}),
            (0, 0, {
                'requirement': "Was there any non-compliance by Internal audit to the Internal auditing standards? If any, was this disclosed in the audit report? (Check content of the final report)"}),
        ]

    @api.model
    def _get_default_general_lines(self):
        return [
            (0, 0, {
                'requirement': "Has a permanent file been opened for the department or activity? (TM electronic file)"}),
            (0, 0, {
                'requirement': "Have the cross referencing been done on Teammate "}),
            (0, 0, {
                'requirement': "Has the team members been evaluated on their performance? (Check client satisfaction survey)"}),
            (0, 0, {
                'requirement': "Was the audit reviewed by the Audit Senior and Audit Manager? (Check coaching notes)"}),
            (0, 0, {
                'requirement': "Were coaching notes raised to guide the team and rectify problems?"}),
            (0, 0, {
                'requirement': "Is the Teammate software being used for conducting the audits? (Check if individual exceptions were raised on TM)"}),
            (0, 0, {
                'requirement': "Are the audits conducted straight away on the Master Teammate File rather than working outside of it and being copied into it at a later stage?"}),
            (0, 0, {
                'requirement': "Are all the relevant work papers and templates(after update by Teammate Committee) being utilised for the audits for the stage the audit is in at the time of updates? (Teammate champions)"}),
            (0, 0, {
                'requirement': "Are backups being done on a regular basis, on laptops or other storage devises ?. (Obtain electronic copy of a file from Manager)"}),
            (0, 0, {
                'requirement': "Are the formats for the Notification letter, Engagement letter, audit reports etc. updated by the Teammate Champions being adhered to? (refer to the apporved templates)"}),
            (0, 0, {
                'requirement': "Are all staff at all levels signing off their workpapers soon after completion sends an email to their senior indicating that their work paper is ready for review?"}),
            (0, 0, {
                'requirement': "Is the quality assurance check list being completed after every stage of the audit? (Check if quality check lists are being hyper linked for all stages)"}),
        ]

    def get_form_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=quality.assurance&view_type=form' % self.id)
        return Urls

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sequence_code = 'quality.assurance'
            vals['assurance_number'] = self.env['ir.sequence'].next_by_code(
                sequence_code)
        res = super(QualityAssurance, self).create(vals_list)
        return res

    # @api.model
    # def create(self, vals):
    #     vals['assurance_number'] = self.env['ir.sequence'].next_by_code(
    #         'quality.assurance')
    #     return super(QualityAssurance, self).create(vals)

    def action_review(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_quality_assurance')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'first_reviewer'

    def action_2nd_review(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_quality_assurance_sec')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'second_reviewer'

    def action_send_approver(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_quality_assurance_approve')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'approver'

    def action_revert(self):
        return {
            'name': 'Audit Reverts/ Review Notes',
            'type': 'ir.actions.act_window',
            'res_model': 'internal.audit.revert.wizard',
            'context': {
                'default_quality_assurance_id': self.id
            },
            'view_mode': 'form',
            'target': 'new',
        }

    def action_reject(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_quality_assurance_reject')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'rejected'

    def action_approve(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_quality_assurance_approve')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'approved'

    def action_update(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_quality_assurance_update')
        mail_template.send_mail(self.id, force_send=True)
        self.state = self.previous_state

    def action_print_quality_assurance(self):
        self.ensure_one()
        data = {
            'model_id': self.id,
        }
        return self.env.ref(
            'internal_audit_management.action_print_quality_assurance'
        ).report_action(self, data=data)

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
                     'report_name': 'Quality Assurance',
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
        sheet.merge_range('E2:L3', 'QUALITY ASSURANCE', head)
        sheet.write('D7', "Name : ", small_head)
        sheet.merge_range('E7:F7', method.name.display_name if method.name else ' ', txt)
        sheet.write('D9', "Period : ", small_head)
        sheet.write('E9', method.period_start if method.period_start else ' ', txt)
        sheet.write('F9', '--> ', txt)
        sheet.write('G9', method.period_end if method.period_end else ' ', txt)
        sheet.write('D11', "Approver : ", small_head)
        sheet.merge_range('E11:F11', method.user_approver_ids.name, txt)

        sheet.merge_range('I7:J7', "Preparer : ", small_head)
        sheet.merge_range('K7:L7', method.user_preparer_ids.name, txt)
        sheet.merge_range('I9:J9', "First Reviewer : ", small_head)
        sheet.merge_range('K9:L9', method.user_reviewer_1_ids.name, txt)
        sheet.merge_range('I11:J11', "Second Reviewer : ", small_head)
        sheet.merge_range('K11:L11', method.user_reviewer_2_ids.name, txt)
        sheet.merge_range('I13:J13', "Approver : ", small_head)
        sheet.merge_range('K13:L13', method.user_approver_ids.name, txt)
        plans = method.planing_admin_ids
        if plans:
            sheet.merge_range('D20:H20', ' ', small_head)
            sheet.write('K20', 'Standards', small_head)
            sheet.write('L20', 'Yes', small_head)
            sheet.write('M20', 'No', small_head)
            sheet.write('N20', 'W/P Reference', small_head)
            sheet.write('O20', 'Remark', small_head)
            row = 22
            col = 3
            for plan in plans:
                sheet.merge_range(row, col, row, col + 6, plan.requirement, cell_format)
                sheet.write(row, col + 7, plan.standards, txt)
                sheet.write(row, col + 8, plan.yes_bool, txt)
                sheet.write(row, col + 9, plan.no_bool, txt)
                sheet.write(row, col + 10, plan.wp_ref, txt)
                sheet.write(row, col + 11, plan.remark, txt)
                row += 1

        prelim = method.field_work_phase
        if prelim:
            sheet.merge_range('D44:H44', ' ', small_head)
            sheet.write('K44', 'Standards', small_head)
            sheet.write('L44', 'Yes', small_head)
            sheet.write('M44', 'No', small_head)
            sheet.write('N44', 'W/P Reference', small_head)
            sheet.write('O44', 'Remark', small_head)
            row = 45
            col = 3
            for pre in prelim:
                sheet.merge_range(row, col, row, col + 6, pre.requirement,
                                  cell_format)
                sheet.write(row, col + 7, pre.standards, txt)
                sheet.write(row, col + 8, pre.yes_bool, txt)
                sheet.write(row, col + 9, pre.no_bool, txt)
                sheet.write(row, col + 10, pre.wp_ref, txt)
                sheet.write(row, col + 11, pre.remark, txt)
                row += 1

        field_work = method.reporting_phase
        if field_work:
            sheet.merge_range('D54:H54', ' ', small_head)
            sheet.write('K54', 'Standards', small_head)
            sheet.write('L54', 'Yes', small_head)
            sheet.write('M54', 'No', small_head)
            sheet.write('N54', 'W/P Reference', small_head)
            sheet.write('O54', 'Remark', small_head)
            row = 55
            col = 3
            for fw in field_work:
                sheet.merge_range(row, col, row, col + 6, fw.requirement,
                                  cell_format)
                sheet.write(row, col + 7, fw.standards, txt)
                sheet.write(row, col + 8, fw.yes_bool, txt)
                sheet.write(row, col + 9, fw.no_bool, txt)
                sheet.write(row, col + 10, fw.wp_ref, txt)
                sheet.write(row, col + 11, fw.remark, txt)
                row += 1

        final = method.general
        if final:
            sheet.merge_range('D67:H67', ' ', small_head)
            sheet.write('K67', 'Standards', small_head)
            sheet.write('L67', 'Yes', small_head)
            sheet.write('M67', 'No', small_head)
            sheet.write('N67', 'W/P Reference', small_head)
            sheet.write('O67', 'Remark', small_head)
            row = 68
            col = 3
            for fin in final:
                sheet.merge_range(row, col, row, col + 6, fin.requirement,
                                  cell_format)
                sheet.write(row, col + 7, fin.standards, txt)
                sheet.write(row, col + 8, fin.yes_bool, txt)
                sheet.write(row, col + 9, fin.no_bool, txt)
                sheet.write(row, col + 10, fin.wp_ref, txt)
                sheet.write(row, col + 11, fin.remark, txt)
                row += 1

        reverts = self.env['audit.revert'].search(
            [('res_id', '=', method.id), ('res_model', '=', method._name)])
        if method.feedback:
            sheet.write('D77', 'Revert Comments', small_head)
            sheet.merge_range('D78:H78', method.feedback, txt)
        if reverts:
            sheet.write('K78', 'Revert Name', small_head)
            sheet.write('L78', 'Created Date', small_head)
            sheet.write('M78', 'Review Comments', small_head)
            sheet.write('N78', 'Audit Proposal', small_head)
            sheet.write('O78', 'State', small_head)
            row = 79
            col = 3
            for revert in reverts:
                sheet.write(row, col, revert.name, txt)
                sheet.write(row, col + 1, revert.date, date)
                sheet.write(row, col + 2, revert.comments, txt)
                sheet.write(row, col + 3, revert.audit_findings, txt)
                sheet.write(row, col + 4, revert.state, txt)
                row = + 1
        sheet.merge_range('D88:E88', "General Notes : ", small_head)
        sheet.merge_range('G88:H88', method.general_note, txt)
        sheet.merge_range('K88:L88', "Conclusion : ", small_head)
        sheet.merge_range('N88:P88', method.conclusion, txt)
        sheet.merge_range('D90:E90', "Prepared By : ", small_head)
        sheet.merge_range('G90:H90', method.prepared_by.name, txt)
        sheet.merge_range('K90:L90', "Reviewed By : ", small_head)
        sheet.merge_range('N90:P90', method.reviewed_by.name, txt)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()


class PlanAdministration(models.Model):

    _name = "plan.administration"
    _rec_name = "requirement"

    requirement = fields.Char(string='Requirement')
    standards = fields.Char(string='Standards')
    yes_bool = fields.Boolean(string='Yes')
    no_bool = fields.Boolean(string='No')
    wp_ref = fields.Char(string='WP Ref')
    remark = fields.Char(string='Remark')

class FieldPhase(models.Model):

    _name = "field.phase"
    _rec_name = "requirement"

    requirement = fields.Char(string='Requirement')
    standards = fields.Char(string='Standards')
    yes_bool = fields.Boolean(string='Yes')
    no_bool = fields.Boolean(string='No')
    wp_ref = fields.Char(string='WP Ref')
    remark = fields.Char(string='Remark')

class ReportingPhase(models.Model):

    _name = "reporting.phase"
    _rec_name = "requirement"

    requirement = fields.Char(string='Requirement')
    standards = fields.Char(string='Standards')
    yes_bool = fields.Boolean(string='Yes')
    no_bool = fields.Boolean(string='No')
    wp_ref = fields.Char(string='WP Ref')
    remark = fields.Char(string='Remark')

class GeneralPhase(models.Model):

    _name = "general.phase"
    _rec_name = "requirement"

    requirement = fields.Char(string='Requirement')
    standards = fields.Char(string='Standards')
    yes_bool = fields.Boolean(string='Yes')
    no_bool = fields.Boolean(string='No')
    wp_ref = fields.Char(string='WP Ref')
    remark = fields.Char(string='Remark')