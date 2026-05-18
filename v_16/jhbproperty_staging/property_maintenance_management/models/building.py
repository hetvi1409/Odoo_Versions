from odoo import fields, models, _


class Maintenance(models.Model):
    _inherit = 'building'

    maintenance_count = fields.Integer(
        string="Maintenance Count",
        help="Maintenance Count",
        compute="_compute_maintenance_count"
    )

    def get_maintenance_request_details(self):
        """Method for getting maintenance request details"""
        maintenance = self.env['helpdesk.ticket'].search([
            ('jmc_number', '=', self.jmc_number)
        ])
        action = {
            'name': _('Maintenance Requests'),
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket',
            'context': {'create': False},
        }
        if len(maintenance) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': maintenance.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', maintenance.ids)],
            })
        return action

    def _compute_maintenance_count(self):
        """Compute the maintenance request count based on the JMC number."""
        for rec in self:
            # Search for maintenance requests with the same JMC number as the property
            maintenance = self.env['helpdesk.ticket'].search_count(
                [('jmc_number', '=', rec.jmc_number)])
            rec.maintenance_count = maintenance
