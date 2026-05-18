from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    deleted_message_log_ids = fields.One2many(
        "mail.message.delete.log",
        "deleted_by",
        string="Deleted Note Audit Logs",
        readonly=True,
    )
