from odoo import models, api, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.constrains('group_ids')
    def _check_studio_group(self):
        studio_group = self.env.ref("e_system.group_studio_access", raise_if_not_found=False)
        admin_group = self.env.ref("base.group_system", raise_if_not_found=False)

        # if groups are not yet loaded, skip the check
        if not studio_group or not admin_group:
            return
        for user in self:
            if studio_group in user.group_ids and admin_group not in user.group_ids:
                raise ValidationError(
                    _("Please add user %s to 'Administrator: Settings' before assigning 'Studio Access'.") % user.name
                )

    # ✅ Optimized: use create_multi for efficiency
    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        Role = self.env['sign.item.role'].sudo()

        # Gather all user IDs and names at once for batch creation
        new_roles = []
        for user in users:
            # Skip if role already exists
            if Role.search_count([('user_id', '=', user.id)]):
                continue
            # Check if a role already exists with same name
            existing_role = Role.search([('name', '=', user.name)], limit=1)
            if existing_role:
                # Link user to that role
                existing_role.write({'user_id': user.id})
            else:
                # Prepare new role record
                new_roles.append({
                    'user_id': user.id,
                    'name': user.name,
                })
        if new_roles:
            Role.create(new_roles)
        return users

    @api.model
    def action_update_linked_user(self):
        users = self.env['res.users'].sudo().search([('active', 'in', [True, False])])

        Role = self.env['sign.item.role'].sudo()

        for user in users:
            # 1) Find existing role linked to this user
            role_for_user = Role.search([('user_id', '=', user.id)], limit=1)

            if role_for_user:
                # Sync the name if changed; this will not violate uniqueness,
                # as we're updating the same record that already holds that name
                if role_for_user.name != user.name:
                    # Before writing, check if some other role already uses this name to avoid UniqueViolation
                    clash = Role.search([
                        ('name', '=', user.name),
                        ('id', '!=', role_for_user.id)
                    ], limit=1)
                    if clash:
                        # If a different role already has that name, do NOT rename to avoid constraint errors.
                        # Decide your policy: either skip, or link this user to that role and remove the old one.
                        # Here we link the user to the existing name-holder and remove the duplicate role.
                        clash.sudo().write({'user_id': user.id})
                        role_for_user.sudo().unlink()
                    else:
                        role_for_user.sudo().write({'name': user.name})
                continue

            # 2) No role yet for this user. See if a role already exists with this name
            existing_by_name = Role.search([('name', '=', user.name)], limit=1)
            if existing_by_name:
                # Reuse and link to the user
                existing_by_name.write({'user_id': user.id})
            else:
                # 3) Create a fresh role
                Role.create({
                    'user_id': user.id,
                    'name': user.name,  # safe: no other role uses this name
                })
