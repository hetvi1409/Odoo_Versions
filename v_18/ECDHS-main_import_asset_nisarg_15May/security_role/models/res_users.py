# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    access_role_id = fields.Many2one(
        'user.role',
        string='Security Role',
        help='Select the role of the user',
        domain="[('id', 'in', available_role_ids)]"
    )

    available_role_ids = fields.Many2many(
        'user.role',
        compute='_compute_available_roles'
    )
    is_debug_mode = fields.Boolean(store=True, readonly=True)

    @api.depends('user_ids')
    def _compute_available_roles(self):
        """Compute available roles for the current user."""
        for user in self:
            user.available_role_ids = self.env['user.role'].search([('user_ids', 'in', user.id)])

    @api.model_create_multi
    def create(self, vals_list):
        # Handle creation of new users
        users = super(ResUsers, self).create(vals_list)
        for user in users:
            if user.access_role_id:
                user.write({
                    'groups_id': [Command.set(user.access_role_id.groups_id.ids)]
                })
        return users

    def write(self, vals):
        """Override write to /** Prevent users with disable_debug from enabling debug mode */
handle role assignment and removal"""
        groups_to_remove = None
        # Handle role removal
        if 'access_role_id' in vals and not vals['access_role_id']:
            if self.access_role_id:
                groups_to_remove = self.access_role_id.groups_id
        result = super(ResUsers, self).write(vals)
        if 'access_role_id' in vals:
            if vals['access_role_id']:
                new_role = self.env['user.role'].browse(vals['access_role_id'])
                self.write({
                    'groups_id': [Command.set(new_role.groups_id.ids)]
                })
            elif groups_to_remove:
                groups_list = groups_to_remove.ids
                if 1 in groups_list:
                    groups_list.remove(1)
                self.write({
                    'groups_id': [Command.unlink(gid) for gid in groups_list]
                })
        return result

    @api.onchange('access_role_id')
    def onchange_access_role_id(self):
        if not self._origin.id and self.access_role_id:  # Record is new (not saved)
            self.access_role_id = False
            return {
                'warning': {
                    'title': _("Warning"),
                    'message': _("Please save the user before assigning an Access Role."),
                }
            }

        if not self.user_id:
            if self._origin.access_role_id:
                self._origin.access_role_id.write(
                    {'user_ids': [(fields.Command.unlink(self._origin.id))]})
            # Assign user to the new role
            if self.access_role_id:
                self.access_role_id.write(
                    {'user_ids': [(fields.Command.link(self._origin.id))]})
        else:
            # Remove user from the previous role
            if self._origin.access_role_id:
                self._origin.access_role_id.write(
                    {'user_ids': [(fields.Command.unlink(self.user_id.id))]})
            # Assign user to the new role
            if self.access_role_id:
                self.access_role_id.write(
                    {'user_ids': [(fields.Command.link(self.user_id.id))]})

