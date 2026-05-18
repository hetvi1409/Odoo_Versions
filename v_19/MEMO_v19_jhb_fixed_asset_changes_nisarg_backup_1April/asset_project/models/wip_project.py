from odoo import api, fields, models

class WipProject(models.Model):
    _name = 'wip.project'

    name = fields.Char(string='Project Name', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, readonly=True,
                                  default=lambda
                                      self: self.env.company.currency_id.id)
    task_id = fields.Many2one('project.task')
    direct = fields.Monetary(string='Direct', required=True)
    indirect = fields.Monetary(string='Indirect', required=True)
    total = fields.Monetary(string='Total', compute='_compute_total_amount')

    @api.depends('direct', 'indirect')
    def _compute_total_amount(self):
        """Compute total amount"""
        for rec in self:
            total = 0.0
            if rec.direct:
                total = total + rec.direct
            if rec.indirect:
                total = total + rec.indirect
            rec.total = total

class UnbundlingProject(models.Model):
    _name = 'unbundling.project'

    name = fields.Char(required=True)
    task_id = fields.Many2one('project.task')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, readonly=True,
                                  default=lambda
                                      self: self.env.company.currency_id.id)
    amount = fields.Monetary(string="Amount", required=True)
    type = fields.Selection([('Direct', 'Direct'), ('Indirect', 'Indirect'),], required=True)
    weighted_average = fields.Float(string='Weighted Average', compute='_compute_weighted_average')
    allocate_indirect = fields.Monetary(string='Allocate Indirect')
    total = fields.Monetary(string='Cost of the unbundled assets TO BE CAPTALISED', compute='_compute_total_amount')

    @api.depends('amount')
    def _compute_weighted_average(self):
        """Compute weighted average"""
        for rec in self:
            task = rec.task_id
            rec.weighted_average = 0
            if len(rec.task_id.unbundling_ids) == 1:
                rec.weighted_average = 100
            if rec.type == 'Indirect':
                rec.weighted_average = 0
            if rec.type == 'Direct':
                average = (rec.amount / rec.task_id.unbundling_direct_total) * 100
                rec.weighted_average = average
            # else:


    @api.depends('amount', 'allocate_indirect')
    def _compute_total_amount(self):
        """Compute total amount"""
        for rec in self:
            total = 0.0
            if rec.amount:
                total = total + rec.amount
            if rec.allocate_indirect:
                total = total + rec.allocate_indirect
            rec.total = total


class WipInputAsPerBOQ(models.Model):
    """Model for WIP input as per BOQ"""
    _name = 'wip.input.boq'
    _description = "Wip input as per boq"

    name = fields.Char(string='Description of cost line', required=True)
    task_id = fields.Many2one('project.task')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, readonly=True,
                                  default=lambda
                                      self: self.env.company.currency_id.id)
    amount = fields.Monetary(string='Amount (excl VAT)', required=True)
    type = fields.Selection([('Direct', 'Direct'), ('Indirect', 'Indirect'),], required=True)


class WipFinal(models.Model):
    """Model for the final"""
    _name = 'wip.final'
    _description = 'Wip Final'

    name = fields.Char(string='BOQ', required=True)
    task_id = fields.Many2one('project.task')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, readonly=True,
                                  default=lambda
                                      self: self.env.company.currency_id.id)
    type = fields.Selection([('Direct', 'Direct'), ('Indirect', 'Indirect'),], required=True)
    amount = fields.Monetary(string='Cost of the unbundled assets TO BE CAPTALISED', required=True)
    asset_type_id = fields.Many2one('asset.type')

class ProjectAsset(models.Model):
    """Model for a project asset"""
    _name = 'project.asset'
    _description = 'Project asset'

    name = fields.Char(string="BOQ")

    task_id = fields.Many2one('project.task')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, readonly=True,
                                  default=lambda
                                      self: self.env.company.currency_id.id)
    amount = fields.Monetary(string="Cost of the unbundled assets TO BE CAPTALISED")
    asset_type_id = fields.Many2one('asset.type')
    date = fields.Date(string="Date")
    location = fields.Char(string="Location")
    description = fields.Char(string="Description")

