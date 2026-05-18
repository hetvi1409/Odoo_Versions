# -*- coding: utf-8 -*-
##############################################################################
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
{
    "name": "The Complete Amortization Management System",
    "version": "16.0.1.0.0",
    'summary': 'The Complete Commercial Loan management Application',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    "category": "Account",
    "depends": ['account', 'sale'],
    "data": [
        'security/account_loan_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/cron.xml',
        'data/ir_rule.xml',
        'views/account_move_view.xml',
        'wizard/account_loan_pay_amount_view.xml',
        'views/account_loan_view.xml',
        'views/res_partner.xml',
        'views/account_invoice_view.xml',
        'views/loan_crons.xml',
        'views/loan_settings_view.xml',
        'wizard/move_due_date_of_loan.xml',
        'report/loan_details_report_template.xml',
        'report/loan_detail_report.xml',
        'report/loan_detail_email_template.xml',
        'views/product_view.xml',
        'views/company_view.xml'
    ],
    'demo': [
        'data/demo_data.xml'
    ],
     
    'license': 'AGPL-3',
    "application": True,
    'installable': True,
    'external_dependencies': {
        'python': [
            'numpy', 'dateutil', 'numpy_financial'
        ],
    },
     'images': ['static/description/banner.gif'],
}
