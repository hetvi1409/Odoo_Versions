from odoo import fields, models, api, _


class SignSendRequest(models.TransientModel):
    _inherit = "sign.send.request"

    current_user_id = fields.Many2one('res.users', string='Current User', default=lambda self: self.env.user,
                                      store=True)
