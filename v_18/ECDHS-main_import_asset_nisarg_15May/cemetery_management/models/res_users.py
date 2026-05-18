from odoo import api, fields, models, Command, _
from odoo.exceptions import UserError


class ResUsers(models.Model):
    """Add a field to the user"""
    _inherit = 'res.users'

    undertaker = fields.Boolean(string="Undertaker")
    under_taker_invoice_id = fields.Many2one('account.move',
                                             string="Undertaker Invoice")
    was_undertaker = fields.Boolean(string="Was Undertaker", compute="_compute_undertaker")


    @api.model
    def create(self, vals):
        """Create the undertaker from the users"""
        res = super(ResUsers, self).create(vals)
        undertaker = self.env.ref('cemetery_management.group_undertaken')
        res.write({"groups_id": [Command.link(undertaker.id)]})
        self.env['undertaker.undertaker'].sudo().create({
            'full_name': res.sudo().name,
            'user_id': res.sudo().id,
        })
        return res

    @api.depends('groups_id')
    def _compute_undertaker(self):
        """Compute the values to the undertaker field"""
        was_undertaker = False
        for rec in self:
            if self.env.ref('cemetery_management.group_undertaken').id in rec.groups_id.ids:
                was_undertaker = True
            rec.was_undertaker = was_undertaker

    def action_create_undertaker_invoice(self):
        """Create the Invoice for undertaken"""
        invoice = self.env["account.move"].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'ref': 'undertaker amount',
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [
                Command.create({
                    'product_id': self.env.ref('cemetery_management.product_product_undertaken').id,
                    'quantity': 1.0,
                }),
            ],
        })
        self.under_taker_invoice_id = invoice.id
        return {
            'name': _('Invoice'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': invoice._name,
            'target': 'current',
            'res_id': invoice.id
        }

    def action_mark_as_undertaker(self):
        """Make the user as undertaker"""
        if not self.under_taker_invoice_id:
            raise UserError(_('Invoice Is not created'))
        if self.under_taker_invoice_id.payment_state == 'paid':
            return {
                'name': _('Undertaker'),
                'type': 'ir.actions.act_window',
                'res_model': 'undertaker.user',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_user_id': self.id,
                    'default_full_name': self.login
                }
            }
        else:
            raise UserError(_("Payment Is not Completed"))


class UndertakerUser(models.TransientModel):
    """Undertaker User"""
    _name = 'undertaker.user'
    _description = "Undertaker User"

    user_id = fields.Many2one('res.users', string="User")
    full_name = fields.Char(string="Full Name", required=True)
    date_of_birth = fields.Date(string="Date Of Birth", required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender', required=True)

    def action_submit(self):
        """Submit the Undertaker"""
        self.env.ref('cemetery_management.group_undertaken').write(
            {'users': [Command.link(self.user_id.id)]})
        self.env['undertaker.undertaker'].create({
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth,
            'gender': self.gender,
            'user_id': self.user_id.id
        })
