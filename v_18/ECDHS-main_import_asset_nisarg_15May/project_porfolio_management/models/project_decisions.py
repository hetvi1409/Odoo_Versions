from odoo import api, fields, models, _


class ProjectDecisions(models.Model):
    _name = 'project.decisions'
    _rec_name = "title"
    _description = "Project Decisions"

    title = fields.Char(string='Title', required=True)
    name = fields.Char(string="Issue", required=True, copy=False,
                       readonly=True, default=lambda self: _('New'))
    decision_type_id = fields.Many2one("decision.type",string='Decision Type')
    decision_status = fields.Selection([('draft','Draft'),('submit','Submit'),('approved','Approved')],string='Decision Status')
    decision_date = fields.Date(string='Decision Date')
    decision_made_at_id = fields.Many2one("decision.made", string='Decision Made At')
    description = fields.Html(string='Description')
    age = fields.Integer(string='Age', compute="_compute_age")
    project_id = fields.Many2one('project.project', string="Project", required=True,
                                 domain=[('is_ppe', '=', True)])

    logged_date = fields.Date(string="Logged Date", default=fields.Date.context_today)
    responsibility_ids = fields.Many2many("res.users", string="Decision Responsibility")
    context = fields.Html(string="Context / Rationale")
    decision_attendees = fields.Html(string="Decision Attendees")

    @api.model
    @api.depends('logged_date')
    def _compute_age(self):
        today = fields.Date.today()
        for rec in self:
            if rec.logged_date:
                rec.age = (today - rec.logged_date).days
            else:
                rec.age = 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('project.decision') or _('New')
        return super().create(vals_list)