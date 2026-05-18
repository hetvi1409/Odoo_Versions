# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError



class ProjectProject(models.Model):
    _inherit = 'project.project'

    plan_id = fields.Many2one('internal.audit.plan', string="Plan")
    department_id = fields.Many2one('hr.department', string='Team')
    project_estimated_start_date = fields.Date(string='Estimated Start Date')
    project_estimated_end_date = fields.Date(string='Estimated End  Date')
    project_scheduled_start_date = fields.Date(string='Scheduled Start Date')
    project_scheduled_end_date = fields.Date(string='Scheduled End Date')
    project_actual_start_date = fields.Date(string='Actual Start Date')
    project_actual_end_date = fields.Date(string='Actual End Date')
    internal_audit_3_years = fields.Many2one('internal.audit.plan',string='Internal Audit 3 year Plan')
    internal_audit_1_years = fields.Many2one('project.project',string='Internal Audit 1 year')
    internal_audit_1_year_id = fields.Many2one('rolling.plan', string='Internal Audit 1 year Plan')
    aop_id = fields.Many2one('operational.plan', string='Internal Audit Operational Plan')
    upload_audit_document_ids= fields.Many2many('ir.attachment',string="Attachment")
    upload_document_name = fields.Char(string="Document Name")
    time_budget_ids = fields.One2many("time.budget", 'project_id',string="Time Budget")
    time_budget_hours = fields.Float(string="Time Budget",compute='_compute_hours')
    project_number = fields.Char(string="Project Number")
    user_preparer_ids = fields.Many2one('res.users',
                                        string="Preparer", tracking=True)
    user_reviewer_1_ids = fields.Many2one('res.users', string="First Reviewer",
                                          tracking=True)
    user_reviewer_2_ids = fields.Many2one('res.users',
                                          string="Second Reviewer ",
                                          tracking=True)
    user_approver = fields.Many2one('res.users', string="Approver",
                                         tracking=True)
    audit_findings = fields.Integer(
        help="To count the number of audit findings",
        compute='_compute_audit_findings')

    template_id = fields.Many2one('project.template',
                                  string="Project Template", )
    team_member_ids = fields.Many2many('hr.employee', string="Team Members")
    audit_type = fields.Selection([('consulting', 'Consulting'),('assurance', 'Assurance')])
    feedback = fields.Char(string="Audit Reverts / Review Notes",
                           tracking=True)
    share_doc_ids = fields.Many2many('documents.document',string='Share Document', compute='_compute_share_doc_ids',store=False)

    q1_allocated_time = fields.Float(string="Q1 Allocated Time",
                                     )
    q2_allocated_time = fields.Float(string="Q2 Allocated Time", )
    q3_allocated_time = fields.Float(string="Q3 Allocated Time", )
    q4_allocated_time = fields.Float(string="Q4 Allocated Time", )
    scope_of_work = fields.Text(string="Scope of Work",
                                help="Detailed scope of the audit work")
    sequence_number = fields.Char(string="ARP Number", related="internal_audit_1_year_id.sequence_no")


    def _compute_share_doc_ids(self):
        for project in self:
            if project.task_ids:
                project.share_doc_ids = self.env['documents.document'].search([
                    ('res_model', '=', 'project.task'),
                    ('res_id', 'in', project.task_ids.ids),
                ])
            else:
                project.share_doc_ids = False

    is_internal_audit_project = fields.Boolean(string="Internal Audit Project",default=False)

    # @api.depends('audit_findings')
    def _compute_audit_findings(self):
        task_id = self.env['project.task'].search([
            ('project_id', '=', self.id)])
        audit_details = []
        for rec in task_id:
            audit_findings = rec.audit_finding_ids.ids
            if audit_findings:
                audit_details.extend(audit_findings)
        self.audit_findings = self.env['audit.finding'].search_count(
            [('id', 'in', audit_details)])
        # task_id = self.env['project.task'].search([
        #     ('project_id', '=', self.id)])
        # audit_details = []
        # for rec in task_id:
        #     audit_findings = rec.audit_finding_ids.ids
        #     if audit_findings:
        #         audit_details.extend(audit_findings)

    @api.depends('time_budget_ids.hours')
    def _compute_hours(self):
        for record in self:
            record.time_budget_hours = sum(record.time_budget_ids.mapped('hours'))

    def action_send_back_review(self):
        return {
            'name': 'Audit Reverts/ Review Notes',
            'type': 'ir.actions.act_window',
            'res_model': 'internal.audit.revert.wizard',
            'context': {
                'default_project_project_id': self.id
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

    @api.onchange('department_id')
    def _onchange_department(self):
        """Change department"""
        self.team_member_ids = self.department_id.employee_ids

    @api.model_create_multi
    def create(self, vals_list):
        created_projects = []

        for vals in vals_list:
            vals['allow_timesheets'] = False
            vals['project_number'] = self.env['ir.sequence'].next_by_code('project.project')
            project = super(ProjectProject, self).create([vals])[0]  # Create the project

            # Determine template
            template_id = None
            if not vals.get('template_id'):
                template_id = self.env.ref('internal_audit_management.project_template_data_1',
                                           raise_if_not_found=False)
            if vals.get('template_id'):
                template_id = self.env['project.template'].browse(int(vals.get('template_id')))

            # Apply template tasks and milestones
            if template_id:
                tasks = template_id.task_template_ids
                project.template_id = template_id.id
                project.department_id = template_id.department_id.id
                project.user_id = template_id.user_id.id
                project.team_member_ids = template_id.department_id.employee_ids

                for task in tasks:
                    if not task.parent_id:
                        task_values = {
                            'name': task.name,
                            'project_id': project.id,
                            'stage_id': task.type_id.sudo().id,
                            'task_type': task.task_type,
                            'type': task.task_type_id.id
                        }
                        self.env['project.task'].create(task_values)

                for milestone in template_id.milestone_ids:
                    milestone.copy().write({'project_id': project.id})

            created_projects.append(project)

        return created_projects

    def action_view_audit_findings(self):
        task_id = self.env['project.task'].search([
            ('project_id', '=', self.id)])
        audit_details = []
        for rec in task_id:
            audit_findings = rec.audit_finding_ids.ids
            if audit_findings:
                audit_details.extend(audit_findings)
        return {
            'res_model': 'audit.finding',
            'name': ' Audit Findings',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'domain': [('id', 'in', audit_details)],
            'context': {'default_project_id': self.id}

        }

        # audit_findings = self.env['audit.finding'].search([
        #     ('task_id', 'in', self.audit_finding_ids.ids)  # Assuming task_ids is the one2many field in project.project
        # ])
    #     return {
    #         'res_model': 'project.task',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'list'
    #
    # }
