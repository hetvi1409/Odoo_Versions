from odoo import api, fields, models, _


class GovernanceRequirements(models.Model):
    _name = 'governance.requirements'

    phase_required_for = fields.Selection([('pre-initiating', 'Pre-Initiating'),
                                           ('initiating', 'Initiating'),
                                           ('planning', 'Planning'),
                                           ('executing', 'Executing'),
                                           ('closing', 'Closing')],
                                          string='Phase Required for')
    required_document_id = fields.Many2one('document.required', string="Required Document")
    status = fields.Selection([('required','Required'),('not_required','Not Required')],string='Status')
    comment = fields.Html(string='Comment')
    sort_order = fields.Integer(string='Sort Order')
    rag = fields.Selection([
        ('normal', 'A'),
        ('done', 'G'),
        ('blocked', 'R')],string='Governance RAG')
    is_document = fields.Selection([('yes','Yes'),('no','No')],string='Is document')
    project_id = fields.Many2one('project.project', string="Project", required=True, domain=[('is_ppe', '=', True)])
    name = fields.Char(string="Reference", required=True, copy=False,
                       readonly=True, default=lambda self: _('New'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'project.governance') or _('New')
        return super().create(vals_list)

