# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    is_internal = fields.Boolean("Internal Audit")
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
    upload_audit_document_ids= fields.Many2many('ir.attachment', 'upload_audit_document_rel', string="Attachment")
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

    # @api.depends('audit_findings')
    def _compute_audit_findings(self):
        task_id = self.env['project.task'].sudo().search([
            ('project_id', '=', self.id)])
        audit_details = []
        for rec in task_id:
            audit_findings = rec.audit_finding_ids.ids
            if audit_findings:
                audit_details.extend(audit_findings)
        self.audit_findings = self.env['audit.finding'].sudo().search_count(
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
        """Handle multi-create safely (called during XML data load)."""
        prepared = []
        for vals in vals_list:
            v = dict(vals or {})
            v.setdefault('allow_timesheets', False)
            try:
                v['project_number'] = self.env['ir.sequence'].next_by_code('project.project') or False
            except Exception:
                v['project_number'] = False
            prepared.append(v)

        # Prefer calling parent create with the whole list (if parent supports model_create_multi).
        # If parent is not multi-create aware, fall back to creating records one-by-one.
        try:
            records = super(ProjectProject, self).create(prepared)
        except Exception:
            _logger.info('Parent create failed for multi-create, falling back to per-record create')
            records = self.browse()
            for v in prepared:
                rec = super(ProjectProject, self).create(v)
                records |= rec

        # Post-process each created record to apply template behaviour (tasks, milestones, defaults)
        for rec, orig_vals in zip(records, prepared):
            template_id = None
            if not orig_vals.get('template_id'):
                try:
                    template_id = self.env.ref('internal_audit_management.project_template_data_1')
                except Exception:
                    template_id = None
            else:
                try:
                    template_id = self.env['project.template'].browse(int(orig_vals.get('template_id')))
                except Exception:
                    template_id = None

            if template_id:
                tasks = template_id.task_template_ids
                rec.template_id = template_id.id
                rec.department_id = template_id.department_id.id if template_id.department_id else False
                rec.user_id = template_id.user_id.id if template_id.user_id else False
                rec.team_member_ids = template_id.department_id.employee_ids if template_id.department_id else False

                for task in tasks:
                    if not task.parent_id:
                        task_values = {
                            'name': task.name,
                            'project_id': rec.id,
                            'stage_id': (task.type_id.sudo().id if task.type_id else False),
                            'task_type': getattr(task, 'task_type', False),
                            'type': (task.task_type_id.id if getattr(task, 'task_type_id', False) else False)
                        }
                        try:
                            self.env['project.task'].create(task_values)
                        except Exception:
                            _logger.exception('Could not create project.task from template task %s', task.id)

                for milestone in template_id.milestone_ids:
                    try:
                        milestone.copy().write({'project_id': rec.id})
                    except Exception:
                        _logger.exception('Could not copy milestone %s for project %s', milestone.id, rec.id)

        return records

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
