from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AssetVerification(models.Model):
    _name = 'asset.verification'
    _description = "Asset Verification"

    # Fields
    asset_id = fields.Many2one('account.asset', string="Asset")
    barcode_number = fields.Char(string="Barcode Number", help="Barcode Number")
    description = fields.Char(string="Description", help="Description")
    verify = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Verify", required=True, help="Whether to verify the asset or not")
    allocation = fields.Many2one('res.users', string="Allocated User")
    location = fields.Many2one('stock.location',string="Location", help="Location of the asset")
    condition = fields.Many2many('asset.condition', string="Condition", help="Condition of the asset")
    verification_job_id = fields.Many2one('asset.verification.job', string="Verification Job", required=True, help="Verification Job associated with this verification")
    user_id = fields.Many2one('res.users', string="Current User", default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', "Draft"),
        ('verified', "Verified"),
    ], string="Status", readonly=True, default='draft')
    custodian_id = fields.Many2one('hr.employee',string='Custodian')


    # @api.model
    # def create(self, vals):
    #     res = super().create(vals)
    #     # Update asset fields based on verification details
    #     if res.asset_id:
    #         res.asset_id.write({
    #             'name': res.description,
    #             'alternative_ref': res.barcode_number,
    #             'allocation': res.allocation,
    #             'location': res.location,
    #             'condition': res.condition,
    #             'is_verified': res.verify == 'yes',
    #             'verification_job_id': res.verification_job_id.id,
    #             'verification_user_id': res.user_id.id,
    #         })
    #     return res
    #
    # def write(self, vals):
    #     result = super().write(vals)
    #     # Update asset fields based on verification details
    #     if self.asset_id:
    #         self.asset_id.write({
    #             'name': self.description,
    #             'alternative_ref': self.barcode_number,
    #             'allocation': self.allocation,
    #             'location': self.location,
    #             'condition': self.condition,
    #             'is_verified': self.verify == 'yes',
    #             'verification_job_id': self.verification_job_id.id,
    #             'verification_user_id': self.user_id.id,
    #         })
    #     return result

    def action_verify(self):
        print('verifyyyyyyyyyyyy', self.env.context)

        if self.verify == 'yes':
            # Get the verification job from the context
            job = self.env['asset.verification.job'].browse(self.env.context.get('default_verification_job_id'))

            if job:
                # Filter the asset lines associated with the job to find the line for the asset being verified
                verification_line = job.asset_ids.filtered(lambda line: line.asset_id.id == self.asset_id.id)

                if verification_line:
                    # Mark the asset line as verified and link to the current verification record
                    verification_line.write({
                        'verified': True,
                        'asset_verification_line_id': self.id
                    })

                # Update the verification job's progress
                verified_assets = len(job.asset_ids.filtered(lambda line: line.verified))
                total_assets = len(job.asset_ids)

                job.write({
                    'state': 'in_progress',
                    'verified_count': verified_assets,
                })

                # If all assets are verified, mark the job as completed
                if total_assets == verified_assets:
                    job.write({'state': 'completed'})
        else:
            # Handle the case where verification is not completed
            pass

        return {'type': 'ir.actions.act_window_close'}

    def action_not_verify(self):
        # Implement logic for not verifying if required
        pass


    def action_modify(self):
        self.ensure_one()
        new_wizard = self.env['asset.modify'].create({
            'asset_id': self.asset_id.id,
            'modify_action': 'resume' if self.env.context.get('resume_after_pause')
            else 'dispose' if self.env.user.has_group('asset_registry.finance_managers_access')
            else 'pause' if self.asset_id.asset_type == 'purchase'
            else 'modify',
        })
        return {
            'name': _('Modify Asset'),
            'view_mode': 'form',
            'res_model': 'asset.modify',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': new_wizard.id,
            'context': self.env.context,
        }

class AssetCondition(models.Model):
    _name = 'asset.condition'
    _description = "Asset Condition"

    name = fields.Char(string="Condition", required=True)
