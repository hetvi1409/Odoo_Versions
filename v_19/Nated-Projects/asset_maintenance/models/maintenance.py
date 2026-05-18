from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Maintenance(models.Model):
    _inherit = 'maintenance.request'

    asset_id = fields.Many2one('account.asset', domain="[('state', '!=', 'model')]")
    is_lock = fields.Boolean(string='Lock and tag out equipment')
    lock_status = fields.Char(string='Lock status')
    check_mounting = fields.Boolean(string='Check mounting',
                                    help='Check all mounting and flange bolts '
                                         'to insure proper torque')
    check_mounting_status = fields.Char(string='Check mounting status')
    soundness = fields.Boolean(string='Soundness',
                               help='Equipment base for soundness')
    soundness_status = fields.Char(string='Soundness status')
    soundness_document_ids = fields.Many2many("ir.attachment")
    mechanical_leak = fields.Boolean(string='Mechanical seal leak',
                                     help="Check the mechanical seal leaks")
    mechanical_leak_status = fields.Char(string='Mechanical leak status', )
    oil_seals = fields.Boolean(string='Oil seal',
                               help='Check the condition of oil and gas seals')
    oil_seals_status = fields.Char(string='Oil seal status')
    excessive_leakage = fields.Boolean(string='Excessive leakage',
                                       help='Check packing for excessive leakage and adjust and/or replace')
    excessive_leakage_status = fields.Char(string='Excessive leakage status')
    guages_operational = fields.Boolean(string='Guages Operational',
                                        help="Make sure all guages are operational")
    guages_operational_status = fields.Char(string='Guages Operational status')
    coupling_guard = fields.Boolean(string='Coupling Guard',
                                    help="Remove coupling guard, check the alignment and correct as required ")
    coupling_guard_status = fields.Char(string='Coupling Guard Status')
    lubricate_assembly = fields.Boolean(string='Lubricate Assembly',
                                        help="Lubricate Coupling assembly as required")
    lubricate_assembly_status = fields.Char(string='Lubricate Assembly Status')
    lubricant_pump = fields.Boolean(string='Lubricant Pump',
                                    help="Lubricant pump and motor")
    lubricant_pump_status = fields.Char(string='Lubricant Pump Status')
    oil_equipment = fields.Boolean(string='Oil Equipment',
                                   help="Change oil on equipment as recommended by OEM")
    oil_equipment_status = fields.Char(string='Oil Equipment Status')
    auxiliary_functionality = fields.Boolean(string='Auxiliary Functionality',
                                             help="Ensure all auxiliary equipment is functioning properly")
    auxiliary_functionality_status = fields.Char(
        string='Auxiliary Functionality Status')

    field_report = fields.Text(string='Field Report')

    municipality = fields.Char(string='Municipality')
    operation_area = fields.Char(string='Operation Area')
    pump_station = fields.Char(string='Pump Station')
    coords = fields.Char(string='Co-Ords')
    source_of_water = fields.Char(string='Source Of Water')
    production_borehole = fields.Char(string='H/Pump or Production borehole')
    type_pump = fields.Char(string='Type of pump')
    no_of_per_station = fields.Char(string='No. of per Station')
    year_installed = fields.Char(string='Year installed')
    make_of_pump = fields.Char(string='Make of pump')
    flow_rate = fields.Char(string='Flow Rate')
    residual_head = fields.Char(string='Residual head')
    servicing_frequency = fields.Char(string='Required Servicing Frequency')
    pump_stations_per_frequency = fields.Char(
        string='Pump Stations Per Frequency')

    corrective_type = fields.Selection([('run_to_failure', 'Run-to-failure'),
                                        ('unplanned_failure',
                                         'Unplanned Failure')])
    run_to_failure_type = fields.Selection(
        [('temporary_repair', 'Temporary Repair'),
         ('repair', 'Repair'), ('overhaul', 'Overhaul'),
         ('refurbishment', 'Refurbishment'), ('replacement', 'Replacement'),
         ('modification', 'Modification')])
    unplanned_failure_type = fields.Selection([('inspection', 'Inspection'),
                                               ('failure diagnosis',
                                                'Failure Diagnose')])
    done_type = fields.Selection(
        [('Internally', 'Internally'), ('Externally', 'Externally')])

    # Internally

    assignee_ids = fields.Many2many('res.users')
    vehicle_id = fields.Many2one('fleet.vehicle')

    # Externally
    specifications = fields.Text(string='Specifications')
    service_provider_ids = fields.Many2many('res.users',
                                            relation='service_provider_rel')

    # Preventive
    preventive_type = fields.Selection(
        [('Periodic', 'Periodic'), ('Predictive', 'Predictive'),
         ('Planned', 'Planned'), ])
    periodic_type = fields.Selection([('time_based', 'Time-based servicing'),
                                      ('overhaul', 'Overhaul'),
                                      ('includes_periodic_inpection',
                                       'Includes periodic inpection'),
                                      ('replacement', 'Replacement')])
    predictive_type = fields.Selection([('surveillance', 'Surveillance'),
                                        ('monitoring', 'Monitoring'),
                                        ('testing', 'Testing'),
                                        ('in_service_inspection',
                                         'In-service inspection'), ])
    planned_type = fields.Selection(
        [('condition_based_servicing', 'Condition-based servicing'),
         ('parts_replacement', 'Parts Replacement'),
         ('overhaul', 'Overhaul'),
         ('refurbishment', 'Refurbishment'),
         ('modification', 'Modification')])
    project_id = fields.Many2one('project.task')
    job_card_count = fields.Integer(string="Job Card Count", compute="compute_job_card_count")
    assessment_details = fields.Text(string="Assessment Details")
    assessment_done_type = fields.Selection([('improved', 'Improved'), ('restored', ' Restored')])

    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, readonly=True,
                                  default=lambda
                                      self: self.env.company.currency_id.id)
    expense_cost = fields.Monetary(string="Expense Cost")
    replacement_type = fields.Selection([('replacement', 'Replacement'), ('no_replacement', 'No Replacement')])
    capitalise_costs = fields.Monetary(string="Capitalise Cost")
    assessment_completed = fields.Boolean(string="Assessment Completed")
    # Fields for importing data
    major_repairs = fields.Char(string="Major Repairs")
    comments = fields.Char(string="Comments")
    production_rate = fields.Char(string="Production Rate")
    capacity_of_plant = fields.Char(string="Capacity of plant")
    type_of_treatment = fields.Char(string="Type of treatment")
    population_served = fields.Float(string="Population served")
    maintenance_work = fields.Char(string="Maintenance Work and Servicing")
    # workflow
    store_ids = fields.Many2many('product.product')
    is_in_progress = fields.Boolean(string="Is In-Progress")
    is_new_request = fields.Boolean(string="Is New Request",
                                    compute="_compute_is_new_request",)
                                    # store=True)
    job_card_ids = fields.One2many('job.card', 'maintenance_id')

    def create_job_card(self):
        """Create a new job card"""
        self.ensure_one()
        if not self.assignee_ids:
            raise UserError(_('You must assign assignees in the request'))
        if not self.vehicle_id:
            raise UserError(_('You must assign vehicle for the request'))
        if not self.store_ids:
            raise UserError(_('You must assign store items for the request'))
        self.env['job.card'].create({
            'name': self.name,
            'maintenance_id': self.id,
            'project_id': self.project_id.id,
            'start_date': fields.Date.today(),
            'user_ids': [(6, 0, self.assignee_ids.ids)]
        })

    @api.depends('project_id', 'done_type')
    def compute_job_card_count(self):
        """compute job card count"""
        for rec in self:
            rec.job_card_count = self.env['job.card'].search_count([('maintenance_id', '=', rec.id)])

    def get_job_card(self):
        """Returns job card details"""
        job_card = self.env['job.card'].search([('maintenance_id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Job Card',
            'view_mode': 'tree,form',
            'res_model': 'job.card',
            'domain': [('id', 'in', job_card.ids)],
            'context': "{'create': False}"
        }

    @api.constrains('stage_id')
    def action_stage_completed(self):
        """ Method to show the waring messages. if there is no completed job card. """
        if self.stage_id.id == self.env.ref('asset_maintenance.maintenance_stage_completed').id:
            job_card = self.env['job.card'].search([('maintenance_id', '=', self.id)])
            for job in job_card:
                if job.state != 'completed':
                    raise UserError(_("Job card is not completed"))
            if not job_card:
                raise UserError(_("Create a job card"))

    def write(self, values):
        print(values, self.id)
        if values.get('stage_id'):
            if values.get('stage_id') == self.env.ref(
                'asset_maintenance.maintenance_stage_completed').id:
                values['assessment_completed'] = True
                job_card = self.env['job.card'].search([('maintenance_id', '=', self.id)])
                for job in job_card:
                    if job.completed_status == 'external_maintenance':
                        values['maintenance_team_id'] = self.env.ref('asset_maintenance.maintenance_team_completed').id
                        values['stage_id'] = self.env.ref('maintenance.stage_0').id
                    if job.completed_status == 'job_not_completed':
                        values['stage_id'] = self.env.ref('maintenance.stage_4')
            else:
                values['assessment_completed'] = False
            if values.get('stage_id') == self.env.ref('maintenance.stage_1').id:
                values['is_in_progress'] = True
            else:
                values['is_in_progress'] = False
        return super().write(values)

    @api.depends('stage_id')
    def _compute_is_new_request(self):
        """Compute Is new request"""
        for rec in self:
            if rec.stage_id.id == self.env.ref('maintenance.stage_0').id:
                rec.is_new_request = True
            else:
                rec.is_new_request =False

    def action_restored_assets(self):
        """Method for restoring the assets"""
        print(self.assessment_done_type)
        print(self.asset_id)
        if self.asset_id:
            self.asset_id.expense_cost = self.expense_cost + self.asset_id.expense_cost
        else:
            raise UserError(_('Please add a asset to the maintenance'))

    def action_no_replacement_assets(self):
        """Method for no replacement assets"""
        if self.asset_id:
            self.asset_id.capitalise_costs = self.capitalise_costs + self.asset_id.capitalise_costs
        else:
            raise UserError(_('Please add a asset to the maintenance'))


    def action_asset_addition(self):
        """Create assets"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Asset Addition from the Maintenance',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'account.asset',
            # 'context': {
            #     'default_maintenance_id': self.id,
            # }
        }
