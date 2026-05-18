# -*- coding: utf-8 -*-
import datetime

import dateutil.utils
from dateutil.utils import today
from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError

class PerformanceContract(models.Model):
    _name = "performance.contract"
    _description = "Employee Performance Contract"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('Name', default=lambda self: _("New"), readonly=True, copy=False)
    employee_id = fields.Many2one("hr.employee", required=True)
    manager_id = fields.Char("Manager", related="employee_id.parent_id.name", readonly=True)
    department_id = fields.Char("Department", related="employee_id.department_id.name", readonly=True)
    job_id = fields.Char("Job Position", related="employee_id.job_id.name", readonly=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("in_process", "In Process"),
        ('signed_by_employee', 'Signed by Employee'),
        ('signed_by_manager', 'Signed by Manager'),
        ("signed", "Signed"),
        ("approval_in_process", "Approval In Process"),
        ("approved", "Approved"),
        ("done", "Completed"),
        ("expired", "Expired"),
        ("rejected", "Rejected"),
    ], default="draft", tracking=True)
    is_locked = fields.Boolean(compute="_compute_is_locked")
    goal_ids = fields.Many2many("hr.appraisal.goal", string="Goals")
    employee_sign_date = fields.Datetime(string="Employee Sign Date")
    manager_sign_date = fields.Datetime(string="Manager Sign Date")
    employee_sign = fields.Binary(string="Employee Signature")
    manager_sign = fields.Binary(string="Company Signature")
    signed_by_manager = fields.Boolean(string="Signed by Manager")
    signed_by_employee = fields.Boolean(string="Signed by Employee")
    start_date = fields.Date('Start Date', default=lambda self: fields.Date.today())
    end_date = fields.Date('End Date')
    attachment_ids = fields.Many2many('ir.attachment','performance_contract_ir_attachments_rel',
        'performance_contract_id','attachment_id',string='Attachments')
    attachment_count = fields.Integer(string='Attachment Count', compute='_compute_attachment_count')


    priority = fields.Selection([('0', 'Low'),('1', 'Normal'),('2', 'High'),('3', 'Very High')], string='Priority', default='1')
    total_weightage = fields.Float(string="Total Weightage", compute="_compute_total_weightage", store=True)
    final_result = fields.Float(string="Final Result", compute='_compute_performance_metrics', store=True)

    approval_team_id = fields.Many2one("approval.team", string="Approval Team", domain="[('model', '=', 'performance.contract')]")
    approval_line_ids = fields.One2many("approval.team.line", "contract_id", string="Approval Lines")

    approval_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('partially_approved', 'Partially Approved'),
        ('fully_approved', 'Fully Approved'),
        ('rejected', 'Rejected'),
    ], default='not_started', tracking=True)
    current_approver_id = fields.Many2one('res.users', string="Current Approver", compute="_compute_current_approver",store=True)
    is_current_approver = fields.Boolean(string="Is Current Approver", compute="_compute_is_current_approver")

    current_employee_skill_new_ids = fields.Many2many("hr.employee.skill", string="Current Employee Skills",
        compute="_compute_current_employee_skills",store=False)

    total_evaluation_score = fields.Float(string="Total Evaluation Score", compute='_compute_performance_metrics', store=True)


    @api.depends('employee_id')
    def _compute_current_employee_skills(self):
        for rec in self:
            if rec.employee_id:
                rec.current_employee_skill_new_ids = rec.employee_id.employee_skill_ids
            else:
                rec.current_employee_skill_new_ids = False


    @api.depends('current_approver_id')
    def _compute_is_current_approver(self):
        for rec in self:
            if rec.current_approver_id == self.env.user:
                rec.is_current_approver = True
            else:
                rec.is_current_approver = False



    @api.depends('approval_line_ids.status', 'approval_line_ids.sequence','approval_team_id')
    def _compute_current_approver(self):
        for rec in self:
            pending_lines = rec.approval_line_ids.filtered(lambda l: l.status == 'pending').sorted('sequence')
            print("\n\n\n PENDING LINES===>",pending_lines)
            rec.current_approver_id = pending_lines[0].user_id if pending_lines else False
            print("\n\n\n CURRENT APPROVER ID===>",rec.current_approver_id)


    # @api.onchange('approval_team_id')
    # def _onchange_approval_team(self):
        # if not self.approval_team_id:
        #     self.approval_line_ids = [(5, 0, 0)]
        #     return

        # lines = []
        # for line in self.approval_team_id.line_ids:
        #     lines.append((0, 0, {
        #         'user_id': line.user_id.id,
        #         'sequence': line.sequence,
        #         'status': 'pending',
        #         'approved': False,
        #     }))

        # self.approval_line_ids = [(5, 0, 0)] + lines



    # @api.onchange('approval_team_id')
    # def _onchange_approval_team(self):
    #     approval_teams = self.env['approval.team'].search([('name', '=', self.approval_team_id.name)])
    #     if approval_teams:
    #         self.approval_line_ids = [(6, 0, approval_teams.line_ids.ids)]
    #     else:
    #         self.approval_line_ids = [(5, 0, 0)]



    def action_start_approval_process(self):
        if not self.approval_team_id:
            approval_team = self.env['approval.team'].search([('model', '=', 'performance.contract')])
            if len(approval_team) > 1:
                raise UserError("Please select an approval team before starting the approval process.")
            else:
                self.approval_team_id = approval_team.id
        self.state = "approval_in_process"
        self.approval_status = 'partially_approved'

        if not self.approval_team_id:
            self.approval_line_ids = [(5, 0, 0)]
            return

        lines = []
        for line in self.approval_team_id.line_ids.sorted('sequence'):
            lines.append((0, 0, {
                'user_id': line.user_id.id,
                'sequence': line.sequence,
                'status': 'pending',
                'approved': False,
            }))

        self.approval_line_ids = [(5, 0, 0)] + lines



    def acction_approve_contract(self):
        print("\n\n\n acction_approve_contract---->",self)
        approval_line = self.approval_line_ids.filtered(lambda line: line.user_id == self.env.user and not line.approved)
        print("\n\n\n Approval line:", approval_line)

        if login_user := self.env.user:
            print("Logged in user:", login_user)

            if login_user != self.current_approver_id:
                print("User is not authorized to approve this contract.")
                raise AccessError(f"You are not authorized to approve this contract. Current approver is {self.current_approver_id.name}.")

            if approval_line:
                approval_line.approved = True
                approval_line.status = 'approved'
                approval_line.approval_date = fields.Datetime.now()
                print("Approval line approved:", approval_line)
                self._update_approval_status()
            else:
                raise AccessError("You are not authorized to approve this contract or have already approved it.")

    def action_reject_contract(self):
        self.ensure_one()
        login_user = self.env.user

        if login_user != self.current_approver_id:
            raise AccessError(_("You are not authorized to reject this contract. Current approver is %s.") % (self.current_approver_id.name or _("Unknown")))

        line = self.approval_line_ids.filtered(lambda l: l.user_id == login_user and l.status == 'pending')[:1]
        if not line:
            raise AccessError(_("No pending approval line found for you."))

        # Mark the line as rejected; user will enter the reason in the popup form
        line.write({
            'status': 'rejected',
            'approval_date': fields.Datetime.now(),
            'approved': False,
        })
        self._update_approval_status()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Reject Contract'),
            'res_model': 'approval.team.line',
            'view_mode': 'form',
            'res_id': line.id,
            'target': 'new',
            'context': {
                'default_contract_id': self.id,
                'default_user_id': login_user.id,
                'form_view_initial_mode': 'edit',
            },
        }



    def _update_approval_status(self):
        total_lines = len(self.approval_line_ids)
        approved_count = len(self.approval_line_ids.filtered(lambda l: l.status == 'approved'))
        rejected_count = len(self.approval_line_ids.filtered(lambda l: l.status == 'rejected'))
        pending_count = len(self.approval_line_ids.filtered(lambda l: l.status == 'pending'))

        print(f"\n\n\n Approved: {approved_count}, Rejected: {rejected_count}, Pending: {pending_count}, Total: {total_lines}")

        if rejected_count > 0:
            self.state = "rejected"
            self.approval_status = 'rejected'
        elif pending_count > 0:
            self.approval_status = 'partially_approved'
        elif total_lines and approved_count == total_lines:
            self.state = "approved"
            self.approval_status = 'fully_approved'
        else:
            self.approval_status = 'partially_approved'



    # @api.depends('total_weightage')
    @api.depends('goal_ids.weightage')
    def _compute_total_weightage(self):
        for record in self:
            total = sum(goal.weightage for goal in record.goal_ids)
            record.total_weightage = total

    @api.constrains('total_weightage')
    def _check_total_amount(self):
        for record in self:
            if record.total_weightage > 100:
                raise UserError("Total weightage of all goals cannot exceed 100.")

    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', self._name),
                ('res_id', '=', record.id)
            ])

    def action_open_attachments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Attachments',
            'res_model': 'ir.attachment',
            'view_mode': 'list,kanban,form',
            'domain': [
                ('res_model', '=', self._name),
                ('res_id', '=', self.id)
            ],
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'default_res_name': self.name,
            }
        }


    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        goal_ids = self.env['hr.appraisal.goal'].search([('employee_ids', 'in', self.employee_id.id)])
        if goal_ids:
            self.goal_ids = [(6, 0, goal_ids.ids)]
        else:
            self.goal_ids = [(5, 0, 0)]


    def employee_sign_contract(self):
        print("Employee Sign Contract Called",self.env.user)
        if self.env.user != self.employee_id.user_id:
            raise AccessError("You are not allowed to sign as employee.")
        self.employee_sign_date = fields.Datetime.now()
        self.state = 'signed_by_employee'
        self.signed_by_employee = True
        return{
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'views': [(self.env.ref('performance_contract.view_performance_contract_form_id').id, 'form')],
        }

    def manager_sign_contract(self):
        print("Manager Sign Contract Called",self.env.user)
        if self.env.user.has_group('base.group_erp_manager'):
            print("ERP Manager - bypassing manager sign check")
            self.manager_sign_date = fields.Datetime.now()
            self.state = 'signed_by_manager'
            self.signed_by_manager = True
            return {
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'new',
                'views': [(self.env.ref('performance_contract.view_performance_contract_form_id_1').id, 'form')],
            }
        else:
            raise AccessError("You are not allowed to sign as manager.")


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals:
                vals['name'] = self.env['ir.sequence'].next_by_code('performance.contract') or _("New")
                vals['end_date'] = fields.Date.to_string(fields.Date.context_today(self).replace(month=12, day=31))
        return super().create(vals_list)


    @api.depends("state")
    def _compute_is_locked(self):
        for rec in self:
            rec.is_locked = rec.state != "draft"

    def action_submit_for_approval(self):
        print("Submit for Approval Called")
        print("USER",self.env.user)
        print("user email",self.env.user.email_formatted)
        if self.total_weightage != 100:
            raise UserError("Total weightage must be 100 before submitting for approval.")
        self.state = "in_process"


        employee_sign_template = self.env.ref('performance_contract.email_template_employee_sign_contract')
        if employee_sign_template:
            employee_sign_template.send_mail(self.id,
                                            email_values={'email_to': self.employee_id.work_email,
                                                          'email_from': self.env.user.email_formatted},
                                            force_send=True)
        manager_sign_template = self.env.ref('performance_contract.email_template_manager_sign_contract')
        if manager_sign_template:
            manager_sign_template.send_mail(self.id,
                                            email_values={'email_to': self.employee_id.parent_id.work_email,
                                                          'email_from': self.env.user.email_formatted},
                                            force_send=True)


    def action_mark_signed(self):
        if self.employee_sign and self.manager_sign:
            self.state = "signed"
        else:
            raise UserError("Both signatures are required to approve the contract.")


    def action_reject(self):
        self.state = "rejected"
        self.approval_line_ids.write({"approved": False})

    def action_set_to_draft(self):
        self.state = "draft"


    def action_mark_done(self):
        self.state = "done"

    @api.depends('total_weightage','goal_ids.result','employee_id.employee_skill_ids.skill_level_progress')
    def _compute_performance_metrics(self):
        for record in self:
            total_w = record.total_weightage or 0.0

            weighted_sum = sum(
                ((g.result or 0.0) * (g.weightage or 0.0))
                for g in record.goal_ids
            )

            if total_w > 0:
                record.final_result = (weighted_sum / total_w) / 100.0
            else:
                record.final_result = 0.0

            skills = record.employee_id.employee_skill_ids
            skill_count = len(skills)
            skills_total_progress = sum(
                (s.skill_level_progress or 0.0) for s in skills
            )

            avg_skill_progress = (skills_total_progress / skill_count if skill_count else 0.0)

            final_result_percent = record.final_result * 100.0
            # print('=====FINAL RESULT PERCENT=====', final_result_percent)
            # print('=====AVG SKILL PROGRESS=====', avg_skill_progress)
            record.total_evaluation_score = (final_result_percent + avg_skill_progress) / 2.0



    def mark_as_complated(self):
        self.state = "done"

