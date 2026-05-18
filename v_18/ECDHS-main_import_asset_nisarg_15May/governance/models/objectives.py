from odoo import api, fields, models

class BusinessObjectives(models.Model):
    _name = "business.objectives"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Business Objectives"

    ref = fields.Char(string='Objective ID', default='New')
    name = fields.Char(string='Title')
    start_date = fields.Date(string='Commence Date')
    end_date = fields.Date(string="End Date")
    goal = fields.Many2one('business.goals', string="Goals")
    objectives = fields.Html(string='Objectives')
    projects = fields.Many2many('project.project', string='Projects')

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('objective.sequence')
        return super(BusinessObjectives, self).create(vals)

