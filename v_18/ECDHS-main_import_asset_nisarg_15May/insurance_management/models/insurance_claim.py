# models/insurance_claim.py
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

CLAIM_STATUS = [
    ('open', 'Open'),
    ('in_review', 'In Review'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('paid', 'Paid'),
]


class InsuranceClaim(models.Model):
    _name = "insurance.claim"
    _description = "Insurance Claim"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "date desc, id desc"

    name = fields.Char(string="Claim Reference",copy=False)
    policy_id = fields.Many2one('insurance.policy', string="Policy", required=True, ondelete='cascade')
    date = fields.Date(string="Claim Date", default=fields.Date.context_today)
    status = fields.Selection(CLAIM_STATUS, string="Claim Status", default='open', tracking=True)
    claim_amount = fields.Monetary(string="Claim Amount")
    payout_amount = fields.Monetary(string="Payout Amount")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)
    contact_person = fields.Char(string="Claims Contact")
    contact_number = fields.Char(string="Claims Contact Number")
    contact_email = fields.Char(string="Claims Email")
    claim_documents_count = fields.Integer(string="Documents", compute='_compute_doc_count')
    incident_id = fields.Many2one('maintenance.request', string="Incident Report")  # optional
    notes = fields.Text(string="Notes")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('insurance.claim') or 'New'
        return super(InsuranceClaim, self).create(vals_list)

    def _compute_doc_count(self):
        for rec in self:
            rec.claim_documents_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'insurance.claim'),
                ('res_id', '=', rec.id),
            ])

    def action_open_documents(self):
        self.ensure_one()
        return {
            'name': _('Claim Documents'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'views': [(self.env.ref('base.view_attachment_tree').id, 'list'), (self.env.ref('base.view_attachment_form').id, 'form')],
            'domain': [('res_model', '=', 'insurance.claim'), ('res_id', '=', self.id)],
        }

    @api.constrains('payout_amount', 'claim_amount')
    def _check_amounts(self):
        for rec in self:
            if rec.payout_amount and rec.claim_amount and rec.payout_amount > rec.claim_amount:
                raise ValidationError(_('Payout cannot exceed claim amount.'))
