from odoo import fields, models


class MaintenanceJobCard(models.TransientModel):
    _name = 'maintenance.job.card'
    _description = 'Maintenance Job Card'


    maintenance_id = fields.Many2one('maintenance.request')
    name = fields.Char(string='Name', required=True)
    start_date = fields.Date(string='Job card start date', required=True)
    planned_hours = fields.Float('Planned Hours', required=True,
                                 help="Planned hour for this task")

    def action_create_job_card(self):
        """Create a new job card"""
        self.env['job.card'].create({
            'name': self.name,
            'maintenance_id': self.maintenance_id.id,
            'project_id': self.maintenance_id.project_id.id,
            'start_date': self.start_date,
            'planned_hours': self.planned_hours
        })
