# -*- coding: utf-8 -*-
import functools
from functools import partial
import logging
import os
import psycopg2
import pytz
import random
import json
from barcode import EAN13
from barcode.writer import ImageWriter
import base64
from base64 import b64encode
from datetime import date, datetime, timedelta
from io import BytesIO
from itertools import groupby
from random import randrange

_logger = logging.getLogger(__name__)

from odoo import fields, models, api, _, tools
from odoo.exceptions import UserError, ValidationError
from odoo.osv.expression import AND
from odoo.tools import config, float_is_zero, float_compare, float_round, DEFAULT_SERVER_DATETIME_FORMAT


class MeasurementCategory(models.Model):
    _name = "pod.measurement.group"
    _description = "Measurement Category"

    date = fields.Date(string='Date', default=fields.Date.today(), tracking=True)
    partner_id = fields.Many2one('res.partner', domain=[('is_patient','=',True)],string="Patient", required= True)
    category_id = fields.Many2one('pos.category', string='Category', required=True)
    measurement_ids = fields.One2many('measurement.measurement', 'measurement_cat_id', 'Measurements')
    measurement_unit = fields.Many2one('uom.uom', string='Measurement Unit', required=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', ondelete='cascade')


class Measurement(models.Model):
    _name = 'measurement.measurement'
    _description = 'Measurement Record'
    _rec_name = 'name'

    name = fields.Char(compute="_compute_measurement_name")
    measurement_cat_id = fields.Many2one('pod.measurement.group', string='Measurement Category', required=True, ondelete='cascade')
    measurement = fields.Char('Measurement')
    measurement_type = fields.Many2one('measurement.type', string='Measurement Type', required=True)
    laterality = fields.Selection([('left', 'Left'), ('right', 'Right'), ('bilateral', 'Bilateral')], string="Laterality")

    @api.depends('measurement_type', 'measurement', 'laterality')
    def _compute_measurement_name(self):
        """Compute a descriptive name based on measurement type, value, and laterality."""
        for rec in self:
            laterality_display = dict(self.fields_get(allfields=['laterality'])['laterality']['selection']).get(rec.laterality)
            rec.name = f"{rec.measurement_type.name}: {rec.measurement} ({laterality_display})" if rec.measurement_type and rec.measurement else False

    # @api.depends('measurement_type', 'measurement')
    # def _compute_measurement_name(self):
    #     """Compute a descriptive name based on measurement type and value."""
    #     for rec in self:
    #         rec.name = f"{rec.measurement_type.name}: {rec.measurement}" if rec.measurement_type and rec.measurement else False
            

class MeasurementType(models.Model):
    _name = "measurement.type"
    _description = "Type of Measurements"

    name = fields.Char(string="Name")

