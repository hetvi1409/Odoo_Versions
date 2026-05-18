# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class PhysicalRecordKeeperCustom(models.Model):
    _name = 'physical.record.keeper.custom'
    _description = "Physical Record Keeper Custom"
    _inherit = ['mail.thread']
    _rec_name = 'record_id'
    _order = "id desc"

    def _get_default_stage_id(self):
        """ Gives default stage_id """
        return self.env['custom.physical.record.stage'].search([('name', '=', 'New')],limit=1).id

    title = fields.Char(
        string='Title',
        required=True,
        copy=True,
    )
    record_id = fields.Many2one(
        'record.name.custom',
        string='Record',
        required=True,
        copy=True,
    )
    description = fields.Text(
        string='Description',
        copy=True
    )
    date_create = fields.Date(
        string='Created Date',
        default=fields.Date.today(),
        copy=False,
    )
    document_type = fields.Selection(
        [('new','Create New'),
         ('transfer','Transferred')],
         default='new',
         string='Record With',
         copy=False,
    )
    physical_record_id = fields.Many2one(
        'physical.record.keeper.custom',
        string='Transfer Document',
        copy=False,
    )
    owner_id = fields.Many2one(
        'res.users',
        string='Owner',
        copy=True
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        copy=True,
    )
    location_id = fields.Many2one(
        'custom.physical.location',
        string='Location',
        copy=True,
    )
    bin_number = fields.Char(
        string='Bin Number',
        copy=True,
    )
    file_number = fields.Char(
        string='File Number',
        copy=True,
    )
    user_create_id = fields.Many2one(
        'res.users',
        string='Created by',
        default=lambda self: self.env.user.id,
        copy=False,
    )
    tag_ids = fields.Many2many(
        'physical.tag.custom',
        string='Tags',
        copy=False,
    )
    record_type_id = fields.Many2one(
        'record.type.custom',
        string='Record Type',
        copy=False,
    )
    record_method_id = fields.Many2one(
        'record.method.custom',
        string='Record Method',
        copy=False,
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        string='Company',
        copy=True,
        readonly=True,
    )
    stage_id = fields.Many2one(
        'custom.physical.record.stage',
        string="Stage",
        ondelete='restrict',
        tracking=True, 
        index=True,
        default=_get_default_stage_id, 
        copy=False
    )
    notes = fields.Text(
        string="Internal Notes",
        copy=True,
    )
    active = fields.Boolean(
        'Active', 
        default=True, 
        tracking=True
    )

    def action_see_record_archived(self):
        for rec in self:
            rec.active = False

class PhysicalTagCustom(models.Model):
    _name = 'physical.tag.custom'
    _description = 'Physical Tag'

    name = fields.Char(
        string='Name',
        required=True,
    )
    color = fields.Integer(
        string='Color',
    )

class RecordTypeCustom(models.Model):
    _name = 'record.type.custom'
    _description = 'Record Type Custom'

    name = fields.Char(
        string='Name',
        required=True,
    )
    code = fields.Char(
        string='Code',
    )

class RecordMethodCustom(models.Model):
    _name = 'record.method.custom'
    _description = 'Record Method Custom'

    name = fields.Char(
        string='Name',
        required=True,
    )
    code = fields.Char(
        string='Code',
    )

class RecordNameCustom(models.Model):
    _name = 'record.name.custom'
    _description = 'Record Name'

    name = fields.Char(
        string='Name',
        required=True,
    )
    code = fields.Char(
        string='Code',
    )          
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: