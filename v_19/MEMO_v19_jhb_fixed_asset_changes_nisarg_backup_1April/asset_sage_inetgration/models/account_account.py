import re

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

ACCOUNT_CODE_REGEX = re.compile(r'^[A-Za-z0-9./!@#$%^&*()-]+$')


class AccountAccount(models.Model):
    _inherit = 'account.account'

    extension_id_account = fields.Char(string="Account Extension Id",
                                       help="Account Extension Id")
    account_link = fields.Char(string="Account Link",
                               help="Account link: Unique identifier in sage")
    account_master = fields.Char(string="Account Master",
                                 help="Master account of GL.")
    account_extension = fields.Char(string="Account Extension",
                                    help="accountExtAccount")
    account_extension_link = fields.Char(string="Account Extension Link",
                                         help="Account Extension Link: Unique identifier")

    project_code = fields.Char(string="Project Code", help="Project Code")
    project_description = fields.Char(string="Project Description", help="Project Description")
    project_long_code = fields.Char(string="Project Long Code", help="Project Long Code")
    project_guid_code = fields.Char(string="Project Guid Code", help="Project Guid Code")
    project_soca_account = fields.Char(string="Project Soca Account", help="Project Soca Account")

    item_code = fields.Char(string="Item Code", help="Item Code")
    item_description = fields.Char(string="Item Description", help="Item Description")
    item_long_code = fields.Char(string="Item Long Code", help="Item Long Code")
    item_guid_code = fields.Char(string="Item Guid Code", help="Item Guid Code")
    item_soca_account = fields.Char(string="Item Soca Account")

    fund_code = fields.Char(string="Fund Code", help="Fund Code")
    fund_description = fields.Char(string="Fund Description", help="Fund Description")
    fund_long_code = fields.Char(string="Fund Long Code", help="Fund Long Code")
    fund_guid_code = fields.Char(string="Fund Guid Code", help="Fund Guid Code")
    fund_soca_account = fields.Char(string="Fund Soca Account")
    
    function_code = fields.Char(string="Function Code", help="Function Code")
    function_description = fields.Char(string="Function Description", help="Function Description")
    function_long_code = fields.Char(string="Function Long Code", help="Function Long Code")
    function_guid_code = fields.Char(string="Function Guid Code", help="Function Guid Code")
    function_soca_account = fields.Char(string="Function Soca Account")
    
    region_code = fields.Char(string="Region Code", help="Region Code")
    region_description = fields.Char(string="Region Description", help="Region Description")
    region_long_code = fields.Char(string="Region Long Code", help="Region Long Code")
    region_guid_code = fields.Char(string="Region Guid Code", help="Region Guid Code")
    region_soca_account = fields.Char(string="Region Soca Account")
    
    costing_code = fields.Char(string="Costing Code", help="Costing Code")
    costing_description = fields.Char(string="Costing Description", help="Costing Description")
    costing_long_code = fields.Char(string="Costing Long Code", help="Costing Long Code")
    costing_guid_code = fields.Char(string="Costing Guid Code", help="Costing Guid Code")
    costing_soca_account = fields.Char(string="Costing Soca Account")

    msc_code = fields.Char(string="MSC Code", help="MSC Code")
    msc_description = fields.Char(string="MSC Description", help="MSC Description")
    scoa_version_id = fields.Char(string="Scoa Version ID", help="Scoa Version ID")

    @api.constrains('code')
    def _check_account_code(self):
        for account in self:
            if not re.match(ACCOUNT_CODE_REGEX, account.code):
                raise ValidationError(_(
                    "The account code can only contain alphanumeric characters and dots."
                ))
