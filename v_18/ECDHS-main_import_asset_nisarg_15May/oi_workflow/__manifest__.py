# -*- coding: utf-8 -*-
{
    'name': 'Workflow Engine Base',
    'summary': 'Configurable Workflow Engine, Workflow, Workflow Engine, Approval, Approval '
               'Engine, Approval Process, Escalation, Multi Level Approval',
    'version': '18.0.2.1.1',
    'category': 'Extra Tools',
    'website': 'https://www.open-inside.com',
    'description': '''
    		Configurable Workflow Engine
    		 
        ''',
    'images': ['static/description/cover.png'],
    'author': 'Openinside',
    'license': 'OPL-1',
    'price': 400.0,
    'currency': 'USD',
    'installable': True,
    'depends': ['mail',
                 'oi_base',
                 'oi_mail',
                 'web', 'base',
                 'base_automation',
                 'oi_fields_selection',
                 ],
    #ME Removed the oi_action_trigger_reload module from depends. Need to solve the issues in this module.
    'data': ['security/ir.model.access.csv',
'data/ir_cron.xml',
              'data/ir_sequence.xml',
              'view/approval_config.xml',
              'view/approval_approve_wizard.xml',
              'view/approval_reject_wizard.xml',
              'view/approval_forward_wizard.xml',
              'view/approval_return_wizard.xml',
              'view/approval_transfer_wizard.xml',
              'view/approval_cancel_wizard.xml',
              'view/approval_escalation.xml',
              'view/approval_state_update.xml',
              'view/approval_settings.xml',
              'view/cancellation_record_view.xml',
              'view/action.xml',
              'view/menu.xml',
              'view/templates.xml',
              'data/mail_activity_type.xml',
              # 'data/mail_template.xml',
              'view/res_config_settings.xml'],

    'assets': {'web.assets_backend': [
            # 'oi_workflow/static/src/js/*.js',
            # 'oi_workflow/static/src/js/action_menu.js',
            # 'oi_workflow/static/src/js/approval_info.js',
            # 'oi_workflow/static/src/js/form_controller.js',
            # 'oi_workflow/static/src/js/statusbar_field.js',
            # 'oi_workflow/static/src/js/view_button.js',
            'oi_workflow/static/src/xml/*.xml'
        ],
                },
    'qweb': ['static/src/xml/*.xml'],
    'odoo-apps': True,
    'application': False
}
