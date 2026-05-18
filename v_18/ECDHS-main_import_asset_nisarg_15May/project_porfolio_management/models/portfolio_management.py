from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class PortfolioManagement(models.Model):
    _name = "portfolio.management"
    _description = "Portfolio Management"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # === Fields ===
    name = fields.Char(string="Portfolio Name", required=True, tracking=True)
    code = fields.Char(string="Sequence", readonly=True,
                       copy=False, tracking=True,)
    description = fields.Text(string="Description")

    owner_id = fields.Many2one("res.users", string="Owner", default=lambda self: self.env.user, tracking=True)
    sponsor_id = fields.Many2one("res.partner", string="Sponsor")

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    priority = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        string="Priority",
        default="medium",
        tracking=True,
    )

    # strategic_objectives_ids = fields.Many2many(
    #     "portfolio.objective",
    #     "portfolio_objective_rel",
    #     "portfolio_id",
    #     "objective_id",
    #     string="Strategic Objectives",
    # )
    #
    program_ids = fields.One2many(
        "portfolio.program", "portfolio_id", string="Programs"
    )

    # budget_total = fields.Monetary(
    #     string="Total Budget", compute="_compute_budget_and_cost", store=True
    # )
    # cost_actual = fields.Monetary(
    #     string="Actual Cost", compute="_compute_budget_and_cost", store=True
    # )
    currency_id = fields.Many2one(
        "res.currency", string="Currency", default=lambda self: self.env.company.currency_id
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("review", "Review"),
            ("active", "Active"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    risk_profile = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        string="Risk Profile",
    )

    # analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account',)

    budget_planned = fields.Monetary(string='Planned Budget',
                                     compute='_compute_budget', store=False)
    budget_actual = fields.Monetary(string='Actual Spend',
                                    compute='_compute_budget', store=False)
    budget_variance = fields.Monetary(string='Variance',
                                      compute='_compute_budget', store=False)
    program_count = fields.Integer(string="Program", compute="_compute_program_count")
    project_count = fields.Integer(string="Program", compute="_compute_program_count")

    @api.depends('program_ids')
    def _compute_budget(self):
        """Budget"""
        for rec in self:
            budget_planned, budget_actual = 0, 0
            budget_planned = sum(rec.program_ids.mapped('budget_planned'))
            budget_actual = sum(rec.program_ids.mapped('budget_actual'))
            rec.budget_planned = budget_planned
            rec.budget_actual = budget_actual
            rec.budget_variance = budget_planned - budget_actual

    # === Compute Methods ===
    # @api.depends("program_ids.budget_total", "program_ids.cost_actual")
    # def _compute_budget_and_cost(self):
    #     for rec in self:
    #         rec.budget_total = sum(rec.program_ids.mapped("budget_total"))
    #         rec.cost_actual = sum(rec.program_ids.mapped("cost_actual"))

    # === Business Constraints ===
    def _check_active_projects_before_close(self):
        for rec in self:
            active_projects = rec.program_ids.mapped("project_ids").filtered(
                lambda p: p.state not in ["closed", "cancelled"]
            )
            if active_projects:
                raise ValidationError(
                    _(
                        "You cannot close portfolio '%s' because it has active projects. "
                        "Please close or cancel them first, or force close with reason."
                    )
                    % rec.name
                )

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

    def action_close(self, force=False, reason=None):
        for rec in self:
            if not force:
                rec._check_active_projects_before_close()
            else:
                if not reason:
                    raise UserError(_("You must provide a reason when force-closing a portfolio."))
                rec.message_post(
                    body=_("Portfolio force-closed. Reason: %s") % reason
                )
            rec.state = "closed"

    @api.depends('program_ids')
    def _compute_program_count(self):
        """Compute Program"""
        for rec in self:
            rec.program_count = len(rec.program_ids)
            rec.project_count = rec.env['project.project'].search_count([('portfolio_id', '=', rec.id)])

    def action_view_program(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Program"),
            "res_model": "portfolio.program",
            "view_mode": "list,form",
            "domain": [("portfolio_id", '=', self.id)],
            "context": {"default_portfolio_id": self.id},
        }

    def action_view_project(self):
        self.ensure_one()
        action = self.env.ref(
            'project_porfolio_management.action_open_view_projects_ppe').read()[
            0]

        # override domain and context dynamically
        action['domain'] = [
            ('is_ppe', '=', True),
            ('portfolio_id', '=', self.id)
        ]
        action['context'] = {
            'default_is_ppe': True,
            'default_portfolio_id': self.id,  # or portfolio_id if applicable
            'display_milestone_deadline': True,
            'create': False
        }
        return action

    # === Sequence for Code ===
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # if vals.get("code", "New") == "New":
            vals["code"] = self.env["ir.sequence"].next_by_code(
                "portfolio.management"
            )
            # account = self.env['account.analytic.account'].create({
            #     'name': "Portfolio" + vals.get('name'),
            #     'plan_id': self.env.ref('analytic.analytic_plan_projects').id,
            #     'code': vals['code']
            # })
            # vals['analytic_account_id'] = account.id
        return super().create(vals_list)
