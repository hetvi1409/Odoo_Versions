from werkzeug import urls

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AuditStrategy(models.Model):
    """Understand The Entity And It's Environment"""
    _name = 'audit.strategy'
    _description = "Audit Strategy"
    _rec_name = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([
        ('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'),
    ], 'State', default='preparer', tracking=True)
    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Audit Strategy")
    name = fields.Char(string="Name", required=True,
                               help="Name")
    requirements = fields.Char(string="Requirements", required=True,
                               help="Requirements")
    record_work_done = fields.Char(string="Work done", required=True,
                                   help="Record of work done")
    conclusion = fields.Char(string="Conclusion", required=True,
                             help="Conclusion")
    user_id = fields.Many2one('res.users', tracking=True,
                              string="Responsible User")
    feedback = fields.Char(string="Feedback", tracking=True)
    team_id = fields.Many2one('hr.department', string="Team", required=True)
    audit_strategy_tracking_ids = fields.One2many('audit.strategy.tracking', 'audit_strategy_tracking_id', string='Tracking')
    user_ids = fields.Many2many('res.users', string="Users",
                                compute="_compute_user_ids")
    user_preparer_ids = fields.Many2one('res.users',
                                         string="Preparer", tracking=True,
                                         required=True,)
    user_reviewer_1_ids = fields.Many2one('res.users',
                                           string="First Reviewer",
                                           tracking=True, required=True,)
    user_reviewer_2_ids = fields.Many2one('res.users',
                                           string="Second Reviewer ",
                                           tracking=True, required=True,)
    user_approver_ids = fields.Many2one('res.users',
                                         string="Approver", tracking=True,
                                         required=True,)
    is_current_user_approver = fields.Boolean(compute='_compute_is_reviewer',
                                              store=False)
    is_current_user_reviewer = fields.Boolean(compute='_compute_is_reviewer', store=False)
    is_current_user_reviewer2 = fields.Boolean(compute='_compute_is_reviewer', store=False)

    @api.depends('user_approver_ids', 'user_reviewer_1_ids', 'user_reviewer_2_ids')
    def _compute_is_reviewer(self):
        current_user = self.env.uid
        for rec in self:
            rec.is_current_user_approver = rec.user_approver_ids.id == current_user
            rec.is_current_user_reviewer = rec.user_reviewer_1_ids.id == current_user
            rec.is_current_user_reviewer2 = rec.user_reviewer_2_ids.id == current_user


    @api.depends('team_id')
    def _compute_user_ids(self):
        """Compute User IDs for adding domains"""
        for rec in self:
            if rec.team_id:
                rec.user_ids = rec.team_id.employee_ids.mapped('user_id')
            else:
                rec.user_ids = False

    def action_review(self):
        """Method for review"""
        self.state = 'first_reviewer'
        self.audit_strategy_tracking_ids.create({
            'audit_strategy_tracking_id': self.id,
            'comment': "Moved to First Review",
            'new_stage_id': self.state,
            'user_id': self.env.user.id,
        })
        mail_template = self.env.ref('internal_audit_management.email_template_audit_strategy_review')
        recipient_ids = self.user_reviewer_1_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)

    def action_2nd_review(self):
        """Second Review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_audit_strategy_review')
        recipient_ids = self.user_reviewer_2_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        previous_state = self.state
        self.state = 'second_reviewer'
        self.audit_strategy_tracking_ids.create({
            'audit_strategy_tracking_id': self.id,
            'comment': "Moved to First Review",
            'new_stage_id': self.state,
            'previous_stage_id': previous_state,
            'user_id': self.env.user.id,
        })

    def action_approve(self):
        """Method for approve"""
        if not self.attachment_ids:
            raise UserError(_('Please attach the documents'))
        previous_state = self.state
        self.state = 'approved'
        self.audit_strategy_tracking_ids.create({
            'audit_strategy_tracking_id': self.id,
            'comment': "Moved to Approved",
            'new_stage_id': self.state,
            'previous_stage_id': previous_state,
            'user_id': self.env.user.id,
        })
        mail_template = self.env.ref('internal_audit_management.email_template_audit_strategy_approve')
        recipient_ids = self.user_approver_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)

    def action_reject(self):
        """Action refuse the request"""
        previous_state = self.state
        self.state = 'rejected'
        self.audit_strategy_tracking_ids.create({
            'audit_strategy_tracking_id': self.id,
            'comment': "Rejected",
            'new_stage_id': self.state,
            'previous_stage_id': previous_state,
            'user_id': self.env.user.id,
        })
        mail_template = self.env.ref(
            'internal_audit_management.email_template_audit_strategy_refuse')
        recipient_ids = self.env.user
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)

    def action_revert(self):
        """Action refuse the request"""
        previous_state = self.state
        self.state = 'reverted'
        self.audit_strategy_tracking_ids.create({
            'audit_strategy_tracking_id': self.id,
            'comment': "Reverted",
            'new_stage_id': self.state,
            'previous_stage_id': previous_state,
            'user_id': self.env.user.id,
        })
        return {
            'name': 'Revert Procedure',
            'type': 'ir.actions.act_window',
            'res_model': 'audit.strategy.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_audit_strategy_id': self.id,
            },
        }

    def action_update(self):
        """Action refuse the request"""
        previous_state = self.state
        self.state = 'preparer'
        self.audit_strategy_tracking_ids.create({
            'audit_strategy_tracking_id': self.id,
            'comment': "Updated",
            'new_stage_id': self.state,
            'previous_stage_id': previous_state,
            'user_id': self.env.user.id,
        })
        mail_template = self.env.ref(
            'internal_audit_management.email_template_audit_strategy_new')
        recipient_ids = self.user_preparer_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)

    def get_list_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url, 'web#id=%s&model=audit.strategy&view_type=list' % self.id)
        return Urls
