# -*- coding: utf-8 -*-


from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_prescription_sale = fields.Boolean("Devices")
    module_website_prescription_meet = fields.Boolean("Discussion Rooms")
    module_website_prescription_track = fields.Boolean("Tracks and Agenda")
    module_website_prescription_track_live = fields.Boolean("Live Mode")
    module_website_prescription_track_quiz = fields.Boolean("Quiz on Tracks")
    module_website_prescription_exhibitor = fields.Boolean("Advanced Sponsors")
    module_website_prescription_questions = fields.Boolean("Registration Survey")
    module_prescription_barcode = fields.Boolean("Barcode")
    module_website_prescription_sale = fields.Boolean("Online Deviceing")
    module_prescription_booth = fields.Boolean("Booth Management")

    @api.onchange('module_website_prescription_track')
    def _onchange_module_website_prescription_track(self):
        """ Reset sub-modules, otherwise you may have track to False but still
        have track_live or track_quiz to True, meaning track will come back due
        to dependencies of modules. """
        for config in self:
            if not config.module_website_prescription_track:
                config.module_website_prescription_track_live = False
                config.module_website_prescription_track_quiz = False
