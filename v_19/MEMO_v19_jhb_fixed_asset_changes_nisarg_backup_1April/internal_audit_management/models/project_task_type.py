from odoo import fields, models


class ProjectTaskStage(models.Model):
    """Project Task Stage"""
    _inherit = 'project.task.type'

    prefix = fields.Char(string="Prefix")
