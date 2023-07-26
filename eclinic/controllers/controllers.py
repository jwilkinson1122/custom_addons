from odoo import http
from odoo.http import request
import io
from reportlab.pdfgen import canvas


class Eclinic(http.Controller):

    @http.route('/eclinic/download_pdf_hello_world', type='http', auth="public")
    def download_pdf_hello_world(self, **kwargs):
        response = http.Response()
        pdf_file = io.BytesIO()
        pdf = canvas.Canvas(pdf_file)
        pdf.drawString(100, 750, "Hello World")
        pdf.save()
        pdf_file.seek(0)
        response.stream.write(pdf_file.read())
        response.stream.flush()
        response.headers.set('Content-Disposition', 'attachment; filename="hello_world.pdf"')
        response.set_cookie('fileToken', 'hello_world')
        response.status = '200 OK'
        response.content_type = 'application/pdf'
        return response
