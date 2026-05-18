from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class AccountAccount(models.Model):
    _inherit = "account.account"

    account_code = fields.Char(string="Account Code")
    account_name = fields.Char(string="Name")
    department = fields.Many2one('account.analytic.account', string="Department")
    product = fields.Many2one('machinery.component', string='Attached to Machine')
    region = fields.Many2one('account.analytic.account', string="Region")

    def _compute_coa_code(self):
        """
        Computes the chart of accounts code based on the department, region, 
        account code, and product reference.
        """
        for rec in self:
            region_code = (rec.region.code or '').strip() if rec.region else ''
            department_code = (rec.department.code or '').strip() if rec.department else ''
            account_code = (rec.account_code or '').strip()
            product_ref = (rec.product.default_code or '').strip() if rec.product else ''

            if not (region_code and department_code and account_code and product_ref):
                raise UserError("Missing required fields: Region, Department, Account Code, or Product Ref")

            final_code = "{}.{}.{}.{}".format(department_code, region_code, account_code, product_ref)
            final_name = "{} - {} - {} - {}".format(
                rec.product.name if rec.product else '',
                rec.department.name.strip() if rec.department and rec.department.name else '',
                rec.region.name.strip() if rec.region and rec.region.name else '',
                rec.account_name or ''
            )

            rec.write({'code': final_code, 'name': final_name})

    def _reverse_fields_from_code(self):
        """
        Extracts fields from the code and populates:
        - department
        - region
        - account_code
        - product (auto-creates if missing)
        """
        try:
            commit_counter = 0
            for rec in self:
                if not rec.code:
                    continue

                parts = rec.code.strip().split('.')
                if len(parts) != 4:
                    raise UserError("Invalid code format. Expected format: department.region.account_code.product_ref")

                department_code, region_code, account_code, product_ref = parts

                _logger.info(f"Processing record: Department={department_code}, Region={region_code}, Account Code={account_code}, Product Ref={product_ref}")

                department = self.env['account.analytic.account'].search([('code', '=', department_code)], limit=1)
                region = self.env['account.analytic.account'].search([('code', '=', region_code)], limit=1)
                product = self.env['machinery.component'].search([('default_code', '=', product_ref)], limit=1)

                # Auto-create product if not found
                if not product:
                    product_name = rec.name.split('-')[0].strip() if rec.name else product_ref
                    product = self.env['machinery.component'].create({
                        'name': f"Auto {product_name}",
                        'default_code': product_ref,
                        'component_type': 'other',
                    })
                    _logger.info(f"Created product: {product_name} with default_code: {product_ref}")

                # Assign COS and income accounts for the product
                cos_accounts = self.env['account.account'].search([
                    ('account_type', '=', 'expense_direct_cost'),
                    ('product', '=', product.id)
                ])
                income_accounts = self.env['account.account'].search([
                    ('account_type', '=', 'income'),
                    ('product', '=', product.id)
                ])
                product.write({
                    'cos_account_ids': [(6, 0, cos_accounts.ids)],
                    'income_account_ids': [(6, 0, income_accounts.ids)],
                })

                update_vals = {'account_code': account_code}
                if department:
                    update_vals['department'] = department.id
                if region:
                    update_vals['region'] = region.id
                if product:
                    update_vals['product'] = product.id

                rec.write(update_vals)

                commit_counter += 1
                if commit_counter >= 1000:
                    self.env.cr.commit()
                    _logger.info(f"Committed after processing 1000 records.")
                    commit_counter = 0

            if commit_counter > 0:
                self.env.cr.commit()
                _logger.info(f"Final commit after processing remaining {commit_counter} records.")

        except Exception as e:
            _logger.error(f"Error in _reverse_fields_from_code: {e}", exc_info=True)
            raise UserError(f"Unexpected error occurred: {str(e)}")
