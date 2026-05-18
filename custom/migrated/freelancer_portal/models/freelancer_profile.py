# -*- coding: utf-8 -*-

from odoo import fields, models, api


class FreelancerProfile(models.Model):
    _name = 'freelancer.profile'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    is_freelancer = fields.Boolean(string='Is a Freelancer', default=False)
    skill_ids = fields.Many2many('freelancer.skill', string='Skills')
    experience_years = fields.Integer(string='Years of Experience')
    portfolio_url = fields.Char(string='Portfolio URL')
    state = fields.Selection([('draft', 'Draft'), ('verified', 'Verified'), ('banned', 'Banned')], string='Status', default='draft')
    proposal_count = fields.Integer(string='Proposal Count')


    @api.constrains('experience_years')
    def _check_experience_years(self):
        for record in self:
            if record.experience_years < 0:
                raise ValueError("Years of experience cannot be negative.")
            if record.experience_years > 50:
                raise ValueError("Years of experience cannot exceed 50.")