import base64
import os
import logging
import io
from PIL import Image
from odoo import http
from odoo.http import request
from werkzeug.wrappers import Response
from PIL import TiffImagePlugin
import mimetypes
_logger = logging.getLogger(__name__)


class TiffDownloadController(http.Controller):

    @http.route('/download/tiff/<int:record_id>', type='http', auth='user')
    def download_tiff(self, record_id, **kwargs):
        """Download a TIFF file from a model's file path field."""
        output_format = "PNG"
        record = request.env['title.deeds'].sudo().browse(record_id)

        if not record or not record.file_path:
            _logger.error("No valid file path for record ID: %s", record_id)
            return request.not_found()

        file_path = record.file_path  # Ensure this is a valid path

        # Ensure the file exists
        if not os.path.isfile(file_path):
            _logger.error("File not found: %s", file_path)
            return request.not_found()

        if file_path.lower().endswith(".pdf"):
            with open(file_path, "rb") as pdf_file:
                binary_data = pdf_file.read()

            # Encode the binary data to Base64 (required for Odoo binary fields)
            encoded_data = base64.b64encode(binary_data).decode("utf-8")
            filename = os.path.basename(file_path)

            # Create a response for downloading the file
            response = Response(encoded_data, content_type='application/pdf')
            response.headers[
                'Content-Disposition'] = f'attachment; filename="{filename}"'

            return response
        elif file_path.lower().endswith((".tif", ".tiff")):
            try:
                # Open and process the TIFF image
                with TiffImagePlugin.TiffImageFile(file_path) as img:
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format="TIFF")  # Save as TIFF format
                    img_buffer.seek(0)

                # Get filename
                filename = os.path.basename(file_path)

                # Create response
                response = Response(img_buffer.getvalue(),
                                    content_type='image/tiff')
                response.headers[
                    'Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            except Exception as e:
                _logger.error("Error processing TIFF file: %s", str(e))
                return request.not_found()
        elif file_path.lower().endswith((".jpg", ".png", ".jpeg")):
            # Handle TIFF
            img = Image.open(file_path)
            img_buffer = io.BytesIO()
            img.save(img_buffer, format=output_format.upper())
            img_buffer.seek(0)
            # Encode the image to base64
            encoded_image = base64.b64encode(img_buffer.read())
            filename = os.path.basename(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"

            # Create response for downloading the file
            response = Response(encoded_image, content_type=mime_type)
            response.headers[
                'Content-Disposition'] = f'attachment; filename="{filename}"'
            return response