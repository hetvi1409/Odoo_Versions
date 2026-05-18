# -*- coding: utf-8 -*-
from odoo import fields, models


class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    header_image = fields.Binary(related='company_id.header_image', readonly=False)
    footer_image = fields.Binary(related='company_id.footer_image', readonly=False)
    non_executive_director_1 = fields.Many2one('hr.employee', related='company_id.non_executive_director_1', readonly=False)
    non_executive_director_2 = fields.Many2one('hr.employee', related='company_id.non_executive_director_2', readonly=False)
    non_executive_director_3 = fields.Many2one('hr.employee', related='company_id.non_executive_director_3', readonly=False)
    non_executive_director_4 = fields.Many2one('hr.employee', related='company_id.non_executive_director_4', readonly=False)
    non_executive_director_5 = fields.Many2one('hr.employee', related='company_id.non_executive_director_5', readonly=False)
    non_executive_director_6 = fields.Many2one('hr.employee', related='company_id.non_executive_director_6', readonly=False)
    non_executive_director_7 = fields.Many2one('hr.employee', related='company_id.non_executive_director_7', readonly=False)
    non_executive_director_8 = fields.Many2one('hr.employee', related='company_id.non_executive_director_8', readonly=False)
    non_executive_director_9 = fields.Many2one('hr.employee', related='company_id.non_executive_director_9', readonly=False)
    non_executive_director_10 = fields.Many2one('hr.employee', related='company_id.non_executive_director_10', readonly=False)
    non_executive_director_11 = fields.Many2one('hr.employee', related='company_id.non_executive_director_11', readonly=False)
    executive_director_1 = fields.Many2one('hr.employee', related='company_id.executive_director_1', readonly=False)
    executive_director_2 = fields.Many2one('hr.employee', related='company_id.executive_director_2', readonly=False)
    company_secretory = fields.Many2one('hr.employee', related='company_id.company_secretory', readonly=False)
    company_registration_number = fields.Char(related='company_id.company_registration_number', readonly=False)
