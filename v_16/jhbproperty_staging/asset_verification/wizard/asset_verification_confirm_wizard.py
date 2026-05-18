from odoo import models, fields , api


class ConfirmWizard(models.TransientModel):
    _name = 'asset.verification.confirm.wizard'
    _description = 'Simple Confirm Wizard'

    custodian_id = fields.Many2one('hr.employee','Custodian')

    asset_ids = fields.One2many('asset.verification.confirm.wizard.line','wizard_id')

    new_custodian_id = fields.Many2one('hr.employee','New Custodian')


    def action_confirm(self):
        if self.new_custodian_id:
            # Define the action when the confirm button is clicked.

            # Filter assets based on location if a location is specified
            domain = [('custodian_id', '=', self.custodian_id.id)]

            # Fetch assets based on the location or all if no location is specified
            assets = self.env['account.asset'].search(domain)

            assets.write({'custodian_id':self.new_custodian_id.id})


            return {
                'type': 'ir.actions.act_window_close'
            }

        else:
            return {
                'type': 'ir.actions.act_window_close'
            }


    @api.model
    def create(self, vals):
        """
        Overwrite the create method to automatically add relevant assets to a new verification job.
        """
        wizard = super(ConfirmWizard, self).create(vals)

        # Fetch the location ID from the job (if provided)
        custodian_id = vals.get('custodian_id')

        # Filter assets based on location if a location is specified
        domain = [('custodian_id', '=', custodian_id)]

        # Fetch assets based on the location or all if no location is specified
        assets = self.env['account.asset'].search(domain)

        # Create verification job lines
        lines = [(0, 0, {'name': asset.name}) for asset in assets]

        wizard.asset_ids = lines
        return wizard


    def action_cancel(self):
        # Define the action when the cancel button is clicked.
        return {
            'type': 'ir.actions.act_window_close'
        }

class ConfirmWizardLine(models.TransientModel):
    _name = 'asset.verification.confirm.wizard.line'

    name = fields.Char()

    wizard_id = fields.Many2one('asset.verification.confirm.wizard')