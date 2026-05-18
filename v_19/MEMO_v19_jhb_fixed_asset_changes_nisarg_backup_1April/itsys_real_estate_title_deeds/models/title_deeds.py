import io

from odoo import api, models, fields, _
import os
import subprocess
from odoo.exceptions import ValidationError, UserError
import logging
from werkzeug.wrappers import Response
from odoo.http import request

_logger = logging.getLogger(__name__)
import base64
from PIL import Image
from io import BytesIO
from PIL import Image
import base64
from PIL import TiffImagePlugin

class TitleDeeds(models.Model):
    """Title Deeds"""
    _name = 'title.deeds'
    _description = 'Title Deeds'

    type = fields.Selection([('title', 'Title Deeds'), ('trim', 'Trim Documents')])
    # trim_type = fields.Selection([('title', 'Title Deeds'), ('trim', 'Trim Documents')], required=True)
    active = fields.Boolean(string="Active", default=True)
    jmc_number = fields.Char(string="JMC Number", required=True)
    # trim_jmc_number = fields.Char(string="JMC Number", required=True)
    full_jmc_number = fields.Char(string="Full JMC Number")
    name = fields.Char(string="Name")
    # trim_name = fields.Char(string="Name")
    number = fields.Char(string="Number")
    year = fields.Char(string="Year")
    file_path = fields.Char(string="File Path")
    # trim_file_path = fields.Char(string="File Path")
    message = fields.Html(string="Message", required=False)
    building_id = fields.Many2one('building', string='Building', required=False)
    trim_building_id = fields.Many2one('building', string='Trim Building', required=False)
    file = fields.Binary(string="File")
    # title_deed_id = fields.Many2one('building', string='Building')
    uri = fields.Char(string="URI")
    filename = fields.Char(string="Filename")
    full_record_id = fields.Char(string="Full Record Id")
    image = fields.Binary('Binary')

    def unlink(self):
        for rec in self:
            if self.building_id:
                rec.building_id.message_post(body=_("%s title document line is deleted.") % (rec.name))
            else:
                rec.trim_building_id.message_post(body=_("%s trim document line is deleted.") % (rec.name))

        return super(TitleDeeds, self).unlink()


    @api.onchange('building_id')
    def _onchange_building(self):
        """On change building"""
        for rec in self:
            rec.jmc_number = self.building_id.jmc_number

    def open_trim_images(self):
        input_filepath = self.file_path
        output_format = "PNG"
        try:
            if input_filepath.lower().endswith(".pdf"):
                try:
                    # Read the PDF file in binary mode
                    with open(input_filepath, "rb") as pdf_file:
                        binary_data = pdf_file.read()

                    # Encode the binary data to Base64 (required for Odoo binary fields)
                    encoded_data = base64.b64encode(binary_data).decode("utf-8")
                    record = self.env['title.document'].create({
                        'pdf': encoded_data,  # Binary field storing the PDF
                        'type': 'pdf',
                        'file': encoded_data,
                    })
                    return {
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'title.document',
                        'res_id': record.id,  # Open the created record
                        'target': 'new',
                    }
                except Exception as e:
                    _logger.info(f"Error saving PDF to binary field: {e}")
                try:
                    # Read the PDF file in binary mode
                    with open(input_filepath, "rb") as pdf_file:
                        binary_data = base64.b64encode(pdf_file.read())
                    _logger.info(binary_data)
                    # Write the binary data to a new file
                    # with open(output_binary_path, "wb") as binary_file:
                    #     binary_file.write(binary_data)
                except Exception as e:
                    _logger.info(f"Error: {e}")
            elif input_filepath.lower().endswith((".jpg", ".png", ".jpeg")):
                # Handle TIFF
                img = Image.open(input_filepath)
                img_buffer = BytesIO()
                img.save(img_buffer, format=output_format.upper())
                img_buffer.seek(0)
                # Encode the image to base64
                encoded_image = base64.b64encode(img_buffer.read())
                return {
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'title.document',
                    'target': 'new',
                    'context': {
                        'default_image': encoded_image,
                        'default_file': encoded_image.decode('utf-8'),
                        'default_type': 'image'
                    },
                }
            elif input_filepath.lower().endswith((".tif", ".tiff")):
                img = TiffImagePlugin.TiffImageFile(input_filepath)
                img.load()  # Force loading the image
                _logger.info('img: %s', img)
                img_buffer = BytesIO()
                img.save(img_buffer, format="TIFF")  # Save as TIFF format
                binary_data = base64.b64encode(img_buffer.getvalue())
                output = io.BytesIO()

                # Handle multi-page TIFF conversion
                if img.n_frames > 1:
                    img.save(output, format="PDF", save_all=True,
                             append_images=[img.seek(i) or img.copy() for i in
                                            range(1, img.n_frames)])
                else:
                    img.save(output, format="PDF")  # Single page TIFF

                pdf_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
                record = self.env['title.document'].create({
                    'pdf': pdf_base64,  # Binary field storing the PDF
                    'type': 'pdf',
                    'file': binary_data,
                })
                _logger.info("Created title.document record with ID: %s",
                             record.id)
                return {
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'title.document',
                    'res_id': record.id,  # Open the created record
                    'target': 'new',
                }
            else:
                raise ValidationError(
                    "Unsupported file type. Only PDF and TIFF are supported.")
        except Exception as e:
            _logger.info(f"Error: {e}")

    def download_tiff(self):
        """Redirect to TIFF file download route"""
        self.ensure_one()
        if not os.path.isfile(self.file_path):
            raise UserError(_("File is not found"))
        if self.file_path.lower().endswith((".jpg", ".png", ".jpeg", ".tif", ".tiff", ".pdf")):
            return {
                'type': 'ir.actions.act_url',
                'url': f'/download/tiff/{self.id}',
                'target': 'self',
            }

    #
    # def open_images(self):
    #     input_filepath = self.file_path
    #     output_format = "PNG"
    #     try:
    #         # try:
    #         #     if os.path.exists(input_filepath):
    #         #         with open(input_filepath, 'r') as file:
    #         #             content = file.read()
    #         #         return content
    #         #     else:
    #         #         return "File not found."
    #         # except Exception as e:
    #         #     return f"An error occurred: {str(e)}"
    #         # Removed this for adding latest code
    #         if input_filepath.lower().endswith(".pdf"):
    #             try:
    #                 # Read the PDF file in binary mode
    #                 with open(input_filepath, "rb") as pdf_file:
    #                     binary_data = pdf_file.read()
    #
    #                 # Encode the binary data to Base64 (required for Odoo binary fields)
    #                 encoded_data = base64.b64encode(binary_data).decode("utf-8")
    #                 return {
    #                     'type': 'ir.actions.act_window',
    #                     'view_mode': 'form',
    #                     'res_model': 'title.document',
    #                     'target': 'new',
    #                     'context': {
    #                         'default_pdf': encoded_data,
    #                         'default_type': 'pdf'
    #                     },
    #                 }
    #                 # Save the encoded data to the binary field in the record
    #                 _logger.info(
    #                     f"PDF saved successfully to record ID {record.id} in field {binary_field}.")
    #             except Exception as e:
    #                 _logger.info(f"Error saving PDF to binary field: {e}")
    #             try:
    #                 # Read the PDF file in binary mode
    #                 with open(input_filepath, "rb") as pdf_file:
    #                     binary_data = base64.b64encode(pdf_file.read())
    #                 _logger.info(binary_data)
    #                 # Write the binary data to a new file
    #                 # with open(output_binary_path, "wb") as binary_file:
    #                 #     binary_file.write(binary_data)
    #
    #                 _logger.info(
    #                     f"Binary file saved successfully to: {output_binary_path}")
    #             except Exception as e:
    #                 _logger.info(f"Error: {e}")
    #         elif input_filepath.lower().endswith((".tif", ".tiff")):
    #             with Image.open(input_filepath) as img:
    #                 output = io.BytesIO()
    #                 img.save(output, format="PDF", save_all=True,
    #                          append_images=[img.seek(i) or img.copy() for i in
    #                                         range(1, img.n_frames)])
    #                 png_base64 = base64.b64encode(output.getvalue()).decode(
    #                     'utf-8')
    #             pdf = png_base64
    #             type = 'pdf'
    #             pass
    #
    #         elif input_filepath.lower().endswith((".tif", ".tiff", ".jpg", ".png", ".jpeg")):
    #             # Handle TIFF
    #             img = Image.open(input_filepath)
    #             img_buffer = BytesIO()
    #             img.save(img_buffer, format=output_format.upper())
    #             img_buffer.seek(0)
    #
    #             # Encode the image to base64
    #             encoded_image = base64.b64encode(img_buffer.read())
    #             return {
    #                 'type': 'ir.actions.act_window',
    #                 'view_mode': 'form',
    #                 'res_model': 'title.document',
    #                 'target': 'new',
    #                 'context': {
    #                     'default_image': encoded_image,
    #                     'default_type': 'image'
    #                 },
    #             }
    #         else:
    #             raise ValidationError(
    #                 "Unsupported file type. Only PDF and TIFF are supported.")
    #
    #     except Exception as e:
    #         _logger.info(f"Error: {e}")
    #
    # def action_open_file(self):
    #     """Open files"""
    #     """ Open a file locally on a Windows server """
    #     for record in self:
    #         pdf = ""
    #         image = ""
    #         type = ""
    #         file_path = record.file_path.strip()
    #         _logger.info('file_path: %s', file_path)
    #         if file_path.lower().endswith(".tif") or file_path.lower().endswith(".tiff"):
    #             img = TiffImagePlugin.TiffImageFile(file_path)
    #             img.load()  # Force loading the image
    #             _logger.info('img: %s', img)
    #             output = io.BytesIO()
    #             img.save(output, format="PDF", save_all=True,
    #                      append_images=[img.seek(i) or img.copy() for i in
    #                                     range(1, img.n_frames)])
    #             png_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
    #             _logger.info('png_base64: %s', png_base64[:20])
    #             with open("/home/cybro-megha/odoo16/JPCEnquiry_Jan_31/at3_1m4.pdf", "wb") as f:
    #                 f.write(output.getvalue())
    #             pdf = output.getvalue()
    #             type = "pdf"
    #         if file_path.lower().endswith(".jpeg") or file_path.lower().endswith(".gif") or file_path.lower().endswith(".png") :
    #             with Image.open(file_path) as img:
    #                 # img = Image.open(file_path)
    #                 # img.load()
    #                 _logger.info('img: %s', img)
    #                 img_bytes_io = io.BytesIO()
    #                 img.save(img_bytes_io,
    #                          format=img.format)  # Use the original format
    #                 img_binary = img_bytes_io.getvalue()  # Get binary data
    #
    #                 _logger.info("Binary image size: %d bytes", len(img_binary))
    #             image = img_binary
    #             type = 'image'
    #         document = self.env['title.document'].create({
    #             'pdf': pdf,
    #             'image': image,
    #             'type': type,
    #         })
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'view_mode': 'form',
    #             'res_model': 'title.document',
    #             'target': 'new',
    #             # 'red_id': document.id,
    #             'domain': [('id', '=', document.id)],
    #             'context': {
    #                 'default_pdf': pdf,
    #                 'default_type': type
    #             },
    #         }
    #
    def action_open_trim_file(self):
        """Open files"""
        """ Open a file locally on a Windows server """
        for record in self:
            file_path = record.file_path.strip()
            if not file_path:
                raise ValidationError("File path is empty.")
            # if not os.path.exists(file_path):
            #     raise ValidationError(f"The file does not exist: {file_path}")
            try:
                if os.name == 'nt':  # windows
                    # subprocess.run(["cmd", "/c", "start", file_path],
                    #                check=True, shell=True)
                    # file_path = fr'{file_path}'
                    _logger.info('file_path: %s', file_path)
                    # os.system('explorer')
                    if os.path.exists(file_path):
                        try:
                            network_path = os.path.dirname(file_path)

                            # Map the network drive
                            subprocess.run(
                                [
                                    "net",
                                    "use",
                                    network_path,
                                    'Logmein@123',
                                    "/user:" + 'Nated@jhbproperty.co.za'
                                ],
                                check=True,
                                shell=True,
                            )

                            # Open the file
                            os.startfile(file_path)

                            # subprocess.run(["start", file_path], shell=True)
                            # # os.startfile(file_path)  # Open file with default application
                            # # subprocess.Popen(['explorer', '/select,', file_path])
                            # _logger.info('Opened file using os.startfile: %s',
                            #              file_path)
                        except Exception as e:
                            _logger.info('Failed to open file: %s', e)
                    else:
                        _logger.info('File does not exist: %s', file_path)
                    # subprocess.Popen(['explorer', file_path])
                elif os.name == 'posix':  # Linux/Mac
                    subprocess.Popen(['xdg-open', file_path])
            except Exception as e:
                raise ValidationError(f"Failed to open file: {str(e)}")
        # if self.file_path:
        #     file_path = self.file_path.strip()
        #     _logger.info('file_path: %s', file_path)
        #     _logger.info('exists: %s', os.path.exists(file_path))
        #     if os.path.exists(file_path):
        #         _logger.info('OS Name: %s', os.name)
        #         if os.name == 'nt':  # Windows
        #             _logger.info('nt os: %s', file_path)
        #             subprocess.Popen(['explorer', file_path])
        #         elif os.name == 'posix':  # Linux/Mac
        #             subprocess.Popen(['xdg-open', file_path])
        #         else:
        #             raise ValidationError("Unsupported OS")
        #     else:
        #         raise ValidationError("The specified file path does not exist.")
        # else:
        #     raise ValidationError("File path is empty.")


class TitleDocument(models.TransientModel):
    _name = 'title.document'
    _description = "Title Documents"

    image = fields.Binary(string="Images")
    pdf = fields.Binary(string="Pdf")
    file = fields.Binary(string="File")
    type = fields.Selection([('pdf', 'PDF'), ('image', 'Image')])

