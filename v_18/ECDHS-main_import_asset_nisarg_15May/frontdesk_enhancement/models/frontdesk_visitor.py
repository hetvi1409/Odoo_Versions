
from odoo import api, fields, models, _



class FrontdesckVisitor(models.Model):
    _inherit = "frontdesk.visitor"

    category = fields.Selection([('Visitor','Visitor'),('Contractor','Contractor')], string= 'Category',default="Visitor")
    # visitor_leptop_register = fields.Boolean(string="Is Visitor'Leptop Registor",default=False)
    visitor_leptop_register = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Does Visitor' Leptop Registor",default=False)
    department_id = fields.Many2one('hr.department',string="Department")
    surname = fields.Char(string="Surname")
    make = fields.Char(string="Make")
    serial_number_or_tag = fields.Char(string="Serial Number OR Tag")
    id_number = fields.Char(string="ID Number")
    office_visiting = fields.Char(string="Office Visiting")
    purpose_of_the_meeting = fields.Text(string="Purpose Of the Meeting")
    x_has_firearm = fields.Boolean(string='Are you in possession of a firearm?')
    x_firearm_serial = fields.Char(string='Serial Number')
    x_firearm_name = fields.Char(string='Name of Firearm')
