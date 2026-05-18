from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    folder_id = fields.Many2one(
        'documents.folder',
        string='Folder',
        help='Folder for upload tender documents',
        config_parameter='tender_management.folder_id',
    )

    ticker_enabled = fields.Boolean(
        string='Show Procurement Ticker',
        help='Show or hide the scrolling message block on the procurement page.',
        default=True,
    )
    ticker_title = fields.Char(
        string='Ticker Title',
        help='Short heading displayed before the scrolling ticker text.',
        config_parameter='tender_management.ticker_title',
        default='STAY UP TO DATE:',
    )
    ticker_message = fields.Char(
        string='Ticker Message',
        help='Scrolling ticker content displayed on the procurement page.',
        config_parameter='tender_management.ticker_message',
        default='Newspapers on behalf of the City of Joburg Property Company SOC Ltd '
                'Appointment of a professional valuer to conduct property valuations '
                'for various projects',
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        config_param = self.env['ir.config_parameter'].sudo()
        ticker_enabled_param = config_param.get_param('tender_management.ticker_enabled', '1')
        res['ticker_enabled'] = ticker_enabled_param not in ('0', 'False', 'false', '')
        return res

    def set_values(self):
        super().set_values()
        config_param = self.env['ir.config_parameter'].sudo()
        config_param.set_param('tender_management.ticker_enabled', '1' if self.ticker_enabled else '0')
