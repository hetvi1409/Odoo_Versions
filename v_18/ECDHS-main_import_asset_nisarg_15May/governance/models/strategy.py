from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StrategicPlanning(models.Model):
    _name = "strategic.planning"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Strategic Planning"

    name = fields.Char(string='Title', required=True)
    ref = fields.Char(string='Strategy ID', default='New')
    strategy = fields.Html(string='Strategy Description')
    goal = fields.One2many('business.goals', 'strategy', string='Goal')
    objectives_count = fields.Integer(string="Objectives Count", compute='_compute_objectives_count')
    objectives_ids = fields.One2many('business.objectives', 'goal', string='Objectives')




    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('strategy.sequence')
        return super(StrategicPlanning, self).create(vals)

    @api.depends('objectives_ids')
    def _compute_objectives_count(self):

        for rec in self:
            rec.objectives_count = 0
            for goalrec in rec.goal:
                rec.objectives_count += self.env['business.objectives'].search_count([('goal','=', goalrec.id)])

    def action_view_objectives(self):
        count = 0
        filters = ""
        for rec in self.goal:
            count += 1
            if count > 1:
                text = ", ('goal', '=', " + str(rec.id) + " )"
            else:
                text = " ('goal', '=', " + str(rec.id) + " )"
            filters += text

        hor = ""
        for ctr in range(1, count):
            hor += "'|', "

        args = "[" + hor + filters + "]"

        if self.goal:
            return {
                'name': _('Objectives'),
                'res_model': 'business.objectives',
                'view_mode': 'list',
                'context': {},
                'domain': args,
                'target': 'current',
                'type': 'ir.actions.act_window',
            }
        else:
            ValidationError(_("No Objectives Found..!!!"))





