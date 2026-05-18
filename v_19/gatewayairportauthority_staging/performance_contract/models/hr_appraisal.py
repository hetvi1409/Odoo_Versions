# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError

class HrAppraisal(models.Model):
    _inherit = "hr.appraisal"

    contract_id = fields.Many2one("performance.contract")

    def action_create_from_contract(self):
        for rec in self:
            if not rec.contract_id:
                raise UserError("No performance contract linked.")
