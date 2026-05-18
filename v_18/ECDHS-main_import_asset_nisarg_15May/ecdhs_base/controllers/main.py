# -*- coding: utf-8 -*-

import io
import base64
import json
import zipfile
import unicodedata

from odoo import _, fields, http
from odoo.addons.mail.controllers.discuss import DiscussController
from odoo.addons.web.controllers.binary import clean
from odoo.exceptions import AccessError
from odoo.http import content_disposition, request
from odoo.tools import replace_exceptions
