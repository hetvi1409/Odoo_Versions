from odoo import models, fields
from odoo.exceptions import UserError

class AssetVerificationStaging(models.Model):
    _name = 'asset.verification.staging'
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
    ], string="Verify", required=True, help="Whether to verify the asset or not")
    category_id = fields.Many2one('asset.category', string="Asset Category", help="Category of the asset")
    approval_user_id = fields.Many2one('res.users', string="Approved by", readonly=True)
    active = fields.Boolean(string='Active', default=True)
    custodian_id = fields.Many2one('hr.employee',string='Custodian')

    def action_submit_for_approval(self):
        """ Submit the asset for approval """
        self.write({'state': 'awaiting_approval'})


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

        }
        asset = self.env['account.asset'].create(asset_vals)

        # Find the related verification job
        job = self.env['asset.verification.job'].search([
            ('id', '=', self.verification_job_id.id)
        ], limit=1)

        if not job:
            raise UserError("Verification job not found.")

        # Add a new job line for the created asset
        job_line_vals = {
            'asset_id': asset.id,
            'account_verification_job_id': job.id,
            'verified': True  # Assuming the new line is marked as verified
        }
        self.env['asset.verification.job.line'].create(job_line_vals)

        # Update the staging asset record
        self.write({
            'state': 'approved',
            'approval_user_id': self.env.user.id,
        })

        # Archive the staging asset
        self.active = False


    def action_reject(self):
        """ Reject the asset (only for manager) """
        if not self.env.user.has_group('asset_verification.group_staging_approval_manager'):
            raise UserError("You do not have the rights to reject this asset.")
        self.write({'state': 'rejected'})

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
