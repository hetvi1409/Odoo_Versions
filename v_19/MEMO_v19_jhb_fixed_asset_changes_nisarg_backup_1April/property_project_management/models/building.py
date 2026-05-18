from odoo import fields, models, _


class Building(models.Model):
    """Class for building"""
    _inherit = 'building'

    task_count = fields.Integer(string='Task Count', compute="compute_task_count")
    def create_project_task(self):
        """Method for create task"""
        return {
            'name': _('Tasks'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'project.task',
            'target': 'new',
            'context': {
                'default_project_id': self.env.ref('property_project_management.project_project_management').id,
                'default_partner_id': self.partner_id.id,
                'default_property_id': self.id
            }
        }

    def compute_task_count(self):
        for rec in self:
            rec.task_count = self.env['project.task'].search_count(
                [('property_id', '=', self.id)])
            
    def get_task_details(self):
        """Methode for show the task details"""
        tasks = self.env['project.task'].search([('property_id', '=', self.id)])
        action = {
            'name': _('Task Details'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'context': {'create': False},
        }
        if len(tasks) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': tasks.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', tasks.ids)],
            })
        return action
