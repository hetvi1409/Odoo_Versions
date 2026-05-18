# -*- coding: utf-8 -*-
##############################################################################
#
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models,_

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    write_off_account_id = fields.Many2one('account.account', string='Write-Off Account', related="company_id.loan_write_off_account_id")
    interest_prod_id = fields.Many2one('product.product', string='Interest Product',
            help='Product used to invoice as interest of the loans.', related="company_id.loan_interest_prod_id")
    processing_fee_prod_id = fields.Many2one('product.product', string='Processing Fee',
           help='Product used as Processing fee of the loans.', related="company_id.loan_processing_fee_prod_id")
    acc_rec_id = fields.Many2one('account.account', string="Amortization Account Receivable", related="company_id.loan_acc_rec_id")
    income_acc_id = fields.Many2one('account.account', string="Amortization Income Account", related="company_id.loan_income_acc_id")
    loan_jou_id = fields.Many2one('account.journal', string="Loans Journal", related="company_id.loan_jou_id")
    disbursement_acc_id = fields.Many2one('account.account', string="Disbursement Account", related="company_id.loan_disbursement_acc_id")
    disbursement_journal_id = fields.Many2one('account.journal', string="Disbursement Journal", related="company_id.loan_disbursement_journal_id",)
    inv_create_date = fields.Integer(string='No. of Days', related="company_id.loan_inv_create_date", help="Installment Invoice Create Date before how much days from installment due date.")
    penalty_product_id = fields.Many2one("product.product", related="company_id.penalty_product_id")
    principal_product_id = fields.Many2one("product.product", related="company_id.loan_principal_prod_id")
    penalty_option = fields.Selection([
        ('penalty', 'Penalty'),
        ('interest', 'Interest')],
        string="Penalty / Interest ?",
        default='penalty')
    charge_option = fields.Selection([
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage')],
        default='fixed',
        string="Due penalty method")

    charge = fields.Float(string="Charge", digits=(16, 2))
    of_days = fields.Integer(string="Allow # of days after due", default=2)
    loan_counter = fields.Integer(related="company_id.loan_counter")

    @api.onchange('penalty_option')
    def onchange_penalty_option(self):
        if self.penalty_option == 'interest':
            self.charge_option = 'percentage'
        if not self.penalty_option:
            self.charge_option = False
            self.charge = 0.00
            self.of_days = 2
            
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        penalty_option = ICPSudo.get_param(
            'jt_loan_management.penalty_option')
        charge_option = ICPSudo.get_param(
            'jt_loan_management.charge_option')
        charge = float(ICPSudo.get_param(
            'jt_loan_management.charge'))
        of_days = int(ICPSudo.get_param(
            'jt_loan_management.of_days'))

        res.update(
            penalty_option=penalty_option,
            charge_option=charge_option,
            charge=charge,
            of_days=of_days,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        charge_option = self.charge_option
        if self.penalty_option == 'interest':
            charge_option = 'percentage'
        ICPSudo.set_param(
            'jt_loan_management.penalty_option', self.penalty_option)
        ICPSudo.set_param(
            'jt_loan_management.charge_option', charge_option)
        ICPSudo.set_param('jt_loan_management.charge', self.charge)
        ICPSudo.set_param(
            'jt_loan_management.of_days', self.of_days or 2)