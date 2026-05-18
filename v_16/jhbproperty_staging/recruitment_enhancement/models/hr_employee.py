from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def create_user(self):
        self.ensure_one()

        if self.user_id:
            raise ValidationError(_("This employee already has a linked user."))

        if not self.work_email:
            raise ValidationError(_("Please set a Work Email before creating a user."))

        existing_user = self.env['res.users'].search(
            [('login', '=', self.work_email)], limit=1
        )
        if existing_user:
            raise ValidationError(
                _("A user with email '%s' already exists.") % self.work_email
            )

        user = self.env['res.users'].with_context(
            no_reset_password=True,
        ).create({
            'name': self.name,
            'login': self.work_email,
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })

        self.env.flush_all()

        ghost_employee = self.env['hr.employee'].search([
            ('user_id', '=', user.id),
            ('id', '!=', self.id),
        ], limit=1)

        if ghost_employee:
            self.env.cr.execute(
                "UPDATE hr_employee SET user_id = NULL WHERE id = %s",
                (ghost_employee.id,)
            )
            ghost_employee.invalidate_recordset(['user_id'])

        self.env.cr.execute(
            "UPDATE hr_employee SET user_id = %s WHERE id = %s",
            (user.id, self.id)
        )
        self.invalidate_recordset(['user_id'])

        if ghost_employee and not ghost_employee.name:
            ghost_employee.unlink()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('User Created'),
                'message': _('User "%s" created and linked successfully.') % user.name,
                'type': 'success',
                'sticky': False,
            },
        }

    @api.model
    def create(self, vals):
        employee = super().create(vals)
        applicant_id = self.env.context.get('default_applicant_id')
        if applicant_id:
            applicant = self.env['hr.applicant'].browse(applicant_id)
            applicant.employee_id = employee.id
        return employee