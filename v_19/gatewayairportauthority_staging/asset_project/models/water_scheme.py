from odoo import api, fields, models


class ProjectConstruction(models.Model):
    """Project construction"""
    _name = 'wip.project.construction'
    _description = 'Project construction'

    inv_date = fields.Date(string="Invoice date", required=True)
    task_id = fields.Many2one('project.task')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, readonly=True,
                                  default=lambda
                                      self: self.env.company.currency_id.id)
    vote_number = fields.Char(string="Vote number")
    certificate_number = fields.Char(string="Certificate number")
    partner_id = fields.Many2one('res.partner', string="Name of payee")
    amount = fields.Monetary(string="Amount", required=True)
    vat = fields.Monetary(string="Vat", required=True)
    vat_include = fields.Monetary(string='Vat Incl')
    retention = fields.Monetary(string="Retention", required=True)
    surety = fields.Monetary(string="Surety")
    guarantee = fields.Monetary(string="Guarantee")
    cap_amount = fields.Monetary(string="Cap Amount")

    @api.onchange('amount', 'retention', 'surety', 'guarantee')
    def _onchange_guarantee(self):
        """Calculate cap amount"""
        amount = 0.0
        for rec in self:
            if rec.amount:
                amount = amount + rec.amount
            if rec.retention:
                amount = amount + rec.retention
            if rec.surety:
                amount = amount + rec.surety
            if rec.guarantee:
                amount = amount + rec.guarantee
            rec.cap_amount = amount


class ProjectProfessional(models.Model):
    """Project professional"""
    _name = 'wip.project.professional'
    _description = 'Project professional'

    inv_date = fields.Date(string="Invoice date", required=True)
    task_id = fields.Many2one('project.task')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, readonly=True,
                                  default=lambda
                                      self: self.env.company.currency_id.id)
    vote_number = fields.Char(string="Vote number")
    certificate_number = fields.Char(string="Certificate number")
    partner_id = fields.Many2one('res.partner', string="Name of payee")
    amount = fields.Monetary(string="Amount", required=True)
    vat = fields.Monetary(string="Vat", required=True)
    vat_include = fields.Monetary(string='Vat Incl')
    retention = fields.Monetary(string="Retention", required=True)
    surety = fields.Monetary(string="Surety")
    guarantee = fields.Monetary(string="Guarantee")
    cap_amount = fields.Monetary(string="Cap Amount")

    @api.onchange('amount', 'retention', 'surety', 'guarantee')
    def _onchange_guarantee(self):
        """Calculate cap amount"""
        amount = 0.0
        for rec in self:
            if rec.amount:
                amount = amount + rec.amount
            if rec.retention:
                amount = amount + rec.retention
            if rec.surety:
                amount = amount + rec.surety
            if rec.guarantee:
                amount = amount + rec.guarantee
            rec.cap_amount = amount
