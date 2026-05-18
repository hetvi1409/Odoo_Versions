# -*- coding: utf-8 -*-
# Copyright 2018 Openinside co. W.L.L.
{
    "name": "Committee Management",
    "summary": "Committee Management, Committee Process, Committee Member, Committee Evaluation, Board, Council",
    "version": "16.0.0.0.3",
    'category': 'Extra Tools',
    "description": """
		Committee Management 
		 
    """,
	'images':[
        'static/description/cover.png'
	],
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    "license": "OPL-1",
    "installable": True,
    "depends": [
        'hr', 'oi_workflow', 'oi_pdf_viewer'
    ],
    "data": [
        'data/ir_cron.xml',
        'data/ir_sequence.xml',
        'security/res_groups.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'view/committee_type.xml',        
        'view/committee.xml',
        'view/committee_meeting.xml',
        'view/approval_config.xml',
        'view/action.xml',
        'view/menu.xml',
        'report/report.xml',
        'data/approval_config.xml'        
    ],
    'external_dependencies' : {
        'python' : [],
    },    
    'installable': True,
    'auto_install': False,    
    'odoo-apps' : True     
}

