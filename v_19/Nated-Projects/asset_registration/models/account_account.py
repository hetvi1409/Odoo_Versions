import re

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

ACCOUNT_CODE_REGEX = re.compile(r'^[A-Za-z0-9./-]+$')


class AccountAccount(models.Model):
    _inherit = 'account.account'

    project = fields.Char(string='Project Name', help='Project')
    project_scoa_account = fields.Char(string='ProjectScoaAccount',
                                       help='ProjectScoaAccount')
    item = fields.Char(string='Item', help='Item')
    item_scoa_account = fields.Char(string='ItemScoaAccount',
                                    help='ItemScoaAccount')
    fund = fields.Char(string='Fund', help='Fund')
    fund_scoa_account = fields.Char(string='FundScoaAccount',
                                    help='FundScoaAccount')
    function = fields.Char(string='Function', help='Function')
    function_scoa_account = fields.Char(string='FunctionScoaAccount',
                                        help='FunctionScoaAccount')
    region = fields.Char(string='Region', help='Region')
    region_scoa_account = fields.Char(string='RegionScoaAccount',
                                      help='RegionScoaAccount')
    cost = fields.Char(string='Cost', help='Cost')
    cost_scoa_account = fields.Char(string='CostScoaAccount',
                                    help='CostScoaAccount')
    msc = fields.Char(string='MSC', help='MSC')

    project_type = fields.Selection([('Capital', 'Capital'),
                                     ('Operational', 'Operational'),
                                     ('Default', 'Default')], string="Project",
                                    help='Project')
    capital_type = fields.Selection([('Infrastructure', 'Infrastructure'),
                                     ('Non Infrastructure',
                                      'Non Infrastructure')], string="Capital",
                                    help='Capital')
    infrastructure_type = fields.Selection(
        [('Existing', 'Existing'), ('New', 'New')],
        string="Infrastructure Type", help='Infrastructure Type')
    non_infrastructure_type = fields.Selection(
        [('Existing', 'Existing'), ('New', 'New')],
        string="Non Infrastructure Type", help='Non Infrastructure Type')

    capital_id = fields.Many2one('project.capital.segment', string="Capital",
                                 help='Capital',
                                 domain="[('id', 'in', capital_ids)]")
    capital_ids = fields.Many2many('project.capital.segment', string="Capital",
                                   help='Capital', )

    def get_segment_id(self):
        segment = self.capital_id.segment_ids
        if segment:
            return [('id', 'in', segment.ids)]

    capital_type_id = fields.Many2one('project.capital.segment.line',
                                      string='Capital Type',
                                      help='Capital Type',
                                      domain=get_segment_id)

    item_type = fields.Selection(
        [('Revenue', 'Revenue'), ('Expenditure', 'Expenditure'),
         ('Gains & Losses', 'Gains & Losses'), ('Asset', 'Asset'),
         ('Liability', 'Liability'), ('Net Asset', 'Net Asset')],
        string='Item type')
    asset_type_ = fields.Selection([('Current Asset', 'Current Asset'),
                                    ('Non Current Asset', 'Non Current Asset')],
                                   string='Asset Type')
    non_current_asset_type = fields.Selection(
        [('Construction Work-in-progress', 'Construction Work-in-progress'),
         ('Property, Plant and Equipment', 'Property, Plant and Equipment')])
    work_progress_type = fields.Selection([('Acquisitions', 'Acquisitions'), (
        'Opening Balance', 'Opening Balance')])
    acquisitions_type = fields.Char()
    equipment_type = fields.Selection([('Cost Model', 'Cost Model')])
    cost_model_type = fields.Selection([('Land', 'Land'),
                                        ('Computer Equipment',
                                         'Computer Equipment'),
                                        ('Furniture and Office Equipment',
                                         'Furniture and Office Equipment'),
                                        ('Machinery and Equipment',
                                         'Machinery and Equipment'),
                                        (
                                            'Transport Assets',
                                            'Transport Assets'),
                                        ('Water Supply Infrastructure',
                                         'Water Supply Infrastructure'),
                                        ('Other Assets', 'Other Assets'), (
                                            'Sanitation Infrastructure',
                                            'Sanitation Infrastructure')])
    use_type = fields.Selection(
        [('Owned and In-use', 'Owned and In-use'), ('In-use', 'In-use'),
         ('Future Use', 'Future Use'),
         ('Boreholes', 'Boreholes'), ('Distribution', 'Distribution'), ])
    cost_type = fields.Selection([('Cost', 'Cost'), (
        'Accumulated Depreciation', 'Accumulated Depreciation'), ])
    cost_type_1 = fields.Selection(
        [('Acquisitions', 'Acquisitions'), ('Depreciation', 'Depreciation'),
         ('Disposals', 'Disposals'), ])

    fund_type = fields.Selection(
        [('Operational', 'Operational'), ('Capital', 'Capital'),
         ('Default', 'Default')])
    fund_operational_type = fields.Selection([(
        'Transfer from Operational Revenue',
        'Transfer from Operational Revenue'),
        ('Transfers and Subsidies',
         'Transfers and Subsidies'),
        ('Borrowing', 'Borrowing'), (
            'Cash Backed Reserves',
            'Cash Backed Reserves'),
        ('Non-funding Transactions', 'Non-funding Transactions')])
    fund_subsidies_type = fields.Selection(
        [('Monetary Allocations', 'Monetary Allocations'),
         ('Allocations In-kind', 'Allocations In-kind')])

    fund_monetary_type = fields.Selection(
        [('National Government', 'National Government'),
         ('Provincial Government', 'Provincial Government')])
    fund_allocation_type = fields.Selection(
        [('Private Enterprises', 'Private Enterprises')])
    fund_subname = fields.Char()
    fund_subname_ = fields.Char()

    function_type = fields.Selection([('Water Management', 'Water Management'),
                                      ('Community and Social Services', 'Community and Social Services'),
                                      ('Finance and Administration', 'Finance and Administration'),
                                      ('Planning and Development', 'Planning and Development'),
                                      ('Public Safety', 'Public Safety'),
                                      ('Finance and Administration', 'Finance and Administration')])
    function_core_type = fields.Selection([('Core Function', 'Core Function'), 
                                           ('Non-core Function', 'Non-core Function')])

    @api.onchange('fund_type', 'fund_operational_type', 'fund_subsidies_type',
                  'fund_monetary_type', 'fund_allocation_type', 'fund_subname_')
    def onchange_fund_type(self):
        name = ''
        if self.fund_type:
            name = 'Fund:' + self.fund_type
        if self.fund_operational_type:
            name = name + ':' + self.fund_operational_type
        if self.fund_operational_type == 'Transfers and Subsidies' and self.fund_subsidies_type:
            name = name + ':' + self.fund_subsidies_type
        if self.fund_operational_type == 'Transfers and Subsidies' and self.fund_subsidies_type == 'Monetary Allocations' and self.fund_monetary_type:
            name = name + ':' + self.fund_monetary_type
        if self.fund_operational_type == 'Transfers and Subsidies' and self.fund_subname:
            name = name + ':' + self.fund_subname
        self.fund = name

    @api.onchange('item_type', 'asset_type_', 'non_current_asset_type',
                  'equipment_type', 'cost_model_type'
                                    'work_progress_type', 'acquisitions_type')
    def onchange_item_type(self):
        name = ''
        if self.item_type != 'Asset':
            self.asset_type_ = ''
            self.non_current_asset_type = ''
            self.work_progress_type = ''
            self.acquisitions_type = ''
            self.equipment_type = ''
            self.cost_model_type = ''
            self.use_type = ''
            self.cost_type = ''
        if self.item_type:
            name = self.item_type
        if self.asset_type_:
            name = name + ':' + self.asset_type_
            # self.non_current_asset_type = ''
        if self.non_current_asset_type == 'Construction Work-in-progress':
            # self.work_progress_type = ''
            # self.equipment_type = ''
            name = name + ':' + self.non_current_asset_type
            if self.work_progress_type:
                name = name + ':' + self.work_progress_type
            if self.acquisitions_type:
                name = name + ':' + self.acquisitions_type
        elif self.non_current_asset_type == 'Property, Plant and Equipment':
            name = name + ':' + self.non_current_asset_type
            if self.equipment_type:
                name = name + ':' + self.equipment_type
            if self.cost_model_type:
                name = name + ':' + self.cost_model_type
            if self.use_type:
                name = name + ':' + self.use_type
            if self.cost_type:
                name = name + ':' + self.cost_type
            if self.cost_type_1:
                name = name + ':' + self.cost_type_1
        self.item = name

    @api.onchange('project_type', 'capital_type', 'infrastructure_type',
                  'non_infrastructure_type', 'capital_id', 'capital_type_id')
    def onchange_capital_type(self):
        name = ''
        segment = []
        if self.project_type == 'Capital':
            name = self.project_type
        if not self.project_type:
            self.capital_type = ''
            self.infrastructure_type = ''
            self.non_infrastructure_type = ''
            self.capital_id = ''
            self.capital_ids = []
            self.capital_type_id = ''
        if self.capital_type:
            name = name + ':' + self.capital_type
        if self.capital_type == 'Infrastructure' and self.infrastructure_type:
            name = name + ':' + self.infrastructure_type
            segment = self.env['project.capital.segment'].search(
                [('capital_type', '=', self.capital_type),
                 ('infrastructure_type', '=', self.infrastructure_type)])
        if self.capital_type == 'Non Infrastructure' and self.non_infrastructure_type:
            name = name + ':' + self.non_infrastructure_type
            segment = self.env['project.capital.segment'].search(
                [('capital_type', '=', self.capital_type),
                 (
                     'non_infrastructure_type', '=',
                     self.non_infrastructure_type)])
        if self.capital_id:
            name = name + ':' + self.capital_id.name
        if self.capital_type_id:
            name = name + ':' + self.capital_type_id.name
        self.project = name
        if segment:
            self.capital_ids = [(6, 0, segment.ids)]
        else:
            self.capital_ids = []

    @api.depends('project_type', 'capital_type', 'infrastructure_type',
                 'non_infrastructure_type', 'capital_id', 'capital_type_id')
    def _compute_capital_ids(self):
        segment = self.env['project.capital.segment'].search([])
        capital_ids = ([4, segment.ids])

    @api.constrains('code')
    def _check_account_code(self):
        for account in self:
            if not re.match(ACCOUNT_CODE_REGEX, account.code):
                raise ValidationError(_(
                    "The account code can only contain alphanumeric characters and dots."
                ))
