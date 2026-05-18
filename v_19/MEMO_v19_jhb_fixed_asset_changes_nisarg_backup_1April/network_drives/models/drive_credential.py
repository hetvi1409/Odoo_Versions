from odoo import models, fields


class NetworkDriveCredential(models.Model):
    _name = 'drive.credential'
    _description = 'Network Drive Credentials'
    _rec_name = 'drive_letter'

    drive_letter = fields.Char(string="Drive Letter", required=False)
    network_share = fields.Char(string="Network Share", required=False)
    server = fields.Char(string="Server", required=False)
    user_name = fields.Char(string="Username", required=True)
    password = fields.Char(string="Password", required=True)
    os_type = fields.Selection([('windows', 'Windows'), ('ubuntu', 'Ubuntu')],
                               required=True,
                               string="Windows/Ubuntu", default='windows')

