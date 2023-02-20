# -*- coding: utf-8 -*-
from odoo import http
from ..models.s3_constants import *
import werkzeug


class TeamsIntegration(http.Controller):
    @http.route(AWS_REDIRECT_URI, auth='public')
    def index(self, **kw):
        return werkzeug.utils.redirect(AWS_REDIRECT_ODOO_URI)
