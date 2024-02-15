# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class ForefootValue(models.Model):
    _name = 'forefoot.value'
    _rec_name = 'name'
    _description = 'Podiatry Forefoot Value'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")


class ForefootCorrection(models.Model):
    _name = 'forefoot.correction'
    _rec_name = 'name'
    _description = 'Podiatry Forefoot Correction'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")


class RearfootCorrection(models.Model):
    _name = 'rearfoot.correction'
    _rec_name = 'name'
    _description = 'Podiatry Rearfoot Correction'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")


class OrthoticMeasure(models.Model):
    _name = 'orthotic.measure'
    _rec_name = 'name'
    _description = 'Podiatry Orthotic Measure'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")


class PrescriptionOrderValues(models.Model):
    _inherit = 'prescription.order'


    laterality = fields.Selection([
            ('lt_single', 'Left'),
            ('rt_single', 'Right'),
            ('bl_pair', 'Bilateral')
        ], string='Laterality', required=True, default='bl_pair')

        # Forefoot Values
    ff_varus_lt = fields.Many2one(comodel_name='forefoot.value', string='FF Varus LT', ondelete='restrict', copy=True)
    ff_varus_rt = fields.Many2one(comodel_name='forefoot.value', string='FF Varus RT', ondelete='restrict', copy=True)
    ff_valgus_lt = fields.Many2one(comodel_name='forefoot.value', string='FF Valgus LT', ondelete='restrict', copy=True)
    ff_valgus_rt = fields.Many2one(comodel_name='forefoot.value', string='FF Valgus RT', ondelete='restrict', copy=True)
    # Forefoot Corrections
    ff_varus_intrinsic_lt = fields.Many2one(comodel_name='forefoot.correction', string='FF Varus Intrinsic LT', ondelete='restrict', copy=True)
    ff_varus_intrinsic_rt = fields.Many2one(comodel_name='forefoot.correction', string='FF Varus Intrinsic RT', ondelete='restrict', copy=True)
    ff_varus_extrinsic_lt = fields.Many2one(comodel_name='forefoot.correction', string='FF Varus Extrinsic LT', ondelete='restrict', copy=True)
    ff_varus_extrinsic_rt = fields.Many2one(comodel_name='forefoot.correction', string='FF Varus Extrinsic RT', ondelete='restrict', copy=True)
    ff_valgus_intrinsic_lt = fields.Many2one(comodel_name='forefoot.correction', string='FF Valgus Intrinsic LT', ondelete='restrict', copy=True)
    ff_valgus_intrinsic_rt = fields.Many2one(comodel_name='forefoot.correction', string='FF Valgus Intrinsic RT', ondelete='restrict', copy=True)
    ff_valgus_extrinsic_lt = fields.Many2one(comodel_name='forefoot.correction', string='FF Valgus Extrinsic LT', ondelete='restrict', copy=True)
    ff_valgus_extrinsic_rt = fields.Many2one(comodel_name='forefoot.correction', string='FF Valgus Extrinsic RT', ondelete='restrict', copy=True)

    # Rearfoot Corrections
    rf_varus_lt = fields.Many2one(comodel_name='rearfoot.correction', string='RF Varus LT', ondelete='restrict', copy=True)
    rf_varus_rt = fields.Many2one(comodel_name='rearfoot.correction', string='RF Varus RT', ondelete='restrict', copy=True)
    rf_valgus_lt = fields.Many2one(comodel_name='rearfoot.correction', string='RF Valgus LT', ondelete='restrict', copy=True)
    rf_valgus_rt = fields.Many2one(comodel_name='rearfoot.correction', string='RF Valgus RT', ondelete='restrict', copy=True)
    rf_neutral_lt = fields.Many2one(comodel_name='rearfoot.correction', string='RF Neutral LT', ondelete='restrict', copy=True)
    rf_neutral_rt = fields.Many2one(comodel_name='rearfoot.correction', string='RF Neutral RT', ondelete='restrict', copy=True)
 
    # Orthotic Measures
    ff_length_lt = fields.Many2one(comodel_name='orthotic.measure', string='FF Length LT', ondelete='restrict', copy=True)
    ff_length_rt = fields.Many2one(comodel_name='orthotic.measure', string='FF Length RT', ondelete='restrict', copy=True)
    heel_depth_lt = fields.Many2one(comodel_name='orthotic.measure', string='Heel Depth LT', ondelete='restrict', copy=True)
    heel_depth_rt = fields.Many2one(comodel_name='orthotic.measure', string='Heel Depth RT', ondelete='restrict', copy=True)
    orthotic_length_lt = fields.Many2one(comodel_name='orthotic.measure', string='Orthotic Length LT', ondelete='restrict', copy=True)
    orthotic_length_rt = fields.Many2one(comodel_name='orthotic.measure', string='Orthotic Length RT', ondelete='restrict', copy=True)
    cap_size_lt = fields.Many2one(comodel_name='orthotic.measure', string='Cap Size LT', ondelete='restrict', copy=True)
    cap_size_rt = fields.Many2one(comodel_name='orthotic.measure', string='Cap Size RT', ondelete='restrict', copy=True)
