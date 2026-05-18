from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
from odoo.tools import pdf

class MemoTemplate(models.Model):
    _name = 'memo.template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Memo Template'

    name = fields.Char(required=True)
    purpose_body = fields.Html("Purpose")
    background_body = fields.Html("Background")
    motivation_body = fields.Html("Motivation")
    project_status = fields.Html("Project Status")
    submission_type = fields.Selection([
        ('general', 'General'),
        ('memo', 'Memo'),
        ('circular', 'Circular'),
        ('procurement', 'Procurement'),
    ], string="Submission Type",default='memo')
    type = fields.Selection([
        ('hr', 'HR'),
        ('finance', 'Finance'),
    ], string="Template Type", default='hr')
    privacy = fields.Selection(
        [('public', 'Public'),
         ('private', 'Private')], 'Privacy',default='private',
        help="People to whom this template will be visible.")
    tagged_user_ids = fields.Many2many(
        'res.users',
        'memo_template_tagged_users_rel',
        'template_id',
        'user_id',
        string='Tagged Users',
        help="Users allowed to access this template if it is public."
    )

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        current_user = self.env.user

        # Admin access
        if current_user.id in [1, 2]:
            return super()._search(domain, offset=offset, limit=limit, order=order)

        # Build list of user IDs who have memo access
        tem_access_users = set()
        memo_ids = self.env['memo.memo'].sudo().search([('template_id', '!=', False)])

        for memo in memo_ids:
            if memo.requester_id:
                tem_access_users.add(memo.requester_id.id)
            if memo.approver_id:
                tem_access_users.add(memo.approver_id.id)
            if memo.quality_assurance_ids:
                tem_access_users.update(memo.quality_assurance_ids.mapped('user_id.id'))
            if memo.recommender_ids:
                tem_access_users.update(memo.recommender_ids.mapped('user_id.id'))
            if memo.acknowledged_ids:
                tem_access_users.update(memo.acknowledged_ids.mapped('user_id.id'))

        # Check if current user is among them
        is_related_to_memo = current_user.id in tem_access_users

        # Build final domain
        if is_related_to_memo:
            # Allow full access to all matching templates (private and public)
            domain = ['|',
                      ('privacy', '=', 'private'),
                      ('privacy', '=', 'public')]
        else:
            domain = [
                '|',
                '&', ('privacy', '=', 'private'), ('create_uid', '=', current_user.id),
                '&', ('privacy', '=', 'public'),
                '|',
                ('tagged_user_ids', 'in', [current_user.id]),
                ('create_uid', '=', current_user.id)
            ]

        return super()._search(domain, offset=offset, limit=limit, order=order)
