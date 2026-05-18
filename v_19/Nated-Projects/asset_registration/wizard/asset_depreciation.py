from odoo import fields, models, _
from odoo.exceptions import ValidationError


class AssetDepreciation(models.TransientModel):
    _name = 'asset.depreciation'
    _description = 'Asset Depreciation'

    asset_ids = fields.Many2many('account.asset', string='Assets', domain=[('state', '=', 'draft')])
    asset_id_no = fields.Char(string='Asset Id', help='Asset Id')

    def action_asset_depreciation(self):
        """Asset Depreciation"""
        if not self.asset_ids and not self.asset_id_no:
            raise ValidationError(_('Please select any asset or add a asset id'))
        if self.asset_id_no:
            assets = self.env['account.asset'].search([('identification_number', '=', self.asset_id_no)])
            if not assets:
                raise ValidationError(_('There is no asset with identifier number'))
        if self.asset_ids:
            assets = self.asset_ids
        for asset in assets:
            if asset.state == 'draft':
                asset.compute_depreciation_board()
            else:
                raise ValidationError(_("Can't depreciation asset not in draft"))
