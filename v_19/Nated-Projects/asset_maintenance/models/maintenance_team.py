from odoo import api, fields, models


class MaintenanceTeam(models.Model):
    _inherit = 'maintenance.team'

    completed_request_count = fields.Integer(string="Completed request count",
                                             compute="compute_request_count")
    in_progress_request_count = fields.Integer(string="In progress request count",
                                             compute="compute_request_count")
    new_request_count = fields.Integer(string="New request count",
                                             compute="compute_request_count")

    @api.depends('request_ids')
    def compute_request_count(self):
        """Compute request completed count"""
        for team in self:
            completed_request = self.env['maintenance.request'].search([('maintenance_team_id', '=', team.id),])
            completed_request_count = 0
            for rec in completed_request:
                if rec.stage_id.done:
                    completed_request_count += 1
            team.completed_request_count = completed_request_count
            team.in_progress_request_count = self.env['maintenance.request'].search_count(
                [('maintenance_team_id', '=', team.id), ('is_in_progress', '=', True)])
            team.new_request_count = self.env['maintenance.request'].search_count(
                [('maintenance_team_id', '=', team.id), ('stage_id', '=', self.env.ref('maintenance.stage_0').id)])

    def action_view_new_request(self):
        """Action to view new request"""
        print('action_view_new_request')

        return {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance Requests',
            'view_mode': 'kanban,tree,form,pivot,graph,calendar',
            'target': 'current',
            'res_model': 'maintenance.request',
            # 'res_id': self.order_id.id,
            'domain': [('stage_id', '=', self.env.ref('maintenance.stage_0').id)]
        }
