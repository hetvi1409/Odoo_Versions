# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ContractTemplateInitWizard(models.TransientModel):
    _name = 'contract.template.init.wizard'
    _description = 'Initialise Contract from Template'

    template_id = fields.Many2one(
        'contract.template', string='Contract Template',
        required=True,
    )
    contract_type = fields.Selection(
        related='template_id.contract_type',
        store=False, readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner', string='Service Provider / Customer',
        required=True,
    )
    amount = fields.Monetary(
        string='Contract Amount', currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date')
    contract_body = fields.Html(string='Contract Body')
    scope_of_work = fields.Html(string='Scope of Work')
    terms_of_reference = fields.Html(string='Terms of Reference')
    notes = fields.Html(string='Terms and Conditions')
    contract_title = fields.Char(string='Contract Title', required=True)
    variable_line_ids = fields.One2many(
        'contract.template.init.wizard.variable',
        'wizard_id',
        string='Template Variables',
    )

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.contract_body = self.template_id.body_html
            self.scope_of_work = self.template_id.scope_of_work
            self.terms_of_reference = self.template_id.terms_of_reference
            self.variable_line_ids = [(5, 0, 0)]
            lines = []
            for var in self.template_id.variable_ids.sorted('sequence'):
                lines.append((0, 0, {
                    'sequence': var.sequence,
                    'placeholder': var.placeholder,
                    'label': var.label,
                    'field_type': var.field_type,
                    'required': var.required,
                    'default_value': var.default_value,
                    'value_text': var.default_value,
                }))
            self.variable_line_ids = lines

    def _placeholder_map(self):
        self.ensure_one()
        amount_text = ''
        if self.amount:
            amount_text = ('%.2f' % self.amount).rstrip('0').rstrip('.')
        date_start_text = self.date_start.isoformat() if self.date_start else ''
        date_end_text = self.date_end.isoformat() if self.date_end else ''

        value_map = {
            'client_name': self.env.company.name or '',
            'service_provider_name': self.partner_id.display_name or '',
            'consultant_name': self.partner_id.display_name or '',
            'recipient_name': self.partner_id.display_name or '',
            'party_b_name': self.partner_id.display_name or '',
            'purchaser_name': self.partner_id.display_name or '',
            'funder_name': self.env.company.name or '',
            'party_a_name': self.env.company.name or '',
            'seller_name': self.env.company.name or '',
            'effective_date': date_start_text,
            'contract_value': amount_text,
            'grant_amount': amount_text,
            'monthly_retainer_fee': amount_text,
            'purchase_price': amount_text,
            'date_start': date_start_text,
            'date_end': date_end_text,
            'contract_title': self.contract_title or '',
        }

        for line in self.variable_line_ids:
            key = (line.placeholder or '').strip().strip('{}').strip()
            if not key:
                continue
            value_map[key] = line.value_text or line.default_value or ''
        return value_map

    def _render_template_text(self, text):
        if not text:
            return text
        rendered = text
        for key, value in self._placeholder_map().items():
            rendered = rendered.replace('{{%s}}' % key, value or '')
        return rendered

    def action_create_contract(self):
        self.ensure_one()
        if not self.template_id:
            raise UserError(_('Please select a contract template.'))

        rendered_body = self._render_template_text(self.contract_body)
        rendered_scope = self._render_template_text(self.scope_of_work)
        rendered_tor = self._render_template_text(self.terms_of_reference)
        rendered_notes = self._render_template_text(self.notes)

        contract = self.env['xf.partner.contract'].create({
            'name': self.contract_title,
            'type': self.template_id.contract_type,
            'partner_id': self.partner_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'template_id': self.template_id.id,
            'contract_body_html': rendered_body,
            'scope_of_work': rendered_scope,
            'terms_of_reference_html': rendered_tor,
            'notes': rendered_notes,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Contract'),
            'res_model': 'xf.partner.contract',
            'res_id': contract.id,
            'view_mode': 'form',
            'target': 'current',
        }


class ContractTemplateInitWizardVariable(models.TransientModel):
    _name = 'contract.template.init.wizard.variable'
    _description = 'Contract Template Init Wizard Variable'
    _order = 'sequence, id'

    wizard_id = fields.Many2one(
        'contract.template.init.wizard',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    placeholder = fields.Char(string='Placeholder', required=True)
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
        readonly=True,
    )
    required = fields.Boolean(string='Required')
    default_value = fields.Char(string='Default Value')
    value_text = fields.Char(string='Value')
