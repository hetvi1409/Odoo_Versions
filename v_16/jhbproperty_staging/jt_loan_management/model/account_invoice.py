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
from odoo import api, fields, models, _
from datetime import datetime
import logging
from dateutil.relativedelta import *
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from dateutil.relativedelta import relativedelta as rd
_logger = logging.getLogger(__name__)

try:
    import numpy
except (ImportError, IOError) as err:
    _logger.error(err)

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    emi = fields.Boolean('Is Installment?')
    is_down_payment = fields.Boolean('Is Downpayment?')
    splitted_invoice = fields.Boolean("Splitted Invoice")
    main_invoice_id = fields.Many2one("account.move")
    penalty = fields.Boolean(string="Penalty?", copy=False)
    interest_inv_id = fields.Integer(string="Interest inv ref", copy=False)
    interest_due_date = fields.Date(string="Interest Due Date", copy=False)
    penalty_day_counter = fields.Integer("Penalty day counter")
    penalty_charged_till = fields.Date("Penalty Charged Till")

    def _prepare_inv_line(self, penalty_prod_id, name, qty, uom_id, unit_price, account_id, invoice):
        invoice_line = {
                'product_id': penalty_prod_id,
                'name': name,
                'quantity': qty,
                'product_uom_id': uom_id,
                'price_unit': unit_price,
                'account_id': account_id,
                'move_id':invoice.id
            }
        return invoice_line

    def _get_inv_principal(self, inv):
        for inv_line in inv.invoice_line_ids:
            if inv_line.account_id and inv_line.account_id.account_type == 'asset_current':
                return inv_line.price_subtotal
        return 0.0

    @api.model
    def check_due_invoice(self):
        invoice_line_obj = self.env['account.move.line']
        current_date = datetime.strptime(str(fields.Date.context_today(self)), DF).date()
        domain = [('move_type', '=', 'out_invoice'),
                  ('state', '=', 'posted'),
                  ('payment_state', '!=', 'paid'),
                  ('company_id.id','=',self.env.user.company_id.id)]
        # Checking penalty configuration
        IPC = self.env['ir.config_parameter'].sudo()
        penalty_option = IPC.get_param(
            'jt_loan_management.penalty_option')
        charge_option = IPC.get_param(
            'jt_loan_management.charge_option')
        charge = float(IPC.get_param(
            'jt_loan_management.charge'))
        of_days = int(IPC.get_param(
            'jt_loan_management.of_days'))
        invoice_ids = self.search(domain)
        _logger.info("Checking Due Invoices")
        try:
            if penalty_option:
                penalty_product_id = self.env.company and self.env.company.sudo().penalty_product_id
                name = 'Penalty Charged for'
                if penalty_option == 'interest':
                    name = 'Interest Charged for '
                for inv in invoice_ids:
                    if not inv.penalty_charged_till:
                        due_date = inv.invoice_date_due
                        new_dt = due_date + rd(days=of_days)
                    else:
                        new_dt = inv.penalty_charged_till
                    if new_dt < current_date:
                        gap = ((current_date - new_dt).days)
                        new_dt = new_dt + rd(days=gap)
                        inv_principal = self._get_inv_principal(inv)
                        charge_amt = charge
                        if penalty_option == 'interest':
                            charge_amt = (charge_amt * inv_principal / 100) * gap
                        elif penalty_option == 'penalty' and charge_option =='percentage':
                            charge_amt = (charge_amt * inv_principal / 100) * gap
                        elif penalty_option =='penalty' and charge_option == 'fixed':
                            charge_amt = charge_amt
                        account = penalty_product_id.property_account_income_id and penalty_product_id.property_account_income_id.id or False 
                        inv_line = self._prepare_inv_line(penalty_product_id.id, name, 1, penalty_product_id.uom_id.id,
                                                       charge_amt, account, inv)
                        inv.button_draft()
                        try:
                            invoice_line_obj.create(inv_line)
                            inv.penalty_charged_till = new_dt
                        except Exception as error:
                            _logger.error("Error ::",error)
                        # Removed this code to solve the conflict issues with invoice module.
                        # Will do the posting by manager after checked the checklist
                        # inv.action_post()
            return True
        except:
            _logger.info("Please check due invoice penalty configuration !")

        def write(self, vals):
            result = super(AccountInvoice, self).write(vals)
            if 'date_due' in vals:
                for rec in self:
                    rec.interest_due_date = vals['invoice_date_due']

class PartnerInherit(models.Model):
    _inherit = 'res.partner'

    loan_count = fields.Integer(string='Loans', compute="get_loan_count")
    total_payment_amount = fields.Float('Total Payment Amount', compute='cal_payment_amt')

    # @api.multi
    def cal_payment_amt(self):
        """
        Calculate total payment amount of loan.
        :return:
        """
        pay_his_obj = self.env['account.payment.history']
        for partner in self:
            histories = pay_his_obj.search([('partner_id', '=', partner.id)])
            partner.total_payment_amount = sum(history.amount for history in histories)
    
    # # @api.multi
    def get_loan_count(self):
        """
        Count total loan of partner.
        :return:
        """
        loan = self.env['account.loan']
        for partner in self:
            partner.loan_count = len(loan.search([('partner_id', '=', partner.id)]))
