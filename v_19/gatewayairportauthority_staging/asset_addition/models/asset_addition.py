from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
import random


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
    salvage_value = fields.Monetary(string="Not Depreciable Value")
    afs_classification = fields.Many2one('asset.category',string='AFS Classification')
    serial_number = fields.Char(string='Serial Number')
    alternative_ref = fields.Char(string='Barcode Number')
    job_location_id = fields.Many2one('asset.verification.job.location', 'Location & Office number')

    supporting_document_ids = fields.Many2many("ir.attachment")
    quantity = fields.Integer(string="Quantity", default=1)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', '1st Approval'),
        ('approved', 'Approved'),
        ('refused', 'Cancelled'),
        ('in_use', 'In Use'),
    ], default='draft', tracking=True)

    created_asset_id = fields.Many2one('account.asset', string="Created Asset", copy=False, readonly=True)
    created_asset_ids = fields.Many2many('account.asset', string="Created Asset", copy=False, readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' not in vals or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'asset.addition') or _('New')
        return super().create(vals_list)

    # -------------------------
    # Actions
    # -------------------------
    def action_submit(self):
        self.write({'state': 'submitted'})
        mail_template = self.env.ref(
            'asset_addition.email_template_asset_addition_submitted')
        recipient_ids = self.env.ref('asset_addition.group_account_reviewer').user_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)

    def action_review(self):
        self.write({'state': 'reviewed'})
        mail_template = self.env.ref(
            'asset_addition.email_template_asset_addition_review')
        recipient_ids = self.env.ref(
            'asset_addition.group_account_final_reviewer').user_ids
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
            'fixed_assets.group_fixed_asset_approver').user_ids
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
            'fixed_assets.group_fixed_asset_approver').user_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)

    def _generate_unique_barcode(self):
        """Generate a unique barcode and ensure no existing asset uses it."""
        Asset = self.env['account.asset'].sudo()
        while True:
            barcode = str(random.randint(100000000000, 999999999999))

            exists = Asset.search_count([('alternative_ref', '=', barcode)],
                                        limit=1)
            if not exists:
                return barcode

    def action_mark_in_use(self):
        for rec in self:

            created_assets = self.env['account.asset']
            Asset = self.env['account.asset'].sudo()

            for i in range(rec.quantity):
                # ---- Generate UNIQUE BARCODE ----
                barcode_val = self._generate_unique_barcode()

                asset = Asset.create({
                    'name': f"{rec.asset_name} - {i + 1}" if rec.quantity > 1 else rec.asset_name,
                    'description': rec.description,
                    'original_value': rec.original_value,
                    'salvage_value': rec.salvage_value,
                    'afs_classification': rec.afs_classification.id,
                    'serial_number': (
                        f"{rec.serial_number} - {i + 1}"
                        if rec.quantity > 1 and rec.serial_number
                        else rec.serial_number
                    ),

                    # ---> Unique Barcode stored in alternative_ref
                    'alternative_ref': barcode_val,

                    'job_location_id': rec.job_location_id.id,
                })

                asset.action_custom_validate()
                created_assets += asset

            rec.created_asset_ids = [(6, 0, created_assets.ids)]
            rec.state = 'in_use'

    def action_view_asset(self):
        self.ensure_one()
        assets = self.created_asset_ids

        if len(assets) == 1:
            return {
                "type": "ir.actions.act_window",
                "name": _("Asset"),
                "res_model": assets._name,
                "view_mode": "form",
                "res_id": assets.id,
                "target": "current",
                "context": {"create": False},
            }

        return {
            "type": "ir.actions.act_window",
            "name": _("Assets"),
            "res_model": assets._name,
            "view_mode": "list,form",
            "domain": [('id', 'in', assets.ids)],
            "target": "current",
            "context": {"create": False},
        }

    def unlink(self):
        """Delete the current record."""
        for rec in self:
            if rec.state not in ('refused', 'draft'):
                raise UserError(_('You cannot delete a asset addition request which is not draft or cancelled!'))
        return super().unlink()