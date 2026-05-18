from odoo import fields, models


class AssetMaintenancePlan(models.Model):
    _name = 'asset.maintenance'
    _description = 'Asset Maintenance'

    name = fields.Char(string='Maintenance Plan name', required=True)
    asset_id = fields.Many2one('account.asset')
    equipment_id = fields.Many2one('maintenance.equipment', required=True, related="asset_id.equipment_id")
    request_date = fields.Date(string='Request Date', default=fields.Date.today())
    maintenance_type = fields.Selection([('corrective', 'Corrective'), ('preventive', 'Preventive')], string='Maintenance Type', default="corrective")
    duration = fields.Date(string='Duration')
    duration_plan = fields.Float('Duration')
    scheduled_date = fields.Date(string='Scheduled Date')

    def create_maintenance_request(self):
        maintenance = self.env['maintenance.request'].create({
            "name": self.name,
            'equipment_id': self.equipment_id.id,
            'request_date': self.request_date,
            'maintenance_type': self.maintenance_type,
            'duration': self.duration_plan,
            'schedule_date': self.scheduled_date,
            'asset_id': self.asset_id.id
        })

    def write(self, vals):
        res = super(AssetMaintenancePlan, self).write(vals)
        return res