from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectIssue(models.Model):
    _name = 'project.issue'
    _description = 'Project Issue'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # Auto sequence for Issue Number
    name = fields.Char(
        string="Issue",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    project_id = fields.Many2one('project.project', string="Project", required=True, domain=[('is_ppe', '=', True)])
    title = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    contact_person_id = fields.Many2one('res.partner', string="Contact Person")

    # Classification
    type = fields.Selection([
        ('Administration', 'Administration'),
        ('Communications', 'Communications'),
        ('Cost', 'Cost'),
        ('Progress', 'Progress'),
        ('Quality', 'Quality'),
        ('Resources', 'Resources'),
        ('Support', 'Support'),
        ('Other', 'Other'),
    ], string="Type", default='Other')

    status = fields.Selection([
        ('Open', 'Open'),
        ('Awaiting Dependency', 'Awaiting Dependency'),
        ('Closed', 'Closed'),
    ], string="Status", default='Open', tracking=True)

    priority = fields.Selection([
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ], string="Priority", default='Medium')

    # Management
    issue_owner_id = fields.Many2one('res.users', string="Issue Owner", required=True)
    follow_up_date = fields.Date(string="Follow Up Date")
    logged_date = fields.Date(string="Logged Date", default=fields.Date.context_today)

    age = fields.Integer(string="Age (days)", compute="_compute_age", store=True)
    days_overdue = fields.Integer(string="Days Overdue", compute="_compute_days_overdue", store=True)

    is_overdue = fields.Selection([
        ('closed', 'Closed'),
        ('update_current', 'Update Current'),('overdue', 'Overdue'),('not_overdue', 'Not Overdue'),
                                ('due_soon', 'Due Soon')], compute="_compute_date_overdue", tracking=True, string="Overdue?",store=True)


    @api.depends("follow_up_date", "status")
    def _compute_date_overdue(self):
        """Compute Overdue"""
        for rec in self:
            if rec.status == 'Closed':
                rec.is_overdue = 'closed'
            else:
                if rec.follow_up_date:
                    today = fields.Date.today()
                    if rec.follow_up_date < today:
                        rec.is_overdue = 'overdue'
                    else:
                        overdue_days = (rec.follow_up_date - today).days
                        if overdue_days > 7:
                            rec.is_overdue = "not_overdue"
                        if overdue_days <= 7:
                            rec.is_overdue = "due_soon"
                else:
                    rec.is_overdue = ''

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('project.issue') or _('New')
        return super().create(vals_list)

    @api.depends('logged_date')
    def _compute_age(self):
        today = fields.Date.today()
        for rec in self:
            if rec.logged_date:
                rec.age = (today - rec.logged_date).days
            else:
                rec.age = 0

    @api.depends('follow_up_date', 'status')
    def _compute_days_overdue(self):
        today = fields.Date.today()
        for rec in self:
            if rec.status != "Closed":
                if rec.follow_up_date and rec.follow_up_date < today:
                    rec.days_overdue = (today - rec.follow_up_date).days
                else:
                    rec.days_overdue = 0
            else:
                rec.days_overdue = 0