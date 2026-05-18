# -*- coding: utf-8 -*-
from odoo import fields, models


class ProjectCreate(models.TransientModel):
    """Project Create"""
    _name = 'project.create.wizard'

    name = fields.Char(string="Project Name", required=True)
    template_id = fields.Many2one('project.template', string="Project Template", required=True)
    audit_type = fields.Selection(
        [('consulting', 'Consulting'), ('assurance', 'Assurance')])

    def action_submit(self):
        """Create Project"""
        project = self.env['project.project'].create({
            'name': self.name,
            'audit_type': self.audit_type,
            # 'type_ids': self.template_id.type_ids,
            'template_id': self.template_id.id,
            'user_id': self.template_id.user_id.id,
            'department_id': self.template_id.department_id.id,
            'team_member_ids': self.template_id.department_id.employee_ids
        })
        if type(project) == list:
            project = project[0]
        # tasks = self.template_id.task_template_ids
        # for task in tasks:
        #     if not task.parent_id:
        #         task_values = {
        #             'name': task.name,
        #             'project_id': project.id,
        #             'type': task.task_type_id.id,
        #             'stage_id': task.type_id.id,
        #             'task_type': task.task_type,
        #             # 'parent_id': task.parent_id.id if task.parent_id else None,
        #         }
        #         self.env['project.task'].create(task_values)
        # for task in tasks:
        #     if task.parent_id:
        #         parent_task = self.env['project.task'].search([('name', '=', task.parent_id.name), ('project_id', '=', project.id)])
        #         task_values = {
        #             'name': task.name,
        #             'project_id': project.id,
        #             'stage_id': task.stage_id.id,
        #             'task_type': task.task_type,
        #             'parent_id': parent_task.id if parent_task else None,
        #         }
        #         self.env['project.task'].create(task_values)
        # milestones = self.template_id.milestone_ids
        # for milestone in milestones:
        #     milestone.copy().write({'project_id': project.id})
        return {
            'res_model': 'project.project',
            'name': 'Project',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': project.id
        }
        # return project.sudo().action_view_tasks()
