from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _group_preparer_reviewer_approver(self):
        group = self.env.ref('base.group_user', raise_if_not_found=False)
        return [('groups_id', 'in', group.ids)] if group else []

    preparer_id = fields.Many2one('res.users', string="Preparer", config_parameter="oi_risk_workflow.preparer_id", domain=_group_preparer_reviewer_approver)
    reviewer_id = fields.Many2one('res.users', string="Reviewer", config_parameter="oi_risk_workflow.reviewer_id", domain=_group_preparer_reviewer_approver)
    approver_id = fields.Many2one('res.users', string="Approver", config_parameter="oi_risk_workflow.approver_id", domain=_group_preparer_reviewer_approver)
