# See LICENSE file for full copyright and licensing details.
from odoo import _, api, models,fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    over_credit = fields.Boolean('Allow Over Credit?')
    credit_hold = fields.Boolean(string="Credit Hold")
    cod_customer = fields.Boolean(string="COD Customer")
    department = fields.Many2one(
        'account.analytic.account',
        string="Department",
        domain="[('plan_id.name', 'ilike', 'Department')]"
    )

    region = fields.Many2one(
        'account.analytic.account',
        string="Region",
        domain="[('plan_id.name', 'ilike', 'Region')]")

    compute_customer_status = fields.Boolean(
        string="Compute Customer Status Automatically", default=True)

    customer_status = fields.Selection([
        ('active', 'Active'),
        ('credit_available', 'Credit Available'),
        ('credit_hold', 'Credit Hold'),
        ('inactive', 'Inactive'),
    ], string="Customer Status")

    available_credit_on_sales = fields.Monetary(
        string="Available Credit on Sales", compute="_compute_credit_values", store=True)
    total_available_credit_limit = fields.Monetary(
        string="Total Available Credit Limit", compute="_compute_credit_values", store=True)
    currency_id = fields.Many2one('res.currency', compute='_compute_currency', store=True)

    @api.depends('credit_limit', 'credit')
    def _compute_credit_values(self):
        for partner in self:
            sales_orders = self.env['sale.order'].search([
                ('partner_id', '=', partner.id),
                ('state', '=', 'sale'),
            ]).filtered(lambda so: not so.invoice_ids or all(inv.state == 'draft' for inv in so.invoice_ids))

            mapped_sales_total = sum(sales_orders.mapped('amount_total'))

            partner.available_credit_on_sales = partner.credit_limit - mapped_sales_total - partner.credit
            partner.total_available_credit_limit = partner.credit_limit - partner.credit

    @api.onchange('credit', 'credit_limit', 'compute_customer_status')
    def _compute_customer_status(self):
        for partner in self:
            if partner.compute_customer_status:
                if partner.credit_limit > 0.0 and partner.credit > partner.credit_limit:
                    partner.customer_status = 'credit_hold'
                    partner.credit_hold = True
                else:
                    partner.customer_status = 'credit_available'
            if partner.customer_status == 'credit_hold':
                partner.credit_hold = True

    @api.depends('company_id')
    def _compute_currency(self):
        for rec in self:
            rec.currency_id = rec.company_id.currency_id
            
    @api.onchange('name', 'ref')
    def _onchange_clean_name_ref(self):
        for partner in self:
            raw_name = partner.name or ""
            new_ref = partner.ref or ""
    
            # --- 1. Split at "|" and keep ONLY the left side ---
            # Example: "John Doe | OLDREF | xyz" → "John Doe"
            base_name = raw_name.split("|")[0].strip()
    
            # --- 2. Rebuild clean name ---
            cleaned_name = base_name
    
            # --- 3. Add the new ref (exactly once) ---
            if new_ref:
                cleaned_name = f"{base_name} | {new_ref}"
    
            partner.name = cleaned_name
    

