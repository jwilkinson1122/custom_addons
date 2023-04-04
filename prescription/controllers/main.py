# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from werkzeug.exceptions import NotFound

from odoo.http import Controller, request, route, content_disposition


class PrescriptionController(Controller):

    @route(['''/prescription/<model("prescription.prescription"):prescription>/ics'''], type='http', auth="public")
    def prescription_ics_file(self, prescription, **kwargs):
        files = prescription._get_ics_file()
        if not prescription.id in files:
            return NotFound()
        content = files[prescription.id]
        return request.make_response(content, [
            ('Content-Type', 'application/octet-stream'),
            ('Content-Length', len(content)),
            ('Content-Disposition', content_disposition('%s.ics' % prescription.name))
        ])
