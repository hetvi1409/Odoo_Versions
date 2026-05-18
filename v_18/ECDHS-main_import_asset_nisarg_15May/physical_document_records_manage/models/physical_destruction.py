# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class CustomPhysicalDestructionReocrd(models.Model):
    _name = 'custom.physical.destruction.record'
    _inherit = ['mail.thread']
    _description = 'Physical Destruction Record'
    _rec_name = 'destroy_method'

    reason = fields.Text(
        string='Reason'
    )
    description = fields.Text(
        string="Description"
    )
    destroy_date = fields.Date(
        string='Destroy Date',
        readonly=True,
        copy=False,
    )
    destroy_by_id = fields.Many2one(
        'res.users',
        string='Destroy by',
        readonly=True,
        copy=False,
    )
    approved_date = fields.Date(
        string='Approved Date',
        readonly=True,
        copy=False,
    )
    approved_by_id = fields.Many2one(
        'res.users',
        string='Approved by',
        readonly=True,
        copy=False,
    )
    destroy_method = fields.Char(
        string='Method',
        copy=True,
    )
    state = fields.Selection(
        [('new','New'),
        ('approved','Approved'),
        ('destroyed','Destroyed')],
        string='State',
        default='new',
        copy=False
    )
    
    def action_approved_by(self):
        for rec in self:
            rec.state = 'approved'
            rec.approved_date = fields.Date.today()
            rec.approved_by_id = self.env.user.id

    def action_destroyed_by(self):
        for rec in self:
            rec.state = 'destroyed'
            rec.destroy_date = fields.Date.today()
            rec.destroy_by_id = self.env.user.id
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: