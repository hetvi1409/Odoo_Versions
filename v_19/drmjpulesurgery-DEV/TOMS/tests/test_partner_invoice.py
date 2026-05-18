from odoo.tests import common, Form
from odoo.tests import tagged
from datetime import datetime

@tagged('-at_install', 'post_install')
class TestTOMSResParnter(common.TransactionCase):
    print('\n\n--------test for res partner.')

    def test_res_partner(self):
        print('\n\n--------test calll method------------------.')
        medical_aid_id = self.env['res.partner'].search([('is_a_medical_aid', '=', True)], limit=1)
        print('\n\n\n\n\n--------medical_aid_id', medical_aid_id)

        company_id = self.env['res.company'].search([('name', '=', 'Spectacle Warehouse Atterbury')], limit=1)
        print('\n\n\n\n\n--------company_id', company_id)

        option_id = self.env['medical.aid.plan'].browse(1)
        print('\n\n\n\n\n--------option_id', option_id)
        plan_option_id = self.env['medical.aid.plan.option'].search([('plan_id', '=', option_id.id)], limit=1)
        print('\n\n\n\n\n---------plan_option_id', plan_option_id)

        occupation_id = self.env['customer.occupation'].search([], limit=1)
        print('\n\n\n\n\n--------occupation_id', occupation_id)

        test_res_partner = self.env['res.partner'].create({
            'name': 'Demo Demo',
            'medical_aid_id': medical_aid_id.id,
            'option_id': option_id.id,
            'plan_option_id': plan_option_id.id,
            'surname': 'Test',
            'first_name': 'Demo',
            'id_number': 123456,
            'company_id': company_id.id,
        })

        print('\n\n\n\n\n--------test_res_partner', test_res_partner)

        test_res_partner.write({
            'phone': 123456789,
            'nick_name': 'Demo',
        })

        print('\n\n\n\n\n--------Your test was succesfull', test_res_partner.property_account_payable_id)

        print('\n\n\n\n\n--------Your test was succesfull ---------->')
        print('\n\n\n\n\n--------partner was created ---------->')

        print('\n\n\n\n\n--------test for create invoice ---------->')

        optometrist_id = self.env['res.users'].search([], limit=1)
        print('\n\n\n\n\n--------optometrist_id ---------->', optometrist_id)
        dispenser_id = self.env['res.users'].search([], limit=1)
        print('\n\n\n\n\n--------dispenser_id ---------->', dispenser_id)

        test_account_invoice = self.env['account.move'].create({
            'partner_id': test_res_partner.id,
            'type': 'out_invoice',
            'is_cash_sale': True,
            'optometrist_id': optometrist_id.id,
            'dispenser_id': dispenser_id.id
        })

        print('\n\n\n\n\n--------test_account_invoice created ---------->', test_account_invoice)

        final_rx_id = self.env['clinical.final.rx'].search([], limit=1)
        print('\n\n\n\n\n--------final_rx_id ---------->', final_rx_id)

        product_id = self.env['product.product'].search([('sale_ok', '=', True)], limit=1)
        print('\n\n\n\n\n--------product_id ---------->', product_id)

        account_id = self.env['account.account'].search([('internal_type', '=', 'other'), ('deprecated', '=', False)],
                                                        limit=1)
        print('\n\n\n\n\n--------account_id ---------->', account_id)

        account_tax_id = self.env['account.tax'].search([], limit=1)
        print('\n\n\n\n\n--------account_tax_id ---------->', account_tax_id)

        icd_codes_ids = self.env['icd.codes'].search([], limit=1)
        print('\n\n\n\n\n--------icd_codes_ids ---------->', icd_codes_ids)

        line_values = {'final_rx_id': final_rx_id.id,
                       'product_id': product_id.id,
                       'name': product_id.name,
                       'account_id': account_id.id,
                       'quantity': 1,
                       'price_unit': product_id.lst_price,
                       'invoice_line_tax_ids': [(4, account_tax_id.id)],
                       'icd_codes_ids': [(4, icd_codes_ids.id)]
                       }

        print('\n\n\n\n\n--------line_values ---------->', line_values)
        test_account_invoice.write({
            'invoice_line_ids': [(0, 0, line_values)]
        })

        print('\n\n\n\n\n--------test_account_invoice update ---------->', test_account_invoice.invoice_line_ids)

        print('\n\n\n\n\n--------test_account_invoice state ---------->', test_account_invoice.state)
        test_account_invoice.action_invoice_open()
        print('\n\n\n\n\n--------test_account_invoice state ---------->', test_account_invoice.state)

        test_res_partner.write({
            'mobile': 123456789,
            'occupation': occupation_id.id,

        })

        print('\n\n\n\n\n--------test_res_partner update ---------->', test_res_partner.occupation)

        print('\n\n\n\n\n--------test for payment  ---------->')

        test_payment = self.env['account.payment']
        journal_id = self.env['account.journal'].search([('id', '=', 10)])

        vals = {
            'amount': test_account_invoice.amount_total,
            'journal_id': journal_id.id,
            'payment_date': datetime.today(),
            'communication': test_account_invoice.reference,
            'invoice_ids': [(4, test_account_invoice.id)],
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'context': {'test_payment': True}
        }

        account_payment = test_payment.create(vals)

        print('\n\n\n\n\n--------test account_payment created  ---------->', account_payment)

        account_payment.action_validate_invoice_payment()

        print('\n\n\n\n\n--------test test_account_invoice state  ---------->', test_account_invoice.state)

        print('\n\n\n\n\n test successfull')
