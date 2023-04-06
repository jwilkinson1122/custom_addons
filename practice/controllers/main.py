# -*- coding: utf-8 -*-

from werkzeug.exceptions import NotFound

from odoo.http import Controller, request, route, content_disposition


class PracticeController(Controller):

    @route(['''/practice/<model("practice.practice"):practice>/ics'''], type='http', auth="public")
    def practice_ics_file(self, practice, **kwargs):
        files = practice._get_ics_file()
        if not practice.id in files:
            return NotFound()
        content = files[practice.id]
        return request.make_response(content, [
            ('Content-Type', 'application/octet-stream'),
            ('Content-Length', len(content)),
            ('Content-Disposition', content_disposition('%s.ics' % practice.name))
        ])
