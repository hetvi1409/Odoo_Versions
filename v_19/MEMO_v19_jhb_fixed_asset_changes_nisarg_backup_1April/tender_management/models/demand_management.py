from odoo import api, models, fields, _


class DemandManagement(models.Model):
    """
    Model representing a class of procurement entity.
    """
    _name = 'demand.management'
    _description = 'Demand Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sequence_number'

    sequence_number = fields.Char(string='Sequence Number', readonly=True, copy=False, default=lambda self: _('New'))
    name = fields.Char(string='Demand Name',
                       help='The name of the demand')
    request_date = fields.Date(string='Request Date', default=fields.Date.today)
    # department_id = fields.Many2one('res.department', string='Department')
    description = fields.Text(string='Description')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True)

    @api.model_create_multi
    def create(self, vals_list):
        """ Create a sequence for the demand.management model """
        for vals in vals_list:
            if vals.get('sequence_number', _('New')) == _('New'):
                vals['sequence_number'] = self.env[
                    'ir.sequence'].next_by_code(
                    'demand.management')
        return super().create(vals_list)

    def action_submit(self):
        self.write({'status': 'submitted'})

