# -*- coding: utf-8 -*-
from odoo import models
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    def write(self, vals):

        res = super(ResUsers, self).write(vals)

        if any(key.startswith('in_group_') for key in vals.keys()):
            print("\n\n\n IFFFFFFFFFFFFFFF Group Change Detected in WRITE======>", vals)
            try:
                viewer_group = self._has_group('fixed_assets.group_fixed_asset_viewer')

                print("Viewer Group:", viewer_group)
                print("Current User ID:", self)
                account_readonly = self._has_group('account.group_account_readonly')
                print("Account Readonly Group:", account_readonly)

                if not viewer_group or not account_readonly:
                    return res

                # Get all other Fixed Asset groups
                capturer_group = self._has_group('fixed_assets.group_fixed_asset_capturer')
                authorizer_group = self._has_group('fixed_assets.group_fixed_asset_authorizer')
                verifier_group = self._has_group('fixed_assets.group_fixed_asset_verifier')
                manager_group = self._has_group('fixed_assets.group_fixed_asset_approver')

                for user in self:
                    print("\n\n\n Checking User ======>", user.name)
                    # Checking User ======> Babalwa Ngoyi

                    print("User Groups:", user.groups_id)
                    # User Groups: res.groups(184, 8, 196, 16, 71, 3, 9, 21, 77, 136, 134, 135, 133, 1, 23, 24, 12, 179, 38, 5, 6, 54, 195, 20, 58, 22, 70, 25, 172, 69, 7, 187, 100, 41, 113, 111, 39, 227)


                    # search that group from user's groups
                    viewer_group = self.env['res.groups'].search([('name', '=', 'Viewer/Reporter')])
                    capturer_group = self.env['res.groups'].search([('name', '=', 'Capturer')])
                    authorizer_group = self.env['res.groups'].search([('name', '=', 'Authorizer')])
                    verifier_group = self.env['res.groups'].search([('name', '=', 'Verifier')])
                    manager_group = self.env['res.groups'].search([('name', '=', 'Fixed Asset Manager')])
                    account_readonly = self.env['res.groups'].search([('name', '=', 'Show Accounting Features - Readonly')])
                    full_account_readonly = self.env['res.groups'].search([('name', '=', 'Show Full Accounting Features')])
                    invoicing_banks = self.env['res.groups'].search([('name', '=', 'Invoicing & Banks')])
                    Invoicing = self.env['res.groups'].search([('name', '=', 'Invoicing')])

                    if viewer_group in user.groups_id:
                        _logger.info(f"User {user.name} has Viewer group")

                        has_other_role = False

                        print("HAS OTHER===============:", has_other_role)

                        if capturer_group and capturer_group in user.groups_id:
                            has_other_role = True
                        if authorizer_group and authorizer_group in user.groups_id:
                            has_other_role = True
                        if verifier_group and verifier_group in user.groups_id:
                            has_other_role = True
                        if manager_group and manager_group in user.groups_id:
                            has_other_role = True

                        # If user has ONLY Viewer (no other FA roles)
                        if not has_other_role:
                            print("IFFFFFFFFFFFFFFFFF NO OTHER ROLES===============:", has_other_role)
                            if account_readonly or full_account_readonly in user.groups_id:
                                print("\n\n\n Removing account_readonly Group from User ======>", user.name)
                                print("User Groups Before Removal:", user.groups_id)
                                print("account_readonly Group:", account_readonly)
                                print("full_account_readonly Group:", full_account_readonly)

                                _logger.info(f"Removing account_readonly from {user.name}")

                                # Use super to avoid recursion
                                super(ResUsers, user.sudo()).write({
                                    'groups_id': [(3, account_readonly.id),(3, full_account_readonly.id),(3, invoicing_banks.id),(3, Invoicing.id)]
                                })
                                print("User Groups After Removal:", user.groups_id)
                        else:
                            _logger.info(f"User {user.name} has other FA roles, keeping account_readonly")

            except Exception as e:
                _logger.error(f"Error in auto-cleanup groups: {str(e)}")

        return res