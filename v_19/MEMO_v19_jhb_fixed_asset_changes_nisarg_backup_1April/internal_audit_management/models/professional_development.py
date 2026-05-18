# -*- coding: utf-8 -*-
import base64
import io
import xlsxwriter
from odoo.tools import date_utils
from odoo.tools.safe_eval import json
from odoo import fields, models, _, api
from datetime import date
from bs4 import BeautifulSoup


class ProfessionalDevelopment(models.Model):
    _name = "professional.development"
    _description = 'Professional Development'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'subject'

    project_id = fields.Many2one('project.project', string='Project')
    professional_development_id = fields.Many2one('project.task', string='Project')
    subject = fields.Char(string='Subject', related='project_id.name', readonly=False)
    start_date = fields.Date()
    end_date = fields.Date()
    date_prof = fields.Date(string='Date')
    wp_reference = fields.Char(string='W/P Reference')
    user_preparer_ids = fields.Many2one('res.users', string='Prepared by: ')
    user_reviewer_1_ids = fields.Many2one('res.users', string='First Reviewer: ')
    user_reviewer_2_ids = fields.Many2one('res.users', string='Second Reviewer: ')
    user_approver_ids = fields.Many2one('res.users', string='Approver: ')
    member_details = fields.One2many('member.details','member_detail_id',string='Team consists out of the following members:')
    document_ids = fields.Many2many('ir.attachment',
                                    'documents_attachment_professional_development_rel',
                                    string="Upload Documents")
    state = fields.Selection([('preparer', 'Preparer'),
                              ('first_reviewer', 'First Reviewer'),
                              ('second_reviewer', 'Second Reviewer'),
                              ('approved', 'Approved'),
                              ('reverted', 'Reverted'),
                              ('rejected', 'Rejected')],
                             default="preparer", string="State", tracking=True)

    previous_state = fields.Selection([
        ('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected')])
    feedback = fields.Char(string="Audit Reverts/ Review Notes", tracking=True)
    is_current_user_preparer = fields.Boolean(compute='_compute_is_reviewer',
                                              store=False)

    @api.depends('user_preparer_ids')
    def _compute_is_reviewer(self):
        current_user = self.env.uid
        for rec in self:
            rec.is_current_user_preparer = rec.user_preparer_ids.id == current_user

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sequence_code = 'professional.development'
            vals['wp_reference'] = self.env['ir.sequence'].next_by_code(
                sequence_code)
        res = super(ProfessionalDevelopment, self).create(vals_list)
        return res
    # @api.model
    # def create(self, vals):
    #     vals['wp_reference'] = self.env['ir.sequence'].next_by_code(
    #         'professional.development')
    #     res = super(ProfessionalDevelopment, self).create(vals)
    #     return res

    def action_review(self):
        """method for review"""
        self.state = 'first_reviewer'

    def action_2nd_review(self):
        """Second Review"""
        self.state = 'second_reviewer'

    def action_approve(self):
        """Method for approve"""
        self.state = 'approved'

    def action_mark_discrepancy(self):
        """Action refuse the request"""
        self.state = 'rejected'

    def action_send_back_review(self):
        self.state = 'reverted'
        return {
            'name': 'Audit Reverts/ Review Notes',
            'type': 'ir.actions.act_window',
            'res_model': 'internal.audit.revert.wizard',
            'context': {
                'default_professional_development_id': self.id
            },
            'view_mode': 'form',
            'target': 'new',
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
                     'report_name': 'Professional Development',
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
        sheet.write('H1', "Report Date", txt)
        sheet.write('I1', fields.Date.today(), date)
        sheet.merge_range('F3:J4', "Professional Development", head)
        sheet.write('D7', "W/P Reference : ", small_head)
        sheet.merge_range('E7:F7', method.wp_reference, txt)
        sheet.write('D9', "Project : ", small_head)
        sheet.merge_range('E9:F9', method.project_id.name, txt)
        sheet.write('D11', "Subject : ", small_head)
        sheet.merge_range('E11:F11', method.subject, txt)
        sheet.write('D13', "Period : ", small_head)
        sheet.write('E13', method.start_date, date)
        sheet.write('F13', method.end_date, date)

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
            sheet.write('D24', 'Revert Comments', small_head)
            sheet.merge_range('E24:G24', method.feedback, txt)
        if reverts:
            sheet.write('D26', 'Revert Name', small_head)
            sheet.write('E26', 'Created Date', small_head)
            sheet.write('F26', 'Review Comments', small_head)
            sheet.write('G26', 'Audit Proposal', small_head)
            sheet.write('H26', 'State', small_head)
            row = 26
            col = 3
            for revert in reverts:
                sheet.write(row, col, revert.name, txt)
                sheet.write(row, col + 1, revert.date, date)
                sheet.write(row, col + 2, revert.comments, txt)
                sheet.write(row, col + 3, revert.audit_findings, txt)
                sheet.write(row, col + 4, revert.state, txt)
                row = + 1

        teams = method.member_details
        if teams:
            sheet.write('D30', 'Name: ', small_head)
            sheet.write('E30', 'Employee Number', small_head)
            sheet.write('F30', 'Rank', small_head)
            sheet.write('G30', 'Qualifications', small_head)
            sheet.write('H30', 'Experience', small_head)
            sheet.write('I30', 'Certifications', small_head)
            sheet.write('J30', 'Training Attended', small_head)
            row = 30
            col = 3
            for plan in teams:
                sheet.write(row, col, plan.name.name, txt)
                sheet.write(row, col + 1, plan.employee_number, txt)
                sheet.write(row, col + 2, plan.rank.name, txt)
                sheet.write(row, col + 3, plan.qualifications, txt)
                sheet.write(row, col + 4, plan.experience, txt)
                sheet.write(row, col + 5, plan.certifications, txt)
                sheet.write(row, col + 6, plan.training_attend, txt)
                row += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

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

    def action_update(self):
        self.state = self.previous_state

    def action_send_back_new(self):
        """Action send back to new"""
        self.state = 'preparer'

class MemberDetails(models.Model):
    _name = "member.details"

    member_detail_id = fields.Many2one('professional.development')
    name = fields.Many2one('res.users',string='Name')
    employee_number = fields.Char(string='Employee Number')
    rank = fields.Many2one('hr.job',string='Rank')
    qualifications = fields.Char(string='Qualifications')
    experience = fields.Char(string='Experience')
    certifications = fields.Char(string='Certifications')
    training_attend = fields.Char(string='Training Attended')
