from odoo import models, fields, api
from datetime import date


class ProjectRisk(models.Model):
    _name = "project.risk"
    _description = "Project Risk"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Risk Info
    name = fields.Char(
        string="Risk",
        required=True,
        readonly=True,
        copy=False,
        default="/"
    )
    project_id = fields.Many2one("project.project", string="Project", required=True, tracking=True, domain=[('is_ppe', '=', True)])
    title = fields.Char(string="Title", required=True, tracking=True)
    description = fields.Text(string="Description")
    contact_person_id = fields.Many2one("res.partner", string="Contact Person")

    # Risk Classification
    type = fields.Selection(
        [("Cost", "Cost"),
            ("Progress", "Progress"),
            ("Quality", "Quality"),
            ("Resources", "Resources"),
            ("Other", "Other"),
        ],
        string="Type",
        tracking=True
    )
    status = fields.Selection(
        [("Open", "Open"), ("Closed", "Closed")],
        string="Status",
        default="Open",
        tracking=True
    )
    probability = fields.Selection(
        [
            ("Rare", "1 - Rare"),
            ("Unlikely", "2 - Unlikely"),
            ("Moderate", "3 - Moderate"),
            ("Likely", "4 - Likely"),
            ("Almost Certain", "5 - Almost Certain"),
        ],
        string="Probability",
        tracking=True
    )
    impact = fields.Selection(
        [
            ("Insignificant", "1 - Insignificant"),
            ("Minor", "2 - Minor"),
            ("Moderate", "3 - Moderate"),
            ("Major", "4 - Major"),
            ("Severe", "5 - Severe"),
        ],
        string="Impact",
        tracking=True
    )
    rating = fields.Integer(
        string="Rating",
        compute="_compute_rating",
        store=True
    )
    rag = fields.Selection(
        [("R", "R"), ("A", "A"), ("G", "G")],
        string="RAG",
        compute="_compute_rag",
        store=True
    )

    # Risk Management
    risk_owner_id = fields.Many2one("res.users", string="Risk Owner")
    follow_up_date = fields.Date(string="Follow Up Date")
    logged_date = fields.Date(string="Logged Date", default=fields.Date.today)
    age = fields.Integer(string="Age (days)", compute="_compute_age", store=True)
    days_overdue = fields.Integer(string="Days Overdue", compute="_compute_overdue", store=True)

    is_overdue = fields.Selection([
        ('closed', 'Closed'),
        ('update_current', 'Update Current'),('overdue', 'Overdue'),('not_overdue', 'Not Overdue'),
                                ('due_soon', 'Due Soon')], compute="_compute_date_overdue", tracking=True, string="Overdue?",store=True)

    # --- Computations ---
    @api.depends("probability", "impact")
    def _compute_rating(self):
        for rec in self:
            probability, impact = 0, 0
            if rec.probability == 'Rare':
                probability = 1
            elif rec.probability == 'Unlikely':
                probability = 2
            elif rec.probability == 'Moderate':
                probability = 3
            elif rec.probability == 'Likely':
                probability = 4
            elif rec.probability == 'Almost Certain':
                probability = 5
            if rec.impact == "Insignificant":
                impact = 1
            elif rec.impact == "Minor":
                impact = 2
            elif rec.impact == "Moderate":
                impact = 3
            elif rec.impact == "Major":
                impact = 4
            elif rec.impact == "Severe":
                impact = 5
            rec.rating = probability * impact

    @api.depends("rating")
    def _compute_rag(self):
        for rec in self:
            if rec.rating != 0:
                if rec.rating >= 15:
                    rec.rag = "R"
                elif rec.rating >= 8:
                    rec.rag = "A"
                else:
                    rec.rag = "G"
            else:
                rec.rag = ""

    @api.model
    @api.depends("logged_date")
    def _compute_age(self):
        for rec in self:
            if rec.logged_date:
                rec.age = (date.today() - rec.logged_date).days
            else:
                rec.age = 0

    @api.model
    @api.depends("follow_up_date", "status")
    def _compute_overdue(self):
        """Compute Overdue"""
        for rec in self:
            overdue = 0
            if rec.status == 'Closed':
                overdue = 0
            else:
                if rec.follow_up_date and rec.follow_up_date <= fields.Date.today():
                    overdue = ( fields.Date.today() - rec.follow_up_date).days
            rec.days_overdue = overdue

    @api.depends("follow_up_date", "days_overdue", "status")
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

    # --- Override Create/Write to handle sequence + last update ---
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("project.risk") or "/"
            # vals["last_updated_by"] = self.env.uid
            # vals["last_update_date"] = fields.Datetime.now()
        return super().create(vals_list)

