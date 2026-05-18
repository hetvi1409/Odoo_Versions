# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, _lt
import ast


class Partner(models.Model):
    _inherit = 'res.partner'

    is_law_client = fields.Boolean(default=False)
    count_trust_account = fields.Integer(compute="_compute_count")
    count_matter = fields.Integer(compute="_compute_count")
    count_case = fields.Integer(compute="_compute_count")

    def _compute_count(self):
        for rec in self:
            rec.count_trust_account = len(self.env['trust.account'].search([('partner_id', '=', rec.id)]))
            rec.count_matter = len(
                self.env['project.project'].search([('partner_id', '=', rec.id), ('is_matter', '=', True)]))
            rec.count_case = len(
                self.env['project.project'].search([('partner_id', '=', rec.id), ('is_case', '=', True)]))

    def open_trust_account_view(self):
        action = self.env.ref('law_firm_bits.law_trust_account_act_action').sudo().read()[0]
        if action.get('domain'):
            domain = ast.literal_eval(action['domain'])
            domain.append(('partner_id', '=', self.id))
            action['domain'] = domain
        if action.get('context'):
            context = ast.literal_eval(action['context'])
            context.update({'default_partner_id': self.id})
            action['context'] = context
        return action

    def open_case_view(self):
        action = self.env.ref('law_firm_bits.action_view_all_cases').sudo().read()[0]
        if action.get('domain'):
            domain = ast.literal_eval(action['domain'])
            domain.append(('partner_id', '=', self.id))
            action['domain'] = domain
        if action.get('context'):
            context = ast.literal_eval(action['context'])
            context.update({'default_partner_id': self.id})
            action['context'] = context
        return action

    def open_matter_view(self):
        action = self.env.ref('law_firm_bits.action_view_all_matters').sudo().read()[0]
        if action.get('domain'):
            domain = ast.literal_eval(action['domain'])
            domain.append(('partner_id', '=', self.id))
            action['domain'] = domain
        if action.get('context'):
            context = ast.literal_eval(action['context'])
            context.update({'default_partner_id': self.id})
            action['context'] = context
        return action
