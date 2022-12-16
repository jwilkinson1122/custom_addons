# -*- coding: utf-8 -*-

from odoo.http import request, Controller, route


class MultiSStepFormController(Controller):

    @route(['/form'], type='http', auth='public', website=True, methods=['GET'])
    def form(self):
        return request.render('podiatry.podiatry_application_id', {

        })
