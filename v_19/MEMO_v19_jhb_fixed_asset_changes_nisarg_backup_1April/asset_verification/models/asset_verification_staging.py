from odoo import models, fields,api, _
from odoo.exceptions import UserError
from datetime import date


class AssetVerificationStaging(models.Model):
    _name = 'asset.verification.staging'
    _inherit = ['mail.thread']
    _description = 'Staging for unverified assets'

    # Fields
    name = fields.Char(string="Asset Name", required=True)
    barcode = fields.Char(string="Barcode", required=True)
    description = fields.Text(string="Description")
    verification_job_id = fields.Many2one('asset.verification.job', string="Verification Job")
    allocation = fields.Many2one('res.users', string="Allocated User")
    location = fields.Many2one('stock.location', string="Location", help="Location of the asset")
    location_job_id = fields.Many2one('asset.verification.job.location', string="Location", help="Location of the asset")
    condition = fields.Many2many('asset.condition', string="Condition", help="Condition of the asset")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('awaiting_approval', 'Awaiting Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string="Status", default='draft')

    # Additional Fields
    user_id = fields.Many2one('res.users', string="Current User", default=lambda self: self.env.user)
    verify = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Verify", required=False, help="Whether to verify the asset or not")
    category_id = fields.Many2one('asset.category', string="Asset Category", help="Category of the asset")
    approval_user_id = fields.Many2one('res.users', string="Approved by", readonly=True)
    active = fields.Boolean(string='Active', default=True)
    custodian_id = fields.Many2one('hr.employee',string='Custodian')
    original_value = fields.Float()
    original_useful_life = fields.Float()
    document_id = fields.Binary(string="Document")
    asset_last_status = fields.Char(string="Asset Last Status", help="Asset Last Status")

    @api.model
    def default_get(self, fields):
        res = super(AssetVerificationStaging, self).default_get(fields)
        asset_id = self.env.context.get('default_asset_id')
        if asset_id:
            history = self.env['asset.verification.history'].search(
                [('history_id', '=', asset_id)],
            )
            if history and len(history) > 0:
                history = history.sorted(key=lambda r: r.create_date)
                history = history[-1]
                res['asset_last_status'] = history.comments
            else:
                res['asset_last_status'] = 'No previous verification history found.'
        else:
            res['asset_last_status'] = 'No previous verification history found.'
        return res

    def action_submit_for_approval(self):
        """ Submit the asset for approval """
        self.write({'state': 'awaiting_approval'})
        manager_group = self.env.ref('asset_verification.group_staging_approval_manager')

        # Get partner objects
        mail_values = {}

        partners = manager_group.user_ids.mapped('partner_id')

        # Send emails to each partner
        # for partner in partners:
        #     if partner.email:  # Ensure the partner has an email address
        #         mail_values = {
        #             'email_to': partner.email,
        #             # Other values can be set as needed
        #         }
        # template = self.env.ref('asset_verification.email_template_asset_approval')
        # template.send_mail(self.id, force_send=True, email_values=mail_values)

        # Send an in-app notification
        for asset in self:
            message_body = (
                f" Asset {asset.name} has been submitted for approval. "
            )
            # Send to all followers and specifically to the Impairment Manager group
            manager_group = self.env.ref('asset_verification.group_staging_approval_manager').id

            partner_ids = self.env['res.groups'].browse(manager_group).user_ids.mapped('partner_id.id')

            asset.message_post(
                body=message_body,
                message_type='email',
                subtype_xmlid='mail.mt_comment',
                partner_ids=partner_ids,
            )


    def action_approve(self):
        """ Approve the staging asset (only for manager) """
        if not self.env.user.has_group('asset_verification.group_staging_approval_manager'):
            raise UserError("You do not have the rights to approve this asset.")

        # Create the asset
        asset_vals = {
            'name': self.name,
            'alternative_ref': self.barcode,
            'description': self.description,
            'location_id': self.location.id if self.location else False,
            'asset_category_id': self.category_id.id if self.category_id else False,
            'custodian_id': self.custodian_id.id if self.custodian_id else False,
            'job_location_id':self.location_job_id.id if self.location_job_id else False,
            'original_value': self.original_value,
            'original_useful_life': self.original_useful_life,
            'afs_classification': self.category_id.id if self.category_id else False,
        }
        asset = self.env['account.asset'].create(asset_vals)

        # Create record in Asset Verification History
        asset_history_vals = {
            'history_id': asset.id,
            'is_verified': self.verify,
            'parent_barcode': self.barcode,
            'location_id': self.location_job_id.id if self.location_job_id else False,
            'this_year': date.today().year,
            'past_year': date.today().year - 1,
            'condition': self.condition if self.condition else False,
            'asset_verification_user_id': self.env.user.id,
            'date_verification': date.today(),
            'major_group_description': self.description
        }

        asset_history = self.env['asset.verification.history'].create(asset_history_vals)

        # Find the related verification job
        job = self.env['asset.verification.job'].search([
            ('id', '=', self.verification_job_id.id)
        ], limit=1)

        # if not job:
        #     raise UserError("Verification job not found.")

        # Add a new job line for the created asset
        job_line_vals = {
            'asset_id': asset.id,
            'account_verification_job_id': job.id if job else False,
            'verified': True  # Assuming the new line is marked as verified
        }
        self.env['asset.verification.job.line'].create(job_line_vals)

        # Update the staging asset record
        self.write({
            'state': 'approved',
            'approval_user_id': self.env.user.id,
        })

        message_body = (
            f" Asset {asset.name} has been approved. "
        )

        asset.message_post(
            body=message_body,
            message_type='email',
            subtype_xmlid='mail.mt_comment',
            # partner_ids=[self.custodian_id.user_id.partner_id.id],
        )

        # Archive the staging asset
        self.active = False


    def action_reject(self):
        """ Reject the asset (only for manager) """
        if not self.env.user.has_group('asset_verification.group_staging_approval_manager'):
            raise UserError("You do not have the rights to reject this asset.")
        self.write({'state': 'rejected'})
        message_body = (
            f" Asset {self.name} has been rejected. "
        )

        self.message_post(
            body=message_body,
            message_type='email',
            subtype_xmlid='mail.mt_comment',
            # partner_ids=[self.custodian_id.user_id.partner_id.id],
        )

    def action_open_asset_creation_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Asset Wizard',
            'res_model': 'account.asset',
            'view_mode': 'form',
            'view_id': self.env.ref('account_asset.view_account_asset_form').id,
            'target': 'new',
            'context': {
                'default_name': self.name,
                'default_alternative_ref': self.barcode,
                'default_description': self.description,
                'default_location_id':self.location.id,
                'default_asset_category_id': self.category_id.id,

            }
        }
