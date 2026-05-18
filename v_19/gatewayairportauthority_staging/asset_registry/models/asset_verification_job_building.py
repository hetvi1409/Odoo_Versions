from odoo import models , fields

class AssetVerificationJobBuilding(models.Model):
    _name = 'asset.verification.job.building'
    _description = 'Asset Verification Job Building'

    name = fields.Char(string='Verification Building')

