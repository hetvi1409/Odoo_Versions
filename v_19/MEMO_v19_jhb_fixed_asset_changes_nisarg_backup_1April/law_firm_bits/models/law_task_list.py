from odoo import models, fields, _


class LawTask(models.Model):
    _name = 'law.task'
    _description = 'Task'

    name = fields.Char(required=True)
    law_task_type = fields.Selection(selection=[('consultation', 'Consultation'),
                                                ('submission', 'Submission'),
                                                ('trial', 'Trial'),
                                                ('meeting', 'Meeting'),
                                                ('other', 'Other'), ])
    description = fields.Text()


class TaskList(models.Model):
    _name = 'law.task.list'
    _description = 'Task List'

    name = fields.Char(required=True)
    task_ids = fields.Many2many("law.task")
    count_task = fields.Integer(compute="_compute_count_task")

    def _compute_count_task(self):
        for rec in self:
            rec.count_task = len(rec.task_ids)
