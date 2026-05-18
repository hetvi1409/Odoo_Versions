from odoo import models, fields, api, _

from odoo.exceptions import UserError


class AssetAddition(models.Model):
    _name = 'asset.addition'
    _description = 'Asset Addition Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date DESC'

    name = fields.Char("Asset Addition Number", readonly=True, copy=False)
    asset_name = fields.Char("Asset Name", required=True)
    description = fields.Text("Description")

    currency_id = fields.Many2one(related="company_id.currency_id", string='Currency', readonly=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    original_value = fields.Monetary(string="Original Value")
    salvage_value = fields.Monetary(string="Original Value")
    afs_classification = fields.Many2one('asset.category',string='AFS Classification')
    serial_number = fields.Char(string='Serial Number')
    alternative_ref = fields.Char(string='Barcode Number')
    job_location_id = fields.Many2one('asset.verification.job.location',
                                      'Location & Office number')

    supporting_document_ids = fields.Many2many("ir.attachment")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Cancelled'),
        ('in_use', 'In Use'),
    ], default='draft', tracking=True)

    created_asset_id = fields.Many2one('account.asset', string="Created Asset", readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('asset.addition') or 'New'
        return super().create(vals)

    # -------------------------
    # Actions
    # -------------------------
    def action_submit(self):
        self.write({'state': 'submitted'})
        mail_template = self.env.ref(
            'asset_addition.email_template_asset_addition_submitted')
        recipient_ids = self.env.ref(
            'fixed_assets.group_fixed_asset_approver').users
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)

    def action_approve(self):
        self.write({'state': 'approved'})
        mail_template = self.env.ref(
            'asset_addition.email_template_asset_addition_approved')
        recipient_ids = self.env.ref(
            'fixed_assets.group_fixed_asset_approver').users
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)

    def action_refuse(self):
        self.write({'state': 'refused'})
        mail_template = self.env.ref(
            'asset_addition.email_template_asset_addition_approved')
        recipient_ids = self.env.ref(
            'fixed_assets.group_fixed_asset_approver').users
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)

    def action_mark_in_use(self):
        for rec in self:
            # Create asset record once approved
            asset = self.env['account.asset'].create({
                'name': rec.asset_name,
                'description': rec.description,
                'original_value': rec.original_value,
                'salvage_value': rec.salvage_value,
                'afs_classification': rec.afs_classification.id,
                'serial_number': rec.serial_number,
                'alternative_ref': rec.alternative_ref,
                'job_location_id': rec.job_location_id.id,
            })
            rec.created_asset_id = asset.id
            rec.created_asset_id.action_custom_validate()
            rec.state = 'in_use'

    def action_view_asset(self):
        action = {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "name": _("Asset"),
            "res_id": self.created_asset_id.id,
            "res_model": self.created_asset_id._name,
            "target": "current",
            'context' : {'create': 'False'}
        }
        return action

    def unlink(self):
        """Delete the current record."""
        for rec in self:
            if rec.state not in ('refused', 'draft'):
                raise UserError(_('You cannot delete a asset addition request which is not draft or cancelled!'))
        return super().unlink()