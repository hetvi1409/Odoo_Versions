# -*- coding: utf-8 -*-
{
    "name": "OneDrive / SharePoint Odoo Integration",
    "version": "16.0.1.2.3",
    "category": "Document Management",
    "license": "Other proprietary",
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "cloud_base"
    ],
    "data": [
        "data/data.xml",
        "security/ir.model.access.csv",
        "views/clouds_client.xml"
    ],
    "assets": {},
    "demo": [

    ],
    "external_dependencies": {
        "python": [
            "microsoftgraph-python",
            "requests"
        ]
    },
    "summary": "The tool to automatically synchronize Odoo attachments with OneDrive files in both ways. Microsoft documents. OneDrive cloud. SkyDrive cloud. SharePoint drives. Microsoft Odoo Integration. OneDrive synchronization. SharePoint synchronization. OneDrive connector. SharePoint connector",
    "description": """
For the full details look at static/description/index.html
* Features *- How synchronization works
#odootools_proprietary""",
    "images": [
        "static/description/main.png"
    ],
}
