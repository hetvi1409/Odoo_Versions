# -*- coding: utf-8 -*-
from odoo import api, models, fields


class Project(models.Model):
    _name = 'task.type'
    _rec_name = 'task_name'

    name = fields.Char(help="Enter the task type")
    task_name = fields.Char(string="Task Name", required=True)
    task_type = fields.Selection([('plan_1', 'Plan 1'), ('plan_2', 'Plan 2'),
                                  ('plan_3', 'Plan 3'), ('plan_4', 'Plan 4'),
                                  ('plan_5', 'Plan 5'), ('plan_6', 'Plan 6'),
                                  ('plan_7', 'Plan 7'), ('plan_8', 'Plan 8'),
                                  ('plan_9', 'Plan 9'), ('plan_10', 'Plan 10'), ('exec_1', 'EXEC 1'),
                                  ('exec_2', 'EXEC 2'), ('exec_3', 'EXEC 3'),
                                  ('rep_1', 'REP 1'), ('rep_2', 'REP 2'),
                                  ('rep_3', 'REP 3'), ('rep_4', 'REP 4'), ('rep_5', 'REP 5'),('pro_mgt_1','PM 1'),('pro_mgt_2','PM 2'),('pro_mgt_3','PM 3'),('pro_mgt_4','PM 4'),('pro_mgt_5','PM 5')],
                                 string="Type", required=True, default="plan_1")
    type_id = fields.Many2one('project.task.type', string="Task Stage",
                              required=True)
    edms_template = fields.Many2one('memo.template', string='EDMS Template')


    @api.onchange('task_type', 'task_name')
    def _onchange_task(self):
        """update the name"""
        task_type = {
            'plan_1': 'Plan 1', 'plan_2': 'Plan 2',
            'plan_3': 'Plan 3', 'plan_4': 'Plan 4',
            'plan_5': 'Plan 5', 'plan_6': 'Plan 6',
            'plan_7': 'Plan 7', 'plan_8': 'Plan 8',
            'plan_9': 'Plan 9', 'plan_10': 'Plan 10', 'exec_1': 'EXEC 1',
            'exec_2': 'EXEC 2', 'exec_3': 'EXEC 3',
            'rep_1': 'REP 1', 'rep_2': 'REP 2',
            'rep_3': 'REP 3', 'rep_4': 'REP 4', 'rep_5': 'REP 5', 'pro_mgt_1' : 'PM 1',
            'pro_mgt_2': 'PM 2', 'pro_mgt_3' : 'PM 3','pro_mgt_4' : 'PM 4','pro_mgt_5' : 'PM 5'
        }
        for rec in self:
            if rec.task_name and rec.task_type:
                rec.name = task_type[rec.task_type] + ' - ' + rec.task_name
