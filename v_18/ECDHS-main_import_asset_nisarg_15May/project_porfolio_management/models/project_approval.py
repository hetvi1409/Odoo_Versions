from email.policy import default

from odoo import api, fields, models, _


class ProjectApproval(models.Model):
    _name = "project.approval"
    _description = "Project Approval"
    _rec_name = "title"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    project_id = fields.Many2one('project.project', string="Project",
                                 required="True", domain=[('is_ppe', '=', True)])
    title = fields.Char(string="Title", required="True")
    state = fields.Selection([('pending', 'Pending'),
                               ('ready', 'Ready'),
                               ('approved', 'Approved'), ('declined', 'Declined')], default='pending', tracking=True)
    approver_id = fields.Many2one('res.users', string="Approver", tracking=True)
    organiser_id = fields.Many2one('res.users', string="Organiser", tracking=True)
    note = fields.Char(string="Note")
    related_entity_type = fields.Integer(string="Related Entity Type")
    related_entity_key = fields.Integer(string="Related Entity Key")
    entity_id = fields.Many2one('project.entity', string="Related Entity")
    days_waiting_approval = fields.Integer(string="Days Awaiting Approval", compute="_compute_days_waiting_approval")

    logged_date = fields.Datetime(string="Last Update", default=fields.Datetime.now())
    loaded_by_id = fields.Many2one('res.users', string="Last Updated By", default=lambda self: self.env.uid)
    name = fields.Char(string="Reference", required=True, copy=False,
                       readonly=True, default=lambda self: _('New'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'project.approval') or _('New')
        return super().create(vals_list)

    def write(self, vals):
        if 'logged_date' not in vals:
            self.logged_date = fields.Datetime.now()
        res = super().write(vals)
        return res

    def action_ready(self):
        """Move to Ready State"""
        self.state = 'ready'

    def action_approved(self):
        """Move to Ready State"""
        self.state = 'approved'

    def action_declined(self):
        """Move to Ready declined"""
        self.state = 'declined'

    @api.depends('logged_date')
    def _compute_days_waiting_approval(self):
        """Compute the overdue"""
        for rec in self:
            overdue_status = 0
            if rec.logged_date:
                delta = fields.Date.today() - rec.logged_date.date()
                rec.days_waiting_approval = delta.days
            else:
                rec.days_waiting_approval = 0
