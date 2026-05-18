from odoo import fields, models


class AssetRemovalApproval(models.Model):
    _inherit = "asset.removal.approval"

    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('send', 'Sent for Approval'),
        ('verified', 'Verified'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', required=True, readonly=True, tracking=True,
        default='draft')
    asset_id = fields.Many2one('account.asset', 'Asset', domain="[('state', '=', 'open')]", required=True)

    def action_approve(self):
        """ Approve the removal request """
        for record in self:
            record.state = 'approved'
            record.asset_id.state = "close"
            record.asset_id.active = False  # Mark the asset as inactive (removed)
            message_body = f"Asset {record.asset_id.name} has been approved for removal."
            mail_values = {}
            if record.user_id.partner_id.email:
                mail_values = {'email_to': record.user_id.partner_id.email}

            template = self.env.ref('asset_verification.email_template_asset_removal_approved')
            template.send_mail(record.id, force_send=True, email_values=mail_values)

            record.message_post(body=message_body, message_type='email', subtype_xmlid='mail.mt_comment',
                                partner_ids=[record.user_id.partner_id.id])


    def action_verify(self):
        self.write({'state': 'verified'})
        mail_template = self.env.ref(
            'asset_addition.email_template_asset_removal_verified')
        recipient_ids = self.env.ref(
            'asset_verification.group_staging_approval_manager').users
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)


