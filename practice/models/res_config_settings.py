# -*- coding: utf-8 -*-


from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_practice_sale = fields.Boolean("Devices")
    module_website_practice_meet = fields.Boolean("Discussion Rooms")
    module_website_practice_track = fields.Boolean("Tracks and Agenda")
    module_website_practice_track_live = fields.Boolean("Live Mode")
    module_website_practice_track_quiz = fields.Boolean("Quiz on Tracks")
    module_website_practice_exhibitor = fields.Boolean("Advanced Sponsors")
    module_website_practice_questions = fields.Boolean("Confirmation Survey")
    module_practice_barcode = fields.Boolean("Barcode")
    module_website_practice_sale = fields.Boolean("Online Deviceing")
    module_practice_booth = fields.Boolean("Booth Management")

    @api.onchange('module_website_practice_track')
    def _onchange_module_website_practice_track(self):
        """ Reset sub-modules, otherwise you may have track to False but still
        have track_live or track_quiz to True, meaning track will come back due
        to dependencies of modules. """
        for config in self:
            if not config.module_website_practice_track:
                config.module_website_practice_track_live = False
                config.module_website_practice_track_quiz = False
