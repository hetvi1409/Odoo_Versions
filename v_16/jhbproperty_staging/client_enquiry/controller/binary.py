import base64
import json
import logging
import unicodedata

try:
    from werkzeug.utils import send_file
except ImportError:
    from odoo.tools._vendor.send_file import send_file
from odoo import http, _
from odoo.exceptions import AccessError, UserError
from odoo.http import request, Response
_logger = logging.getLogger(__name__)
from odoo.addons.web.controllers.binary import Binary

def clean(name):
    return name.replace('\x3c', '')


class BinaryCheck(Binary):


    @http.route('/web/binary/upload_attachment', type='http', auth="user")
    def upload_attachment(self, model, id, ufile, callback=None):
        files = request.httprequest.files.getlist('ufile')
        Model = request.env['ir.attachment']
        out = """<script language="javascript" type="text/javascript">
                    var win = window.top.window;
                    win.jQuery(win).trigger(%s, %s);
                </script>"""
        args = []
        for ufile in files:

            filename = ufile.filename
            if request.httprequest.user_agent.browser == 'safari':
                # Safari sends NFD UTF-8 (where é is composed by 'e' and [accent])
                # we need to send it the same stuff, otherwise it'll fail
                filename = unicodedata.normalize('NFD', ufile.filename)

            try:
                if model == 'check.ownership':
                    attachment = Model.sudo().create({
                        'name': filename,
                        'datas': base64.encodebytes(ufile.read()),
                        'res_model': model,
                        'res_id': int(id),
                        # 'public': True
                    })
                else:
                    attachment = Model.create({
                        'name': filename,
                        'datas': base64.encodebytes(ufile.read()),
                        'res_model': model,
                        'res_id': int(id),
                        # 'public': True
                    })
                attachment._post_add_create()
            except AccessError:
                args.append({'error': _("You are not allowed to upload an attachment here.")})
            except Exception:
                args.append({'error': _("Something horrible happened")})
                _logger.exception("Fail to upload attachment %s", ufile.filename)
            else:
                args.append({
                    'filename': clean(filename),
                    'mimetype': ufile.content_type,
                    'id': attachment.id,
                    'size': attachment.file_size
                })
        return out % (json.dumps(clean(callback)), json.dumps(args)) if callback else json.dumps(args)
