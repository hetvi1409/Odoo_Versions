from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AssetVerificationHistory(models.Model):
    _name = 'asset.verification.history'
    _description = "Asset Verification History"
    _rec_name = 'history_id'

    history_id = fields.Many2one('account.asset')

    is_verified = fields.Boolean(string="Verified", readonly=True)
    major_group_description = fields.Char(string="Description",help="Description of the asset")
    barcode_past_year = fields.Char(string="Barcode Past Year",help="Barcode Past Year")
    current_condition_past_year = fields.Char(string="Current Condition Past Year",help="Current Condition Past Year")
    current_condition_this_year = fields.Char(string="Current Condition This Year",help="Current Condition This Year")
    name_installation = fields.Char(string="Name Installation",help="Name Installation")
    asset_component = fields.Char(string="Asset Component",help="Asset Component")
    parent_barcode = fields.Char(string="Parent Barcode", help="Parent Barcode")
    asset_size = fields.Char(string="Asset Size", help="Asset Size")
    asset_make_type = fields.Many2one("asset.type", help="Asset Make Type")
    estimated_useful_life_month = fields.Char(string="Estimated Useful Life Month",help="Estimated Useful Life Month")
    date_verification = fields.Date(string="Date of verification",help="Date of verification")
    comments = fields.Char(string="Comments", help="Comments")
    condition = fields.Many2many('asset.condition', string="Condition", help="Condition of the asset",)
    inspector = fields.Char(string="Inspector", help="Inspector")
    asset_verification_user_id = fields.Many2one('res.users',string="Verification User")
    asset_type_id = fields.Many2one('asset.type')
    location_id = fields.Many2one('stock.location', string="Location", help="Location of the asset")
    past_year = fields.Char('Past Year')
    this_year = fields.Char('This Year')
    location_id = fields.Many2one('asset.verification.job.location',string="Location", help="Location of the asset")

    # Images
    image_ids = fields.One2many('asset.verification.image', 'history_id', string='Images')
    image_count = fields.Integer(string='Image Count', compute='_compute_image_count')

    @api.depends('image_ids')
    def _compute_image_count(self):
        for record in self:
            record.image_count = len(record.image_ids)


    def cron_copy_comments_to_condition(self):
        histories = self.search([])
        for history in histories:
            if history.comments:
                condition_names = history.comments.split(', ')
                condition_ids = self.env['asset.condition'].search([('name', 'in', condition_names)]).ids
                history.condition = [(6, 0, condition_ids)]
                # history.condition = condition_ids
            else:
                history.condition = [(5, 0, 0)]  # Clear the M2M field if no comments

    # def open_kanban_view(self):
    #     self.ensure_one()
    #     return {
    #         'name': _('Asset Verification History'),
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'asset.verification.history',
    #         'view_mode': 'kanban',
    #         'views': [(False, 'kanban'), (False, 'form')],
    #         'domain': [('id', '=', self.id)],
    #         'target': 'current',
    #     }


    def open_kanban_view(self):
        self.ensure_one()

        return {
            'name': _('Asset Verification Images'),
            'type': 'ir.actions.act_window',
            'res_model': 'asset.verification.image',
            'view_mode': 'kanban,form',
            'domain': [('history_id', '=', self.id)],
            'target': 'current',
            'context': {
                'default_history_id': self.id,
            },
        }


