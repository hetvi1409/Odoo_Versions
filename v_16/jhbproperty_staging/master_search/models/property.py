from odoo import fields, models, _


class Building(models.Model):
    """property Asset Register"""
    _inherit = 'building'

    def action_open_record(self):
        """Action Open Record"""
        return {
            'name': _('Property'),
            'view_mode': 'form',
            'res_model': self._name,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.id
        }

class AssetRegister(models.Model):
    """Asset Register"""
    _inherit = 'account.asset'

    def action_open_record(self):
        """Action Open Record"""
        return {
            'name': _('Asset'),
            'view_mode': 'form',
            'res_model': self._name,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.id
        }

class OutdoorAdvertisement(models.Model):
    """Asset Register"""
    _inherit = 'outdoor.advertisement'

    def action_open_record(self):
        """Action Open Record"""
        return {
            'name': _('Outdoor Advertisement'),
            'view_mode': 'form',
            'res_model': self._name,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.id
        }

class RentalContract(models.Model):
    """Asset Register"""
    _inherit = 'rental.contract'

    def action_open_record(self):
        """Action Open Record"""
        return {
            'name': _('Lease'),
            'view_mode': 'form',
            'res_model': self._name,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.id
        }
