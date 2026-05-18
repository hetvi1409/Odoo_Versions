# -*- coding: utf-8 -*-
from odoo import api, fields, models

class BusinessChallenges(models.Model):
    _name = "business.challenges"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Business.Challenges"

    name = fields.Char(string='Challenge ID', default='New', tracking=True)
    challenge = fields.Text(string='Challenges', tracking=True)
    impact = fields.Text(string='Impact')
    cause = fields.Text(string='Cause', tracking=True)
    solution = fields.Text(string='Solution', tracking=True)
    owner = fields.Many2one('res.users', string='Owner', tracking=True)
    tag_ids = fields.Many2many('challenges.tag', string="Tags")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('challenge.sequence')
        return super(BusinessChallenges, self).create(vals)


