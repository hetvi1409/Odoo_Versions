from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountAsset(models.Model):
    """ account.asset model has been inherited for add some fields """
    _inherit = 'account.asset'

    location_id = fields.Many2one('stock.location', 'Stock Location')
    identification_number = fields.Char(string="Asset ID", copy=False,
                                        help='Identification number for the asset')
    state = fields.Selection(
        selection_add=[('disposal_request_sent', 'Disposal Request Sent'), ('close',), ('impaired', 'Impaired'), ('close',)], ondelete={
            'impaired': 'set default',
        }, )
    description = fields.Char(string='Description', help='Description'
                                                         'for the asset')
    asset_type_id = fields.Many2one('asset.type',
                                    domain="[('category_id', '=', asset_category_id)]")
    asset_category_id = fields.Many2one('asset.category')

    asset_type = fields.Selection([('minor', 'Minor Asset'), ('major', 'Major Asset')],string="Asset Type",store=True)
    afs_classification = fields.Many2one('asset.category',string='AFS Classification',domain="[('id', 'in', allowed_category_ids)]")
    classification_type = fields.Selection([('movables','Movables'),('immovable','Immovable'),('intangible','Intangible')])
    allowed_category_ids = fields.Many2many('asset.category',string="Allowed Categories",compute="_compute_allowed_categories")
    serial_number = fields.Char(string='Serial Number')
    alternative_ref = fields.Char(string='Barcode Number')
    job_location_id = fields.Many2one('asset.verification.job.location',
                                      'Location & Office number')
    notes = fields.Text('Notes')
    invoice_number = fields.Char(string='Invoice Number')

    room_number_id = fields.Many2one('asset.verification.job.building',string='Room Number')

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


    comp_id = fields.Float(string='Company ID')
    alternative_ref = fields.Char(string='Barcode Number')
    closing_accum_w_and_t_2024 = fields.Float(string='Closing Accum.W & T 2024')
    total_depreciation_2024 = fields.Float(string='Total Depreciation 2024')
    total_depreciation_2025 = fields.Float(string='Total Depreciation 2025')
    closing_tax_value_2024 = fields.Float(string='Closing Tax Value 2024')
    closing_tax_value_2025 = fields.Float(string='Closing Tax Value 2025')
    depreciation_on_days = fields.Float(string='Depreciation on Days')
    total_depreciation_2022 = fields.Float(string='Total Depreciation 2022')
    total_depreciation_2023 = fields.Float(string='Total Depreciation 2023')
    accumulated_depreciation_2022 = fields.Float(string='Accumulated Depreciation 2022')
    accumulated_depreciation_2023 = fields.Float(string='Accumulated Depreciation 2023')
    accumulated_depreciation_2024 = fields.Float(string='Accumulated Depreciation 2024')
    accumulated_depreciation_2025 = fields.Float(string='Accumulated Depreciation 2025')
    closing_book_value_2022 = fields.Float(string='Closing Book Value 2022')
    closing_book_value_2023 = fields.Float(string='Closing Book Value 2023')
    closing_book_value_2025 = fields.Float(string='Closing Book Value 2025')
    closing_book_value_2024 = fields.Float(string='Closing Book Value 2024')
    w_and_t_per = fields.Float(string='W&T%')
    current_w_and_t_2022 = fields.Float(string='Current W&T 2022')
    current_w_and_t_2023 = fields.Float(string='Current W&T 2023')
    current_w_and_t_2024 = fields.Float(string='Current W&T 2024')
    current_w_and_t_2025 = fields.Float(string='Current W&T 2025')
    closing_accum_w_and_t_2022 = fields.Float(string='Closing Accum.W & T 2022')
    closing_accum_w_and_t_2023 = fields.Float(string='Closing Accum.W & T 2023')
    closing_accum_w_and_t_2025 = fields.Float(string='Closing Accum.W & T 2025')
    closing_tax_value_2022 = fields.Float(string='Closing Tax Value 2022')
    closing_tax_value_2023 = fields.Float(string='Closing Tax Value 2023')
    disposal_reason = fields.Char(string='Disposal Reason', readonly=True)
    asset_barcode = fields.Char(string="Barcode", help="Barcode")

    original_useful_life = fields.Integer('Original Useful Life')
    useful_life_ids = fields.One2many('asset.useful.life', 'asset_id')

    # Asset depreciation
    asset_sub_category_id = fields.Many2one('asset.category',
                                            string="Asset Sub Category")
    useful_life_month = fields.Char(string="Useful Life Month")
    useful_life_day = fields.Char(string="Useful Life Day")
    remaining_useful_life_month = fields.Char(
        string="Remaining Useful Life Month")
    remaining_useful_life_day = fields.Char(string="Remaining Useful Life Days")
    days_from_last_run = fields.Float(string="Days From Last Run")

    impairment = fields.Monetary(string="Impairment for the year")

    # Impairment

    # fair_amount = fields.Monetary(string="Fair amount", help="Asset fair amount")
    impairment_date = fields.Date(string="Impairment date")
    is_impaired = fields.Boolean(string="Impaired or not",
                                 help="Whether asset is impaired or not",
                                 copy=False)
    value_in_use = fields.Monetary("Value in use", help="Asset value in use")
    fair_value_less_cost_to_sell = fields.Monetary(
        "Fair value less cost to sell",
        help="Asset fair value less "
             "cost to sell")
    carrying_amount = fields.Monetary(string="Carrying amount",
                                      help="Asset carrying amount")
    cessation = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                 string='Cessation, or near cessation',
                                 help="Cessation, or near cessation, of "
                                      "the demand or need for services "
                                      "provided by the asset.")
    long_term_change = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                        string='Significant long-term changes',
                                        help="Significant long-term changes with "
                                             "an adverse effect on the entity have"
                                             " taken place during the period or "
                                             "will take place in the near future, "
                                             "in the technological, legal or "
                                             "government policy environment in "
                                             "which the entity operates.")
    evidence = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                string='Evidence is available',
                                help='Evidence is available of obsolescence or '
                                     'physical damage of an asset')
    evidence_document_ids = fields.Many2many('ir.attachment',
                                             'evidence_document',
                                             string="Evidence document",
                                             help='Evidence document details')
    significant_long_term_change = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Significant long-term "
               "changes",
        help="Significant long-term changes with "
             "an adverse effect on the entity have "
             "taken place during the period, or "
             "are expected to take place in the "
             "near future, in the extent to which, "
             "or manner in which, an asset is used "
             "or is expected to be used. These "
             "changes include the asset becoming"
             " idle, plans to discontinue or "
             "restructure the operation to which an"
             " asset belongs, plans to dispose of "
             "an asset before the previously "
             "expected date and reassessing the "
             "useful life of an asset as finite "
             "rather than indefinite.")
    decision = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                string='Decision to halt the construction of '
                                       'the asset',
                                help="decision to halt the construction of the "
                                     "asset before it is complete or in a "
                                     "usable condition.")
    evidence_internal_report = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                                string='Evidence internal report',
                                                help="Evidence is available from internal "
                                                     "reporting that indicates that the "
                                                     "service performance of an asset is, "
                                                     "or will be, significantly worse "
                                                     "than expected.")
    evidence_internal_report_document_ids = fields.Many2many('ir.attachment',
                                                             'evidence_internal_report_document',
                                                             string="Evidence document",
                                                             help='Evidence document details')
    # state = fields.Selection(
    #     selection_add=[('impaired', 'Impaired'), ('close',)], ondelete={
    #         'impaired': 'set default',
    #     }, )
    reason_impairment = fields.Char(string='Reason impairment',
                                    help='Reason for impairment', copy=False)
    image_1920 = fields.Binary(string='Image')

    def action_asset_impairment(self):
        """Method for asset impairment"""
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'asset.impairment',
            'target': 'new',
            'context': {
                'default_asset_ids': [(6, 0, self.ids)]
            },
        }

    def action_account_asset_impairment(self):
        """Method for asset impairment"""
        assets = self.env['account.asset'].browse(
            self.env.context.get('active_ids'))
        for asset in assets:
            if asset.state in ['close' 'cancelled', 'impaired']:
                raise ValidationError(
                    _("Can't impaired this asset, it is already in cancelled or impaired state."))

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'asset.impairment',
            'target': 'new',
            'context': {
                'default_asset_ids': [(6, 0, assets.ids)]
            },
        }

    def action_dispose_approval(self):
        print("llkddd")

    def action_dispose_reject(self):
        print("cccccccccc")

    def action_asset_modify(self):
        """ Override this function Returns an action opening the asset
            modification wizard. Dispose Request option and funtion for the
            Dispose Request added
        """
        self.ensure_one()

        try:
            new_wizard = self.env['asset.modify'].create({
                'asset_id': self.id,
                'modify_action': 'resume' if self.env.context.get(
                    'resume_after_pause')
                else 'dispose' if self.env.user.has_group(
                    'asset_registry.finance_managers_access')
                else 'pause' if self.asset_type == 'purchase'
                else 'modify',
            })
        except:
            new_wizard = self.env['asset.modify'].create({
                'asset_id': self.id,
                'modify_action': 'resume' if self.env.context.get(
                    'resume_after_pause')
                else 'dispose_request' if self.env.user.has_group(
                    'asset_registry.department_users_access')
                else 'pause' if self.asset_type == 'purchase'
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

    @api.model
    def action_jmc_number_change(self):
        """Change the jmc number of assets"""

        records = self.env['account.asset'].search([])

        for record in records:
            if record.alternative_ref:
                # Remove 'jpc' from the name field
                new_name = record.alternative_ref.replace('JPC', '').strip()
                record.write({'alternative_ref': new_name})
                new_name = record.alternative_ref.replace('JCP', '').strip()
                record.write({'alternative_ref': new_name})

    @api.model
    def action_computation_change(self):
        """Change the computation of assets"""

        records = self.env['account.asset'].search([])

        for record in records:
            if record.prorata_computation_type != 'daily_computation':
                record.write({'prorata_computation_type': 'daily_computation'})

    @api.model
    def action_change_category(self):
        """Change the category"""
        records = self.env['account.asset'].search([('asset_category_id', '=', 18)])
        for rec in records:
            rec.asset_category_id = 20