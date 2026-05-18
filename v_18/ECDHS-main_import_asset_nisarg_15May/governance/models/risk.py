# -*- coding: utf-8 -*-
from odoo import api, fields, models

class BusinessRisk(models.Model):
    _name = "business.risk"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Business Risk"

    name = fields.Char(string='Risk ID', default='New', tracking=True)
    summary = fields.Char(string='Title', tracking=True)
    description = fields.Text(string='Risk Description')
    owner = fields.Many2one('res.users', string='Owner', tracking=True)
    probability = fields.Selection([('low', 'Low'), ('low-medium', 'Low Medium'), ('medium', 'Medium'),
                                    ('medium-high', 'Medium High'), ('high', 'High')], string="Probability",
                                    tracking=True, default='low', required=True)
    impact = fields.Selection([('low', 'Low'), ('low-medium', 'Low Medium'), ('medium', 'Medium'),
                                    ('medium-high', 'Medium High'), ('high', 'High')], string="Impact",
                                    tracking=True, default='low', required=True)
    severity = fields.Char(string="Risk Severity", compute='_compute_severity')

    action = fields.Text(string='Mitigation Actions', tracking=True)
    status = fields.Selection([ ('undetermined', 'Undetermined'),
                                ('mitigated', 'Mitigated'), 
                                ('accepted', 'Accepted'), 
                                ('transferred', 'Transferred')],
                                 string="Risk Status", default="undetermined", required=True, tracking=True)
    last_date = fields.Date(string='Previous Review')
    next_date = fields.Date(string='Next Review')
    solution = fields.Text(string='Solution', tracking=True)

    category = fields.Many2many('risk.category', string="Category Tag")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('risk.sequence')
        return super(BusinessRisk, self).create(vals)

    @api.depends('impact', 'probability')
    def _compute_severity(self):
        severity = {
            2: "Low",
            3: "Low",
            4: "Low",
            5: "Low-medium",
            6: "Medium",
            7: "Medium-high",
            8: "High",
            9: "High",
            10: "High",
        }
        vals = {
            "low": 1,
            "low-medium": 2,
            "medium": 3,
            "medium-high": 4,
            "high": 5,
        }
        for rec in self:
            # look up numeric values
            impact = vals[rec.impact]
            prob = vals[rec.probability]

            # calculate the severity
            sevval = impact + prob

            # increase severity under these conditions
            if impact == 3 and prob == 1:
                sevval += 1
            elif impact == 3 and prob == 5:
                sevval -= 1

            sev = severity[sevval]
            rec.severity = sev
        return


