from odoo import models, fields, api
from datetime import date
import logging
_logger = logging.getLogger(__name__)

class AssetUsefulLife(models.Model):
    _inherit = 'account.asset'

    original_useful_life = fields.Integer(string="Original Useful Life (Years)", required=True)
    remaining_useful_life = fields.Float(string="Remaining Useful Life", compute='_compute_remaining_useful_life',
                                         store=True)
    depreciation_rate = fields.Float(string="Monthly Depreciation", compute='_compute_depreciation_rate')
    time_lapsed = fields.Float(string="Time Lapsed", compute='_compute_time_lapsed')
    carrying_amount = fields.Float(string="Carrying Amount", compute='_compute_carrying_amount', store=True)

    # Fields to keep track of accumulated depreciation
    accumulated_depreciation = fields.Float(string="Accumulated Depreciation",
                                            compute='_compute_accumulated_depreciation', store=True)

    revised_useful_life = fields.Float(string="Revised Useful Life", default=0)

    def adjust_remaining_useful_life(self, new_remaining_life):
        self.remaining_useful_life = new_remaining_life
        # Update the revised useful life
        self.revised_useful_life = new_remaining_life
        self._compute_depreciation_rate()

    def _compute_time_lapsed(self):
        for asset in self:
            if asset.acquisition_date:
                asset.time_lapsed = (date.today() - asset.acquisition_date).days / 365.0  # convert days to years
            else:
                asset.time_lapsed = 0

    # Calculate the remaining useful life of the asset
    @api.depends('original_useful_life', 'time_lapsed')
    def _compute_remaining_useful_life(self):
        for asset in self:
            if asset.original_useful_life and asset.time_lapsed:
                asset.remaining_useful_life = max(asset.original_useful_life - asset.time_lapsed, 0)
            else:
                asset.remaining_useful_life = asset.original_useful_life

    # Compute the carrying amount (original value minus accumulated depreciation)
    @api.depends('accumulated_depreciation')
    def _compute_carrying_amount(self):
        for asset in self:
            asset.carrying_amount = asset.original_value - asset.accumulated_depreciation

    # Compute accumulated depreciation based on the time passed and original depreciation
    @api.depends('time_lapsed', 'original_useful_life')
    def _compute_accumulated_depreciation(self):
        for asset in self:
            if asset.original_useful_life > 0:
                # Perform the depreciation calculation only if original_useful_life is not zero
                asset.accumulated_depreciation = (asset.original_value / asset.original_useful_life) * asset.time_lapsed
            else:
                # Handle the case where useful life is zero, set accumulated depreciation to zero or a default value
                asset.accumulated_depreciation = 0
                # Optionally, you can log a warning or raise a custom error
                _logger.warning(
                    f"Original useful life is zero for asset {asset.name}. Depreciation calculation skipped.")

    # Calculate depreciation rate based on the remaining useful life and current carrying amount
    @api.depends('remaining_useful_life', 'carrying_amount', 'revised_useful_life')
    def _compute_depreciation_rate(self):
        for asset in self:
            if asset.revised_useful_life > 0:
                asset.depreciation_rate = asset.carrying_amount / asset.revised_useful_life
            elif asset.remaining_useful_life > 0:
                asset.depreciation_rate = asset.carrying_amount / asset.remaining_useful_life
            else:
                asset.depreciation_rate = 0

