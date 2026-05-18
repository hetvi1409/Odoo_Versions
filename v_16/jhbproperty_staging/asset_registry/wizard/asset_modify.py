from odoo import api, fields, models, _, Command


class YourNewModel(models.TransientModel):
    _inherit = 'asset.modify'

    # @api.depends('asset_id')
    # def _get_selection_modify_options(self):
    #     if self.env.context.get('resume_after_pause'):
    #         return [('resume', _('Resume'))]
    #     if self.env.context.get('asset_type') in ('sale', 'expense'):
    #         return [('modify', _('Re-evaluate'))]
    #     if self.env.user.has_group('asset_registry.department_users_access'):
    #         return [('dispose_request', _("Dispose Request"))]
    #     if self.env.user.has_group('asset_registry.finance_managers_access'):
    #         return [('dispose', _("Dispose"))]
    #     return [
    #         ('sell', _("Sell")),
    #         ('modify', _("Re-evaluate")),
    #         ('pause', _("Pause")),
    #     ]

    @api.depends('asset_id')
    def _get_selection_modify_options(self):
        """
        Override this function for adding one more selection option 'Request
        Dispose' according to the groups
        """
        options = [
            ('sell', _("Sell")),
            ('modify', _("Re-evaluate")),
            ('pause', _("Pause")),
        ]
        if self.env.user.has_group('asset_registry.department_users_access'):
            options.append(('dispose_request', _("Dispose Request")))
        if self.env.user.has_group('asset_registry.finance_managers_access'):
            options.append(('dispose', _("Dispose")))
        if self.env.context.get('resume_after_pause'):
            options.append(('resume', _('Resume')))
        if self.env.context.get('asset_type') in ('sale', 'expense'):
            options.append(('modify', _('Re-evaluate')))
        return options

    def request_disposal(self):
        """
        This function for Requesting Disposal by Department User
        """
        self.ensure_one()
        self.asset_id.write({'state': 'disposal_request_sent'})
        if self.name:
            self.asset_id.write({'disposal_reason': self.name})
        approval_category = self.env['approval.category'].search([('name', '=', self.asset_id.asset_category_id.name)],
                                                                 limit=1)
        if not approval_category:
            approval_category = self.env['approval.category'].create({
                'name': self.asset_id.asset_category_id.name,
            })

        # Create an approval request in the approval.request model
        self.env['approval.request'].create({
            'name': f'Request for Disposal of {self.asset_id.name}',
            'request_owner_id': self.env.user.id,
            'category_id': approval_category.id,
            'reason': self.name or 'No reason provided',
        })

        # Link the approval request to the asset, if necessary
        # self.asset_id.write({'approval_request_id': approval_request.id})
