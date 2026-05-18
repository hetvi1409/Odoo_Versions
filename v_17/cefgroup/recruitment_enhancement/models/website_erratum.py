from odoo import models, fields

class WebsiteErratum(models.Model):
    _name = 'website.erratum'
    _description = 'Website Erratum'
    _rec_name = 'title'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # section = fields.Char(string='Section', required=True, tracking=True)  # For grouping by section
    title = fields.Char(string='Title', required=True, tracking=True)  # Erratum title
    description = fields.Text(string='Description', required=True, tracking=True)  # Erratum details
    active = fields.Boolean(string='Active', default=True, tracking=True)  # Control visibility
