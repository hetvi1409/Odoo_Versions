# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ContractTemplate(models.Model):
    _name = 'contract.template'
    _description = 'Contract Template'
    _order = 'name'

    name = fields.Char(string='Template Name', required=True)
    active = fields.Boolean(default=True)
    contract_type = fields.Selection(
        selection=[
            ('sale', 'Customer Contract'),
            ('purchase', 'Vendor Contract'),
        ],
        string='Contract Type',
        required=True,
    )
    description = fields.Char(string='Description')
    body_html = fields.Html(
        string='Contract Body',
        help='Use placeholders like {{service_provider_name}} which will be '
             'substituted when initialising a new contract from this template.',
    )
    scope_of_work = fields.Html(
        string='Default Scope of Work',
        help='Default scope text pre-filled on contracts created from this template.',
    )
    terms_of_reference = fields.Html(
        string='Default Terms of Reference',
    )
    variable_ids = fields.One2many(
        'contract.template.variable', 'template_id',
        string='Template Variables',
    )

    def action_preview(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web#action=&model=contract.template&id=%d' % self.id,
            'target': 'new',
        }


class ContractTemplateVariable(models.Model):
    _name = 'contract.template.variable'
    _description = 'Contract Template Variable'
    _order = 'sequence, id'

    template_id = fields.Many2one(
        'contract.template', string='Template',
        required=True, ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    placeholder = fields.Char(
        string='Placeholder',
        required=True,
        help='e.g. {{service_provider_name}}',
    )
    label = fields.Char(string='Label', required=True)
    field_type = fields.Selection(
        selection=[
            ('char', 'Text'),
            ('date', 'Date'),
            ('float', 'Amount'),
        ],
        string='Field Type',
        default='char',
        required=True,
    )
    required = fields.Boolean(string='Required', default=False)
    default_value = fields.Char(string='Default Value')
