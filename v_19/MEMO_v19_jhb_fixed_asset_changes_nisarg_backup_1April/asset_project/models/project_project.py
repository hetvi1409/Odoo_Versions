from odoo import fields, models


class ProjectProject(models.Model):
    """Inherits from"""
    _inherit = 'project.project'


    def import_project_task(self):
        """Importing project tasks"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import Project',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'import.project.task',
            'context': {
                'default_project_id': self.id
            }
        }