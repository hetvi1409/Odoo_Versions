from odoo import fields, models, _


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    state = fields.Selection(
        selection_add=[('draft',), ('submit', 'Submitted For Approval'),
                       ('open',), ('reject', 'Rejected')])
    redirect_url = fields.Char(string='Redirect URL')

    def get_record_url(self):
        """Generate the URL for the current record"""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        # self.redirect_url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
        self.redirect_url = f"{base_url}/odoo/{self._name}/{self.id}"

    def action_submit_asset(self):
        self.state = 'submit'
        self.get_record_url()
        manager_group = self.env.ref('asset_approval.group_asset_manager')
        mail_values = {}
        partners = manager_group.user_ids.mapped('partner_id')
        for partner in partners:
            if partner.email:
                mail_values = {
                    'email_to': partner.email,
                }
        template = self.env.ref(
            'asset_approval.email_template_to_confirm_asset')
        template.send_mail(self.id, force_send=True, email_values=mail_values)
        for asset in self:
            message_body = (
                f" Asset {asset.name} has been submitted for approval.")
            manager_group = self.env.ref(
                'asset_approval.group_asset_manager')
            partner_ids = manager_group.user_ids.mapped('partner_id.id')
            asset.message_post(
                body=message_body,
                message_type='email',
                subtype_xmlid='mail.mt_comment',
                partner_ids=partner_ids,
            )

    def validate(self):
        fields = [
            'method',
            'method_number',
            'method_period',
            'method_progress_factor',
            'salvage_value',
            'original_move_line_ids',
        ]
        ref_tracked_fields = self.env['account.asset'].fields_get(fields)
        self.write({'state': 'open'})
        for asset in self:
            tracked_fields = ref_tracked_fields.copy()
            if asset.method == 'linear':
                del tracked_fields['method_progress_factor']
            dummy, tracking_value_ids = asset._mail_track(tracked_fields,
                                                          dict.fromkeys(fields))
            asset_name = {
                'purchase': (_('Asset created'),
                             _('An asset has been created for this move:')),
                'sale': (_('Deferred revenue created'),
                         _('A deferred revenue has been created for this move:')),
                'expense': (_('Deferred expense created'),
                            _('A deferred expense has been created for this move:')),
            }[asset.asset_type]
            msg = asset_name[1] + f' {asset._get_html_link()}'
            asset.message_post(body=asset_name[0],
                               tracking_value_ids=tracking_value_ids)
            for move_id in asset.original_move_line_ids.mapped('move_id'):
                move_id.message_post(body=msg)
            if not asset.depreciation_move_ids:
                asset.compute_depreciation_board()
            asset._check_depreciations()
            asset.depreciation_move_ids.filtered(
                lambda move: move.state != 'posted')._post()
            if asset.account_asset_id.create_asset == 'no':
                asset._post_non_deductible_tax_value()
            message_body = (
                f" Asset {asset.name} has been approved. "
            )
            mail_values = {}
            if asset.custodian_id.work_email:
                mail_values = {
                    'email_to': asset.custodian_id.work_email,
                }
            template = self.env.ref(
                'asset_approval.email_template_approval_confirmed_asset')
            template.send_mail(asset.id, force_send=True,
                               email_values=mail_values)
            asset.message_post(
                body=message_body,
                message_type='email',
                subtype_xmlid='mail.mt_comment',
                partner_ids=[asset.custodian_id.work_contact_id.id],
            )

    def action_reject_asset(self):
        for record in self:
            record.state = 'reject'
            message_body = (
                f" Asset {record.name} has been rejected."
            )
            mail_values = {}

            if record.custodian_id.work_email:
                mail_values = {
                    'email_to': record.custodian_id.work_email,
                }
            template = self.env.ref(
                'asset_approval.email_template_rejected_asset')
            template.send_mail(record.id, force_send=True,
                               email_values=mail_values)
            record.message_post(
                body=message_body,
                message_type='email',
                subtype_xmlid='mail.mt_comment',
                partner_ids=[record.custodian_id.work_contact_id.id],
            )
