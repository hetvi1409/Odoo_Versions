# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class MultiGoalManagment(models.TransientModel):
    _name = 'multi.goal.managment'
    _description = 'Wizard for Managing Goals for Multiple Employees'

    employee_ids = fields.Many2many('hr.employee',string="Employees", required=True)
    deadline = fields.Date(string="Deadline")
    tag_ids = fields.Many2many('hr.appraisal.goal.tag',string="Tags")
    name = fields.Char(string="Name", required=True,)
    description = fields.Html(string="Description")


    def action_apply_goals(self):
        print("Apply Goal to Employees Called======>",self)
        print("Apply Goal to Employees Called======>",self.read())
        employees = self.employee_ids
        for employee in employees:
            goal = self.env['hr.appraisal.goal'].create({
                'employee_ids': [(6, 0, [employee.id])],
                'employee_id':employee.id,
                'deadline':self.deadline,
                'name':self.name,
                'description':self.description,
                'tag_ids': [(6, 0, self.tag_ids.ids)],

            })
            print('=======>',goal)
            print('=======>',goal.read())
    #     goal = self.goal_id
    #     print("Goal======>",goal)
    #     employees = self.employee_ids
    #     print("Employees======>",employees)
    #
    #
    #     for employee in employees:
    #         existing_goals = self.env['hr.appraisal.goal'].search([
    #             ('id', '=', goal.id),
    #             ('employee_id', '=', employee.id)
    #         ])
    #         if not existing_goals:
    #             new_goal = goal.create({
    #                 # 'employee_id': [(6, 0, [employee.id])],
    #                 'name': goal.name,
    #                 'description': goal.description,
    #                 'deadline': self.deadline,
    #             })
    #             print("New Goal Created:", new_goal)
    #         else:
    #             print("Goal already exists for employee:", employee.name)
    #     return True