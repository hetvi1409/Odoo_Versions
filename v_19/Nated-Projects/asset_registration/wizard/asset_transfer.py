from odoo import fields, models, _
from odoo.exceptions import ValidationError


class AssetTransfer(models.TransientModel):
    _name = 'asset.transfer'
    _description = 'Asset Transfer'
    """Class for asset transfer"""

    asset_ids = fields.Many2many('account.asset', string="Asset",
                                 help="List of asset")
    asset_id_no = fields.Char(string='Asset Id', help='Asset Id')

    date = fields.Date(string="Date Requested", help="Date requested for the transfer",
                       default=fields.Date.today())
    asset_barcode = fields.Char(string="Barcode", help="Barcode")
    department = fields.Char(string="Department", help="Department")
    transfer_description = fields.Char(string="Asset Description", help="Asset Description")
    asset_category_id = fields.Many2one('asset.category', string='Classification of asset', help="Classification of asset")

    transfer_condition = fields.Char(string="Condition of asset", help="Condition of asset")
    reason = fields.Char(string="Reason for transfer", help="Reason for transfer")
    name_surname = fields.Char(string="Name & Surname", help="Name & Surname")
    sign_signature = fields.Binary(string="Digital Signature")
    current_location = fields.Char(string="Current Location", help="Current Location")
    new_location = fields.Char(string="New Location", help="New Location")
    current_department = fields.Char(string="Current Department", help="Current Department")
    new_department = fields.Char(string="New Department", help="New Department")
    current_unit = fields.Char(string="Current Unit", help="Current Unit")
    new_unit = fields.Char(string="New Unit", help="New Unit")
    transferring_official = fields.Char(string="Transferring official", help="Transferring official")
    receiving_official = fields.Char(string="Receiving official", help="Receiving official")
    transferring_official_signature = fields.Char(string="Transferring official signature", help="Transferring official signature")
    gm_name_surname = fields.Char(string="GM Name & Surname", help="GM Name & Surname")
    new_gm_name_surname = fields.Char(string="GM Name & Surname", help="GM Name & Surname")
    gm_signature = fields.Char(string="GM Signature", help="GM Signature")
    new_gm_signature = fields.Char(string="GM Signature", help="GM Signature")
    date_transferred = fields.Date(string="Date transferred", help="Date transferred",
                       default=fields.Date.today())
    date_received = fields.Date(string="Date received", help="Date received",
                       default=fields.Date.today())

    def action_asset_transfer(self):
        """Method for asset transfer"""
        if not self.asset_ids and not self.asset_id_no:
            raise ValidationError(
                _('Please select any asset or add a asset id'))
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
                asset.date = self.date
                asset.asset_barcode = self.asset_barcode
                asset.department = self.department
                asset.transfer_description = self.transfer_description
                asset.asset_category_id = self.asset_category_id.id
                asset.transfer_condition = self.transfer_condition
                asset.reason = self.reason
                asset.name_surname = self.name_surname
                asset.sign_signature = self.sign_signature
                asset.current_location = self.current_location
                asset.new_location = self.new_location
                asset.current_department = self.current_department
                asset.new_department = self.new_department
                asset.current_unit = self.current_unit
                asset.new_unit = self.new_unit
                asset.transferring_official = self.transferring_official
                asset.receiving_official = self.receiving_official
                asset.transferring_official_signature = self.transferring_official_signature
                asset.gm_name_surname = self.gm_name_surname
                asset.new_gm_name_surname = self.new_gm_name_surname
                asset.gm_signature = self.gm_signature
                asset.new_gm_signature = self.new_gm_signature
                asset.date_transferred = self.date_transferred
                asset.date_received = self.date_received
                asset.is_transferred = True
            else:
                raise ValidationError(
                    _("Can't transfer asset not in draft"))
