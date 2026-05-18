# -*- coding: utf-8 -*-
{
    'name': 'Customer Care',
    'version': '18.0.1.0.0',
    'summary': """The system should support multiple channels for receiving complaints. Each channel will be integrated into the system to ensure all complaints are captured in one centralized platform.
    """,
    'description': """The system should support multiple channels for receiving complaints. Each channel will be integrated into the system to ensure all complaints are captured in one centralized platform.
    """,
    'category': 'Services',
    'depends': ['helpdesk', 'portal', 'web', 'base', 'website_helpdesk', 'website', 'whatsapp', 'hr', 'xf_partner_contract'],
    'data': [
        'data/team_data.xml',
        'security/customer_care_groups.xml',
        'security/ir.model.access.csv',
        'security/customer_care_groups.xml',
        'views/helpdesk_ticket_view.xml',
        'views/complaint_form.xml',
        'views/facebook_config_view.xml',
        'wizard/customer_care_summary_wizard.xml',
        'report/case_register.xml',
        'report/customer_care_summary.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'customer_care/static/src/css/ticket_list_view.css',
            "customer_care/static/src/js/channel_icon_widget.js",
            "customer_care/static/src/xml/channel_icon_widget.xml",
        ],
    },
    'external_dependencies': {
        'python': ['phonenumbers']
    },
    'qweb': [],
    'images': [],
    'license': 'OEEL-1',
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
}