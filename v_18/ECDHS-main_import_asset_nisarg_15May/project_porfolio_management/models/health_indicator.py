from odoo import api, fields, models, _


class HealthIndicator(models.Model):
    _name = 'health.indicator'
    _description = "Heath Indicator"
    _rec_name = "project_id"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    project_id = fields.Many2one('project.project', string="Project", required=False, domain=[('is_ppe', '=', True)])
    title = fields.Selection([('issue', 'Issue'), ('progress', 'Progress'),
                              ('risk', 'Risks'), ('scope', 'Scope'), ('costs', 'Costs')],
                             string="Title", required=True, tracking=True)
    rag_indicator = fields.Selection([
        ('normal', 'A'),
        ('done', 'G'),
        ('blocked', 'R')], string="Rag Indicator", tracking=True)
    previous_rag = fields.Selection([('normal', 'A'),
        ('done', 'G'),
        ('blocked', 'R')],  string="Previous Rag", tracking=True)
    comments = fields.Text(string="Comments", tracking=True)
    overdue = fields.Selection([
        ('update_current', 'Update Current'),('overdue', 'Overdue'),
                                ('update_due_soon', 'Update Due Soon')], compute="_compute_date_overdue", tracking=True)
    last_update = fields.Integer(string="Days since last update", default=1, compute="_compute_date_overdue", tracking=True)

    logged_date = fields.Datetime(string="Last Update", default=fields.Datetime.now())
    loaded_by_id = fields.Many2one('res.users', string="Loaded By", default=lambda self: self.env.uid)
    name = fields.Char(string="Reference", required=True, copy=False,
                       readonly=True, default=lambda self: _('New'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'project.health') or _('New')
        return super().create(vals_list)

    @api.depends('logged_date')
    def _compute_date_overdue(self):
        """Compute the overdue"""
        for rec in self:
            overdue_status = 0
            if rec.logged_date:
                delta = fields.Date.today() - rec.logged_date.date()
                rec.last_update = delta.days
                if rec.last_update < 5:
                    rec.overdue = 'update_current'
                elif 5 <= rec.last_update <= 7:
                    rec.overdue = 'update_due_soon'
                else:  # rec.last_update > 7
                    rec.overdue = 'overdue'
            else:
                rec.last_update = 0
                rec.overdue = 'update_current'

    def write(self, vals):
        if vals.get('rag_indicator'):
            self.previous_rag = self.rag_indicator
        if 'logged_date' not in vals:
            self.logged_date = fields.Datetime.now()
        res = super().write(vals)
        return res

