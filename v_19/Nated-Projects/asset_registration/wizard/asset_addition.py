from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AssetAddition(models.Model):
    _name = 'asset.addition'
    _description = 'Asset Addition'
    """model for Asset Addition"""

    asset_id = fields.Many2one('account.asset', string='Asset',
                               help='Asset ID')
    asset_ids = fields.Many2many('account.asset', string="Assets", domain="[('state', '=', 'draft')]")
    asset_id_no = fields.Char(string="Asset Id no", help="Asset Identity number")
    type = fields.Selection([('cash', 'Cash'), ('non_cash', 'Non-cash')],
                            required=True, string='Type',
                            help='Type of addition')
    cash_type = fields.Selection([('purchase', 'Purchase'),
                                  ('maintenance', 'Maintenance')],
                                 string='Cash Type', help="Type of cash addition")
    purchase_order_id = fields.Many2one('purchase.order', domain="[('state', '=', 'purchase')]",
                                        string='Purchase Order', help='Purchase order details')
    purchase_amount = fields.Monetary(string='Purchase Amount')

    def _default_currency_id(self):
        """get currency id"""
        return self.env.user.company_id.currency_id
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True,
                                  default=lambda self: self._default_currency_id())
    maintenance_id = fields.Many2one('maintenance.request')
    maintenance_amount = fields.Monetary(string='Maintenance Amount')
    non_cash_type = fields.Selection([('donated', 'Donated'), ('newly_asset', 'Newly Asset')], string='Non cash type')
    best_fair = fields.Monetary(string='Best fair')
    deprecated_replacement = fields.Monetary(string='Deprecated replacement')
    invoice_number = fields.Char(string="Invoice number", required=True)
    supplier_id = fields.Many2one('res.partner', string="Supplier Name", required=True)
    voucher_number = fields.Char(string="Payment Voucher number/ EFT number", required=True)

    @api.onchange('purchase_order_id')
    def onchange_purchase_id(self):
        """method for onchange purchase id"""
        for rec in self:
            if rec.purchase_order_id:
                rec.purchase_amount = rec.purchase_order_id.amount_total

    def action_asset_addition(self):
        """Method for asset addition"""
        pass
        if self.asset_id:
            if self.type == 'cash':
                if self.cash_type == 'purchase':
                    self.asset_id.original_value = self.purchase_amount
                if self.cash_type == 'maintenance':
                    self.asset_id.original_value = self.maintenance_amount
            if self.type == 'non_cash':
                if self.non_cash_type == 'donated':
                    self.asset_id.original_value = self.best_fair
                if self.non_cash_type == 'newly_asset':
                    self.asset_id.original_value = self.deprecated_replacement
        else:
            if not self.asset_ids and not self.asset_id_no:
                raise ValidationError(_('Please select any asset or add a asset id'))
            if self.asset_id_no:
                assets = self.env['account.asset'].search(
                    [('identification_number', '=', self.asset_id_no)])
                if not assets:
                    raise ValidationError(
                        _('There is no asset with identifier number'))
        if self.asset_ids:
            assets = self.asset_ids
        for asset in assets:
            if asset.state == 'draft':
                if self.type == 'cash':
                    if self.cash_type == 'purchase':
                        asset.original_value = self.purchase_amount
                    if self.cash_type == 'maintenance':
                        asset.original_value = self.maintenance_amount
                if self.type == 'non_cash':
                    if self.non_cash_type == 'donated':
                        asset.original_value = self.best_fair
                    if self.non_cash_type == 'newly_asset':
                        asset.original_value = self.deprecated_replacement
            else:
                raise ValidationError(_("Can't impair the asset with draft state"))

