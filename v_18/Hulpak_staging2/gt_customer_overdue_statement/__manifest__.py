# -*- coding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2013-Today Globalteckz (http://www.globalteckz.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Overdue Statements of customers/suppliers',
    'version': '17.00',
    'website' : 'https://www.globalteckz.com',
    'category': ' Accounting & Finance',
    'summary': 'Apps for print customer statement report print vendor statement payment reminder customer payment followup send customer statement print account statement reports print overdue statement reports send overdue statement print supplier statement reports customer overdue statements suppliers overdue statements manage over due payments overdue customer payments payments reminder for vendor vendors overdue statements partners overdue payments non paid statements unpaid statements outstanding statements due dates reminders customer statement supplier statement overdue statement pending statement customer follow up customer overdue statement customer account statement supplier account statement Send customer overdue statements by email send overdue email outstanding invoice customer overdue payments invoice reminder monthly ' ,
    'description': """This module should allow you to print customer statement report from top of customer/supplier list/form view
    """,
    'author': 'Globalteckz',
	"price": "25.00",
    "currency": "EUR",
    'images': ['static/description/Banner.gif'],
    "license" : "Other proprietary",
    'depends': ['sale_management',
                'purchase',
                'account',
                'stock',
                'sale_stock',
                ],
    'data': [
        'report/email_overdue.xml',
        'report/report_view.xml',
        'views/partner_view.xml',
        'views/send_mail_view.xml',
    ],
    'qweb' : [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
