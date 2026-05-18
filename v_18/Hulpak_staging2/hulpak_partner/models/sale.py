from odoo import _, api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    credit_hold = fields.Boolean(string="Credit Hold")
    cod_customer = fields.Boolean(string="COD Customer")
    # credit_check_passed = fields.Boolean(string="Credit Check Passed", compute="_compute_credit_check", store=True)

    partner_credit_dynamic_warning = fields.Html(
        string="Dynamic Credit Warning",
        compute="_compute_partner_credit_warning_hulpak",
        store=False,
        sanitize=False,
    )

    @api.onchange('partner_id')
    def _onchange_partner_id_set_credit_hold(self):
        if self.partner_id:
            self.credit_hold = self.partner_id.credit_hold
            self.cod_customer = self.partner_id.cod_customer

    @api.depends('state')
    def _onchange_state_credit_check(self):
        for order in self:

            # ✅  New condition for COD customer without POP file
            if order.partner_id.cod_customer and order.partner_id.credit >= 0:
                raise UserError(
                    _("❌ You cannot confirm this Sale Order because the customer is marked as COD (Cash on Delivery) \n\n 💰💰💰R💵 Payment must be allocated to Customer Account to Proceed.")

                )

            if order.state in ['draft', 'sent', 'cancel', 'reject']:
                partner = order.partner_id
                partner._compute_credit_values()

                mapped_sales_orders = self.env['sale.order'].search([
                    ('partner_id', '=', partner.id),
                    ('state', '=', 'sale'),
                ]).filtered(lambda so: not so.invoice_ids or all(inv.state == 'draft' for inv in so.invoice_ids))

                mapped_sales_total = sum(mapped_sales_orders.mapped('amount_total'))
                available_credit_on_sales = partner.credit_limit - mapped_sales_total - partner.credit

                if available_credit_on_sales < 0 or (available_credit_on_sales - order.amount_total < 0):
                    if not partner.over_credit:
                        partner.customer_status = 'credit_hold'
                        partner.credit_hold = True

                        sales_list = "\n".join([
                            f"| {s.name:<15} | {s.user_id.name or 'N/A':<20} | R{s.amount_total:>10.2f} |"
                            for s in mapped_sales_orders
                        ])

                        header = (
                            "+-----------------+----------------------+-------------+\n"
                            "| Order           | Salesperson          | Amount      |\n"
                            "+-----------------+----------------------+-------------+"
                        )
                        footer = "+-----------------+----------------------+-------------+"

                        warning_msg = _(
                            "You cannot save/confirm this Sale Order.\n"
                            "Client balance owing is higher than credit limit.\n\n"
                            "Credit Limit:R %.2f\n"
                            "Available Credit on Sales:R %.2f\n"
                            "Current Order Amount:R %.2f\n\n"
                            "%s\n%s\n%s"
                        ) % (
                            partner.credit_limit,
                            available_credit_on_sales,
                            order.amount_total,
                            header,
                            sales_list,
                            footer
                        )

                        raise UserError(warning_msg)

    def write(self, vals):
        for order in self:
            if 'state' in vals and vals['state'] not in ['draft', 'sent']:
                order._onchange_state_credit_check()
        return super(SaleOrder, self).write(vals)

    @api.depends('partner_id', 'partner_id.credit_limit', 'partner_id.available_credit_on_sales','amount_total')
    def _compute_partner_credit_warning_hulpak(self):
        for order in self:
            partner = order.partner_id
            html = ""

            if partner and partner.credit_limit > 0:
                credit_limit = partner.credit_limit or 0.0
                available = partner.available_credit_on_sales or 0.0
                credit_owing = partner.credit or 0.0
                over_credit = (
                    "<span style='color:green; font-weight:bold;'>✅ YES</span>"
                    if partner.over_credit else
                    "<span style='color:red; font-weight:bold;'>❌ NO</span>"
                )

                html += f"""
                    <div style="line-height: 1.6; text-align: center; background-color:#FFCCCB;">
                        <strong style="font-size: 16px;">📊 Credit Summary</strong> |→ 
                        <span>💳 <strong>Credit Limit:</strong> <span style='color:blue;'>{credit_limit:,.2f}</span></span> |→ 
                        <span>🟠 <strong>Amount Owing (Client):</strong> <span style='color:orange;'>{credit_owing:,.2f}</span></span> |→ 
                        <span>📉 <strong>Available Credit on Sales:</strong> <span style='color:{'red' if available < 0 or available < order.amount_total else 'green'};'>{available:,.2f}</span></span> |→ 
                        <span>🛡 <strong>Allowed Over Credit:</strong> {over_credit}</span>
                """

                if available < 0:
                    html += """
                        <h4 style="color: red; margin-top: 1em;">
                            🚨 Client has exceeded their credit limit.
                        </h4>
                    """
                elif available < order.amount_total:
                    html += """
                        <h4 style="color: red; margin-top: 1em;">
                            ⚠️ This order will exceed the available credit on sales.
                        </h4>
                    """

                html += "</div>"

            order.partner_credit_dynamic_warning = html

    # @api.depends('state')
    # def _compute_credit_check(self):
    #     for order in self:
    #         if order.state not in ['draft', 'sent']:
    #             try:
    #                 order.credit_check_passed = order._check_credit_limit(simulate=True)
    #             except UserError:
    #                 order.credit_check_passed = False
