from odoo import api, fields, models, _


class ScopeChanges(models.Model):
    _name = 'scope.changes'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Scope"

    request_date = fields.Date(string='Request Date', default=fields.Date.today())
    description = fields.Html(string="Description")
    reason = fields.Html(string="Reason for Change")
    impact = fields.Html(string="Impact On Scope")
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, readonly=True,
                                  default=lambda
                                      self: self.env.company.currency_id.id)
    impact_on_cost = fields.Monetary(string='Impact on Cost')
    impact_on_time = fields.Integer(string='Impact on time(Days)')
    approval_date = fields.Date(string="Approval Date")
    approval_status = fields.Selection([('draft','Draft'),
                                        ('submitted','Submitted'),
                                        ('approved','Approved'),
                                        ('rejected','Rejected'),
                                        ],
                                       default="draft",
                                       string='Approval Status')
    project_id = fields.Many2one('project.project', string="Project",
                                 required=True, domain=[('is_ppe', '=', True)])
    leaded_by_id = fields.Many2one("res.users", string="Loaded By")
    requested_by_ids = fields.Many2many("res.users", string="Requested By")
    name = fields.Char(string="Reference", required=True, copy=False,
                       readonly=True, default=lambda self: _('New'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'project.scope') or _('New')
        return super().create(vals_list)

    def action_approve(self):
        self.approval_status = "approved"
        self.approval_date = fields.Date.today()

    def action_submitted(self):
        self.approval_status = "submitted"

    def action_rejected(self):
        self.approval_status = "rejected"
