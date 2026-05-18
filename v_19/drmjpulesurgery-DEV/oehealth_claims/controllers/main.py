from odoo import http
from odoo.http import request

class HealthClaimController(http.Controller):

    @http.route('/health_claim/save_audio', type='json', auth='user')
    def save_audio(self, record_id, model, filename, data):
        record = request.env[model].browse(int(record_id))
        if record.exists():
            attachment = request.env['ir.attachment'].create({
                'name': filename,
                'res_model': model,
                'res_id': record.id,
                'datas': data,
                'mimetype': 'audio/webm',
            })
            # Add it to chatter
            record.message_post(
                body="New audio recording attached",
                attachment_ids=[attachment.id]
            )
            return {"success": True}
        return {"success": False, "error": "Record not found"}
