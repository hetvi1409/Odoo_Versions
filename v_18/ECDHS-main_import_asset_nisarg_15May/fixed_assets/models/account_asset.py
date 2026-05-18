from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountAsset(models.Model):
    _inherit = 'account.asset'

    state = fields.Selection(
        selection=[('model', 'Model'),
                   ('draft', 'Draft'),
                   ('request_for_approval', 'Submit for Approval'),
                   ('open', 'In-Use'),
                   ('damaged', 'Damaged'),
                   ('paused', 'On Hold'),
                   ('close', 'Closed'),
                   ('cancelled', 'Cancelled'),
                   ('asset_disposed','Asset Disposed')],
        string='Status',
        copy=False,
        default='draft',
        readonly=True,
        help="When an asset is created, the status is 'Draft'.\n"
             "If the asset is confirmed, the status goes in 'Running' and the depreciation lines can be posted in the accounting.\n"
             "The 'On Hold' status can be set manually when you want to pause the depreciation of an asset for some time.\n"
             "You can manually close an asset when the depreciation is over.\n"
             "By cancelling an asset, all depreciation entries will be reversed")
    active = fields.Boolean(default=True)
    minor_major_classification = fields.Selection([('minor', 'Minor'), ('major', 'Major')],
                                                  string="Classification",
                                                  compute="_compute_minor_major")

    @api.depends('original_value')
    def _compute_minor_major(self):
        for rec in self:
            minor_major_classification = ""
            if rec.original_value > 3000:
                minor_major_classification = 'major'
            else:
                minor_major_classification = 'minor'
            rec.minor_major_classification = minor_major_classification

    def action_approve(self):
        self.state='request_for_approval'

    def action_view_verification(self):
        """View Verification"""
        today = fields.Datetime.now()

        job = self.env['asset.verification.job'].search([
            ('verification_period_from', '<=', today),
            ('verification_period_to', '>=', today),
        ]).mapped('asset_ids')
        job_line = job.filtered(lambda x: x.asset_id.id == self.id)[:1]
        # job = self.env['asset.verification.job.line'].search([('asset_id', '=', self.id)])
        if job_line:
            return {
                'name': _('Verification'),
                'view_mode': 'form',
                'res_model': 'asset.verification',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context':
                    {
                        'default_verification_job_id': job_line.account_verification_job_id.id,
                        'default_asset_id': self.id,
                        'default_barcode_number': self.alternative_ref,
                        'default_description': self.description,
                        'default_location_id': self.job_location_id.id,
                        'default_user_id': self.env.uid,
                        'default_custodian_id': self.custodian_id.id,
                        'default_custodian_department_id': self.custodian_department_id.id,
                    }
            }
        else:
            raise UserError(_("Please assign this product to a job Location"))
