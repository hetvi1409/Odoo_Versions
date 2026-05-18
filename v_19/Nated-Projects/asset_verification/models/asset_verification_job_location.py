from odoo import models , fields

class AssetVerificationJobLocation(models.Model):
    _name = 'asset.verification.job.location'
    _description = 'Asset Verification Job Location'

    name = fields.Char(string='Verification Location')