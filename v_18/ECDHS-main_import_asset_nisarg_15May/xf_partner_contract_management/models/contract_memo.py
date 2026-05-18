from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ContractMemo(models.Model):
    _name = 'contract.memo'
    _description = 'Contract Memo'
    _inherit = "mail.thread", "mail.activity.mixin"

    name = fields.Char(string="Reference No", readonly=True, tracking=True, copy=False)
    description = fields.Char(string="Description", required=True,
                              tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer',
                                 help="Customer Details", required=True)
    total_amount = fields.Monetary(string="Total Amount", help="Total amount",
                                   required=True)
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id',
                                  string='Currency', readonly=True)
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.company,
                                 required=True)
    date = fields.Date(string="Date", help="Memo date",
                       readonly=True, tracking=True,
                       default=fields.Date.today())
    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Signed Documents", help="Documents")

    type = fields.Selection([
        ('sale', 'Sale'),
        ('payment_session', 'Cession for payment'),
        ('funding_agreement', 'Funding Agreement'),
        ('default_notice', 'Notice of Defualt'),
        ('termination', 'Termination'),
        ('addendum', 'Addendum to Funding Agreement'),
        ('service_level', 'Service Level Agreement'),
        ('deed_of_sale', 'Deed of Sale'),
        ('mou', 'MOU'),
        ('purchase', 'Purchase'), ], string='Contract Type',
        required=True
    )
    contract_amount_type = fields.Selection([
        ('Fixed Value', 'Fixed Value'),
        ('Rate Based', 'Rate Based'), ], string='Contract Amount Type',
        required=True
    )
    date_start = fields.Date(
        string='Contract Start Date',
        required=True,
        default=fields.Date.today,
        help='Start date of the contract.',
        tracking=True,
    )
    date_end = fields.Date(
        string='Contract End Date',
        help='End date of the contract (if it is a fixed-term contract).',
        tracking=True,
    )
    budget_id = fields.Many2one('account.analytic.account', string="Budget / Analytic Account")
    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submit Request To Draft SLA'),
                              ('approved', 'Approved'),
                              ], default='draft',)
    contract_id = fields.Many2one('xf.partner.contract', string="Contract", copy=False)

    @api.model
    def create(self, vals):
        """generate purchase requisition sequence"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'contract.memo') or 'New'
        result = super().create(vals)
        return result

    def action_submit(self):
        """Submit the memo"""
        self.state = 'submit'
        self.sudo().message_post(body="Submitted the memo %s" %(self.name))

    def action_documents(self):
        """Documents"""
        return {
            'name': _('Documents'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'memo.evaluation',
            'target': 'new',
            'context': {
                'default_memo_id': self.id
            }
        }

    def view_contract_details(self):
        """Method for view contract"""
        contract = self.contract_id
        action = {
            'name': _('Contract'),
            'type': 'ir.actions.act_window',
            'res_model': contract._name,
            'context': {'create': False},
        }
        if len(contract) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': contract.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', contract.ids)],
            })
        return action
