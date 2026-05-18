from odoo import api, fields, models, _


class JobCard(models.Model):
    _name = 'job.card'
    _description = 'Job Card'
    """Model for Job Card"""

    name = fields.Char(string="Name", required=True)
    sequence = fields.Char(string="Sequence", default='New')
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string='End Date')
    deadline = fields.Date(string="Deadline")
    user_ids = fields.Many2many('res.users', string='Assigned To')
    maintenance_id = fields.Many2one('maintenance.request')
    project_id = fields.Many2one('project.task')
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'),
                              ('approve', 'Approved')], default='draft')

    @api.model
    def create(self, values):
        """Method for generating consumer number for the contacts"""
        if values.get('sequence', _('New')) == _('New'):
            values['sequence'] = self.env['ir.sequence'].next_by_code(
                'job.card.name') or _('New')
        res = super(JobCard, self).create(values)
        return res

    def action_submit(self):
        """Method for submit the job card"""
        self.state = 'submitted'
    def action_approve(self):
        """Method for submit the job card"""
        self.state = 'approve'