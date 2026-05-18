from odoo import models, fields, api
from io import BytesIO
import xlsxwriter
import base64


class AssetImpairment(models.Model):
    _inherit = 'account.asset'

    fv_c2s = fields.Float(string="Fair Value Less Cost to Sell (FV-C2S)")
    value_in_use = fields.Float(string="Value in Use (VIU)")
    recoverable_amount = fields.Float(string="Recoverable Amount", compute="_compute_recoverable_amount")
    carrying_amount = fields.Float(string="Carrying Amount")
    impairment_loss = fields.Float(string="Impairment Loss", compute="compute_impairment_loss")
    impairment_move_ids = fields.One2many(
        'asset.impairment.move',
        'asset_id',
        string='Impairment Lines',
        readonly=True,
        states={'draft': [('readonly', False)], 'open': [('readonly', False)], 'paused': [('readonly', False)]}
    )

    @api.depends('fv_c2s', 'value_in_use')
    def _compute_recoverable_amount(self):
        for record in self:
            record.recoverable_amount = max(record.fv_c2s, record.value_in_use)

    @api.depends('carrying_amount', 'recoverable_amount')
    def compute_impairment_loss(self):
        for record in self:
            record.impairment_loss = record.carrying_amount - record.recoverable_amount if record.carrying_amount > record.recoverable_amount else 0

    def action_notify_impairment(self):
        # Send an email notification
        manager_group = self.env.ref('asset_impairment.group_asset_impairment_manager')

        # Get partner objects
        mail_values = {}

        partners = manager_group.users.mapped('partner_id')

        # Send emails to each partner
        for partner in partners:
            if partner.email:  # Ensure the partner has an email address
                mail_values = {
                    'email_to': partner.email,
                    # Other values can be set as needed
                }
        template = self.env.ref('asset_impairment.email_template_asset_impairment')
        template.send_mail(self.id, force_send=True, email_values=mail_values)

        # Send an in-app notification
        for asset in self:
            message_body = (
                f"An impairment has been detected for the asset {asset.name}. "
                f"Impairment Loss: {asset.impairment_loss}."
            )
            # Send to all followers and specifically to the Impairment Manager group
            manager_group = self.env.ref('asset_impairment.group_asset_impairment_manager').id

            partner_ids = self.env['res.groups'].browse(manager_group).users.mapped('partner_id.id')

            asset.message_post(
                body=message_body,
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
                partner_ids=partner_ids,
            )

    @api.model
    def create(self, vals):
        res = super(AssetImpairment, self).create(vals)
        if res.impairment_loss > 0:
            # Notify on creation if impairment loss is detected
            res.impairment_date = fields.Date.context_today(self)
            res.action_notify_impairment()
        return res

    def write(self, vals):
        res = super(AssetImpairment, self).write(vals)
        if 'impairment_loss' in vals and self.impairment_loss > 0:
            # Notify on update if impairment loss is updated
            res.impairment_date = fields.Date.context_today(self)
            self.action_notify_impairment()
        return res

    def export_asset_impairment_xlsx(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Impairment Report')

        header = ['Asset', 'Carrying Amount', 'Fair Value Less Cost to Sell (FV-C2S)', 'Value in Use (VIU)',
                  'Recoverable Amount', 'Impairment Loss']
        worksheet.write_row(0, 0, header)

        row = 1
        for asset in self:
            worksheet.write(row, 0, asset.name)
            worksheet.write(row, 1, asset.carrying_amount)
            worksheet.write(row, 2, asset.fv_c2s)
            worksheet.write(row, 3, asset.value_in_use)
            worksheet.write(row, 4, asset.recoverable_amount)
            worksheet.write(row, 5, asset.impairment_loss)
            row += 1

        workbook.close()
        output.seek(0)
        return output.read()

    def action_export_xlsx(self):
        self.ensure_one()
        # Use the asset ID to create the URL for the report download
        report_url = '/asset_impairment/report?asset_id={}'.format(self.id)
        return {
            'type': 'ir.actions.act_url',
            'url': report_url,
            'target': 'self',  # or '_blank' if you want to open it in a new tab
        }

    def compute_impairment_board(self):
        self.ensure_one()
        # Logic to compute new impairment moves
        if self.impairment_loss > 0:
            new_impairment_moves_data = self._recompute_impairment_board()
            new_impairment_moves = self.env['asset.impairment.move'].create(new_impairment_moves_data)

            return True

    def _recompute_impairment_board(self):
        # Implement your logic here to compute impairment moves
        # Return a list of dictionaries with data to create impairment moves
        values = {
            'impairment_date':self.impairment_date,
            'reference': self.name,
            'impairment_value': self.impairment_loss,
            'cumulative_impairment_value': self.impairment_loss,
            'current_value':self.original_value - self.impairment_loss,
            'asset_id':self.id,
        }
        return values
