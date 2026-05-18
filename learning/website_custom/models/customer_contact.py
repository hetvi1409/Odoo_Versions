# -*- coding: utf-8 -*-
from odoo import models, fields


class WebsiteCustomerContact(models.Model):
    _name = 'website.customer.contact'
    _description = 'Website Customer Contact'
    _rec_name = 'name'
    _order = 'create_date desc'

    name = fields.Char(string='Full Name', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    company_name = fields.Char(string='Company Name')
    street = fields.Char(string='Street')
    city = fields.Char(string='City')
    zip = fields.Char(string='Zip')
    country_id = fields.Many2one('res.country', string='Country')
    message = fields.Text(string='Message')
    partner_id = fields.Many2one(
        'res.partner', string='Portal User',
        default=lambda self: self.env.user.partner_id
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
    ], default='submitted', string='State')
