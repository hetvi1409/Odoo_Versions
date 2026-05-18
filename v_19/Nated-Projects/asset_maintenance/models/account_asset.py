from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    equipment_id = fields.Many2one('maintenance.equipment')
    maintenance_ids = fields.One2many('asset.maintenance', 'asset_id')
    equipment_state = fields.Selection([('draft', 'Draft'), ('submit', 'Submit'), ('approve', 'Approve'), ('refuse', 'Refuse')])

    def create_equipment(self):
        """Create a equipment from asset"""
        equipment = self.env['maintenance.equipment'].create({
            "name": self.name,
        })
        self.equipment_id = equipment.id


    def create_maintenance_request(self):
        maintenance = self.env['maintenance.request'].create({
            "name": 'Maintenance ' + self.name + ' ' + str(fields.Date.today()),
            'equipment_id': self.equipment_id.id,
            'maintenance_type': 'preventive',
            'asset_id': self.id
        })

    @api.onchange('maintenance_ids')
    def onchange_maintenance_ids(self):
        if self.maintenance_ids:
            self.equipment_state = 'draft'
        else:
            self.equipment_state = ''

    def action_submit(self):
        if self.equipment_state == 'draft':
            if self.maintenance_ids:
                self.equipment_state = 'submit'
            else:
                raise UserError(_('Please add the maintenance plans'))
        else:
            raise UserError(_('Cannot submit the request'))

    def action_approve(self):
        if self.maintenance_ids:
            self.equipment_state = 'approve'
        else:
            raise UserError(_('Please add the maintenance plans'))
    def action_refuse(self):
        if self.maintenance_ids:
            self.equipment_state = 'refuse'
        else:
            raise UserError(_('Please add the maintenance plans'))

    def action_maintenance_request(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance Request',
            'view_mode': 'tree,form',
            'res_model': 'maintenance.request',
            'domain': [('asset_id', '=' ,self.id)],
        }