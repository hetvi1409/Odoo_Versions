from odoo import models, api, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.constrains('groups_id')
    def _check_studio_group(self):
        studio_group = self.env.ref("e_system.group_studio_access", raise_if_not_found=False)
        admin_group = self.env.ref("base.group_system", raise_if_not_found=False)

        # if groups are not yet loaded, skip the check
        if not studio_group or not admin_group:
            return
        for user in self:
            if studio_group in user.groups_id and admin_group not in user.groups_id:
                raise ValidationError(
                    _("Please add user %s to 'Administrator: Settings' before assigning 'Studio Access'.") % user.name
                )

class HrDepartment(models.Model):
    _inherit = "hr.department"

    def name_get(self):
        """Show hierarchical name only if context key 'hierarchical_naming' is True."""
        result = []
        hierarchical = self.env.context.get('hierarchical_naming', True)
        hierarchical = False
        for department in self:
            if hierarchical and department.parent_id:
                department.complete_name = '%s / %s' % (department.parent_id.complete_name, department.name)
                name = department.complete_name
            else:
                department.complete_name = department.name
                name = department.name
            result.append((department.id, name))
        return result

    @api.depends('name', 'parent_id.complete_name')
    @api.depends_context('hierarchical_naming')
    def _compute_complete_name(self):
        for department in self:
            if department.parent_id and self.env.context.get('hierarchical_naming', True):
                department.complete_name = '%s / %s' % (department.parent_id.complete_name, department.name)
            else:
                department.complete_name = department.name