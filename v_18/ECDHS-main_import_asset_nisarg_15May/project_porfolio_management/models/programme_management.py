from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PortfolioProgram(models.Model):
    _name = "portfolio.program"
    _description = "Portfolio Program"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # === Fields ===
    name = fields.Char(string="Program Name", required=True, tracking=True)
    code = fields.Char(
        string="Code",
        required=True,
        readonly=True,
        copy=False,
        default="New",
        tracking=True,
    )
    description = fields.Text(string="Description")

    portfolio_id = fields.Many2one(
        "portfolio.management",
        string="Portfolio",
        required=True,
        ondelete="cascade",
        tracking=True,
    )

    manager_id = fields.Many2one(
        "res.users", string="Program Manager", default=lambda self: self.env.user
    )

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("review", "Review"),
            ("active", "Active"),
            ("on_hold", "On Hold"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    project_ids = fields.One2many(
        "project.project", "program_id", string="Projects"
    )

    # === Aggregates ===
    # budget_total = fields.Monetary(
    #     string="Total Budget", compute="_compute_total_budget_cost", store=True
    # )
    # cost_actual = fields.Monetary(
    #     string="Actual Cost", compute="_compute_total_budget_cost",  store=True
    # )
    # percent_complete = fields.Float( compute="_compute_total_budget_cost",
    #     string="% Complete",  store=True
    # )
    risk_score = fields.Float(
        string="Risk Score",  store=True, compute="compute_risk_rating"
    )
    budget_planned = fields.Monetary(string='Planned Budget',
                                     compute='_compute_budget', store=False)
    budget_actual = fields.Monetary(string='Actual Spend',
                                    compute='_compute_budget', store=False)
    budget_variance = fields.Monetary(string='Variance',
                                      compute='_compute_budget', store=False)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    project_count = fields.Integer(compute="_compute_project_count")
    # analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',)
    # === Milestone Management ===
    # milestone_ids = fields.One2many(
    #     "project.task",
    #     "program_id",
    #     string="Milestones",
    #     domain=[("is_milestone", "=", True)],
    # )

    @api.depends('project_ids')
    def _compute_budget(self):
        """Budget"""
        for rec in self:
            budget_planned, budget_actual = 0, 0
            budget_planned = sum(rec.project_ids.mapped('budget_planned'))
            budget_actual = sum(rec.project_ids.mapped('budget_actual'))
            rec.budget_planned = budget_planned
            rec.budget_actual = budget_actual
            rec.budget_variance = budget_planned - budget_actual

    @api.depends('project_ids')
    def compute_risk_rating(self):
        """Calculate risk Rating"""
        for rec in self:
            if rec.project_ids:
                rec.risk_score = sum(rec.project_ids.mapped('risk_rating')) / len(rec.project_ids)
            else:
                rec.risk_score = 0

    @api.depends('project_ids')
    def _compute_project_count(self):
        """Compute project count"""
        for rec in self:
            rec.project_count = len(rec.project_ids)


    def action_view_project(self):
        self.ensure_one()
        action = self.env.ref(
            'project_porfolio_management.action_open_view_projects_ppe').read()[0]

        # override domain and context dynamically
        action['domain'] = [
            ('is_ppe', '=', True),
            ('program_id', '=', self.id)
            # or ('portfolio_id', '=', self.id) depending on your relation
        ]
        action['context'] = {
            'default_is_ppe': True,
            'default_program_id': self.id,  # or portfolio_id if applicable
            'display_milestone_deadline': True,
        }
        return action

    # @api.depends('project_ids')
    # def _compute_total_budget_cost(self):
    #     """Compute budget and cost"""
    #     for rec in self:
    #         rec.budget_total = sum(rec.project_ids.mapped('total_budget'))
    #         rec.cost_actual = sum(rec.project_ids.mapped('actual_cost'))
    #         rec.percent_complete = sum(rec.project_ids.mapped('actual_progress'))/len(rec.project_ids) if rec.project_ids else False

    # === Sequence ===
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("code", "New") == "New":
                vals["code"] = self.env["ir.sequence"].next_by_code(
                    "portfolio.program"
                ) or "New"
            # parent_id = self.env['portfolio.management'].browse(int(vals.get('portfolio_id'))).analytic_account_id
            # account = self.env['account.analytic.account'].create({
            #     'name': vals.get('name'),
            #     'plan_id': self.env.ref('analytic.analytic_plan_projects').id,
            #     'code': vals['code'],
            #     'parent_id': parent_id.id
            # })
            # vals['analytic_account_id'] = account.id
        return super().create(vals_list)

    # === Button Actions ===
    def action_activate(self):
        for rec in self:
            rec.state = "active"

    def action_review(self):
        for rec in self:
            rec.state = "review"
    def action_cancelled(self):
        for rec in self:
            rec.state = "cancelled"
