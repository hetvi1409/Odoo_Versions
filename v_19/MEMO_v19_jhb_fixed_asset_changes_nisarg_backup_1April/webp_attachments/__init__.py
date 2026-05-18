# -*- coding: utf-8 -*-
from PIL import Image

webp_plugin = False # to ensure the import once only
original_preinit = Image.preinit


# used python monkey patching to override default preinit of PIL.Image
def pre_init_with_webp():
    global webp_plugin
    if not webp_plugin:
        webp_plugin = True # do following only once
        try:
            from PIL import WebPImagePlugin
            assert WebPImagePlugin
        except ImportError:
            pass
    original_preinit()


Image.preinit = pre_init_with_webp

# convert_image_to_web => usage
# from odoo.addons.webp_attachments import convert_image_to_web
# or simply
# image_object = Image.open(src_path)
# image_object.save(des_path, format="webp")


def convert_image_to_web(des_path, src_path='', image_object=None):
    if not image_object:
        image_object = Image.open(src_path) # any image type like png, jpeg, bmp etc
    image_object.save(des_path, format="webp")
