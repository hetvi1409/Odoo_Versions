from odoo import models, fields, api, _
import json

class ProjectCost(models.Model):
    _name = "project.cost"
    _description = "Project Cost Information"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @staticmethod
    def year_range_selection(start_offset, end_offset, steps=1):
        current_year = fields.Datetime.now().year
        return [(str(year), str(year)) for year in range(current_year - start_offset, current_year + end_offset, steps)]

    name = fields.Char(string="Cost", copy=False, required=True, readonly=True, default='/')
    project_id = fields.Many2one(
        'project.project',
        string="Project",
        required=True,
        tracking=True
    )
    category_id = fields.Many2one(
        'project.cost.category',
        string="Category",
        tracking=True
    )
    sub_category_id = fields.Many2one(
        'project.cost.subcategory',
        string="Sub-Category",
        tracking=True
    )
    year = fields.Selection(string='Year',
                            selection=lambda self: self.year_range_selection(50, 20),
                            default=lambda self: str(fields.Datetime.now().year),
                            tracking=True
                            )
    month = fields.Selection(
        [('01', '01'), ('02', '02'), ('03', '03'),
         ('04', '04'), ('05', '05'), ('06', '06'),
         ('07', '07'), ('08', '08'), ('09', '09'),
         ('10', '10'), ('11', '11'), ('12', '12')],
        string="Month",
        tracking=True
    )
    other_description = fields.Char(string="Other Description")
    budget = fields.Float(string="Budget", tracking=True)
    spent = fields.Float(string="Spent", tracking=True)
    committed = fields.Float(string="Committed", tracking=True)
    estimate_to_complete = fields.Float(string="Estimate to Complete", tracking=True)
    document_ids = fields.Many2many('ir.attachment',
                                    'project_cost_attachment_rel',
                                    'cost_id',
                                    'attachment_id',
                                    string="Linked Documents"
                                    )
    # Computed Field Example
    total_at_completion = fields.Float(
        string="Total at Completion",
        compute="_compute_variance",
        store=True
    )
    variance = fields.Float(
        string="Variance",
        compute="_compute_variance",
        store=True
    )
    chart_data = fields.Json(
        string="Chart Data",
        compute="_compute_chart_data",
        store=False
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Analytic Account",
        related="project_id.account_id",
        store=True,
        readonly=False
    )
    company_id = fields.Many2one('res.company',
        string="Company", required=True,
        default=lambda self: self.env.company)

    # def write(self, vals):
    #     res = super().write(vals)
    #     for rec in self:
    #         rec._create_or_update_analytic_line()
    #     return res
    #
    # def _create_or_update_analytic_line(self):
    #     """Sync project.cost with analytic lines"""
    #     self.ensure_one()
    #     if not self.analytic_account_id:
    #         return
    #
    #     analytic_line = self.env['account.analytic.line'].search([
    #         ('ref', '=', self.name),
    #         ('account_id', '=', self.analytic_account_id.id),
    #     ], limit=1)
    #
    #     vals = {
    #         'name': self.other_description or self.category_id.name or self.name,
    #         'account_id': self.analytic_account_id.id,
    #         'date': fields.Date.context_today(self),
    #         'amount': - (self.spent * self.budget),  # Expense goes negative
    #         'unit_amount': 1.0,
    #         'ref': self.name,
    #         'company_id': self.company_id.id,
    #     }
    #
    #     if analytic_line:
    #         analytic_line.write(vals)
    #     else:
    #         self.env['account.analytic.line'].create(vals)

    def _compute_chart_data(self):
        for rec in self:
            rec.chart_data = {
                "labels": ["Budget", "Spent", "Committed",
                           "Estimate to Complete"],
                "values": [
                    float(rec.budget or 0.0),
                    float(rec.spent or 0.0),
                    float(rec.committed or 0.0),
                    float(rec.estimate_to_complete or 0.0),
                ],
            }

    @api.depends('budget', 'spent', 'committed', 'estimate_to_complete')
    def _compute_variance(self):
        for rec in self:
            rec.total_at_completion = (rec.spent or 0.0) + (rec.estimate_to_complete or 0.0) + rec.committed
            rec.variance = 1 - (rec.spent+ rec.estimate_to_complete+ rec.committed)

    @api.model_create_multi
    def create(self, vals_list):
        """Allow multi-create with sequence assignment"""
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('project.cost') or '/'
        records = super(ProjectCost, self).create(vals_list)
        # for rec in records:
        #     rec._create_or_update_analytic_line()
        return records

    def action_view_analytic_lines(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Analytic Entries'),
            'res_model': 'account.analytic.line',
            'view_mode': 'list,form',
            'domain': [
                ('account_id', '=', self.analytic_account_id.id),
                ('ref', '=', self.name)],
            'context': {'create': False},
        }

    def action_view_cost_graph(self):
        """Inspection smart button"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicle Inspections',
            'view_mode': 'graph',
            'res_model': 'project.cost',
            'domain': [('id', '=', self.id)],
            'target': 'new',
            'view_id': self.env.ref(
                'project_porfolio_management.project_cost_view_graph').id,
        }

class ProjectCostCategory(models.Model):
    _name = "project.cost.category"
    _description = "Cost Category"

    name = fields.Char(string="Category Name", required=True)


class ProjectCostSubCategory(models.Model):
    _name = "project.cost.subcategory"
    _description = "Cost Sub-Category"

    name = fields.Char(string="Sub-Category Name", required=True)
    category_id = fields.Many2one('project.cost.category', string="Category")
