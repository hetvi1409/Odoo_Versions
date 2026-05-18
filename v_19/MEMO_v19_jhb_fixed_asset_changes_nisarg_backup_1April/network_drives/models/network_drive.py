from odoo import models, fields, api
import os
import zipfile
import io
import logging

from odoo.exceptions import UserError
from odoo.http import request
import platform

os_type = platform.system()

if os_type == "Windows":
    import win32wnet
    import win32netcon
elif os_type == "Linux":
    from smbprotocol.connection import Connection
    from smbprotocol.session import Session
    from smbclient import register_session, scandir
    from uuid import uuid4

elif os_type == "Darwin":
    print("Running on macOS")
else:
    print(f"Unknown OS: {os_type}")

_logger = logging.getLogger(__name__)


class NetworkDrive(models.Model):
    _name = 'network.drive'
    _description = 'Network Drive'

    name = fields.Char(string='Name', required=True)
    file_path = fields.Char(string='File Path', required=True)
    content_ids = fields.One2many('network.drive.content', 'drive_id', string='Contents')
    os_type = fields.Selection([('windows', 'Windows'), ('ubuntu', 'Ubuntu')], required=True,
                               string="Windows/Ubuntu", default='windows')

    # Access Rights Fields
    allowed_user_ids = fields.Many2many('res.users', string='Allowed Users', help='Users who can access this record.')
    allowed_group_ids = fields.Many2many('res.groups', string='Allowed Groups', help='Groups whose members can access this record.')
    is_networkdrive = fields.Boolean(string="Is Network Drives")
    drive_credential_id = fields.Many2one('drive.credential', string="Drive Credentials")

    def action_open_driver_controller(self):
        """Open Driver using controller"""
        url = f"/folder/open/?path={self.file_path}"
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
            }

    @api.model
    def create(self, vals):
        admin_group = self.env.ref('base.group_system')  # Administrator group
        admin_user = self.env.ref('base.user_admin')  # base.user_admin user
        if 'allowed_group_ids' not in vals or not vals.get('allowed_group_ids'):
            vals['allowed_group_ids'] = [(4, admin_group.id)]
        elif isinstance(vals['allowed_group_ids'], list):
            vals['allowed_group_ids'].append((4, admin_group.id))
        if 'allowed_user_ids' not in vals or not vals.get('allowed_user_ids'):
            vals['allowed_user_ids'] = [(4, admin_user.id)]
        elif isinstance(vals['allowed_user_ids'], list):
            vals['allowed_user_ids'].append((4, admin_user.id))
        return super(NetworkDrive, self).create(vals)

    def write(self, vals):
        # Prevent removal of Administrator group and base.user_admin user
        admin_group = self.env.ref('base.group_system')
        admin_user = self.env.ref('base.user_admin')
        if 'allowed_group_ids' in vals:
            for record in self:
                if admin_group.id not in [cmd[1] for cmd in vals.get('allowed_group_ids', []) if cmd[0] == 4] + [g.id for g in record.allowed_group_ids]:
                    vals['allowed_group_ids'].append((4, admin_group.id))
        if 'allowed_user_ids' in vals:
            for record in self:
                if admin_user.id not in [cmd[1] for cmd in vals.get('allowed_user_ids', []) if cmd[0] == 4] + [u.id for u in record.allowed_user_ids]:
                    vals['allowed_user_ids'].append((4, admin_user.id))
        return super(NetworkDrive, self).write(vals)

    def _connect_to_share(self):
        """Internal method to establish connection"""
        _logger.info("Start _connect_to_share%s:", self.name)
        try:
            _logger.info(f"Initialization net_resource: {self.name}")
            path = fr'{self.file_path}'
            username = self.drive_credential_id.sudo().user_name  # or just "username" if not domain-based
            password = self.drive_credential_id.sudo().password

            win32wnet.WNetAddConnection2(0, None, path, None, username, password, 0)
            _logger.info(f"Connected  : {self.name}")
            return True
        except Exception as e:
            _logger.info(f"Not Connected : {str(e)}")
            raise UserError(f"Connection failed: {str(e)}")

    def _connect_to_share_ubuntu(self):

        # server = "103.154.36.85"
        # server = "192.168.1.11"
        # server = "192.168.1.16"
        # # server = "103.176.185.124"
        # username = "user"
        # password = "1234"
        try:
            server = self.drive_credential_id.server
            username = self.drive_credential_id.user_name
            password = self.drive_credential_id.password

            register_session(server, username=username, password=password)
            # Establish connection
            conn = Connection(uuid4(), server, 445)
            # conn = Connection( server=server, port=445)
            conn.connect()

            # Create session
            session = Session(connection=conn, username=username, password=password)
            session.connect()
            share_name = "testing"
            # path = self.file_path.replace("/", r"\")
            path = server + '/' + self.file_path

            # tree = TreeConnect(session, fr"\\{path}")
            # tree.connect()

            contents = []
            for entry in scandir(fr"\\{path}"):
                item_path = fr"{self.file_path}/{entry.name}"
                item_type = 'Folder' if entry.is_dir() else 'File'
                contents.append({
                    'name': entry.name,
                    'path': item_path,
                    'item_type': item_type,
                    'drive_id': self.id,
                })
            self.env['network.drive.content'].create(contents)
            # if os.path.exists(fr"\\{server}\{share_name}"):
            #     contents = []
            #     for item in os.listdir(f"smb://{server}/{share_name}"):
            #         print(item)
        except Exception as e:
            _logger.warning(f"Failed to access mapped drive: {self.file_path}")
            raise UserError(f"Connection failed: {str(e)}")

        # Cleanup
        # tree.disconnect()
        # session.disconnect()
        # conn.disconnect()

    def action_refresh_contents(self):
        _logger.info(f"Refreshing contents for drive: {self.name}")
        self.content_ids.unlink()  # Clear existing contents
        if self.file_path:
            if self.is_networkdrive:
                if self.os_type == 'windows':
                    self._connect_to_share()
                else:
                    self._connect_to_share_ubuntu()
                # Map the drive
                # os.system(
                    # f'net use {drive_letter} "{network_share}" /user:{username} {password}')

                # Use the drive
                try:
                    files = os.listdir(rf'{self.file_path}\\')
                    for file in files:
                        print(file)
                except Exception as e:
                    _logger.warning(f"Failed to access mapped drive: {self.file_path}")
                    # raise UserError(f"Connection failed: {str(e)}")

            path = self.file_path.replace('file:///', '')
            if os.path.exists(path):
                contents = []
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    item_type = 'Folder' if os.path.isdir(item_path) else 'File'
                    contents.append({
                        'name': item,
                        'path': item_path,
                        'item_type': item_type,
                        'drive_id': self.id,
                    })
                self.env['network.drive.content'].create(contents)
            else:
                _logger.warning(f"Path does not exist: {path}")

    # Restrict visibility of records based on access rights
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # Add domain filter to show only records where the current user is in allowed_user_ids
        # or belongs to one of the allowed_group_ids
        user = self.env.user
        if not user.has_group('base.group_system'):  # Bypass for Administrators
            args = [
                '|',
                ('allowed_user_ids', 'in', [user.id]),
                ('allowed_group_ids', 'in', user.group_ids.ids)
            ] + (args or [])
        return super(NetworkDrive, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

class NetworkDriveContent(models.Model):
    _name = 'network.drive.content'
    _description = 'Network Drive Content'
    _parent_store = True

    name = fields.Char(string='Name', required=True)
    path = fields.Char(string='Path', required=False)
    item_type = fields.Selection([('File', 'File'), ('Folder', 'Folder')], string='Type', required=False)
    drive_id = fields.Many2one('network.drive', string='Drive', required=True, ondelete='cascade')
    parent_id = fields.Many2one('network.drive.content', string='Parent', index=True, ondelete='cascade')
    child_ids = fields.One2many('network.drive.content', 'parent_id', string='Children')
    parent_path = fields.Char(index=True)
    has_children = fields.Boolean(string='Has Children', compute='_compute_has_children', store=True)
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note')
    ], default=False, readonly=True)

    @api.depends('child_ids')
    def _compute_has_children(self):
        for record in self:
            record.has_children = len(record.child_ids) > 0

    def action_expand_folder(self):
        if self.drive_id.os_type == 'ubuntu' and self.drive_id.is_networkdrive:
            server = self.drive_id.drive_credential_id.server
            username = self.drive_id.drive_credential_id.user_name
            password = self.drive_id.drive_credential_id.password
            try:
                register_session(server, username=username, password=password)
                # Establish connection
                conn = Connection(uuid4(), server, 445)
                # conn = Connection( server=server, port=445)
                conn.connect()

                # Create session
                session = Session(connection=conn, username=username, password=password)
                session.connect()
                # share_name = "testing"
                # path = self.file_path.replace("/", r"\")
                path = server + '/' + self.path

                # tree = TreeConnect(session, fr"\\{self.drive_id.file_path}")
                # tree.connect()

                existing_paths = self.drive_id.content_ids.mapped('path')
                contents = []
                for entry in scandir(fr"\\{path}"):
                    item_path = fr"{self.path}/{entry.name}"
                    item_type = 'Folder' if entry.is_dir() else 'File'
                    if item_path not in existing_paths:
                        contents.append({
                            'name': entry.name,
                            'path': item_path,
                            'item_type': item_type,
                            'drive_id': self.drive_id.id,
                            'parent_id': self.id,
                        })
                self.env['network.drive.content'].create(contents)
            except Exception as e:
                _logger.info(f"Not Connected : {str(e)}")
                raise UserError(f"Connection failed: {str(e)}")

        if self.item_type == 'Folder' and os.path.exists(self.path):
            existing_paths = self.child_ids.mapped('path')
            contents = []
            self.env['network.drive.content'].sudo().create({
                'name': 'Sub Folders: ' + self.name,
                'display_type': 'line_section',
                'drive_id': self.drive_id.id,
                'path': self.path + '/',
                'parent_id': self.id,
            })
            for item in os.listdir(self.path):
                item_path = os.path.join(self.path, item)
                if item_path not in existing_paths:  # Avoid duplicates
                    item_type = 'Folder' if os.path.isdir(item_path) else 'File'
                    contents.append({
                        'name': item,
                        'path': item_path,
                        'item_type': item_type,
                        'drive_id': self.drive_id.id,
                        'parent_id': self.id,  # Set parent_id to the current folder
                    })
            if contents:
                self.env['network.drive.content'].create(contents)

    def action_collapse_folder(self):
        if self.item_type == 'Folder':
            self.child_ids.unlink()  # Unlink only direct children

    def action_download(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/file/download/{self.id}',
            'target': 'self',
        }

    def action_open_folder(self):

        if self.drive_id.os_type == 'ubuntu' and self.drive_id.is_networkdrive:
            path = rf"/run/user/1000/gvfs/smb-share:server={self.drive_id.drive_credential_id.server},share={self.path[1:]}"
            url = f"/folder/open/?path={path}"
            # url = f'file:///{self.path.replace("\\", "/")}'
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',  # Opens in a new tab
            }
        if self.item_type == 'Folder' and os.path.exists(self.path):
            # Properly format the file URL
            url = f"/folder/open/?path={self.path}"
            # url = f'file:///{self.path.replace("\\", "/")}'
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',  # Opens in a new tab
            }
        else:
            _logger.error(f"Path does not exist or is not a folder: {self.path}")
            return False
