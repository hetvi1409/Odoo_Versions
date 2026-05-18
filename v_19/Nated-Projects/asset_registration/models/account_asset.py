from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountAsset(models.Model):
    _inherit = 'account.asset'
    # _sql_constraints = [
    #     ('identification_number_uniq', 'unique (identification_number)',
    #      """Identification number must be unique"""),
    # ]

    name = fields.Char(string='Asset Description', compute='_compute_name',
                       store=True,
                       required=True, readonly=False, tracking=True)

    description = fields.Text(string='Description', help='Description '
                                                         'for the asset')
    location_id = fields.Many2one('stock.location', 'Stock Location')
    office = fields.Char(string='Office Name')
    identification_number = fields.Char(string="Asset ID", copy=False,
                                        help='Identification number for the asset')
    deed_number = fields.Char(string="Deed Number",
                              help='Deed number for the asset',
                              copy=False)
    stand_number = fields.Char(string="Stand Number",
                               help='Stand number for the asset',
                               copy=False)
    physical_street = fields.Char('Street', help='street name')
    physical_street2 = fields.Char('Street', help='street')
    physical_city = fields.Char('City', help='City name')
    physical_zip = fields.Char('Zip Code', help='zip code')
    physical_state_id = fields.Many2one("res.country.state", string='State',
                                        ondelete='restrict')
    physical_country_id = fields.Many2one('res.country', string='Country',
                                          ondelete='restrict')
    revaluation_date = fields.Date(string='Revaluation Date')
    re_valued_value = fields.Monetary(string='ReValued Value')
    accumulated_depreciation = fields.Monetary(
        string='Accumulated Depreciation On disposal for the year',
        help="Accumulated Depreciation")
    accumulated_depreciation_transfer = fields.Monetary(
        string='Accumulated Depreciation On disposal for the year',
        help="Accumulated Depreciation")
    depreciation_charge = fields.Monetary(string='Depreciation Charge')
    impairment_losses = fields.Monetary(string='Impairment Losses')
    funding_source = fields.Char(string='Funding Source')
    retired_date = fields.Date(string='Retired Date')
    disposal = fields.Char(string='Disposal of the year')
    condition_asset = fields.Char(string='Condition of the Asset')
    remaining_life = fields.Char(string='Remaining Life')
    expected_life = fields.Char(string='Expected Life')

    asset_category_id = fields.Many2one('asset.category')
    asset_type_id = fields.Many2one('asset.type',
                                    domain="[('category_id', '=', asset_category_id)]")
    serial_number = fields.Char(string='Serial Number')
    conditional_assessment = fields.Char(string='Conditional Assessment')

    asset_reason = fields.Selection([('loss', 'Loss'), ('theft', 'Theft'),
                                     ('destruction', 'Destruction'),
                                     ('material_impairment',
                                      'Material Impairment')], "Asset Reasons")
    loss_description = fields.Text(string="Loss Description")

    life_in_months = fields.Float('Revised/original useful life in months',
                                  help='Revised/original useful Life in months')
    useful_life_ids = fields.One2many('asset.useful.life', 'asset_id')
    addition = fields.Float('Addition for the year')

    adjustment = fields.Float('Adjustment')
    closing_cost = fields.Monetary('Closing Cost')
    acc_dep_opening = fields.Monetary('Acc Dep opening')
    closing_accumulated_depreciation = fields.Monetary(
        'Closing Accumulated Depreciation')
    opening_book_value_july_22 = fields.Monetary(
        'Opening Book Value of the year')
    closing_book_value_july_22 = fields.Monetary(
        'Closing Book Value of the year')
    condition = fields.Char(string="Condition")
    type = fields.Selection(
        [('FAR', 'FAR'), ('INFRASTRUCTURE', 'INFRASTRUCTURE')])
    custodian = fields.Char('Custodian')
    opening_cost = fields.Monetary('Opening Cost')
    original_useful_life = fields.Integer('Original Useful Life')
    component = fields.Char(string='Component')
    impair = fields.Char('Number of months to impair')

    equipment_id = fields.Many2one('maintenance.equipment')

    method_period = fields.Selection([('1', 'Months'), ('12', 'Years')],
                                     string='Number of Months in a Period',
                                     readonly=True, default='1',
                                     states={'draft': [('readonly', False)],
                                             'model': [('readonly', False)]},
                                     help="The amount of time between two depreciations")
    transfer = fields.Monetary('Transfer for the year')
    impairment = fields.Monetary(string="Impairment for the year")
    accumulated_impairment_disposal = fields.Monetary(
        string="Accumulated impairment on disposal for the year")
    accumulated_impairment_transfer = fields.Monetary(
        string="Accumulated impairment on transfer for the year")

    # Maintenance

    expense_cost = fields.Monetary(string="Expense Cost")
    capitalise_costs = fields.Monetary(string="Capitalise Cost")

    # Disposal

    direct_attachement_ids = fields.Many2many('ir.attachment', string="Files")
    current_value_asset = fields.Monetary(string="Current value asset")
    loss_asset = fields.Boolean(string="Asset Loss")
    money_received_sale_asset = fields.Monetary(
        string="Money received from sale of asset")

    # for report
    disposal_type = fields.Selection(
        [('cash', 'Cash'), ('non_cash', 'Non-cash')],
        string='Type',
        help='Type of addition')
    cash_type = fields.Selection([('direct_disposal', 'Direct Disposal')])
    non_cash_type = fields.Selection([('scrapping', 'Scrapping of asset'),
                                      ('newly_found_asset',
                                       'NEWLY FOUND ASSET FROM THE VERIFICATION'),
                                      ('other_modules', 'From other modules')])
    direct_disposal_amount = fields.Monetary(string='Proceeds')
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
    state = fields.Selection(
        selection_add=[('impaired', 'Impaired'), ('close',)], ondelete={
            'impaired': 'set default',
        }, )
    reason_impairment = fields.Char(string='Reason impairment',
                                    help='Reason for impairment', copy=False)

    # Transfer
    is_transferred = fields.Boolean(string="Transferred")
    date = fields.Date(string="Date Requested",
                       help="Date requested for the transfer")
    asset_barcode = fields.Char(string="Barcode", help="Barcode")
    department_id = fields.Many2one('asset.transfer.department', string="Department", help="Department")
    transfer_description = fields.Char(string="Asset Description",
                                       help="Asset Description")
    classification = fields.Char(string='Classification of asset',
                                 help="Classification of asset")
    transfer_condition = fields.Char(string="Condition of asset",
                                     help="Condition of asset")
    reason = fields.Char(string="Reason for transfer",
                         help="Reason for transfer")
    name_surname = fields.Char(string="Name & Surname", help="Name & Surname")
    sign_signature = fields.Binary(string="Digital Signature")
    current_location = fields.Char(string="Current Location",
                                   help="Current Location")
    new_location = fields.Char(string="New Location", help="New Location")
    current_department = fields.Char(string="Current Department",
                                     help="Current Department")
    new_department = fields.Char(string="New Department", help="New Department")
    current_unit = fields.Char(string="Current Unit", help="Current Unit")
    new_unit = fields.Char(string="New Unit", help="New Unit")
    transferring_official = fields.Char(string="Transferring official",
                                        help="Transferring official")
    receiving_official = fields.Char(string="Receiving official",
                                     help="Receiving official")
    transferring_official_signature = fields.Char(
        string="Transferring official signature",
        help="Transferring official signature")
    gm_name_surname = fields.Char(string="GM Name & Surname",
                                  help="GM Name & Surname")
    new_gm_name_surname = fields.Char(string="GM Name & Surname",
                                      help="GM Name & Surname")
    gm_signature = fields.Char(string="GM Signature", help="GM Signature")
    new_gm_signature = fields.Char(string="GM Signature", help="GM Signature")
    date_transferred = fields.Date(string="Date transferred",
                                   help="Date transferred")
    date_received = fields.Date(string="Date received", help="Date received")

    # Acquisition report
    asset_parent_id = fields.Many2one('account.asset',
                                      help="An asset has a parent",
                                      domain="[('state', 'not in', ['model', 'cancelled', 'closed'])]")

    # Asset Transfer
    transfer_department_id = fields.Many2one('asset.transfer.department',
                                             string="Transfer From Department",
                                             help="Asset Transfer From Department")
    transfer_division_id = fields.Many2one('asset.transfer.division',
                                           string="Transfer From Division",
                                           help="Asset Transfer From Division")
    transfer_ownership_id = fields.Many2one('asset.transfer.ownership',
                                            string="Transfer From Asset "
                                                   "Ownership")
    transfer_from_custodian_name = fields.Char(string="Transfer From Custodian "
                                                      "Name")
    transfer_from_custodian_id_number = fields.Char(string="Transfer From "
                                                           "Custodian ID Number")
    transfer_new_department_id = fields.Many2one('asset.transfer.department',
                                                 string="Transfer To New "
                                                        "Department")
    transfer_new_division_id = fields.Many2one('asset.transfer.division',
                                               string="Transfer To New "
                                                      "Division")
    transfer_new_ownership_id = fields.Many2one('asset.transfer.ownership',
                                                string="Transfer To New Asset "
                                                       "Ownership")
    transfer_to_new_custodian_name = fields.Char(string="Transfer To New "
                                                        "Custodian Name")
    transfer_to_new_custodian_id_number = fields.Char(string="Transfer To New "
                                                        "Custodian ID Number")
    building = fields.Char(string="Building")
    room_number = fields.Char(string="Room Number")

    # asset Useful life
    replacement_value = fields.Monetary(string="Replacement Value")
    market_value = fields.Monetary(string="Market Value")
    ready_for_use = fields.Char(string="Ready For Use")
    sub_category_description = fields.Char(string="Asset Sub Category "
                                                  "Description")
    method_disposal = fields.Char(string="Method Disposal")

    #Asset depreciation
    asset_sub_category_id = fields.Many2one('asset.category', string="Asset Sub Category")
    useful_life_month = fields.Char(string="Useful Life Month")
    useful_life_day = fields.Char(string="Useful Life Day")
    remaining_useful_life_month = fields.Char(string="Remaining Useful Life Month")
    remaining_useful_life_day = fields.Char(string="Remaining Useful Life Days")
    days_from_last_run = fields.Float(string="Days From Last Run")

    # Asset Insurance

    insured_value = fields.Monetary(string="Insured Value")
    policy_number = fields.Char(string="Policy Number")
    premium_monthly = fields.Monetary(string="Premium Monthly")
    premium_annually = fields.Monetary(string="Premium Annually")
    insured_period = fields.Selection([('Monthly', 'Monthly'),
                                       ('Annually', 'Annually')],
                                      string="Insurance Period")
    claim_date = fields.Date(string="Claim Date")

    #Disposal report
    division_id = fields.Many2one('asset.transfer.division',
                                  string="Asset division")
    ownership_id = fields.Many2one('asset.transfer.ownership',
                                  string="Asset ownership")

    def create_equipment(self):
        """Create a equipment from asset"""
        equipment = self.env['maintenance.equipment'].create({
            "name": self.name,
        })
        self.equipment_id = equipment.id

    # def action_asset_lose(self):
    #     """Open asset lose"""
    #     # if self.state == 'impaired':
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'asset.lose',
    #         'target': 'new',
    #         'context': {
    #             'default_asset_id': self.id,
    #             'default_direct_disposal_amount': self.fair_value_less_cost_to_sell
    #         },
    #     }
    #     # else:
    #     #     raise ValidationError(_('Only Impaired asset can done the disposal process'))

    def create_maintenance_request(self):
        maintenance = self.env['maintenance.request'].create({
            "name": 'Maintenance ' + self.name + ' ' + str(fields.Date.today()),
            'equipment_id': self.equipment_id.id
        })

    def action_asset_addition(self):
        """Asset addition"""
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'asset.addition',
            'target': 'new',
            'context': {
                'default_asset_id': self.id
            },
        }

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

    def action_asset_transfer(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'asset.transfer',
            'target': 'new',
            'context': {
                'default_asset_ids': [(6, 0, [self.id])],
                'default_asset_barcode': self.asset_barcode,
                'default_department': self.department,
                'default_transfer_description': self.transfer_description,
                'default_asset_category_id': self.asset_category_id.id,
                'default_transfer_condition': self.transfer_condition,
                'default_reason': self.reason,
                'default_name_surname': self.name_surname,
                'default_sign_signature': self.sign_signature,
                'default_current_location': self.current_location,
                'default_new_location': self.new_location,
                'default_current_department': self.current_department,
                'default_new_department': self.new_department,
                'default_current_unit': self.current_unit,
                'default_new_unit': self.new_unit,
                'default_transferring_official': self.transferring_official,
                'default_receiving_official': self.receiving_official,
                'default_transferring_official_signature': self.transferring_official_signature,
                'default_gm_name_surname': self.gm_name_surname,
                'default_new_gm_name_surname': self.new_gm_name_surname,
                'default_gm_signature': self.gm_signature,
                'default_new_gm_signature': self.new_gm_signature,
                'default_date_transferred': self.date_transferred,
                'default_date_received': self.date_received
            },
        }

    def set_to_draft(self):
        """rewrite this methode for remove the details of asset disposal"""
        self.write({'state': 'draft',
                    'loss_asset': False,
                    'current_value_asset': 0.0,
                    'direct_attachement_ids': [(5)]})

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

    def action_account_asset_depreciation(self):
        """Method for asset Depreciation"""
        assets = self.env['account.asset'].browse(
            self.env.context.get('active_ids'))
        for asset in assets:
            if asset.state != 'draft':
                raise ValidationError(
                    _("Please select a asset in draft state"))
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'asset.depreciation',
            'target': 'new',
            'context': {
                'default_asset_ids': [(6, 0, assets.ids)]
            },
        }

    # def action_account_asset_disposal(self):
    #     """Method for asset Disposal"""
    #     assets = self.env['account.asset'].browse(
    #         self.env.context.get('active_ids'))
    #     # for asset in assets:
    #     #     if asset.state != 'impaired':
    #     #         raise ValidationError(
    #     #             _("Please select a asset in impaired state"))
    #     amount = 0.0
    #     if len(assets) == 1:
    #         amount = assets.fair_value_less_cost_to_sell
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'asset.lose',
    #         'target': 'new',
    #         'context': {
    #             'default_asset_ids': [(6, 0, assets.ids)],
    #             'default_direct_disposal_amount': amount
    #         },
    #     }

    def action_account_asset_addition(self):
        """Method for asset Addition"""
        assets = self.env['account.asset'].browse(
            self.env.context.get('active_ids'))
        for asset in assets:
            if asset.state != 'draft':
                raise ValidationError(
                    _("Please select a asset in draft state"))
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'asset.addition',
            'target': 'new',
            'context': {
                'default_asset_ids': [(6, 0, assets.ids)]
            },
        }

    def action_account_asset_transfer(self):
        """Method for asset Addition"""
        assets = self.env['account.asset'].browse(
            self.env.context.get('active_ids'))
        for asset in assets:
            if asset.state != 'draft':
                raise ValidationError(
                    _("Please select a asset in draft state"))
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'asset.transfer',
            'target': 'new',
            'context': {
                'default_asset_ids': [(6, 0, assets.ids)]
            },
        }

    # Asset search by id and barcode
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search(
                [('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search(
                    [('identification_number', operator, name)] + (args or []),
                    limit=limit)
            if not recs:
                recs = self.search(
                    [('asset_barcode', operator, name)] + (args or []),
                    limit=limit)
            return recs.name_get()
        return super(AccountAsset, self).name_search(
            name, args=args, operator=operator, limit=limit)
