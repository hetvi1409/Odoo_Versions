# -*- coding: utf-8 -*-
# Eastern Cape DSD – Contract Templates

from odoo import api, fields, models
from odoo.osv import expression


class EcdhsContractTemplate(models.Model):
    _name = 'ecdhs.contract.template'
    _description = 'Contract Template'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    is_addendum = fields.Boolean(string='Addendum', default=False)
    body_html = fields.Html(
        string='Template Body',
        required=True,
        help='HTML clause set appended to Draft Contract Terms when selected on a contract.',
    )

    _sql_constraints = [
        ('ecdhs_contract_template_name_uniq', 'unique(name)', 'Template name must be unique.'),
    ]

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        domain = list(args or [])
        if name:
            domain = expression.AND([domain, [('name', operator, name)]])
        templates = self.search(domain, limit=limit, order=self._order)
        return [(template.id, template.display_name) for template in templates]
