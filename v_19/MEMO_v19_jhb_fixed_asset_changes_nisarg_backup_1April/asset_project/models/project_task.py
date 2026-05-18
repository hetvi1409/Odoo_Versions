from odoo import api, fields, models, _
# from odoo.tools.populate import compute


class ProjectTask(models.Model):
    _inherit = 'project.task'
    """Adding fields in project Task"""

    location = fields.Char(string="Location")

    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, readonly=True,
                                  default=lambda
                                      self: self.env.company.currency_id.id)
    payments = fields.Monetary(string='Payments(O/B) of the year')
    addition = fields.Monetary(string='Additions of the year')
    retention_paid = fields.Monetary(string='Retention paid of the year')
    accumulated_payment =  fields.Monetary(string='Accumulated Payment', help='Accumulated Payment (PAYMENTS/OB + ADDITIONS + RETENTION PD+adjustments')
    retention = fields.Monetary(string='Retention (O/B) of the year')
    retention_held  = fields.Monetary(string='Retention Held (Current) of the year')
    retention_reserved = fields.Monetary(string='Retention reversed (in current year) of the year')
    total_retention_held  = fields.Monetary(string="Total Retention Held of the year(OB+   CURRENT-PAID)")
    retention_added = fields.Monetary(string="Retention Added", help="Retention added to value of works but not due to Contractor - Termination & other")
    completed_project = fields.Monetary(string="Completed Projects (Partial & Full)")
    value_work  = fields.Monetary(string="Value of work", help="Value of work (total ret + Acc payment")
    # as_per_tb = fields.Monetary(string='As per T.B.- OB IA02438')
    # IA01952 = fields.Monetary(string="IA01952")
    # rts = fields.Monetary(string="RTS FOR MAY DONE IN JUNE")
    # total = fields.Monetary(string="Total")
    is_completed = fields.Boolean()
    is_paid = fields.Boolean()
    wip_financial_year = fields.Integer('Financial Year')
    wip_fiscal_period = fields.Integer('Fiscal Period')
    project_status = fields.Char('Project Status')
    funding_description = fields.Char('Funding Description')
    classification_level0 = fields.Char('Classification Level0')
    classification_level1 = fields.Char('Classification Level1')
    classification_level2 = fields.Char('Classification Level2')
    classification_level3 = fields.Char('Classification Level3')
    classification_level4 = fields.Char('Classification Level4')
    classification_level5 = fields.Char('Classification Level5')
    classification_level6 = fields.Char('Classification Level6')
    classification_level7 = fields.Char('Classification Level7')
    opening_balance= fields.Float('Opening Balance')
    adjusted_opening_balance= fields.Float(' Ajusted Opening Balance')
    opening_balance_adjustment= fields.Float('Opening Balance Adjustment')
    expenditure= fields.Float('Expenditure')
    net_carry_value= fields.Float('Net Carry Value')
    asset_id = fields.Many2one('account.asset')
    attachment_ids = fields.Many2many("ir.attachment",'project_task_attachment_rel')

    approved_plans_ids = fields.Many2many('ir.attachment', relation='approved_plans_attachement_rel', string='Approved Plans')
    award_letter_ids = fields.Many2many('ir.attachment', relation='award_letter_attachement_rel', string='Award Letter')
    contract_ids = fields.Many2many('ir.attachment', relation='contract_attachement_rel', string='Contract/Bid Documents')
    invoice_attachement_ids = fields.Many2many('ir.attachment', relation='invoice_attachement_rel', string='Invoices/Project Expenditure vouchers')
    # site_meeting_attachement_ids = fields.Many2many('ir.attachment', relation='site_meeting_attachement_rel', string='Site Meeting Minutes')
    completion_certificate_attachement_ids = fields.Many2many('ir.attachment', relation='completion_certificate_attachement_rel', string='Completion Certificates')
    project_attachement_ids = fields.Many2many('ir.attachment', relation='project_attachement_rel', string='Project close out report')
    asbuilt_attachement_ids = fields.Many2many('ir.attachment', relation='asbuilt_attachement_rel', string='Asbuilt drawings')
    other_project_attachement_ids = fields.Many2many('ir.attachment', relation='other_project_attachement_rel', string='Other Project Related Documents')

    invoice_id = fields.Many2one('account.move', domain="[('move_type', '=', 'out_invoice')]")

    project_number = fields.Char(string='Project Number', required=True,
                                  copy=False, readonly=True,
                                  default=lambda self: _('New'))
    project_category = fields.Selection([('WATER', 'WATER'),
                                         ('SEWERAGE', 'SEWERAGE'),
                                         ('Building', 'Building')])
    contract_id = fields.Many2one('res.partner')
    consultant_id = fields.Many2one('res.partner')
    contract_value = fields.Float(string='Contract Value')
    contingencies_vat = fields.Char(string='Contingencies')
    vat = fields.Char(string='Vat')
    date_completion = fields.Date(string='Date Completion')

    wip_project_ids = fields.One2many('wip.project', 'task_id')
    wip_project_total = fields.Monetary(string='Wip Amount', compute="_compute_wip_project_total")
    unbundling_ids = fields.One2many('unbundling.project', 'task_id')
    unbundling_direct_total = fields.Monetary(compute='_compute_unbundling_amounts')
    unbundling_indirect_total = fields.Monetary(compute='_compute_unbundling_amounts')
    unbundling_total_weighted_average = fields.Monetary(string='Total Weighted Average', compute='_compute_unbundling_amounts')
    unbundling_total_allocate_indirect  = fields.Monetary(string='Total Allocate Indirect ', compute='_compute_unbundling_amounts')
    unbundling_total_cost  = fields.Monetary(string='Total Cost of the unbundled assets TO BE CAPTALISED', compute='_compute_unbundling_amounts')
    boq_ids = fields.One2many('wip.input.boq', 'task_id')
    boq_amount = fields.Monetary(compute='_compute_boq_amount')
    final_ids = fields.One2many('wip.final', 'task_id')
    final_total = fields.Monetary(string='Final Total', compute='_compute_final_total')
    final_asset_ids = fields.One2many('project.asset', 'task_id')

    wip_construction_ids = fields.One2many('wip.project.construction', 'task_id')
    wip_const_total_amount = fields.Monetary(string="Total Amount", compute='_compute_wip_construction_amounts')
    wip_const_total_vat = fields.Monetary(string="Total Vat", compute='_compute_wip_construction_amounts')
    wip_const_total_vat_include = fields.Monetary(string="Total Vat Include", compute='_compute_wip_construction_amounts')
    wip_const_total_retention = fields.Monetary(string="Total Retention", compute='_compute_wip_construction_amounts')
    wip_const_total_surety = fields.Monetary(string="Total Surety", compute='_compute_wip_construction_amounts')
    wip_const_total_guarantee = fields.Monetary(string="Total Guarantee", compute='_compute_wip_construction_amounts')
    wip_const_total_cap_amount = fields.Monetary(string="Total Cap Total", compute='_compute_wip_construction_amounts')
    wip_professional_ids = fields.One2many('wip.project.professional', 'task_id')
    wip_pro_total_amount = fields.Monetary(string="Total Amount", compute='_compute_wip_professional_amounts')
    wip_pro_total_vat = fields.Monetary(string="Total Vat", compute='_compute_wip_professional_amounts')
    wip_pro_total_vat_include = fields.Monetary(string="Total Vat Include", compute='_compute_wip_professional_amounts')
    wip_pro_total_retention = fields.Monetary(string="Total Retention", compute='_compute_wip_professional_amounts')
    wip_pro_total_surety = fields.Monetary(string="Total Surety", compute='_compute_wip_professional_amounts')
    wip_pro_total_guarantee = fields.Monetary(string="Total Guarantee", compute='_compute_wip_professional_amounts')
    wip_pro_total_cap_amount = fields.Monetary(string="Total Cap Total", compute='_compute_wip_professional_amounts')

    project_planning_ids = fields.One2many('task.project.planning', 'task_id')
    project_implementation_ids = fields.One2many('task.project.implementation', 'task_id')
    project_monitoring_ids = fields.One2many('task.project.monitoring', 'task_id')
    project_commissioning_ids = fields.One2many('task.project.commissioning', 'task_id')

    @api.depends('unbundling_ids')
    def _compute_unbundling_amounts(self):
        """Calculate unbundling amount"""
        for rec in self:
            unbundling_direct_total = 0.0
            unbundling_indirect_total = 0.0
            for unbundling in rec.unbundling_ids:
                if unbundling.type == 'Direct':
                    unbundling_direct_total = unbundling_direct_total + unbundling.amount
                if unbundling.type == 'Indirect':
                    unbundling_indirect_total = unbundling_indirect_total + unbundling.amount
            rec.unbundling_direct_total = unbundling_direct_total
            rec.unbundling_indirect_total = unbundling_indirect_total
            rec.unbundling_total_weighted_average = sum(rec.unbundling_ids.mapped('weighted_average'))
            rec.unbundling_total_allocate_indirect = sum(rec.unbundling_ids.mapped('allocate_indirect'))
            rec.unbundling_total_cost = sum(rec.unbundling_ids.mapped('total'))

    @api.depends('wip_project_ids')
    def _compute_wip_project_total(self):
        """Compute the wip amount"""
        for rec in self:
            wip_project_total = 0.0
            for wip in rec.wip_project_ids:
                wip_project_total = wip_project_total + wip.total
            rec.wip_project_total = wip_project_total

    @api.depends('boq_ids')
    def _compute_boq_amount(self):
        """Compute the boq amount"""
        for rec in self:
            rec.boq_amount = sum(rec.boq_ids.mapped('amount'))

    @api.depends('final_ids')
    def _compute_final_total(self):
        """Compute the final total"""
        for rec in self:
            rec.final_total = sum(rec.final_ids.mapped('amount'))

    @api.depends('wip_construction_ids')
    def _compute_wip_construction_amounts(self):
        """Calculating wip construction amount"""
        for rec in self:
            rec.wip_const_total_amount = sum(rec.wip_construction_ids.mapped('amount'))
            rec.wip_const_total_vat = sum(rec.wip_construction_ids.mapped('vat'))
            rec.wip_const_total_vat_include = sum(rec.wip_construction_ids.mapped('vat_include'))
            rec.wip_const_total_retention = sum(rec.wip_construction_ids.mapped('retention'))
            rec.wip_const_total_surety = sum(rec.wip_construction_ids.mapped('surety'))
            rec.wip_const_total_guarantee = sum(rec.wip_construction_ids.mapped('guarantee'))
            rec.wip_const_total_cap_amount = sum(rec.wip_construction_ids.mapped('cap_amount'))

    @api.depends('wip_professional_ids')
    def _compute_wip_professional_amounts(self):
        """Calculating wip professional amount"""
        for rec in self:
            rec.wip_pro_total_amount = sum(rec.wip_professional_ids.mapped('amount'))
            rec.wip_pro_total_vat = sum(rec.wip_professional_ids.mapped('vat'))
            rec.wip_pro_total_vat_include = sum(rec.wip_professional_ids.mapped('vat_include'))
            rec.wip_pro_total_retention = sum(rec.wip_professional_ids.mapped('retention'))
            rec.wip_pro_total_surety = sum(rec.wip_professional_ids.mapped('surety'))
            rec.wip_pro_total_guarantee = sum(rec.wip_professional_ids.mapped('guarantee'))
            rec.wip_pro_total_cap_amount = sum(rec.wip_professional_ids.mapped('cap_amount'))

    @api.model
    def create(self, values):
        """Method for generating consumer number for the contacts"""
        # Check if values is a list (batch creation)
        if isinstance(values, list):
            for val in values:
                if val.get('project_number', _('New')) == _('New'):
                    val['project_number'] = self.env['ir.sequence'].next_by_code(
                        'wip.project.name') or _('New')
        else:
            if values.get('project_number', _('New')) == _('New'):
                values['project_number'] = self.env['ir.sequence'].next_by_code(
                    'wip.project.name') or _('New')

        res = super(ProjectTask, self).create(values)
        return res

    @api.onchange('payments', 'addition')
    def onchange_payments_addition(self):
        """Add value to accumulated_payment"""
        for rec in self:
            if rec.payments and rec.addition:
                rec.accumulated_payment = rec.payments + rec.addition
            elif rec.payments:
                rec.accumulated_payment = rec.payments
            else:
                rec.accumulated_payment = 0.00

    @api.onchange('retention', 'retention_held')
    def onchange_retention_retention_held(self):
        """adding value to total_retention_held"""
        for rec in self:
            if rec.retention and rec.retention_held:
                rec.total_retention_held = rec.retention + rec.retention_held
            elif rec.retention:
                rec.total_retention_held = rec.retention
            else:
                rec.total_retention_held = 0.00

    @api.onchange('accumulated_payment', 'retention_held', 'completed_project')
    def onchange_accumulated_payment_retention_held_completed_project(self):
        """Adding Values into value_work"""
        for rec in self:
            amount = 0.0
            if rec.accumulated_payment:
                amount = amount + rec.accumulated_payment
            if rec.retention_held:
                amount = amount + rec.retention_held
            if rec.completed_project:
                amount = amount + rec.completed_project
            rec.value_work = amount

    # @api.onchange('as_per_tb', 'IA01952')
    # def onchange_as_per_tb_IA01952(self):
    #     """Adding Values into total"""
    #     for rec in self:
    #         amount = 0.0
    #         if rec.as_per_tb:
    #             amount = amount + rec.as_per_tb
    #         if rec.IA01952:
    #             amount = amount + rec.IA01952
    #         rec.total = amount

    @api.onchange('stage_id')
    def onchange_stage_ids(self):
        if self.stage_id ==  self.env.ref('asset_project.project_task_type_wip_done'):
            self.is_completed = True
            self.is_paid = False
        else:
            self.is_completed = False

    def create_asset_project(self):
        """Create a new asset"""
        asset_model = self.env['account.asset'].sudo().search(
            [('state', '=', 'model'), ('name', '=', self.name)], limit=1)
        if not asset_model:
            asset_model = self.env['account.asset'].create({
                'name': self.name,
                'state': 'model',
                'account_depreciation_id': 2,
                'account_depreciation_expense_id': 26,
                'method': 'linear',
                'asset_type': 'purchase',
                'method_period': '1',
            })

        asset = self.env['account.asset'].create({
            'name': self.name,
            'model_id': asset_model.id,
            'account_depreciation_id': 2,
            'account_depreciation_expense_id': 26,
            'method': 'linear',
            'asset_type': 'purchase',
            'method_period': '1',
        })
        self.stage_id = self.env.ref('asset_project.project_task_type_asset').id
        self.is_completed = False
        self.asset_id = asset.id

    def get_asset_details(self):
        """Returns Asset Details"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Asset',
            'view_mode': 'form',
            'res_model': 'account.asset',
            'res_id': self.asset_id.id
        }

    def get_invoice_details(self):
        """Returns Asset Details"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id
        }

class TaskProjectPlanning(models.Model):
    _name = 'task.project.planning'
    _description = "Task Project Planning"
    """Task Project Planning"""


    name = fields.Char(string='Project Planning', required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date")
    description = fields.Char(string='Description')
    task_id = fields.Many2one('project.task')


class TaskProjectImplementation(models.Model):
    _name = 'task.project.implementation'
    _description = 'Task Project Implementation'
    """Task Project Implementation"""


    name = fields.Char(string='Project Implementation', required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date")
    description = fields.Char(string='Description')
    task_id = fields.Many2one('project.task')

class TaskProjectMonitoring(models.Model):
    _name = 'task.project.monitoring'
    _description = 'Task Project Monitoring'
    """Task Project Monitoring"""

    name = fields.Char(string='Project Monitoring', required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date")
    description = fields.Char(string='Description')
    task_id = fields.Many2one('project.task')

class TaskProjectCommissioning(models.Model):
    _name = 'task.project.commissioning'
    _description = 'Task Project Commissioning'
    """Task Project Commissioning"""

    name = fields.Char(string='Project Commissioning', required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date")
    description = fields.Char(string='Description')
    task_id = fields.Many2one('project.task')

