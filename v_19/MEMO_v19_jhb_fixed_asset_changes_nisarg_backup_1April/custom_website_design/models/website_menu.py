from odoo import api, fields, models, modules
from odoo.http import request
from odoo.tools.translate import html_translate


class WebsiteMenu(models.Model):
    _inherit = 'website.menu'


    parent_id = fields.Many2one('website.menu', 'Parent Menu', index=True, ondelete="cascade",domain="[('website_id', '=', website_id)]")
