from odoo import api, fields, models, _
from odoo.exceptions import UserError


class JobCard(models.Model):
    _name = 'job.card'
    _description = 'Job Card'
    """Model for Job Card"""

    name = fields.Char(string="Name", required=True)
    sequence = fields.Char(string="Sequence", default='New')
    sequence_name = fields.Char(string="Sequence", stored=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string='End Date')
    deadline = fields.Date(string="Deadline")
    user_ids = fields.Many2many('res.users', string='Assigned To')
    maintenance_id = fields.Many2one('maintenance.request')
    project_id = fields.Many2one('project.task')
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'),
                              ('approve', 'Approved'), ('invoice', 'Invoiced'),
                              ('completed', 'Completed')], default='draft')
    quality_check_ids = fields.Many2many('quality.check.list')
    work_shop_id = fields.Many2one('workshop.team')
    categ_ids = fields.Many2many('job.card.tag')
    description = fields.Text(string='Description')

    def _default_currency_id(self):
        """get currency id"""
        return self.env.user.company_id.currency_id
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, default=lambda
            self: self._default_currency_id())
    instruction_ids = fields.One2many('job.card.instruction', 'job_card_id')
    instruction_count = fields.Integer(default=1)
    job_cost_sheet_ids = fields.One2many('job.cost.sheet', 'job_card_id')
    cost_sheet_amount = fields.Monetary(compute='_compute_cost_sheet_amount',
                                        store=True)
    job_cost_sheet_untaxed_amount = fields.Monetary(
        compute='_compute_cost_sheet_amount', store=True)
    invoice_id = fields.Many2one('account.move', string="Invoice")

    job_card_timesheet_ids = fields.One2many('job.card.timesheet',
                      'job_card_id')
    total_hours = fields.Float('Total Working Hour', store=True,
                               compute="_compute_hour")
    hours = fields.Float('Total working hour', store=True,
                         compute="_compute_hour")
    planned_hours = fields.Float('Planned Hours',
                                 help="Planned hour for this task")
    mpr_count = fields.Integer(compute='compute_count')
    progress = fields.Float(help="progress of this job card")

    hr_timesheet_ids = fields.One2many('account.analytic.line', 'job_card_id')
    analytic_account_id = fields.Many2one('account.analytic.account')
    mr_count = fields.Integer(compute='compute_count')

    # Assessment
    job_completed = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                     string='Was the job successful?', copy=False)
    external_maintenance = fields.Selection([('yes', 'Yes'), ('no', 'No')], copy=False,
                                            string='Is there is a need for external maintenance?')
    completed_status = fields.Selection([('job_completed', 'Job Completed'),
                                         ('job_not_completed', 'Job Not completed'),
                                         ('external_maintenance', 'External Maintenance')],
                                        copy=False, readonly=True)

    @api.model
    def create(self, values):
        """Method for generating consumer number for the contacts"""
        if values.get('sequence', _('New')) == _('New'):
            values['sequence'] = self.env['ir.sequence'].next_by_code(
                'job.card.name') or _('New')
        res = super(JobCard, self).create(values)
        return res

    @api.onchange('name', 'sequence')
    def onchange_name(self):
        if self.sequence:
            sequence = self.sequence
        if self.name:
            sequence = sequence + ': ' + self.name
        self.sequence_name = self.name

    def action_submit(self):
        """Method for submit the job card"""
        self.state = 'submitted'

    def action_approve(self):
        """Method for submit the job card"""
        self.state = 'approve'

    @api.depends('job_cost_sheet_ids.amount')
    def _compute_cost_sheet_amount(self):
        """calculate time cost sheet amount"""
        for rec in self:
            rec.cost_sheet_amount = sum(rec.job_cost_sheet_ids.mapped('amount'))
            rec.job_cost_sheet_untaxed_amount = sum(
                rec.job_cost_sheet_ids.mapped('untaxed_amount'))

    def action_create_invoice(self):
        """Create invoice"""
        lines = []
        for rec in self:
            if rec.job_cost_sheet_ids:
                for job in rec.job_cost_sheet_ids:
                    value = (0, 0, {
                        'product_id': job.product_id.id,
                        'price_unit': job.amount,
                        'quantity': job.quantity,
                    })
                    lines.append(value)

            invoice_line = {
                'move_type': 'out_invoice',
                'partner_id': rec.user_ids.partner_id.id,
                'invoice_user_id': rec.env.user.id,
                'invoice_origin': rec.name,
                'ref': rec.sequence,
                # 'invoice_line_ids': lines,
            }
            inv = self.env['account.move'].create(invoice_line)
            if rec.job_cost_sheet_ids:
                inv.invoice_line_ids = []
            rec.state = 'invoice'
            rec.invoice_id = inv.id

    def action_completed(self):
        """Method for submit the job card"""
        if not self.job_completed:
            raise UserError(_("please verify the assessment details"))
        if self.job_completed == 'yes':
            self.completed_status = 'job_completed'
        if self.job_completed == 'no':
            if self.external_maintenance == 'no':
                self.completed_status = 'job_not_completed'
            if self.external_maintenance == 'yes':
                self.completed_status = 'external_maintenance'
        self.state = 'completed'


    @api.onchange('planned_hours', 'total_hours')
    def _onchange_progress(self):
        if self.planned_hours and self.total_hours:
            self.progress = round(100.0 * self.total_hours / self.planned_hours,
                                  2)
        else:
            self.progress = 0.0

    @api.depends('job_card_timesheet_ids.time')
    def _compute_hour(self):
        """calculate time cost amount"""
        for rec in self:
            rec.cost_sheet_amount = sum(
                rec.job_card_timesheet_ids.mapped('time'))
            rec.total_hours = sum(
                rec.job_card_timesheet_ids.mapped('time'))
            rec.hours = rec.planned_hours - rec.total_hours

    @api.depends('name')
    def compute_count(self):
        """Compute mr count"""
        for rec in self:
            if rec.env['material.requisition'].search(
                    [('job_card_id', '=', rec.id)]):
                rec.mr_count = rec.env['material.requisition'].search_count(
                    [('job_card_id', '=', rec.id)])
            else:
                rec.mr_count = 0

    # def create_material_requisition(self):
    #     """create purchase material request"""
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'PMR',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'res_model': 'material.requisition',
    #         'context': {
    #             'default_job_card_id': self.id
    #         }
    #
    #     }

    def get_material_requisition(self):
        """Get purchase material request"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Material Requisition',
            'view_mode': 'tree,form',
            'res_model': 'material.requisition',
            'domain': [('job_card_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def get_invoice(self):
        """Returns invoice"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Order',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'res_ids': self.invoice_id.id,
            # 'domain': [('id', 'in', self.po_order_ids.ids)]
        }


