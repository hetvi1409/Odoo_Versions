import base64

from werkzeug import urls
import io
import json
import xlsxwriter
from odoo.tools import date_utils
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class InternalAuditPlan(models.Model):
    """Internal Audit Plan"""
    _name = 'internal.audit.plan'
    _description = "Internal Audit Plan"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([
        ('new', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'),],
                             default="new", string="State")
    previous_state = fields.Selection([
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer')])
    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Upload Internal Audit Plan")
    name = fields.Char(string="Name", required=True,
                               help="Name")
    user_id = fields.Many2one('res.users', tracking=True,
                              string="Responsible User")
    manager_id = fields.Many2one('hr.employee', string="Manager")
    # company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    feedback = fields.Char(string="Audit Reverts/ Review Notes", tracking=True)
    date_from = fields.Date(string="From Date", required=True)
    date_to = fields.Date(string="To Date", required=True)
    period = fields.Char(string="Period")
    # entity_type_id = fields.Many2one('entity.type', string='Section')
    period_term = fields.Selection(
        [('first', 'Q1'), ('second', 'Q2'),
         ('third', 'Q3'), ('fourth', 'Q4')],
        string="Period", required=False, default='first',
        help="Period of the AOP (e.g., 2024, 2025).")

    arp_ids = fields.One2many('rolling.plan', 'plan_id', string="ARP")
    aop_task_ids = fields.One2many('operational.plan', 'plan_id',
                              string="Annual Operational Plans")
    team_members_ids = fields.Many2many('hr.employee', string="Team Members", compute="_compute_team_members", store=True)
    user_ids = fields.Many2many('res.users', string="Users", compute="_compute_user_ids")
    year_ids = fields.Many2many('arp.year', string="Years")
    user_preparer_ids = fields.Many2one('res.users',string="Preparer",
                                        tracking=True,required=True,)
    user_reviewer_1_ids = fields.Many2one('res.users',string="First Reviewer",
                                           tracking=True,required=True,)
    user_reviewer_2_ids = fields.Many2one('res.users',string="Second Reviewer ",
                                           tracking=True,required=True,)
    user_approver_ids = fields.Many2one('res.users',string="Approver", tracking=True,required=True,)
    internal_audit_plan_tracking_ids = fields.One2many(
        'internal.audit.plan.tracking', 'internal_audit_plan_tracking_id',
        string='Tracking')
    line_ids = fields.One2many('arp.line', 'arp_id', string="Lines")
    arp_count = fields.Integer(string="ARP 1 Year", compute="_compute_arp_count")
    project_ids = fields.One2many('project.project', 'internal_audit_3_years', string="Projects")
    folder_id = fields.Many2one('documents.document', string="Folder", domain=[('type', '=', 'folder')])
    sequence_no = fields.Char(string="Sequence Number")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sequence_code = 'internal.audit.plan'
            vals['sequence_no'] = self.env['ir.sequence'].next_by_code(
                sequence_code)
        res = super(InternalAuditPlan, self).create(vals_list)
        for record in res:
            if not self.folder_id:
                folder = self._create_folder(record.name)
                record.folder_id = folder.id
            if 'attachment_ids' in vals_list:
                self._sync_documents(vals_list['attachment_ids'])
        return res

    # @api.model
    # def create(self, vals):
    #     vals['sequence_no'] = self.env['ir.sequence'].next_by_code('internal.audit.plan')
    #     record = super(InternalAuditPlan, self).create(vals)
    #     if not self.folder_id:
    #         folder = self._create_folder(record.name)
    #         record.folder_id = folder.id
    #     if 'attachment_ids' in vals:
    #         self._sync_documents(vals['attachment_ids'])
    #     return record

    def write(self, vals):
        existing_attachments = self.attachment_ids
        res = super(InternalAuditPlan, self).write(vals)
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
        """Create a folder in documents.document if it doesn't exist."""
        folder = self.env['documents.document']
        documents_folder_id = self.env.ref('internal_audit_management.documents_arp_3_folder').id
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

    def _remove_documents(self, attachment_ids):
        """Remove documents linked to detached attachments."""
        Document = self.env['documents.document']
        documents_to_remove = Document.search(
            [('attachment_id', 'in', attachment_ids)])
        documents_to_remove.unlink()

    def unlink(self):
        self.env['documents.document'].sudo().search([('attachment_id', 'in', self.attachment_ids.ids)]).unlink()
        return super(InternalAuditPlan, self).unlink()

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


    @api.depends('line_ids')
    def _compute_arp_count(self):
        """Compute the number of arp"""
        for rec in self:
            rec.arp_count = len(self.env['rolling.plan'].search([('plan_id', '=', rec.id)]))

    #
    @api.depends()
    def _compute_team_members(self):
        """ Automatically populate employees when the department changes """
        for record in self:
            record.team_members_ids = self.env['hr.employee'].search([('user_id', '!=', False)])


    @api.onchange('date_from', 'date_to')
    def _onchange_period(self):
        """"Return period in string format"""
        for rec in self:
            if rec.date_from and rec.date_to:
                period_from = rec.date_from.strftime("%B %Y")
                period_to = rec.date_to.strftime("%B %Y")
                rec.period = period_from + ' - ' + period_to

    @api.depends('date_form')
    @api.onchange('date_from', 'date_to')
    def _onchange_date_year(self):
        if self.date_from:
            year = self.date_from.year
            year_string_1 = str(year) + ' - ' + str(year + 1)
            year_1 = self.env['arp.year'].search([('name', '=', year_string_1)])
            if not year_1:
                year_1 = self.env['arp.year'].create({'name': year_string_1})
            year_string_2 = str(year + 1) + ' - ' + str(year + 2)
            year_2 = self.env['arp.year'].search([('name', '=', year_string_2)])
            if not year_2:
                year_2 = self.env['arp.year'].create({'name': year_string_2})
            year_string_3 = str(year + 2) + ' - ' + str(year + 3)
            year_3 = self.env['arp.year'].search([('name', '=', year_string_3)])
            if not year_3:
                year_3 = self.env['arp.year'].create({'name': year_string_3})
            self.year_ids = [year_1.id, year_2.id, year_3.id]

    @api.depends()
    def _compute_user_ids(self):
        """Compute User IDs for adding domains"""
        for rec in self:
            user = []
            employee_ids = self.env['hr.employee'].search(
                [('user_id', '!=', False)])
            user = employee_ids.mapped('user_id')
            rec.user_ids = user

    @api.onchange('date_from', 'date_to')
    def _onchange_date(self):
        """Onchange the Date"""
        if self.date_from:
            self.date_to = self.date_from + relativedelta(years=3) + relativedelta(days=-1)
        else:
            self.date_to = ""

    def get_list_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=internal.audit.plan&view_type=list' % self.id)
        return Urls

    def action_review(self):
        """method for review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_internal_audit_plan_review')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.state
        # Concatenate all comments into a single string
        self.state = 'first_reviewer'
        for record in self:
            # Add a new line in the tracking
            self.env['internal.audit.plan.tracking'].create({
                'internal_audit_plan_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': record.state,
                'date': fields.Datetime.now(),
            })

    def action_2nd_review(self):
        """Second Review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_internal_audit_plan_review')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.state
        self.state = 'second_reviewer'
        for record in self:
            # Add a new line in the tracking
            self.env['internal.audit.plan.tracking'].create({
                'internal_audit_plan_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': record.state,
                'date': fields.Datetime.now(),
            })

    def action_approve(self):
        """Method for approve"""
        if not self.attachment_ids:
            raise UserError(_("Please Attach the documents"))
        mail_template = self.env.ref(
            'internal_audit_management.email_template_internal_audit_plan_approve')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.state
        # Concatenate all comments into a single string
        self.state = 'approved'
        for record in self:
            # Add a new line in the tracking
            self.env['internal.audit.plan.tracking'].create({
                'internal_audit_plan_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': record.state,
                'date': fields.Datetime.now(),
            })

    def action_mark_discrepancy(self):
        """Action refuse the request"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_internal_audit_plan_refuse')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.state
        self.state = 'rejected'
        for record in self:
            # Add a new line in the tracking
            self.env['internal.audit.plan.tracking'].create({
                'internal_audit_plan_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': record.state,
                'date': fields.Datetime.now(),
            })

    def action_revert(self):
        """Action SEND BACK TO REVIEW"""
        return {
            'name': 'Audit Reverts/ Review Notes',
            'type': 'ir.actions.act_window',
            'res_model': 'internal.audit.revert.wizard',
            'context': {
                'default_internal_audit_plan_id': self.id
            },
            'view_mode': 'form',
            'target': 'new',
        }

    def action_update(self):
        """Action send back to newt"""
        # self.state = 'new'
        mail_template = self.env.ref(
            'internal_audit_management.email_template_internal_audit_plan_new')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.state
        self.feedback = ""
        # Concatenate all comments into a single string
        self.state = self.previous_state
        for record in self:
            # Add a new line in the tracking
            self.env['internal.audit.plan.tracking'].create({
                'internal_audit_plan_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': record.state,
                'date': fields.Datetime.now(),
            })

    def action_create_arp_1_year(self):
        """Create Arp 1 year"""
        for rec in self:
            for line in rec.line_ids:
                line.action_create_arp_one_year()

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

    def action_view_arp(self):
        """Add a performance"""
        return {
            'name': _('Internal Audit Rolling Plan: 1 Year'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'rolling.plan',
            'target': 'current',
            'domain': [('plan_id', '=', self.id)],
            'context': {
                'default_plan_id': self.id
            }
        }

    def sale_report_excel(self):
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
                     'report_name': 'ARP 3 Year',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        plan = self.env[self._name].browse(int(data['plan']))
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
        sheet.insert_image('J2', "image.png", {
            'image_data': image_data,
            'x_scale': 0.5,  # Scale image if needed
            'y_scale': 0.5,
            'positioning': 1  # Move and resize with cells
        })
        sheet.write('J1', "Report Date" , txt)
        sheet.write('K1', fields.Date.today(), date)

        sheet.merge_range('B2:I3', plan.name, head)
        sheet.write('B5', "Start Date : ", small_head)
        sheet.write('C5', plan.date_from, date)
        sheet.write('D5', "End Date : ", small_head)
        sheet.write('E5', plan.date_to, date)
        sheet.write('F5', "Period : ", small_head)
        sheet.write('G5', plan.period, txt)
        sheet.write('H5', "State : ", small_head)
        sheet.write('I5', plan.state, txt)

        sheet.write('B6', "Preparer: ", small_head)
        sheet.write('C6', plan.user_preparer_ids.name, date)
        sheet.write('D6', "First Reviewer: ", small_head)
        sheet.write('E6', plan.user_reviewer_1_ids.name, date)
        sheet.write('F6', "Second Reviewer:", small_head)
        sheet.write('G6', plan.user_reviewer_2_ids.name, txt)
        sheet.write('H6', "Approver: ", small_head)
        sheet.write('I6', plan.user_approver_ids.name, txt)

        sheet.write('B8', 'Process Name',small_head)
        sheet.write('C8', 'Category',small_head)
        sheet.write('D8', 'Departments',small_head)
        sheet.write('E8', 'Risk Priority',small_head)
        sheet.write('F8', 'Year 1',small_head)
        sheet.write('G8', 'Year 2',small_head)
        sheet.write('H8', 'Year 3',small_head)
        row = 8
        col = 1
        for line in plan.line_ids:
            teams = ""
            sheet.write(row, col, line.name, txt)
            sheet.write(row, col + 1, line.category_id.name, txt)
            sheet.write(row, col + 1, line.category_id.name, txt)
            for team in line.team_ids:
                teams += team.name
            sheet.write(row, col + 2, teams, txt)
            sheet.write(row, col + 3, line.risk_priority_rating, txt)
            sheet.write(row, col + 4, 'Yes' if line.year_1 else 'No', txt)
            sheet.write(row, col + 5, 'Yes' if line.year_2 else 'No', txt)
            sheet.write(row, col + 6, 'Yes' if line.year_3 else 'No', txt)
            row += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

class ARPYear(models.Model):
    """ARP Year"""
    _name = 'arp.year'
    _description = "ARP Year"

    _unique_tag_name = models.Constraint(
        'unique (name)',
        'Name must be unique.',
    )
    name = fields.Char(string="Name", required=True)

class ARPLine(models.Model):
    _name = 'arp.line'
    _description = 'ARP Line'

    arp_id = fields.Many2one('internal.audit.plan', string="ARP 3 year")
    name = fields.Char(string="Process Name", required=True)
    team_ids = fields.Many2many('hr.department', string="Department", required=True)
    risk_priority_rating = fields.Selection([('low', 'Low'),
                                             ('low-medium', 'Low Medium'),
                                             ('medium', 'Medium'),
                                             ('medium-high', 'Medium High'),
                                             ('high', 'High')],
                                            string="Risk Priority Rating",
                                            tracking=True,
                                            default='low', required=True)
    year_1 = fields.Boolean(string="Year 1", required=True)
    year_2 = fields.Boolean(string="Year 2", required=True)
    year_3 = fields.Boolean(string="Year 3", required=True)
    category_id = fields.Many2one('audit.assignment.category',
                                  string='Category', tracking=True)

    def action_create_arp_one_year(self):
        """Create ARP 1 year"""
        vals = {
            'name': self.name,
            'risk_priority_rating': self.risk_priority_rating,
            'plan_id': self.arp_id.id,
            'category_id': self.category_id.id,
            'department_ids': self.team_ids,
            'user_preparer_ids': self.arp_id.user_preparer_ids.id,
            'user_reviewer_1_ids': self.arp_id.user_reviewer_1_ids.id,
            'user_reviewer_2_ids': self.arp_id.user_reviewer_2_ids.id,
            'user_approver_ids': self.arp_id.user_approver_ids.id,
        }
        for year in self.arp_id.year_ids:
            year = self.arp_id.date_from.year
            year_string_1 = str(year) + ' - ' + str(year + 1)
            year_1 = self.env['arp.year'].search([('name', '=', year_string_1)])
            year_string_2 = str(year + 1) + ' - ' + str(year + 2)
            year_2 = self.env['arp.year'].search([('name', '=', year_string_2)])
            year_string_3 = str(year + 2) + ' - ' + str(year + 3)
            year_3 = self.env['arp.year'].search([('name', '=', year_string_3)])
        if self.year_1:
            vals['arp_year_id'] = year_1.id
            plan = self.env['rolling.plan'].search([
                ('name', '=', self.name), ('plan_id', '=', self.arp_id.id),
                ('arp_year_id', '=', year_1.id)])
            if not plan:
                plan_new = self.env['rolling.plan'].create(
                    vals
                )
                plan_new._onchange_year_plan()
        if self.year_2:
            vals['arp_year_id'] = year_2.id
            plan = self.env['rolling.plan'].search([
                ('name', '=', self.name), ('plan_id', '=', self.arp_id.id),
                ('arp_year_id', '=', year_2.id)])
            if not plan:
                plan_new = self.env['rolling.plan'].create(
                    vals
                )
                plan_new._onchange_year_plan()
        if self.year_3:
            vals['arp_year_id'] = year_3.id
            plan = self.env['rolling.plan'].search([
                ('name', '=', self.name), ('plan_id', '=', self.arp_id.id),
                ('arp_year_id', '=', year_3.id)])
            if not plan:
                plan_new = self.env['rolling.plan'].create(
                    vals
                )
                plan_new._onchange_year_plan()
