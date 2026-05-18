from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"


    folder_id = fields.Many2one('documents.document', domain=[('type', '=', 'folder')],
        string='Folder',
        help='Folder for upload tender documents',
        config_parameter='tender_management.folder_id')
