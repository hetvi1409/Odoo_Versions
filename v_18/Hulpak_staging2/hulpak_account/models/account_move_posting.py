from odoo import models, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        for move in self:
            move._process_split_cost_lines()
        return super().action_post()

    def _process_split_cost_lines(self):
        for move in self:
            if move.move_type not in ['out_invoice', 'out_refund']:
                continue
    
            is_refund = move.move_type == 'out_refund'
            invoice_products = move.invoice_line_ids.mapped('product_id')
            cogs_lines = move.line_ids.filtered(lambda l: l.product_id in invoice_products)
    
            product_cogs_map = {}
            chatter_logs = []
            created_line_ids = []
    
            for line_id in cogs_lines:
                product = line_id.product_id
                if not product:
                    continue
                product_cogs_map.setdefault(product, {'lines': []})['lines'].append(line_id)
    
            for product, data in product_cogs_map.items():
                original_account = (
                    product.property_account_expense_id or
                    product.categ_id.property_account_expense_categ_id
                )
                if not original_account:
                    raise UserError(f"No expense account found for product '{product.display_name}'")
    
                split = self.env['product.cost.split'].search([
                    ('main_product_id', '=', product.id)
                ], limit=1)
    
                if not split or not split.line_ids:
                    continue
    
                for line in data['lines']:
                    quantity = line.quantity
                    partner_id = line.partner_id.id
    
                    for split_line in split.line_ids:
                        if split_line.amount == 0:
                            continue
    
                        region_account = split_line.account_id.filtered(
                            lambda acc: acc.region == move.region_id
                        )
                        if not region_account:
                            raise UserError(
                                f"No matching COS account found for product '{split_line.component_product_id.display_name}' "
                                f"with region '{move.region_id.name}'. Please check account mappings."
                            )
    
                        selected_account = region_account[0]
    
                        # Create reversal line
                        reversal = self.env['account.move.line'].create({
                            'move_id': move.id,
                            'name': f"Reverse COS - {split_line.component_product_id.display_name}",
                            'account_id': original_account.id,
                            'debit': 0.0,
                            'credit': 0.0,
                            'quantity': quantity,
                            'partner_id': partner_id,
                            'product_id': product.id,
                            'display_type': 'cogs',
                        })
                        created_line_ids.append((reversal.id, 'reverse', split_line.amount, quantity))
    
                        # Create split line
                        split_jl = self.env['account.move.line'].create({
                            'move_id': move.id,
                            'name': f"COS Split - {split_line.component_product_id.display_name}",
                            'account_id': selected_account.id,
                            'debit': 0.0,
                            'credit': 0.0,
                            'quantity': quantity,
                            'partner_id': partner_id,
                            'product_id': split_line.component_product_id.id,
                            'display_type': 'cogs',
                        })
                        created_line_ids.append((split_jl.id, 'split', split_line.amount, quantity))
    
                        split_jl._compute_analytic_distribution()
    
                        chatter_logs.append(
                            f"Split COS for '{product.display_name}' → '{split_line.component_product_id.display_name}': "
                            f"{split_line.amount} × {quantity} = {split_line.amount * quantity:.2f} to account "
                            f"'{selected_account.code} - {selected_account.name}'"
                        )
    
            # SQL update for correct amounts per line
            for line_id, line_type, amount, quantity in created_line_ids:
                total_amount = amount * quantity
    
                if is_refund:
                    debit = 0.0 if line_type == 'reverse' else total_amount
                    credit = total_amount if line_type == 'reverse' else 0.0
                else:
                    debit = total_amount if line_type == 'split' else 0.0
                    credit = total_amount if line_type == 'reverse' else 0.0
    
                balance = -credit if credit > 0 else debit
                amount_currency = balance
    
                self.env.cr.execute("""
                    UPDATE account_move_line
                    SET debit = %s,
                        credit = %s,
                        balance = %s,
                        amount_currency = %s
                    WHERE id = %s
                """, (debit, credit, balance, amount_currency, line_id))
    
            # Post logs to chatter
            # if chatter_logs:
            #     move.message_post(
            #         body="💡<b>Cost of Sales (COS) Split Breakdown:</b><br/>" +
            #              "<br/>".join(chatter_logs)
            #     )
