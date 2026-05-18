# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import ValidationError

class HrDepartureWizard(models.TransientModel):
    _inherit = 'hr.departure.wizard'

    release_campany_car = fields.Boolean("Release Company Car", default=lambda self: self.env.user.user_has_groups('fleet.fleet_group_user'))

    def action_register_departure(self):
        assets = self.env['account.asset'].search([('custodian_id','=',self.employee_id.id)])
        if assets:
            raise ValidationError(_('Please transfer over all assets to another custodian first'))
        else:
            super(HrDepartureWizard, self).action_register_departure()
