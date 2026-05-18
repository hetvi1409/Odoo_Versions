from odoo import models, fields, _, api


class CrimeType(models.Model):
    _name = 'crime.type'
    _description = 'Matter Type'
    _rec_name = 'complete_name'

    name = fields.Char()
    parent_id = fields.Many2one('crime.type')
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name', recursive=True,
        store=True)
    description = fields.Text()

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name
