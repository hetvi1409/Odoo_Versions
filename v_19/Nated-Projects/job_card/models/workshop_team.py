from odoo import fields, models

class WorkshopTeam(models.Model):
    _name = 'workshop.team'
    _description = 'Workshop Team'

    name = fields.Char('Team Name', help='name of the workshop team',
                       required=True)
