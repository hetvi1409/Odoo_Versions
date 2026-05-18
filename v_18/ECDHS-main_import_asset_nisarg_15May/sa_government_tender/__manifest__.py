
# -*- coding: utf-8 -*-
{
    'name': 'SCM - SA Government Tender Management',
    'version': '18.0.1.0.0',
    'category': 'Supply Chain Management',
    'summary': 'Comprehensive South African Government Tender Management System',
    'description': """
        SA Government Tender Management Module
        =======================================

        Complete tender management solution for South African government entities,
        compliant with PFMA, MFMA, PPPFA, and National Treasury regulations.

        Key Features:
        -------------
        * 12-Step Tender Process Workflow
        * Purchase Requisition Management (linked to APP)
        * Budget Confirmation Process
        * Specification Development
        * SCM Processing & Advertisement
        * Tender Briefing Sessions (Compulsory/Optional)
        * Attendee Registration & Management
        * Questions & Answers Tracking
        * Site Visit Coordination
        * Bid Opening Register
        * Compliance Verification (CSD, Tax, COID, B-BBEE)
        * Declaration of Interest Management
        * Bid Evaluation Committee (BEC) Process
        * Bid Adjudication Committee (BAC) Review
        * Tender Award Management
        * Standard Bidding Documents (SBD) Support
        * 80/20 and 90/10 Preference Point Systems
        * Audit Trail & Transparency Features
        * Committee Management
        * Document Management
        * Email Notifications

        Compliance:
        -----------
        * Constitution Section 217
        * PFMA (Public Finance Management Act)
        * MFMA (Municipal Finance Management Act)
        * PPPFA (Preferential Procurement Policy Framework Act)
        * B-BBEE Act
        * National Treasury Regulations

        .PY DOT Model Renamings:
        -----------
        budget.confirmation
        sagovbudget.confirmation
        tender.specification
        sagovtender.specification
        #####tender
        tender.bid
        sagovtender.bid
        bid.opening.register
        sagovbid.opening.register
        compliance.check
        sagovcompliance.check
        declaration.interest
        sagovdeclaration.interest
        bid.evaluation
        sagovbid.evaluation
        bac.review
        sagovbac.review
        tender.award
        sagovtender.award
        tender.committee
        sagovtender.committee
        tender.document
        sagovtender.document
        annual.procurement.plan
        sagovannual.procurement.plan
        tender.purchase.requisition
        sagovtender.purchase.requisition
        tender.bac.signatory
        sagovtender.bac.signatory

        .PY UNDERSCORE Model Renamings:
        -----------
        budget_confirmation
        sagovbudget_confirmation
        tender_specification
        sagovtender_specification
        #####tender
        tender_bid
        sagovtender_bid
        bid_opening_register
        sagovbid_opening_register
        compliance_check
        sagovcompliance_check
        declaration_interest
        sagovdeclaration_interest
        bid_evaluation
        sagovbid_evaluation
        bac_review
        sagovbac_review
        tender_award
        sagovtender_award
        tender_committee
        sagovtender_committee
        tender_document
        sagovtender_document
        annual_procurement_plan
        sagovannual_procurement_plan
        tender_purchase_requisition
        sagovtender_purchase_requisition
        tender_bac_signatory
        sagovtender_bac_signatory

    """,
    'author': 'SA Government Solutions',
    'website': 'https://www.example.com',
    'depends': [
        'base',
        'mail',
        'contacts',
        'account',
        'account_budget',
        'purchase',
        'calendar',
        'product',
        'hr',
        'portal',
        'sign',
        'web',
        'website_event',
        'website',
        'e_system',
        # 'supply_chain_management',
        # 'tender_management',
        # 'governance',
        # 'performance_management',
    ],
    'data': [
        # Security (load groups early)
        'security/sagovtender_security.xml',
        'security/ir.model.access.csv',

        'data/email_template.xml',
        'data/ir_rule.xml',
        'data/app_sequence.xml',
        'views/website_menus.xml',
        'wizard/app_line_import_wizard.xml',
        'wizard/app_rejection_wizard_views.xml',
        'views/annual_procurement_plan_views.xml',
        'views/annual_procurement_plan_line_views.xml',
        'wizard/signature_wizard_views.xml',

        # Website Templates
        'views/templates/tender_pages.xml',
        'views/templates/bid_pages.xml',
        'views/templates/supplier_pages.xml',

        # Views - Bid
        'views/sagovtender_bid_views.xml',

        # Views - Purchase Requisition
        'views/sagovpurchase_requisition_views.xml',

        # Views - Budget
        'views/sagovbudget_views.xml',
        'views/sagovbudget_confirmation_views.xml',

        # Views - Tender Main
        'views/sagovtender_views.xml',
        'views/sagovtender_specification_views.xml',

        # Views - Bidding
        # 'views/sagovtender_bid_views.xml',
        'views/sagovbid_opening_register_views.xml',

        # Views - Compliance
        'views/sagovcompliance_check_views.xml',
        'views/sagovdeclaration_interest_views.xml',

        # Views - Evaluation
        'views/sagovbid_evaluation_views.xml',
        'views/sagovbac_review_views.xml',

        # Views - Award
        'views/sagovtender_award_views.xml',

        # Views - Supporting
        'views/sagovtender_committee_views.xml',
        'views/sagovtender_document_views.xml',
        'views/sagovannual_procurement_plan_views.xml',

        # Views - Configuration (MUST be loaded early)
        'views/sagovprocurement_method_views.xml',
        'views/sagovprocurement_workflow_stage_views.xml',
        'views/sagovprocurement_document_requirement_views.xml',
        'views/sagovprocurement_evaluation_criteria_views.xml',
        'views/sagovpreference_point_criteria_views.xml',
        'views/sagovpreference_point_system_views.xml',

        # Views - Menu (MUST be loaded AFTER all view files with actions)
        'views/sagovres_partner_views.xml',
        'views/sagovtender_menu.xml',
        'views/sagovtender_briefing_views.xml',

        # Wizard
        'wizard/sagovtender_publish_wizard_views.xml',
        'wizard/sagovtender_award_wizard_views.xml',
        'wizard/sagovcompliance_check_wizard_views.xml',
        'wizard/sagovbriefing_confirmation_wizard_views.xml',
        'wizard/sagovspecification_wizard_views.xml',
        'wizard/sagovbudget_confirmation_wizard_views.xml',

        # Reports
        'reports/sagovtender_reports.xml',
        'reports/sagovbid_opening_register_report.xml',
        'reports/sagovbec_report_template.xml',
        'reports/sagovbac_report_template.xml',

        # Data
        'data/sagovtender_sequence.xml',
        'data/sagovtender_briefing_sequence.xml',
        'data/sagovtender_type_data.xml',
        'data/sagovevaluation_criteria_data.xml',
        'data/sagovprocurement_method_data.xml',
        'data/sagovtender_ui_section_data.xml',
        'data/sagovtender_stage_visibility_data.xml',
        'data/sagovtender_ui_section_menu_data.xml',
        'data/sagovemail_template_data.xml',
        'data/sagovproduct.xml',
        'data/sagovdata_res_users.xml',
        'data/data_res_currency.xml',

        # Demo
        'demo/sagovdemo_data_app_laptops.xml',
        'demo/sagovdemo_data_committees.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sa_government_tender/static/src/css/style.css',
        ],
    },
    'demo': [
        # Demo
        'demo/sagovdemo_data_app_laptops.xml',
        'demo/sagovdemo_data_committees.xml',
    ],
    'images': ['sa_government_tender/static/description/icon.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,

}
