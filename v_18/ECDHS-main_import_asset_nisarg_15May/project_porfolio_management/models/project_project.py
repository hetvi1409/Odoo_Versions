from odoo import api, fields, models
from collections import Counter
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, timedelta


class ProjectProject(models.Model):
    _inherit = 'project.project'

    sequence_code = fields.Char(copy=False, readonly=True)
    is_ppe = fields.Boolean(string="Project Portfolio", tracking=True)
    objective_deliverables = fields.Text(string="Objectives and Deliverables", tracking=True)
    project_benefits = fields.Text(string="Project Benefits", tracking=True)
    required_date = fields.Date(string="Required Date", tracking=True)
    critical_success_factor = fields.Text(string="Critical Success Factor", tracking=True)
    dependencies = fields.Text(string="Dependencies", tracking=True)
    constraints = fields.Text(string="Constraints", tracking=True)
    assumption = fields.Text(string="Assumption", tracking=True)
    logged_date = fields.Datetime(string="Logged Date", default=fields.Datetime.now(), tracking=True)
    loaded_by_id = fields.Many2one('res.users', string="Loaded By", default=lambda self: self.env.uid, tracking=True)

    phase_id = fields.Many2one('project.phase', tracking=True)
    priority = fields.Selection([('0', 'Normal'), ('1', 'Low'),
                                 ('2', 'High'), ('3', 'Very High')], string='Priority', index=True, tracking=True)
    planned_progress = fields.Float(string="Planned Progress", compute="_compute_planned_actual_progress")
    actual_progress = fields.Float(string="Actual Progress", compute="_compute_planned_actual_progress", store=True)
    variance_progress = fields.Float(string="Variance Progress", compute="_compute_variance_progress", store=True)

    @api.model
    @api.depends('task_ids', 'task_ids.planned_progress')
    def _compute_planned_actual_progress(self):
        """"""
        for rec in self:
            planned_progress, actual_progress = 0, 0
            if rec.task_ids:
                planned_progress = sum(rec.task_ids.mapped('planned_progress')) / len(rec.task_ids)
                actual_progress = sum(rec.task_ids.mapped('allocation')) / len(rec.task_ids)
            rec.planned_progress = planned_progress
            rec.actual_progress = actual_progress

    @api.depends('actual_progress', 'planned_progress')
    def _compute_variance_progress(self):
        for rec in self:
            rec.variance_progress = rec.planned_progress - rec.actual_progress

    department_id = fields.Many2one('hr.department', tracking=True)
    sponsor_id = fields.Many2one('hr.employee', string="Project Sponsor", tracking=True)
    owner_id = fields.Many2one('hr.employee', string="Project Owner", tracking=True)
    project_manager_id = fields.Many2one('hr.employee', string="Project Manager", tracking=True)

    type_id = fields.Many2one('project.type', tracking=True)
    parent_id = fields.Many2one('project.project', string="Parent Project", tracking=True)
    admin_project = fields.Boolean(string="Admin Project", tracking=True)
    rate_to_use = fields.Many2one('project.rate', string="Rate To Use", tracking=True)
    cost_estimate = fields.Selection([
        ('0_100k', '0-100K'), ('100_500', '100K-500K'), ('500_1', '500K-1M'), ('1m', '1M Plus'),
    ], string="Cost Estimate", tracking=True)
    duration_estimation = fields.Selection([
        ('3_months', '<3 Months'), ('3_6_months', '3-6 Months'), ('6_9_months', '6-9 Months'),
        ('9_months', '>9 Months')
    ], tracking=True)

    health_indicator_ids = fields.One2many('health.indicator', 'project_id', string="Health Indicator", tracking=True)
    comments_ids = fields.One2many('project.comments', 'project_id', string="Comments", tracking=True)
    document_project_ids = fields.One2many('project.documents', 'project_id', string="Documents", tracking=True)
    health_indicator = fields.Selection([
        ('normal', 'A'),
        ('done', 'G'),
        ('blocked', 'R')], string="Health Rag Indicator", compute="_compute_health_indicator",
        store=True)
    governance_rag = fields.Selection([
        ('normal', 'A'),
        ('done', 'G'),
        ('blocked', 'R')], string="Governance Rag", compute="_compute_governance_rag",
        store=True)
    resource_allocations_ids = fields.One2many('resource.allocations', 'project_id', string="Resource Allocations",
                                               tracking=True)
    scope_changes_ids = fields.One2many('scope.changes', 'project_id', string="Scope Changes", tracking=True)
    governance_requirements_ids = fields.One2many('governance.requirements', 'project_id',
                                                  string="Governance Requirements", tracking=True)
    decision_ids = fields.One2many('project.decisions', 'project_id', string="Decisions", tracking=True)
    risk_ids = fields.One2many('project.risk', 'project_id', string="Risks", tracking=True)
    issue_ids = fields.One2many('project.issue', 'project_id', string="Issues", tracking=True)
    cost_ids = fields.One2many('project.cost', 'project_id', string="Cost", tracking=True)
    program_id = fields.Many2one('portfolio.program', string="Program")
    portfolio_id = fields.Many2one('portfolio.management', related="program_id.portfolio_id", string="Program")
    # total_budget = fields.Float("Total Budget", compute="_compute_total_budget")
    # actual_cost = fields.Float("Total Actual Cost", compute="_compute_total_budget")
    risk_rating = fields.Float("Total Risk Rating", compute="compute_risk_rating")
    budget_planned = fields.Monetary(string='Planned Budget',
                                     compute='_compute_budget_planned', store=False)
    budget_actual = fields.Monetary(string='Actual Spend',
                                    compute='_compute_budget_planned', store=False)
    budget_variance = fields.Monetary(string='Variance',
                                      compute='_compute_budget_planned', store=False)
    currency_id = fields.Many2one('res.currency', string='Currency')
    comment_update_status = fields.Selection([
        ('g', 'G'),
        ('r', 'R'),
    ], string='Comments Updated', compute='_compute_comment_update_status', store=False)

    health_update_status = fields.Selection([
        ('g', 'G'),
        ('r', 'R'),
    ], string='Health Indicators Updated', compute='_compute_health_update_status', store=False)

    data_quality = fields.Selection([
        ('g', 'G'),
        ('a', 'A'),
        ('r', 'R'),
    ], string="Data Quality", default='r', compute="_compute_data_quality", store=True)

    resource_allocations_exist = fields.Selection([
        ('g', 'G'),
        ('r', 'R'),
    ], string="Resource Allocations Exist", default='r', compute="_compute_resource_allocation_status", store=True)

    date_end = fields.Date(string='Date To', help="End date for project")

    @api.depends('write_date', 'user_id', 'date_start', 'date_end', 'partner_id', 'tasks.user_ids',
                 'tasks.date_deadline')
    def _compute_data_quality(self):
        for project in self:
            rules_passed = 0
            total_rules = 5

            if project.user_id:
                rules_passed += 1
            if project.date_start and project.date_end:
                rules_passed += 1
            if project.partner_id:
                rules_passed += 1
            if project.write_date and (fields.Date.today() - project.write_date.date()).days <= 14:
                rules_passed += 1
            if project.tasks.filtered(lambda t: not t.user_ids or not t.date_deadline):
                pass
            else:
                rules_passed += 1

            compliance = (rules_passed / total_rules) * 100
            if compliance == 100:
                project.data_quality = 'g'
            elif compliance >= 70:
                project.data_quality = 'a'
            else:
                project.data_quality = 'r'

    @api.depends('resource_allocations_ids')
    def _compute_resource_allocation_status(self):
        for project in self:
            if project.resource_allocations_ids:
                # At least one allocation record exists
                project.resource_allocations_exist = 'g'
            else:
                # No allocation records found
                project.resource_allocations_exist = 'r'

    @api.depends('comments_ids.write_date', 'comments_ids.create_date')
    def _compute_comment_update_status(self):
        """Checks if all comments are updated/created within the last 7 days."""
        for project in self:
            seven_days_ago = fields.Datetime.now() - timedelta(days=7)
            if project.comments_ids:
                all_recent = True
                for c in project.comments_ids:
                    date_value = c.write_date or c.create_date
                    if not date_value or date_value < seven_days_ago:
                        all_recent = False
                        break
                project.comment_update_status = 'g' if all_recent else 'r'
            else:
                project.comment_update_status = 'r'

    @api.depends('health_indicator_ids.write_date',
                 'health_indicator_ids.create_date')
    def _compute_health_update_status(self):
        """Checks if all health indicators are updated/created within the last 7 days."""
        for project in self:
            seven_days_ago = datetime.now() - timedelta(days=7)
            if project.health_indicator_ids:
                all_recent = True
                for h in project.health_indicator_ids:
                    date_value = h.write_date or h.create_date
                    if not date_value or date_value < seven_days_ago:
                        all_recent = False
                        break
                project.health_update_status = 'g' if all_recent else 'r'
            else:
                project.health_update_status = 'r'

    @api.depends('account_id')
    def _compute_budget_planned(self):
        """Compute planned vs actual budgets safely"""
        for rec in self:
            planned = 0.0
            actual = 0.0

            aa = getattr(rec, 'account_id', False)
            if aa:
                planned = sum(self.env['budget.line']
                              .search([('account_id', '=', aa.id)])
                              .mapped('budget_amount')) or 0.0

                actual = sum(self.env['account.analytic.line']
                             .search([('account_id', '=', aa.id)])
                             .mapped('amount')) or 0.0

            # ✅ ALWAYS assign values
            rec.budget_planned = planned
            rec.budget_actual = actual
            rec.budget_variance = planned - actual

    # def _compute_budget(self):
    #     for rec in self:
    #         budget_amount, actual = 0, 0
    #         # if rec.account_id:
    #         #     aa = rec.account_id
    #         #     print('fghjk')
    #         #     budget_amount = sum(self.env['budget.line'].search([('account_id', '=', aa.id)]).mapped('budget_amount'))
    #         #     print(budget_amount, 'adszd')
    #         #     # actual = sum of analytic lines underneath this AA (SQL efficient with parent_left/right)
    #         #     actual = sum(self.env[
    #         #                      'account.analytic.line'].search(
    #         #         [('account_id', '=', aa.id)]).mapped('amount'))
    #         #     rec.budget_planned = budget_amount
    #         #     rec.budget_actual = actual
    #         #     rec.budget_variance = rec.budget_planned - rec.budget_actual
    #         rec.budget_planned = budget_amount
    #         # rec.budget_actual = actual
    #         # rec.budget_variance = rec.budget_planned - rec.budget_actual

    @api.depends('risk_ids')
    def compute_risk_rating(self):
        """Calculate risk Rating"""
        for rec in self:
            if rec.risk_ids:
                rec.risk_rating = sum(rec.risk_ids.mapped('rating')) / len(rec.risk_ids)
            else:
                rec.risk_rating = 0

    # @api.depends('cost_ids')
    # def _compute_total_budget(self):
    #     """Compute total budget and actual cost"""
    #     for rec in self:
    #         rec.total_budget = sum(rec.cost_ids.mapped('budget'))
    #         total_cost = 0
    #         for cost in rec.cost_ids:
    #             total_cost += cost.total_at_completion * cost.budget
    #         rec.actual_cost = total_cost

    @api.depends('health_indicator_ids.rag_indicator')
    def _compute_health_indicator(self):
        for project in self:
            rag_values = project.health_indicator_ids.mapped('rag_indicator')
            if rag_values:
                project.health_indicator = Counter(rag_values).most_common(1)[0][0]
            else:
                project.health_indicator = ""

    @api.depends('governance_requirements_ids', 'governance_requirements_ids.rag')
    def _compute_governance_rag(self):
        for project in self:
            rag_values = project.governance_requirements_ids.mapped('rag')
            if rag_values:
                project.governance_rag = Counter(rag_values).most_common(1)[0][0]
            else:
                project.governance_rag = ""

    @api.model
    def create(self, vals_list):
        """Method to super create function"""
        seq = self.env['ir.sequence'].next_by_code(
            'project.project')
        vals_list['sequence_code'] = seq
        # if vals_list.get('program_id'):
        #     parent_id = self.env['portfolio.program'].browse(
        #         int(vals_list.get('program_id'))).analytic_account_id
        # else:
        #     parent_id = False
        account = self.env['account.analytic.account'].create({
            'name': vals_list.get('name'),
            'plan_id': self.env.ref('analytic.analytic_plan_projects').id,
            'code': vals_list['sequence_code'],
            # 'parent_id': parent_id.id if parent_id else False
        })
        vals_list['account_id'] = account.id
        res = super().create(vals_list)
        self.env['health.indicator'].create({
            'project_id': res.id,
            'title': 'issue'
        })
        self.env['health.indicator'].create({
            'project_id': res.id,
            'title': 'progress'
        })
        self.env['health.indicator'].create({
            'project_id': res.id,
            'title': 'risk'
        })
        self.env['health.indicator'].create({
            'project_id': res.id,
            'title': 'scope'
        })
        self.env['health.indicator'].create({
            'project_id': res.id,
            'title': 'costs'
        })
        self.env['project.comments'].create({
            'project_id': res.id,
            'title': 'next_period'
        })
        self.env['project.comments'].create({
            'project_id': res.id,
            'title': 'achieved_period'
        })
        self.env['project.comments'].create({
            'project_id': res.id,
            'title': 'issues'
        })
        return res

    def action_view_ppe_tasks(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window'].with_context(active_id=self.id)._for_xml_id(
            'project_porfolio_management.action_view_all_task'
        )
        action['display_name'] = self.name

        # Safely evaluate context if it's a string
        context = action.get('context', {})
        if isinstance(context, str):
            context = safe_eval(context)

        # Update context
        context.update({
            'default_project_id': self.id,
            'create': self.active,
            'active_test': self.active,
        })
        action['domain'] = [('project_id', '=', self.id)]
        action['context'] = context
        return action

    def action_view_approvals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Win Loss Ratio',
            'view_mode': 'list,form',
            'res_model': 'project.approval',
            'domain': [('project_id', '=', self.id),
                       ],
            'context': {'default_project_id': self.id}
        }
