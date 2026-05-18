from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta



class AccountAsset(models.Model):
    """ account.asset model has been inherited for add some fields """
    _inherit = 'account.asset'

    supplier_id = fields.Many2one('res.partner',string='Supplier')
    payment_number = fields.Integer(string='Payment Number')
    order_number = fields.Char(string='Order Number')
    description = fields.Char(string='Description', help='Description '
                                                         'for the asset')
    state = fields.Selection(
        selection_add=[('disposed', 'Disposed'),('damaged', 'Damaged'),('written_off', 'Written Off'),('lost', 'Lost')])
    afs_classification = fields.Many2one('asset.category',string='AFS Classification',domain="[('id', 'in', allowed_category_ids)]")
    allowed_category_ids = fields.Many2many('asset.category',string="Allowed Categories",compute="_compute_allowed_categories")
    serial_number = fields.Char(string='Serial Number')
    alternative_ref = fields.Char(string='Barcode Number')
    job_location_id = fields.Many2one('asset.verification.job.location',
                                      'Location & Office number')
    department_id = fields.Many2one('hr.department',string='Chief Directorate & Directorate')
    custodian_id = fields.Many2one('hr.employee', 'Custodian / User', tracking=True)
    # condition = fields.Char(string='Condition', help='Condition of the asset', readonly=True, store=True, compute='_compute_condition')
    original_useful_life = fields.Integer('Life Cycle')
    disposal_date = fields.Date(string='Disposal Date')
    disposal_price = fields.Float(string='Disposal Price')
    disposal_method = fields.Char(string='Disposal Method')
    classification_type = fields.Selection([('movables','Movables'),('immovable','Immovable'),('intangible','Intangible')])
    asset_type = fields.Selection([('minor', 'Minor Asset'), ('major', 'Major Asset')],string="Asset Type",store=True)
    notes = fields.Text('Notes')
    invoice_number = fields.Char(string='Invoice Number')

    room_number_id = fields.Many2one('asset.verification.job.building',string='Room Number')
    last_depreciation_move_id = fields.Many2one('account.move',string='Last Depreciation Move',compute='_compute_last_depreciation_move_id')
    last_depreciation_date = fields.Date(string='Last Depreciation Date',related='last_depreciation_move_id.date')
    remaining_days = fields.Integer(string='Remaining Days',compute='_compute_remaining_time')
    remaining_months = fields.Integer(string='Remaining Months',compute='_compute_remaining_time')
    floor = fields.Char(string='Floor')


    def _compute_last_depreciation_move_id(self):
        for asset in self:
            last_move = asset.depreciation_move_ids.sorted(lambda m: m.date, reverse=True)[:1]
            asset.last_depreciation_move_id = last_move.id if last_move else False

    @api.depends('last_depreciation_date')
    def _compute_remaining_time(self):
        today = fields.Date.today()

        for asset in self:
            asset.remaining_days = 0
            asset.remaining_months = 0

            if not asset.last_depreciation_date:
                continue

            if asset.last_depreciation_date <= today:
                continue

            delta_days = (asset.last_depreciation_date - today).days
            asset.remaining_days = delta_days

            rd = relativedelta(asset.last_depreciation_date, today)
            asset.remaining_months = rd.years * 12 + rd.months


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'original_value' in vals and vals['original_value']:
                threshold = float(
                    self.env['ir.config_parameter'].sudo().get_param(
                        'asset_registry.minor_major_threshold', 1000
                    )
                )
                if vals['original_value'] > threshold:
                    vals['asset_type'] = 'major'
                else:
                    vals['asset_type'] = 'minor'
            if vals.get('afs_classification'):
                category = self.env['asset.category'].browse(vals['afs_classification'])
                if category:
                    vals['classification_type'] = category.get_classification_type()


        return super(AccountAsset, self).create(vals_list)

    def write(self, vals):
        if 'original_value' in vals and vals['original_value']:
            threshold = float(
                self.env['ir.config_parameter'].sudo().get_param(
                    'asset_registry.minor_major_threshold', 1000
                )
            )
            if vals['original_value'] > threshold:
                vals['asset_type'] = 'major'
            else:
                vals['asset_type'] = 'minor'
        elif vals.get('afs_classification'):
                category = self.env['asset.category'].browse(vals['afs_classification'])
                if category:
                    vals['classification_type'] = category.get_classification_type()

        return super(AccountAsset, self).write(vals)



    # @api.constrains('original_value', 'asset_type')
    # def _check_asset_value_type(self):
    #     threshold = float(
    #         self.env['ir.config_parameter'].sudo().get_param(
    #             'asset_registry.minor_major_threshold', 1000
    #         )
    #     )

    #     for rec in self:
    #         if rec.asset_type == 'minor' and rec.original_value > threshold:
    #             raise ValidationError(
    #                 f"Minor Asset value cannot be greater than the threshold ({threshold})."
    #             )

    #         if rec.asset_type == 'major' and rec.original_value <= threshold:
    #             raise ValidationError(
    #                 f"Major Asset value must be greater than the threshold ({threshold})."
    #             )

    @api.depends('classification_type')
    def _compute_allowed_categories(self):
        for rec in self:
            domain = []
            if rec.classification_type == 'movables':
                domain = [('is_movable', '=', True)]
            elif rec.classification_type == 'immovable':
                domain = [('is_immovable', '=', True)]
            elif rec.classification_type == 'intangible':
                domain = [('is_intangible', '=', True)]

            rec.allowed_category_ids = self.env['asset.category'].search(domain)
