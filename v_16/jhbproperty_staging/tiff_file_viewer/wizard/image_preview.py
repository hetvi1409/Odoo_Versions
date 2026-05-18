import io
import logging

_logger = logging.getLogger(__name__)
from odoo import fields, models
from PIL import Image
import base64
import filetype
from PIL import TiffImagePlugin

from odoo.tools.mimetypes import guess_mimetype

class ImagePreview(models.TransientModel):
    _name = 'image.preview'
    _description = "Image Preview"

    image = fields.Binary(string="Images")
    pdf = fields.Binary(string="Pdf")
    file = fields.Binary('File', required=True)
    filename = fields.Char(string="Filename")
    type = fields.Selection([('pdf', 'PDF'), ('image', 'Image')])

    def action_open_images(self, data):
        """Open images"""
        if data['model'] == 'ir.attachment':
            file = self.env['ir.attachment'].browse(int(data['value'])).datas
        else:
            file = self.env[data['model']].browse(int(data['id']))
            file = file[data['field_name']]
            # file = data['value']
        binary_data = base64.b64decode(file)
        mime_type = guess_mimetype(binary_data)
        _logger.warning("Image Format %s", mime_type)
        kind = filetype.guess(binary_data)
        mime_type = kind.mime
        # mime_type = magic.from_buffer(binary_data, mime=True)
        _logger.warning("Image Format Filetype %s", mime_type)
        type = ""
        image = ""
        pdf = ""
        image_svg = ""
        if mime_type in ['image/tiff', 'image/tif']:
            try:
                img = TiffImagePlugin.TiffImageFile(io.BytesIO(binary_data))
                img.load()  # Force loading the image
                output = io.BytesIO()
                img.save(output, format="PDF", save_all=True,
                         append_images=[img.seek(i) or img.copy() for i in
                                        range(1, img.n_frames)])
                png_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
            except Exception as e:
                print(f"Error: {e}")
            try:
                img = Image.open(io.BytesIO(binary_data))
                img.verify()  # Verify if it's a valid image
            except Exception as e:
                print(f"Error: {e}")
            with Image.open(io.BytesIO(binary_data)) as img:
                output = io.BytesIO()
                img.save(output, format="PDF", save_all=True,
                         append_images=[img.seek(i) or img.copy() for i in
                                        range(1, img.n_frames)])
                png_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
            pdf = png_base64
            type= 'pdf'
        if mime_type == 'image/svg+xml':
            image_svg = file
        if mime_type in ['image/jpeg', 'image/gif', 'image/png', 'image/svg+xml',]:
            image = file
            type= 'image'
        if mime_type == 'application/pdf':
            pdf = file
            type = 'pdf'
        file = self.env[self._name].create({
            'file': file,
            'type': type,
            'image': image,
            'pdf': pdf,
        })
        return file.id
