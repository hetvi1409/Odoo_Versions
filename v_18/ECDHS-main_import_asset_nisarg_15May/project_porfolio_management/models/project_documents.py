from odoo import api, fields, models, _


class ProjectDocuments(models.Model):
    _name ="project.documents"
    _description = "Project Documents"

    project_id = fields.Many2one('project.project', string="Project", required=True, domain=[('is_ppe', '=', True)])
    title = fields.Char(string="Title")
    type = fields.Selection([('business_case', 'Business Case'), ('project_charter', 'Project Charter'),
                             ('project_plan', 'Project Plan/ Schedule'),
                             ('specification', 'Specification'),
                             ('communication', 'Communication Plan')
                             ])
    files = fields.Binary(string="Document")

    logged_date = fields.Datetime(string="Last Update",
                                  default=fields.Datetime.now())
    loaded_by_id = fields.Many2one('res.users', string="Loaded By",
                                   default=lambda self: self.env.uid)
    state = fields.Selection([('working', 'Working'), ('final', 'Final'), ('approved', 'Approved')],
                             default="working")

    name = fields.Char(string="Reference", required=True, copy=False,
                       readonly=True, default=lambda self: _('New'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'project.documents') or _('New')
        return super().create(vals_list)

