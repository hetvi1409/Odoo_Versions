from odoo import models, fields


class MemoTemplate(models.Model):
    _inherit = 'memo.template'

    type = fields.Selection(
        selection_add=[("internal_audit", "Internal Audit")],
        required=True,
        ondelete={"internal_audit": "cascade"},
    )
