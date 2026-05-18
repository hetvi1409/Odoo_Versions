from odoo import api, fields, models, Command, _


class DocumentFolder(models.Model):
    _inherit = 'documents.document'

    # sharepoint_site_url = fields.Char(string="SharePoint Site URL")
    sharepoint_base_url = fields.Char(
        string="SharePoint URL",
        help="The SharePoint URL should have the form https://[URL]/: the last '/' is required. The site name should\
    not be included in the URL",
    )
    sharepoint_site_name = fields.Char(
        string="SharePoint site",
        help="""The SharePoint site should be either 'my_site_name' (in that case it is considered\
    'sites/my_site_name') or 'sites/my_site_name'. Instead of 'sites', it might be 'teams', for example. There should be no\
    '/' at the beginning or at the end"""
    )

