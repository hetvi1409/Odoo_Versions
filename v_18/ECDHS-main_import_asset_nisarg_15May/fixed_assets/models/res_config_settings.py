from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    minor_major_threshold = fields.Float(
        string="Minor/Major Asset Threshold",
        default=1000,
        config_parameter="asset_registry.minor_major_threshold"
    )

    # when change in threshold, validate it's positive also check existing assets and update their asset_type
    @api.onchange('minor_major_threshold')
    def _onchange_minor_major_threshold(self):
        if self.minor_major_threshold <= 0:
            return {
                'warning': {
                    'title': "Invalid Threshold",
                    'message': "The threshold must be a positive number greater than zero.",
                }
            }
        threshold = self.minor_major_threshold
        assets = self.env['account.asset'].search([])
        for asset in assets:
            if asset.original_value > threshold:
                asset.asset_type = 'major'
            else:
                asset.asset_type = 'minor'