class JobCardInstruction(models.Model):
    _name = "job.card.instruction"
    _description = 'Job Cards Instruction'
    _rec_name = 'instruction'

    @api.depends('job_card_id')
    def _compute_name(self):
        for rec in self:
            name = rec.job_card_id.sequence + '/' + rec.job_card_id.name + '/' + str(
                rec.job_card_id.instruction_count)
            if not rec.name:
                rec.job_card_id.instruction_count += 1
            rec.name = name

    job_card_id = fields.Many2one('job.card')
    name = fields.Char('Name', compute='_compute_name', store=True)
    start_date = fields.Datetime('Starting Date', required=True)
    end_date = fields.Datetime('Ending Date', required=False)
    user_id = fields.Many2one('res.users', string='Assigned To', required=True)
    instruction = fields.Char(help='Instructions', required=True)
    notes = fields.Char(help='notes for this instruction')
    state = fields.Selection(
        [('to_do', 'To Do'), ('in_progress', 'In progress'), ('done', 'Done')],
        default='to_do')


class CostSheet(models.Model):
    _name = 'job.cost.sheet'
    _description = 'Cost Sheet'
    """Job Cost Sheet"""

    type = fields.Selection([('material', 'Material'), ('labour', 'Labour'),
                             ('overhead', 'Overhead')], required=True,
                            help='Type of product')
    job_card_id = fields.Many2one('job.card')
    product_id = fields.Many2one('product.product', required=True)
    quantity = fields.Float('Quantity', default=1)
    unit_price = fields.Float('Unit Price')
    discount = fields.Float('Discount %')
    tax = fields.Many2one('account.tax')
    amount = fields.Float('Amount')
    untaxed_amount = fields.Float('Untaxed Amount')

    @api.onchange('product_id', 'discount', 'tax')
    def _onchange_product_id(self):
        """calculate the amount"""
        for rec in self:
            if rec.unit_price == 0.0:
                rec.unit_price = rec.product_id.list_price
            rec.amount = rec.unit_price * rec.quantity
            rec.untaxed_amount = rec.unit_price * rec.quantity
            if rec.tax:
                taxes = rec.tax.compute_all(**rec._prepare_compute_all_values())
                rec.amount = taxes['total_included']
                rec.untaxed_amount = taxes['total_excluded']
            if rec.discount:
                rec.amount = rec.amount - (rec.amount * rec.discount / 100)
                rec.untaxed_amount = rec.untaxed_amount - (
                        rec.untaxed_amount * rec.discount / 100)

    def _prepare_compute_all_values(self):
        """prepare values"""
        self.ensure_one()
        return {
            'price_unit': self.unit_price,
            'currency': self.job_card_id.currency_id,
            'quantity': self.quantity,
            'product': self.product_id,
            'partner': self.job_card_id.user_ids.partner_id,
        }

class JobCardTimesheet(models.Model):
    _name = 'job.card.timesheet'
    _description = 'Job Card TimeSheet'

    job_card_id = fields.Many2one('job.card', default=lambda
        self: self._default_job_card_id())
    name = fields.Char('Instruction Name', store=True)
    instruction_id = fields.Many2one('job.card.instruction', required=True, domain="[('job_card_id', '=', job_card_id)]")
    description = fields.Char('Description')
    leader_id = fields.Many2one('hr.employee', required=True,
                                domain=[('workshop_position', '=', 'leader')],
                                help="leader for this instruction")
    worker_id = fields.Many2one('hr.employee', required=True,
                                help="workers for this instruction",
                                string="Workers")
    date = fields.Date('Date', default=fields.Date.today())
    time = fields.Float('Time')

    @api.onchange('instruction_id')
    def _onchange_instruction_id(self):
        for rec in self:
            if rec.instruction_id:
                rec.name = rec.instruction_id.name + ':' + rec.instruction_id.instruction

    @api.model
    def create(self, vals_list):
        res = super(JobCardTimesheet, self).create(vals_list)
        job_card = self.env['job.card'].browse(vals_list['job_card_id'])
        self.env['account.analytic.line'].create({
            'date': vals_list['date'],
            'project_id': job_card.project_id.project_id.id,
            'employee_id': vals_list['worker_id'],
            'name': vals_list['description'],
            'unit_amount': vals_list['time'],
            'task_id': job_card.project_id.id,
            'job_card_id': job_card.id,
        })
        return res
