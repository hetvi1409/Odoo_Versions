from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountAsset(models.Model):
    _inherit = 'account.asset'
    state = fields.Selection(
        selection=[('model', 'Model'),
                   ('draft', 'Draft'),
                   ('request_for_approval', 'Submit for Approval'),
                   ('open', 'Running'),
                   ('paused', 'On Hold'),
                   ('close', 'Closed'),
                   ('cancelled', 'Cancelled'),
                   ('asset_disposed','Asset Disposed')],
        string='Status',
        copy=False,
        default='draft',
        readonly=True,
        help="When an asset is created, the status is 'Draft'.\n"
             "If the asset is confirmed, the status goes in 'Running' and the depreciation lines can be posted in the accounting.\n"
             "The 'On Hold' status can be set manually when you want to pause the depreciation of an asset for some time.\n"
             "You can manually close an asset when the depreciation is over.\n"
             "By cancelling an asset, all depreciation entries will be reversed")
    active = fields.Boolean(default=True)


    def action_approve(self):
        if not self.env.user.has_group('fixed_assets.group_fixed_asset_capturer'):
            raise UserError("You do not have the rights to submit this.")
        self.state='request_for_approval'
