# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields,api

class PerformanceContractApprovalTeam(models.Model):
    _name = "approval.team"
    _description = "Approval Team"
    _rec_name = "name"

    sequence = fields.Integer("Sequence", default=1)
    name = fields.Char("Team Name", required=True)
    line_ids = fields.One2many("approval.team.line", "team_id", string="Approval Lines")
    model = fields.Char(index=True)
    model_id = fields.Many2one("ir.model", string="Model", compute='_compute_model_id', inverse='_inverse_compute_model_id')


    @api.depends('model')
    def _compute_model_id(self):
        for record in self:
            record.model_id = self.env['ir.model']._get(record.model)

    def _inverse_compute_model_id(self):
        for record in self:
            record.model = record.model_id.model


class PerformanceContractApprovalTeamLine(models.Model):
    _name = "approval.team.line"
    _description = "Approval Team Line"
    _rec_name = "user_id"

    contract_id = fields.Many2one("performance.contract", ondelete="cascade")
    sequence = fields.Integer("Sequence",default=1)
    user_id = fields.Many2one("res.users")
    team_id = fields.Many2one("approval.team", string="Approval Team")
    status = fields.Selection([('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                              default='pending', string="Status")
    approved = fields.Boolean(default=False)
    approval_date = fields.Datetime(string="Approval Date")
    reject_reason = fields.Text(string="Reject Reason")