# CRON METHODS

    def performance_contract_expire_check(self):
        today = datetime.date.today()
        expired_contracts = self.search([
            ('end_date', '<', today),
            ('state', '!=', 'expired')
        ])
        if expired_contracts:
            expired_contracts.write({'state': 'expired'})

    def send_goal_deadline_reminders(self):
        send_mail_before = int(self.env['ir.config_parameter'].sudo().get_param('performance_contract.send_mail_before', default=3))
        print("Send Mail Before (Days):", send_mail_before)
        today = fields.Date.today()
        print("Today's Date:", today)
        reminder_date = today + datetime.timedelta(days=send_mail_before)
        print("Reminder Date:", reminder_date)

        goals_to_remind = self.env['hr.appraisal.goal'].search([
            ('deadline', '=', reminder_date),
            ('progression', '!=', '100'),
        ])
        print("Goals to remind:", goals_to_remind)

        for goal in goals_to_remind:
            employee = goal.employee_id
            print(f"Sending reminder for Goal ID {goal.id} to Employee: {employee.name}, Email: {employee.work_email}")
            if employee.work_email:
                template = self.env.ref('performance_contract.email_template_goal_deadline_reminder')
                print("Email Template:", template)
                self.env['mail.template'].browse(template.id).send_mail(goal.id, force_send=True)



