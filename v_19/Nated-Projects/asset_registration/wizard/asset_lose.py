# from odoo import api, fields, models, _
# from odoo.exceptions import ValidationError
#
#
# class AssetLose(models.TransientModel):
#     _name = 'asset.lose'
#     _description = 'Asset Loss'
#     """Class for asset disposal"""
#
#     asset_id = fields.Many2one('account.asset', string="Asset")
#     asset_ids = fields.Many2many('account.asset', string="Asset", domain="[('state', '!=', 'model')]")
#     asset_id_no = fields.Char(string="Asset Id no", help="Asset Identity number")
#     asset_reason = fields.Selection([('loss', 'Loss'), ('theft', 'Theft'),
#                                      ('destruction', 'Destruction'),
#                                      ('material_impairment',
#                                       'Material Impairment')], "Asset Reasons")
#     description = fields.Text(string="Description")
#     type = fields.Selection([('cash', 'Cash'), ('non_cash', 'Non-cash')],
#                             required=True, string='Type',
#                             help='Type of addition')
#     direct_attachement_ids = fields.Many2many('ir.attachment', string="Files")
#     cash_type = fields.Selection([('direct_disposal', 'Direct Disposal')])
#     non_cash_type = fields.Selection([('scrapping', 'Scrapping of asset'),
#                                       ('newly_found_asset', 'NEWLY FOUND ASSET FROM THE VERIFICATION'),
#                                       ('other_modules', 'From other modules')])
#     direct_disposal_amount = fields.Monetary(string='Proceeds')
#     def _default_currency_id(self):
#         """get currency id"""
#         return self.env.user.company_id.currency_id
#     currency_id = fields.Many2one('res.currency', string='Currency',
#                                   required=True,
#                                   default=lambda self: self._default_currency_id())
#     disposal_date = fields.Date(string='Disposal Date')
#
#     # Removed based on the review of jul 31st
#     # @api.depends('asset_id')
#     # def _compute_proceed_amount(self):
#     #     """Calculate the proceed amount"""
#     #     amount = 0.0
#     #     if self.asset_id:
#     #         if self.asset_id.value_in_use == self.asset_id.fair_value_less_cost_to_sell:
#     #             amount = self.asset_id.money_received_sale_asset
#     #         elif self.asset_id.value_in_use > self.asset_id.fair_value_less_cost_to_sell:
#     #             amount =  self.asset_id.money_received_sale_asset
#     #         else:
#     #             amount = self.asset_id.original_value - \
#     #                      self.asset_id.accumulated_depreciation - \
#     #                      self.asset_id.accumulated_impairment_disposal
#     #     self.direct_disposal_amount = amount
#
#     def action_submit(self):
#         """submit loss asset"""
#         if self.asset_id:
#             self.asset_id.state = 'cancelled'
#             self.asset_id.loss_asset = True
#             for rec in self.direct_attachement_ids:
#                 self.asset_id.direct_attachement_ids = [(4, rec.id)]
#             self.asset_id.current_value_asset = self.direct_disposal_amount
#             self.asset_id.disposal_type = self.type
#             self.asset_id.cash_type = self.cash_type
#             self.asset_id.non_cash_type = self.non_cash_type
#             self.asset_id.direct_disposal_amount = self.direct_disposal_amount
#             self.asset_id.asset_reason = self.asset_reason
#             self.asset_id.disposal_date = self.disposal_date
#         else:
#             if not self.asset_ids and not self.asset_id_no:
#                 raise ValidationError(_('Please select any asset or add a asset id'))
#             if self.asset_id_no:
#                 assets = self.env['account.asset'].search(
#                     [('identification_number', '=', self.asset_id_no)])
#                 if not assets:
#                     raise ValidationError(
#                         _('There is no asset with identifier number'))
#             if self.asset_ids:
#                 assets = self.asset_ids
#
#             for asset in assets:
#                 # if asset.state != 'impaired':
#                 #     raise ValidationError(_("Can't impair the asset with impaired"))
#                 if asset.value_in_use == asset.fair_value_less_cost_to_sell:
#                     amount = asset.money_received_sale_asset
#                 elif asset.value_in_use > self.asset_id.fair_value_less_cost_to_sell:
#                     amount = asset.money_received_sale_asset
#                 else:
#                     amount = asset.original_value - \
#                              asset.accumulated_depreciation - \
#                              asset.accumulated_impairment_disposal
#                 asset.state = 'cancelled'
#                 asset.loss_asset = True
#                 for rec in self.direct_attachement_ids:
#                     asset.direct_attachement_ids = [(4, rec.id)]
#                 asset.current_value_asset = self.direct_disposal_amount
#                 asset.disposal_type = self.type
#                 asset.cash_type = self.cash_type
#                 asset.non_cash_type = amount
#                 asset.asset_reason = self.asset_reason
#                 asset.disposal_date = self.disposal_date
#
#     @api.onchange('asset_ids')
#     def _onchange_asset_id(self):
#         """Change the asset id of the asset"""
#         if len(self.asset_ids) == 1:
#             self.direct_disposal_amount = self.asset_ids.fair_value_less_cost_to_sell
#         else:
#             self.direct_disposal_amount = 0.0
