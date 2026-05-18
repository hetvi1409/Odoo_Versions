from odoo import api, fields, models, _

class ActionLog(models.Model):
    _name = "action.log"
    _description = "Action Log"

    name = fields.Char(string='Action', tracking=True)
    color = fields.Integer(string="Color")
    level = fields.Selection([('eliminate', 'Eliminate'), ('substitute', 'Substitute'), ('engineering', 'Engineering'),
                                   ('administration', 'Administration'), ('ppe', 'PPE')], string="Level Of Prevention",
                                  tracking=True, required=True)
    employee = fields.Many2one('hr.employee', string='Employee Responsible', tracking=True)
    target_date = fields.Date(string='Target Date')
    close_date = fields.Date(string='Close Out Date')


    # @api.returns('self', lambda value: value.id)
    # def copy(self, default=None):
    #     if default is None:
    #         default = {}
    #     if not default.get('name'):
    #         default['name'] =_("%s (copy)", self.name)
    #
    #         default['sequence'] = 10
    #     return super(ActionLog, self).copy(default)
    #
    # _sql_constraints = [
    #     ('unique_tag_name', 'unique (name)', 'Name must be unique.'),
    #     ('check_sequence', 'check (sequence > 0)', 'Sequence must be non zero positive number.')
    # ]