from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def action_create_maintenance(self):
        """Create maintenance from ticket"""
        maintenance = self.env['maintenance.request'].create({
            "name": self.name,
            'maintenance_type': 'preventive',
        })
        self.stage_id = self.env.ref('helpdesk.stage_in_progress').id

