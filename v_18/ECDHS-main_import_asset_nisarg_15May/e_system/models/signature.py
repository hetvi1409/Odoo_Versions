from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SignItemRole(models.Model):
    _inherit = "sign.item.role"

    user_id = fields.Many2one(
        'res.users',
        string='Linked User',
        help="Assign this role to a specific user.",
        tracking=True
    )

    # Auto-populate name from linked user
    name = fields.Char(required=True, translate=True, readonly=False)

    @api.onchange('user_id')
    def _onchange_user_id(self):
        """Auto-fill role name from user."""
        if self.user_id:
            self.name = self.user_id.name

    @api.constrains('user_id')
    def _check_unique_user(self):
        """Prevent multiple roles per user."""
        for rec in self:
            if rec.user_id and self.sudo().search_count([
                ('user_id', '=', rec.user_id.id),
                ('id', '!=', rec.id)
            ]):
                raise ValidationError(_("This user already has a Signature Role."))

    @api.model
    def create(self, vals):
        """Force name to match linked user on create."""
        if vals.get('user_id') and not vals.get('name'):
            user = self.env['res.users'].sudo().browse(vals['user_id'])
            vals['name'] = user.name
        return super().create(vals)

    def write(self, vals):
        """Keep name synced when user_id changes."""
        res = super().write(vals)
        for rec in self:
            if 'user_id' in vals and rec.user_id:
                rec.name = rec.user_id.name
        return res


class SignItem(models.Model):
    _inherit = "sign.item"

    responsible_id = fields.Many2one("sign.item.role", string="Responsible", ondelete="restrict")