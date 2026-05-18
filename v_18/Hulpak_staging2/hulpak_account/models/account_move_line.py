
from odoo import models, fields, api ,_
from odoo.exceptions import UserError
import json

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('move_id.region_id', 'move_id.department_id','account_id', 'product_id', 'move_id')
    def _compute_analytic_distribution(self):
        for line in self:
            if line.move_id.state != 'posted':                
                selected_analytics = []
                region = line.move_id.region_id
                department = line.move_id.department_id

                if region:
                    selected_analytics.append(region.id)
                if department:
                    selected_analytics.append(department.id)

                if selected_analytics:
                    # Instead of using json.dumps, build a real dictionary
                    percentage = 100
                    distribution = {str(analytic_id): percentage for analytic_id in selected_analytics}
                    line.analytic_distribution = distribution
                else:
                    line.analytic_distribution = False


    @api.onchange('move_id.region_id', 'move_id.department_id','account_id', 'product_id', 'move_id')
    def _onchange_set_account_id_from_mapping(self):
        for line in self:
            move = line.move_id
            if not (line.product_id and move.region_id):
                continue

            # First, check Machinery Component mapping
            component = self.env['machinery.component'].search([
                ('product_ids', 'in', line.product_id.id)
            ], limit=1)

            account = False
            if component:
                for income_account in component.income_account_ids:
                    if income_account.region.id == move.region_id.id:
                        account = income_account
                        break

            # # Fallback to your original logic if no Machinery Component mapping found
            # if not account and move.department_id:
            #     account = self.env['account.account'].search([
            #         ('product', '=', line.product_id.product_tmpl_id.id),
            #         ('region', '=', move.region_id.id),
            #         ('department', '=', move.department_id.id),
            #         ('account_type', '=', 'income'),
            #     ], limit=1)

            if account:
                line.account_id = account.id
