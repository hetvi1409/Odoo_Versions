from odoo import models , fields

class AssetVerificationJobLocation(models.Model):
    _name = 'asset.verification.job.location'
    _description = 'Asset Verification Job Location'

    name = fields.Char(string='Verification Location')
    code = fields.Char(string='Code')
    building_id = fields.Many2one('asset.verification.job.building')