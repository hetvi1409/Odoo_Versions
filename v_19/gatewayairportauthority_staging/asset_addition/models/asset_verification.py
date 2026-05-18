from odoo import fields, models


class AssetVerification(models.Model):
    _inherit = "asset.verification"


    state = fields.Selection([
        ('draft', "Draft"),
        ('verified', "Verified"),
        ('approved', "Approved"),
        ('rejected', "Rejected")
    ], string="Status", readonly=True, default='draft')


    def action_approve(self):
        self.write({'state': 'approved'})
        mail_template = self.env.ref(
            'asset_addition.email_template_asset_verification_approved')
        recipient_ids = self.env.ref(
            'fixed_assets.group_fixed_asset_approver').users
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
    def action_reject(self):
        self.write({'state': 'rejected'})
        mail_template = self.env.ref(
            'asset_addition.email_template_asset_verification_reject')
        recipient_ids = self.env.ref(
            'fixed_assets.group_fixed_asset_approver').users
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)

    def action_verify(self):
        res = super().action_verify()
        self.state = 'verified'
        return res
