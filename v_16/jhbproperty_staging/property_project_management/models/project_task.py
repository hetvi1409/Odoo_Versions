from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    property_id = fields.Many2one('building', string="Property")
    project_plan_documents = fields.Many2many('ir.attachment', 'project_task_plan_document_rel', 'task_id',
                                              'document_id', string="Project Plan Documents")
