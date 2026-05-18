from odoo import models, fields, api


class ActivityTag(models.Model):
    _name = 'oi_risk_management.activity_tag'
    _description = 'Activity Tags'

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name should be unique!'),
    ]

    name = fields.Char(required=True)

    activity_id = fields.Many2many('oi_risk_management.activity', required=True)
    risk_id = fields.Many2many('oi_risk_management.risk', required=True)

class ActivityCategory(models.Model):
    _name = 'oi_risk_management.activity_category'
    _description = 'Activity Category'

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name should be unique!'),
    ]

    name = fields.Char(required=True)

    activity_id = fields.One2many('oi_risk_management.activity', 'category_id', required=True)


class Activity(models.Model):
    _name = 'oi_risk_management.activity'
    _description = 'Activities'
    _inherit = ['approval.record', 'mail.thread', 'mail.activity.mixin']

    @api.model
    def _after_approval_states(self):
        return [('complete', 'Complete')]

    name = fields.Char(required=True)
    description = fields.Text()

    risks_count = fields.Integer(compute="_compute_risks_count", readonly=True, string="Risks Count", default=0,
                                 store=True)
    risk_ids = fields.One2many('oi_risk_management.risk', 'activity_id')

    tag_ids = fields.Many2many('oi_risk_management.activity_tag', 'activity_id')
    category_id = fields.Many2one('oi_risk_management.activity_category')
    department_id = fields.Many2one('hr.department')
    parent_department_id = fields.Many2one('hr.department', compute="_compute_parent_department_id")
    sequence = fields.Char(string="Risk Factor ID", copy=False, readonly=True)
    factor_state = fields.Selection([('draft', 'Draft'), ('prepared', 'Prepared'),
                                   ('reviewed', 'Reviewed'),
                                   ('approved', 'Approved'),('reverted','Reverted'),
                                   ('rejected', 'Rejected')],
                                  string="State", copy=False, default="draft", tracking=True)

    def action_risk_prepare(self):
        self.factor_state = 'prepared'

    def action_risk_reviewed(self):
        self.factor_state = 'reviewed'

    def action_risk_approved(self):
        self.factor_state = 'approved'

    def action_risk_rejected(self):
        self.factor_state = 'rejected'

    @api.depends('department_id')
    def _compute_parent_department_id(self):
        for record in self:
            record.parent_department_id = record.department_id.parent_id

    @api.depends('risk_ids')
    def _compute_risks_count(self):
        for record in self:
            record.risks_count = len(record.risk_ids)

    def action_view_risks(self):
        # action = self.env.ref('oi_risk_management.list_of_risks_action').read()[0]
        # action['domain'] = [('activity_id', '=', self.id)]
        # action['context'] = {'default_activity_id': self.id}
        # return action
        return {
            'type': 'ir.actions.act_window',
            'name': 'Risks',
            'res_model': 'oi_risk_management.risk',
            'view_mode': 'list,form,pivot,activity',
            'views': [(self.env.ref('oi_risk_management.risks_tree').id, 'list'), (self.env.ref('oi_risk_management.risk_form').id, 'form'), (False, 'pivot'),
                      (False, 'activity')],
            'domain': [('activity_id', '=', self.id)],
            'context': {'default_activity_id': self.id}
        }

    @api.model_create_multi
    def create(self, vals_list):
        """Create multiple records and assign sequence numbers."""
        for vals in vals_list:
            if not vals.get('sequence'):
                vals['sequence'] = self.env['ir.sequence'].next_by_code('risk.activity')
        res = super(Activity, self).create(vals_list)
        return res