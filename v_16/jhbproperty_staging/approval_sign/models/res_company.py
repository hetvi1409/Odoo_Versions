# -*- coding: utf-8 -*-
from odoo import fields, models

class ResUser(models.Model):
    _inherit = 'res.company'

    header_image= fields.Binary(string='Header Image')
    footer_image= fields.Binary(string='Footer Image')
    non_executive_director_1 = fields.Many2one('hr.employee', string='Non-Executive Director 1')
    non_executive_director_2 = fields.Many2one('hr.employee', string='Non-Executive Director 2')
    non_executive_director_3 = fields.Many2one('hr.employee', string='Non-Executive Director 3')
    non_executive_director_4 = fields.Many2one('hr.employee', string='Non-Executive Director 4')
    non_executive_director_5 = fields.Many2one('hr.employee', string='Non-Executive Director 5')
    non_executive_director_6 = fields.Many2one('hr.employee', string='Non-Executive Director 6')
    non_executive_director_7 = fields.Many2one('hr.employee', string='Non-Executive Director 7')
    non_executive_director_8 = fields.Many2one('hr.employee', string='Non-Executive Director 8')
    non_executive_director_9 = fields.Many2one('hr.employee', string='Non-Executive Director 9')
    non_executive_director_10 = fields.Many2one('hr.employee', string='Non-Executive Director 10')
    non_executive_director_11 = fields.Many2one('hr.employee', string='Non-Executive Director 11')
    executive_director_1 = fields.Many2one('hr.employee', string='Executive Director 1')
    executive_director_2 = fields.Many2one('hr.employee', string='Executive Director 2')
    company_secretory = fields.Many2one('hr.employee', string='Company Secretary')
    company_registration_number = fields.Char(string='Company Registration Number')