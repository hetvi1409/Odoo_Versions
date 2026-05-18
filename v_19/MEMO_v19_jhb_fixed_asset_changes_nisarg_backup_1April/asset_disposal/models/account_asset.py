from odoo import fields, models , _
from odoo.exceptions import UserError
from math import copysign

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

    def sell_dispose(self):
        self.ensure_one()

        # Validate the gain and loss accounts
        if self.gain_account_id == self.asset_id.account_depreciation_id or self.loss_account_id == self.asset_id.account_depreciation_id:
            raise UserError(_("You cannot select the same account as the Depreciation Account"))

        # Determine the invoice lines based on the action
        invoice_lines = self.env['account.move.line'] if self.modify_action == 'dispose' else self.invoice_line_ids

        # Handle the different disposal methods
        if self.disposal_method == 'sale':
            # Sale-specific disposal
            return self.asset_id.set_to_close(invoice_line_ids=invoice_lines, date=self.date, message=self.name)

        elif self.disposal_method in ['scrapping','donation']:
            # Scrap-specific disposal
            return self.asset_id.set_to_close(invoice_line_ids=invoice_lines, date=self.date,
                                              message=_("Asset scrapped. %s") % self.name)

        elif self.disposal_method == 'other':
            # Other-specific disposal
            consideration_value = self.consideration_value if hasattr(self, 'consideration_value') else 0
            message = _("Asset disposed (Other method). Consideration value: %s") % consideration_value
            return self.asset_id.set_to_close(invoice_line_ids=invoice_lines, date=self.date, message=message)

        else:
            raise UserError(_("Unknown disposal method."))

    def set_to_close(self, invoice_line_ids, date=None, message=None):
        self.ensure_one()

        disposal_date = date or fields.Date.today()

        # Check the fiscal lock date
        if disposal_date <= self.company_id._get_user_fiscal_lock_date():
            raise UserError(_("You cannot dispose of an asset before the lock date."))

        # Ensure no ongoing gross increase
        if invoice_line_ids and self.children_ids.filtered(
                lambda a: a.state in ('draft', 'open') or a.value_residual > 0):
            raise UserError(
                _("You cannot automate the journal entry for an asset that has a running gross increase. Please use 'Dispose' on the increase(s)."))

        full_asset = self + self.children_ids
        move_ids = full_asset._get_disposal_moves([invoice_line_ids] * len(full_asset), disposal_date)

        for asset in full_asset:
            asset.message_post(body=_(
                'Asset sold. %s' if invoice_line_ids else 'Asset disposed. %s'
            ) % (message if message else ""))

        full_asset.write({'state': 'close'})

        if move_ids:
            name = _('Disposal Move')
            view_mode = 'form'
            if len(move_ids) > 1:
                name = _('Disposal Moves')
                view_mode = 'list,form'
            return {
                'name': name,
                'view_mode': view_mode,
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': move_ids[0],
                'domain': [('id', 'in', move_ids)]
            }

    def _get_disposal_moves(self, invoice_lines_list, disposal_date):
        """Create the move for the disposal of an asset.

        :param invoice_lines_list: list of recordset of `account.move.line`
            Each element of the list corresponds to one record of `self`
            These lines are used to generate the disposal move
        :param disposal_date: the date of the disposal
        """

        def get_line(asset, amount, account):
            return (0, 0, {
                'name': asset.name,
                'account_id': account.id,
                'balance': -amount,
                'analytic_distribution': analytic_distribution,
                'currency_id': asset.currency_id.id,
                'amount_currency': -asset.company_id.currency_id._convert(
                    from_amount=amount,
                    to_currency=asset.currency_id,
                    company=asset.company_id,
                    date=disposal_date,
                )
            })

        move_ids = []
        assert len(self) == len(invoice_lines_list)
        for asset, invoice_line_ids in zip(self, invoice_lines_list):
            asset._create_move_before_date(disposal_date)

            analytic_distribution = asset.analytic_distribution

            dict_invoice = {}
            invoice_amount = 0

            initial_amount = asset.original_value
            initial_account = asset.original_move_line_ids.account_id if len(
                asset.original_move_line_ids.account_id) == 1 else asset.account_asset_id

            all_lines_before_disposal = asset.depreciation_move_ids.filtered(lambda x: x.date <= disposal_date)
            depreciated_amount = asset.currency_id.round(copysign(
                sum(all_lines_before_disposal.mapped('depreciation_value')) + asset.already_depreciated_amount_import,
                -initial_amount,
            ))
            depreciation_account = asset.account_depreciation_id
            for invoice_line in invoice_line_ids:
                dict_invoice[invoice_line.account_id] = copysign(invoice_line.balance,
                                                                 -initial_amount) + dict_invoice.get(
                    invoice_line.account_id, 0)
                invoice_amount += copysign(invoice_line.balance, -initial_amount)
            list_accounts = [(amount, account) for account, amount in dict_invoice.items()]
            difference = -initial_amount - depreciated_amount - invoice_amount
            difference_account = asset.company_id.gain_account_id if difference > 0 else asset.company_id.loss_account_id
            line_datas = [(initial_amount, initial_account),
                          (depreciated_amount, depreciation_account)] + list_accounts + [
                             (difference, difference_account)]
            vals = {
                'asset_id': asset.id,
                'ref': asset.name + ': ' + (_('Disposal') if not invoice_line_ids else _('Sale')),
                'asset_depreciation_beginning_date': disposal_date,
                'date': disposal_date,
                'journal_id': asset.journal_id.id,
                'move_type': 'entry',
                'line_ids': [get_line(asset, amount, account) for amount, account in line_datas if account],
            }
            asset.write({'depreciation_move_ids': [(0, 0, vals)]})
            move_ids += self.env['account.move'].search([('asset_id', '=', asset.id), ('state', '=', 'draft')]).ids

        return move_ids


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
        closest_move = self.depreciation_move_ids.sorted(
            key=lambda mv: abs((mv.date - date).days)
        )

        if closest_move:
            latest_value = closest_move[-1].asset_remaining_value  # Get the closest move
        else:
            latest_value = self.original_value  # If no move is found, return the original value

        return latest_value





