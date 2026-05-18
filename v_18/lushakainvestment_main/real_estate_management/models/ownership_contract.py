import base64

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta


class RentalContract(models.Model):
    _inherit = "ownership.contract"

    installment_count = fields.Integer(string="Installment", compute="_compute_installment_count")
    attach_line_count = fields.Integer(string="Installment", compute="_compute_installment_count")
    company_id = fields.Many2one('res.company', 'Company',
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id")
    sales_price = fields.Monetary(string="Sale Price")
    deposit = fields.Float(string="Deposit")
    deposit_amount = fields.Monetary(string="Deposit Amount", compute="_deposit_amount")
    purchase_balance_amount = fields.Monetary(string="Purchase Balance Amount", compute="_deposit_amount")
    current_rates_taxes = fields.Monetary(string="Current Rates & Taxes")
    current_levy_taxes = fields.Monetary(string="Current Levy Rate")
    no_parking_bays = fields.Integer(string="No Parking Bays")
    parking_bay_no = fields.Integer(string="Parking Bay No")

    lead_id = fields.Many2one('crm.lead', string="Lead")

    def action_crm_lead(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lead',
            'view_mode': 'form',
            'res_model': self.lead_id._name,
            'res_id': self.lead_id.id,
            'context': "{'create': False}"
        }

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        if res.lead_id:
            res.lead_id.ownership_contract_id = res.id
        return res

    @api.depends()
    def _compute_installment_count(self):
        for rec in self:
            rec.installment_count = len(rec.loan_line)
            rec.attach_line_count = len(rec.attach_line)

    def action_view_installment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Installments',
            'view_mode': 'list',
            'res_model': 'loan.line.rs.own',
            'domain': [('id', 'in', self.loan_line.ids)
                       ],
            'context': "{'create': False}"
        }

    def action_view_attach_line(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Installments',
            'view_mode': 'list,form',
            'res_model': 'own.attachment.line',
            'domain': [('id', 'in', self.attach_line.ids)],
            'context': {'default_own_contract_id_att': self.id}
        }

    @api.depends('deposit', 'sales_price')
    def _deposit_amount(self):
        """Deposit Amount"""
        for rec in self:
            rec.deposit_amount = rec.deposit * rec.sales_price
            rec.purchase_balance_amount =  rec.sales_price - rec.deposit_amount
