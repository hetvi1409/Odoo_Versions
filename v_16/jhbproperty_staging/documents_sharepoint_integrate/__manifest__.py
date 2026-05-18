# -*- coding: utf-8 -*-
{
    "name": "Documents Sharepoint Integration",
    "version": "16.0.1.3.32",
    "category": "Document Management",
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": ["base", "documents"],
    "data": [
        "data/cron_job.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings_view.xml",
        "views/documents_view.xml",
        "views/sharepoint_service_view.xml",
    ],
    "external_dependencies": {
        "python": [
            "msal"
        ]
    },
    "demo": [],
    "summary": "The tool to automatically synchronize Odoo attachments with Sharepoint folders-files in both ways. Microsoft documents. SharePoint drives. Microsoft Odoo Integration. SharePoint synchronization. SharePoint connector.",
    "description": """(1) Fetching Folders from SharePoint to Odoo as well ODoo to Sharepoint Retrieves all parent and child folders from SharePoint. Ensures proper folder hierarchy in Odoo without duplication. Matches existing Odoo folders before creating new ones.
(2) Fetching Files from SharePoint to Odoo as well Odoo to Sharepoint Downloads all files from SharePoint and stores them in the correct Odoo folders. Ensures files are not duplicated in Odoo. Fetches folders and files in parallel to improve efficiency.""",
    "images": [],
}
