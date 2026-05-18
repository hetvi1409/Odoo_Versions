# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class EcdhsContractVerifyWarningWizard(models.TransientModel):
    _name = 'ecdhs.contract.verify.warning.wizard'
    _description = 'Contract Verify Missing Documents Warning'

    contract_id = fields.Many2one('ecdhs.contract', required=True, readonly=True)
    warning_type = fields.Selection([
        ('annexure', 'Annexures / Appendices'),
        ('supporting', 'Supporting Documents'),
        ('jbcc', 'JBCC'),
        ('gcc', 'GCC'),
    ], required=True, readonly=True)
    warning_message = fields.Text(compute='_compute_warning_message', readonly=True)

    @api.depends('warning_type')
    def _compute_warning_message(self):
        for wizard in self:
            if wizard.warning_type == 'annexure':
                wizard.warning_message = _(
                    'Are you sure you want to proceed without any attached Annexures / Appendices?'
                )
            elif wizard.warning_type == 'supporting':
                wizard.warning_message = _(
                    'Are you sure you want to proceed without any attached Supporting Documents?'
                )
            elif wizard.warning_type == 'jbcc':
                wizard.warning_message = _(
                    'Are you sure you want to proceed without any attached JBCC?'
                )
            else:
                wizard.warning_message = _(
                    'Are you sure you want to proceed without any attached GCC?'
                )

    def action_proceed(self):
        self.ensure_one()
        vals = {}
        if self.warning_type == 'annexure':
            vals['verify_without_annexures_confirmed'] = True
        elif self.warning_type == 'supporting':
            vals['verify_without_supporting_confirmed'] = True
        elif self.warning_type == 'jbcc':
            vals['verify_without_jbcc_confirmed'] = True
        elif self.warning_type == 'gcc':
            vals['verify_without_gcc_confirmed'] = True
        if vals:
            self.contract_id.write(vals)
        return {'type': 'ir.actions.act_window_close'}
