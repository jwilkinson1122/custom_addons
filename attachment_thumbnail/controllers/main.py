# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

import logging
from odoo import http
from odoo.http import request
from odoo.http import Controller, request, route
# from odoo.addons.web.http import Controller, route, request
import base64

_logger = logging.getLogger(__name__)

class PdfThumbController(Controller):

    @route(['/web/pdfthumb/<int:record_id>'], type='http', auth='public')
    def content(self, record_id, xmlid=None, model='ir.attachment', id=None, field='datas', filename_field='datas_fname', unique=None, filename=None, mimetype=None, download=None, width=0, height=0):
        attach_id = request.env['ir.attachment'].browse(record_id)
        result_dict = attach_id.read()[0]
        file = result_dict.get('datas_fname')
        image_base64 = base64.b64decode(attach_id.file_image_pdf)
        return image_base64

