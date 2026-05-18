# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class LoanType(models.Model):
    _name = 'loan.types'
    _order = "id"
    _description = "Loan Type"
    
    # Fields definition for the Loan Type model
    name = fields.Char(string="Loan Type")
    num_of_days= fields.Integer(string="Number of Days")
   