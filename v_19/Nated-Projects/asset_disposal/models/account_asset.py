from odoo import fields, models
from odoo.exceptions import UserError

class AccountAssetModify(models.TransientModel):
    _inherit = 'asset.modify'

    disposal_method = fields.Selection([
        ('sale', 'Sale'),
        ('donation', 'Donation'),
        ('scrapping', 'Scrapping'),
        ('other', 'Other')
    ], string='Disposal Method', required=True , default="scrapping")
    consideration_input = fields.Float(string='Consideration Value')
    selling_input = fields.Float(string='Sell Value')
    asset_depreciated_value = fields.Float(related="asset_id.asset_depreciated_value")



    #
    # disposal_date = fields.Date(string='Disposal Date', default=fields.Date.context_today, required=True)
    # selling_price = fields.Float(string='Selling Price')
    # carrying_amount = fields.Float(string='Carrying Amount', compute='_compute_carrying_amount', store=True)
    # disposal_state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('done', 'Done'),
    # ], string='Disposal State', default='draft')
    #
    # audit_log = fields.Text(string='Audit Log')

    # @api.depends('value', 'depreciation_move_ids')
    # def _compute_carrying_amount(self):
    #     for asset in self:
    #         total_depreciation = sum(asset.depreciation_move_ids.mapped('amount_total'))
    #         asset.carrying_amount = asset.value - total_depreciation
    #
    # def action_dispose_asset(self):
    #     for asset in self:
    #         if asset.disposal_method == 'sale' and asset.selling_price <= 0:
    #             raise UserError(_("Selling price must be greater than zero for sale."))
    #
    #         asset._compute_carrying_amount()
    #
    #         if asset.disposal_method == 'sale':
    #             profit_loss = asset.selling_price - asset.carrying_amount
    #         else:
    #             profit_loss = -asset.carrying_amount
    #
    #         journal_entries = self._generate_disposal_journal_entries(profit_loss)
    #         asset.audit_log = _(
    #             "Disposal Method: %s\nDisposal Date: %s\nCarrying Amount: %s\nProfit/Loss: %s\nJournal Entries: %s") % (
    #                               dict(self._fields['disposal_method'].selection).get(asset.disposal_method),
    #                               asset.disposal_date,
    #                               asset.carrying_amount,
    #                               profit_loss,
    #                               journal_entries.name,
    #                           )
    #         asset.disposal_state = 'done'
    #         asset.active = False
    #
    # def _generate_disposal_journal_entries(self, profit_loss):
    #     journal = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
    #     move = self.env['account.move'].create({
    #         'journal_id': journal.id,
    #         'date': self.disposal_date,
    #         'ref': self.name,
    #         'line_ids': [
    #             (0, 0, {
    #                 'name': _('Disposal of %s') % self.name,
    #                 'account_id': self.account_asset_id.id,
    #                 'debit': profit_loss < 0 and -profit_loss or 0,
    #                 'credit': profit_loss > 0 and profit_loss or 0,
    #             }),
    #             (0, 0, {
    #                 'name': _('Disposal of %s') % self.name,
    #                 'account_id': self.account_depreciation_id.id,
    #                 'debit': profit_loss > 0 and profit_loss or 0,
    #                 'credit': profit_loss < 0 and -profit_loss or 0,
    #             }),
    #         ],
    #     })
    #     move.post()
    #     return move

class AccountAsset(models.Model):
    _inherit = 'account.asset'

    disposal_method = fields.Selection([
        ('sale', 'Sale'),
        ('donation', 'Donation'),
        ('scrapping', 'Scrapping'),
        ('other', 'Other')
    ], string='Disposal Method', required=True , default="scrapping")
    consideration_input = fields.Float(string='Consideration Value')
    selling_input = fields.Float(string='Sell Value')
    asset_depreciated_value = fields.Float(compute='_compute_asset_depreciated_value')

    def _compute_asset_depreciated_value(self):
        for record in self:
            record.asset_depreciated_value = record.get_latest_depreciation_value(fields.Date.context_today(self))

    def get_latest_depreciation_value(self, date):
        self.ensure_one()

        # Find the latest posted depreciation move before the given date
        closest_move = self.depreciation_move_ids.filtered(
            lambda mv: mv.date < date  # Use '<' to exclude the specified date
        ).sorted(key=lambda mv: mv.date)  # Sort in ascending order

        if closest_move:
            latest_value = closest_move[-1].asset_remaining_value  # Get the closest move
            print(latest_value, 'Latest Depreciation Value')
        else:
            latest_value = self.original_value  # If no move is found, return the original value
            print(latest_value, 'No Depreciation Moves Found')

        return latest_value





