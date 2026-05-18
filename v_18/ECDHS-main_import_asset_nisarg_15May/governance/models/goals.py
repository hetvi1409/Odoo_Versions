from odoo import api, fields, models

class BusinessGoals(models.Model):
    _name = "business.goals"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Business goals"

    name = fields.Char(string='Title')
    ref = fields.Char(string='Goal ID', default='New')
    goal = fields.Html(string='Goal')
    strategy = fields.Many2one('strategic.planning', string='Strategy')
    objectives = fields.One2many('business.objectives', 'goal', string='Objectives')
    projects = fields.Many2many('project.project', string='Projects')


    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('goal.sequence')
        return super(BusinessGoals, self).create(vals)



