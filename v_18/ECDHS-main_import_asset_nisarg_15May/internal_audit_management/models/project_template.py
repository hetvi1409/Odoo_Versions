# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, Command


class ProjectTemplate(models.Model):
    """Project Template"""
    _name = 'project.template'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Template Name", required=True)
    user_id = fields.Many2one('res.users', 'Manger', required=True)
    project_id = fields.Many2one('project.project', string="Project")
    project_type = fields.Selection([('EVAL', 'EVAL'), ('IA', 'IA'),
                                     ('MIR', 'MIR')], string="Project")
    department_id = fields.Many2one('hr.department', string='Department')
    # type_ids = fields.Many2many('project.task.type', 'project_template_task_type_rel', string='Tasks Stages')
    # task_ids = fields.Many2many('project.task', string="Default Task",)
    milestone_ids = fields.Many2many('project.milestone', string="Milestone")
    task_template_ids = fields.One2many('project.task.line', 'template_id', string="Tasks")

    @api.onchange('project_id')
    def _onchange_project_id(self):
        """Onchange the project details"""
        if self.project_id:
            self.sudo().write({
                'milestone_ids': [Command.link(milestone.id) for milestone in self.project_id.milestone_ids],
            })

    def action_create_project(self):
        """Create a new project"""
        action = self.env.ref('internal_audit_management.action_project_create_wizard')
        result = action.read()[0]
        result['context'] = {
            'default_template_id': self.id,
        }
        return result

class ProjectTaskLine(models.Model):
    """Project Task Line"""
    _name = 'project.task.line'
    _description = "Task Templates"


    template_id = fields.Many2one('project.template', string="Template")
    name = fields.Char(string="Task Name", required=True)
    # task_id = fields.Many2one('project.task', string="Task Name", required=True)
    parent_id = fields.Many2one('project.task', string="Parent Task Name")
    type_id = fields.Many2one('project.task.type', string="Task Stage", required=True)
    task_type_id = fields.Many2one('task.type', string="Task Type", required=True)
    task_type = fields.Selection([('plan_1', 'Plan 1'), ('plan_2', 'Plan 2'),
                                  ('plan_3', 'Plan 3'), ('plan_4', 'Plan 4'),
                                  ('plan_5', 'Plan 5'), ('plan_6', 'Plan 6'),
                                  ('plan_7', 'Plan 7'), ('plan_8', 'Plan 8'),
                                  ('plan_9', 'Plan 9'), ('plan_10', 'Plan 10'),('exec_1', 'EXEC 1'),
                                  ('exec_2', 'EXEC 2'), ('exec_3', 'EXEC 3'),
                                  ('rep_1', 'REP 1'), ('rep_2', 'REP 2'),
                                  ('rep_3', 'REP 3'), ('rep_4', 'REP 4'), ('rep_5', 'REP 5'),('pro_mgt_1','PM 1'),('pro_mgt_2','PM 2'),('pro_mgt_3','PM 3'),('pro_mgt_4','PM 4'),('pro_mgt_5','PM 5')], string="Type" , related="task_type_id.task_type")


    @api.onchange('task_type_id')
    def _onchange_project_id(self):
        """Onchange the project details"""
        if self.task_type_id:
            self.task_type = self.task_type_id.task_type
            self.name = self.task_type_id.name
            self.type_id = self.task_type_id.type_id.id
