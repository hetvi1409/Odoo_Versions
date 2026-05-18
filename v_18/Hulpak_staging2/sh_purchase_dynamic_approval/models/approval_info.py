from odoo import api, fields, tools, models, _


class ApprovalInfo(models.Model):
    _inherit = 'sh.approval.info'
    _description = "Approval Information"

    purchase_order_id = fields.Many2one('purchase.order')
