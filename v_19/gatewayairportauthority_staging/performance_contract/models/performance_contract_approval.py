# -*- coding: utf-8 -*-
from odoo import models, fields

class PerformanceContractApproval(models.Model):
    _name = "performance.contract.approval"
    _description = "Performance Contract Approval"

    contract_id = fields.Many2one("performance.contract", ondelete="cascade")
    user_id = fields.Many2one("res.users", required=True)
    approved = fields.Boolean(default=False)
    approval_date = fields.Datetime()

class PerformanceContractApprovalLine(models.Model):
    _name = "performance.contract.approval.line"
    _description = "Performance Contract Approval Line"

    contract_id = fields.Many2one("performance.contract", ondelete="cascade")
    user_id = fields.Many2one("res.users", required=True)
    approved = fields.Boolean(default=False)
    approval_date = fields.Datetime()
    status = fields.Selection([('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                              default='pending', string="Status")
