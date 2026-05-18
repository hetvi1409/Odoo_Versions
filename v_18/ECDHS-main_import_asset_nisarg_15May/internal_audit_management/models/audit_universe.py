# -*- coding: utf-8 -*-

from odoo import fields, models,_,api
import base64

from werkzeug import urls
import io
import json
import xlsxwriter
from odoo.tools import date_utils


class AuditUniverse(models.Model):
    _name = "audit.universe"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"
    _description = "Audit Universe"

    name = fields.Char(string="Name", required=True)
    sequence_no = fields.Char(string='Sequence Number', readonly=True, copy=False)
    stages = fields.Selection([('draft','Draft'),
        ('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Reviewer'),
        ('reverted', 'Reverted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], 'State', copy=False, default='draft', tracking=True)

    stage = fields.Selection([('draft','Draft'),
        ('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('reverted', 'Reverted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], 'State', default='preparer', tracking=True)

    state = fields.Selection([('in_preparer', 'In Preparer'),
                              ('01_in_progress', 'In Progress'), ('02_changes_requested', 'Changes Requested'),
                              ('03_approved', 'Approved'), ('1_done', 'Done'), ('1_canceled', 'Canceled'),
                              ('04_waiting_normal', 'Waiting'),('in_updated','Updated')],
                             string='State')
    # user_id = fields.Many2one('res.users', related="head_department_id.user_id")


    user_preparer_ids = fields.Many2many('res.users', 'user_audit_preparer_rel',
                                         string="Preparer", tracking=True)
    user_reviewer_1_ids = fields.Many2many('res.users', 'user_first_audit_reviewers_rel',
                                           string="First Reviewer", tracking=True)
    user_reviewer_2_ids = fields.Many2many('res.users', 'user_second_audit_reviewers_rel',
                                           string="Second Reviewer ", tracking=True)
    user_approver_ids = fields.Many2many('res.users', 'user_approvers_audit_rel',
                                         string="Approver", tracking=True)
    period = fields.Char(string="Period",help="Enter the period.")
    start_date = fields.Date(string= "Start Date",help="Enter the start date")
    end_date = fields.Date(string= "End Date",help="Enter the end date")
    audit_line_ids = fields.One2many("audit.universe.lines", 'audit_universe_id',string="Audit Lines")
    audit_revert_line_ids = fields.One2many("audit.universe.tracking", 'audit_universe_revert_id',string="Audit Lines")

    project_id = fields.Many2one('project.project', string="Project")
    feedback = fields.Char(string="Audit Reverts/ Review Notes", tracking=True)

    @api.onchange('start_date', 'end_date')
    def _onchange_period(self):
        """"Return period in string format"""
        for rec in self:
            if rec.start_date:
                period = rec.start_date.strftime("%B %Y")
                if rec.end_date:
                    period += ' - ' + rec.end_date.strftime("%B %Y")
                rec.period = period

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['sequence_no'] = self.env['ir.sequence'].next_by_code('audit.universe')
        records = super(AuditUniverse, self).create(vals_list)
        return records


    def get_list_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=audit.universe&view_type=form' % self.id)
        # Urls = urls.url_join(base_url,
        #                      'web#id=15&action=360&model=audit.finding&view_type=form')

        return Urls

    def action_update(self):
        self.env['audit.universe.tracking'].create({
            'audit_universe_revert_id': self.id,
            'period': self.period,  # Replace with actual fields in audit.task
            'comments': "The revert has been updated",  # Map to appropriate fields  # Example: Link to the source record
            'stage': "Updated",  # Map to appropriate fields  # Example: Link to the source record
        })
        self.state = 'in_updated'
        # Determine recipient IDs based on stage
        if self.stage == 'preparer':
            recipient_ids = self.user_reviewer_1_ids
            self.stages = 'draft'
            self.state = 'in_updated'
        else:
            recipient_ids = self.user_reviewer_2_ids
            self.stages = 'second_reviewer'


        mail_template = self.env.ref(
            'internal_audit_management.email_template_audit_universe_to_update')
        partner_ids = recipient_ids.mapped('partner_id').ids
        email_values = {'recipient_ids': [(6, 0, partner_ids)]}
        mail_template.send_mail(self.id, force_send=True, email_values=email_values)

        self.message_post(body=_('The Audit Universe %s was updated by %s') % (
            self.period, self.env.user.name))
        self.state = '01_in_progress'


    def action_review(self):
        """First Review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_audit_universe_to_review')
        recipient_ids = self.user_reviewer_2_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(body=_('The Audit Universe %s was reviewed by %s') % (
            self.period, self.env.user.name))
        self.stage=  self.stages
        self.stages = 'preparer'
        self.state = '01_in_progress'

    def action_2nd_review(self):
        """Second Review"""
        mail_template = self.env.ref('internal_audit_management.email_template_audit_universe_to_approve')
        recipient_ids = self.user_approver_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Audit Universe %s was reviewed by %s') % (
                self.period, self.env.user.name))
        self.stage = self.stages
        self.stages = 'second_reviewer'
        self.state = 'in_updated'

    def action_approve(self):
        """First Review"""
        mail_template = self.env.ref('internal_audit_management.email_template_audit_universe_to_approve')
        recipient_ids = self.env.user
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Audit Universe %s was Approved by %s') % (
                self.period, self.env.user.name))
        self.stages = 'approved'
        self.state = '03_approved'

    def action_reject(self):
        """First Review"""
        self.state = '1_canceled'
        mail_template = self.env.ref('internal_audit_management.email_template_audit_universe_to_rejected')
        recipient_ids = self.env.user
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Audit Universe %s was Rejected by %s') % (
                self.period, self.env.user.name))
        self.stages = 'rejected'

    def action_revert(self):
        return {
            'name': 'Revert Procedure',
            'type': 'ir.actions.act_window',
            'res_model': 'audit.universe.revert.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_audit_details_id': self.id,
                'default_period': self.period,
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
        sheet.set_column(1, 11, 15, txt)

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
        sheet.write('D5', "Period : ", small_head)
        sheet.write('E5', method.period, txt)
        sheet.write('F5', "State : ", small_head)
        sheet.write('G5', method.stages, txt)

        sheet.write('B6', "Start Date : ", small_head)
        sheet.write('C6', method.start_date, date)
        sheet.write('D6', "End Date : ", small_head)
        sheet.write('E6', method.end_date, date)
        sheet.write('F6', "Preparer : ", small_head)
        sheet.write('G6', ", ".join(user.name for user in method.user_preparer_ids), txt)

        sheet.write('B7', "First Reviewer : ", small_head)
        sheet.write('C7', ", ".join(user.name for user in method.user_reviewer_1_ids), txt)
        sheet.write('D7', "Second Reviewer : ", small_head)
        sheet.write('E7', ", ".join(user.name for user in method.user_reviewer_2_ids), txt)
        sheet.write('F7', "Approver : ", small_head)
        sheet.write('G7', ", ".join(user.name for user in method.user_approver_ids), txt)
        row = 9
        col = 1

        if method.audit_line_ids:
            sheet.write(row, col, 'Number', small_head)
            sheet.write(row, col + 1, 'Process / Activity', small_head)
            sheet.write(row, col + 2, 'Department', small_head)
            sheet.write(row, col + 3, 'Head Of Department', small_head)
            sheet.write(row, col + 4, 'Unit', small_head)
            sheet.write(row, col + 5, 'Unit Head', small_head)
            sheet.write(row, col + 6, 'Identifiable Area Of Audit Interest', small_head)
            row += 1
            for line in method.audit_line_ids:
                sheet.write(row, col, line.sequence, txt)
                sheet.write(row, col + 1, line.activity, txt)
                sheet.write(row, col + 2, line.department_id.name, txt)
                sheet.write(row, col + 3, line.department_head_id.name, txt)
                sheet.write(row, col + 4, line.unit.name, txt)
                sheet.write(row, col + 5, line.unit_head.name, txt)
                sheet.write(row, col + 6, line.audit_interest, txt)
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
