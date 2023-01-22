# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ForefootValue(models.Model):
    _name = 'podiatry.forefoot.value'
    _rec_name = 'name'
    _description = 'Podiatry Forefoot Value'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")
    
    # forefoot varus values
    # ff_rt_varus = fields.char()
    # ff_lt_varus = fields.char()
    
    # @api.onchange('ff_rt_varus', 'ff_lt_varus')
    # def onchange_ff_varus(self):
    
    #     if self.ff_rt_varus and self.ff_rt_varus.isdigit():
    #         self.ff_rt_varus = "+" + "{:.2f}".format(float(self.ff_rt_varus))
    #     elif self.ff_rt_varus:
    #         if '-' in self.ff_rt_varus:
    #             self.ff_rt_varus = "{:.2f}".format(float(self.ff_rt_varus))
    #     if self.ff_lt_varus and self.ff_lt_varus.isdigit():
    #         self.ff_lt_varus = "+" + "{:.2f}".format(float(self.ff_lt_varus))
    #     elif self.ff_lt_varus:
    #         if '-' in self.ff_lt_varus:
    #             self.ff_lt_varus = "{:.2f}".format(float(self.ff_lt_varus))
    
    # forefoot valgus values
    # ff_rt_valgus = fields.char()
    # ff_lt_valgus = fields.char()
    
    # @api.onchange('ff_rt_valgus', 'ff_lt_valgus')
    # def onchange_ff_valgus(self):
    
    #     if self.ff_rt_valgus and self.ff_rt_valgus.isdigit():
    #         self.ff_rt_valgus = "+" + "{:.2f}".format(float(self.ff_rt_valgus))
    #     elif self.ff_rt_valgus:
    #         if '-' in self.ff_rt_valgus:
    #             self.ff_rt_valgus = "{:.2f}".format(float(self.ff_rt_valgus))
    #     if self.ff_lt_valgus and self.ff_lt_valgus.isdigit():
    #         self.ff_lt_valgus = "+" + "{:.2f}".format(float(self.ff_lt_valgus))
    #     elif self.ff_lt_valgus:
    #         if '-' in self.ff_lt_valgus:
    #             self.ff_lt_valgus = "{:.2f}".format(float(self.ff_lt_valgus))
    

class ForefootCorrection(models.Model):
    _name = 'podiatry.forefoot.correction'
    _rec_name = 'name'
    _description = 'Podiatry Forefoot Correction'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")
    
    # forefoot varus intrinsic values
    # ff_rt_varus_int = fields.char()
    # ff_lt_varus_int = fields.char()
    
    # @api.onchange('ff_rt_varus_int', 'ff_lt_varus_int')
    # def onchange_ff_varus_int(self):
    
    #     if self.ff_rt_varus_int and self.ff_rt_varus_int.isdigit():
    #         self.ff_rt_varus_int = "+" + "{:.2f}".format(float(self.ff_rt_varus_int))
    #     elif self.ff_rt_varus_int:
    #         if '-' in self.ff_rt_varus_int:
    #             self.ff_rt_varus_int = "{:.2f}".format(float(self.ff_rt_varus_int))
                
    #     if self.ff_lt_varus_int and self.ff_lt_varus_int.isdigit():
    #         self.ff_lt_varus_int = "+" + "{:.2f}".format(float(self.ff_lt_varus_int))
    #     elif self.ff_lt_varus_int:
    #         if '-' in self.ff_lt_varus_int:
    #             self.ff_lt_varus_int = "{:.2f}".format(float(self.ff_lt_varus_int))
    
    # forefoot varus extrinsic values
    # ff_rt_varus_ext = fields.char()
    # ff_lt_varus_ext = fields.char()
    
    # @api.onchange('ff_rt_varus_ext', 'ff_lt_varus_ext')
    # def onchange_ff_varus_int(self):
    
    #     if self.ff_rt_varus_ext and self.ff_rt_varus_ext.isdigit():
    #         self.ff_rt_varus_ext = "+" + "{:.2f}".format(float(self.ff_rt_varus_ext))
    #     elif self.ff_rt_varus_ext:
    #         if '-' in self.ff_rt_varus_ext:
    #             self.ff_rt_varus_ext = "{:.2f}".format(float(self.ff_rt_varus_ext))
    #     if self.ff_lt_varus_ext and self.ff_lt_varus_ext.isdigit():
    #         self.ff_lt_varus_ext = "+" + "{:.2f}".format(float(self.ff_lt_varus_ext))
    #     elif self.ff_lt_varus_ext:
    #         if '-' in self.ff_lt_varus_ext:
    #             self.ff_lt_varus_ext = "{:.2f}".format(float(self.ff_lt_varus_ext))
    
    # forefoot valgus intrinsic values
    # ff_rt_valgus_int = fields.char()
    # ff_lt_valgus_int = fields.char()
    
    # @api.onchange('ff_rt_valgus_int', 'ff_lt_valgus_int')
    # def onchange_ff_varus_int(self):
    
    #     if self.ff_rt_valgus_int and self.ff_rt_valgus_int.isdigit():
    #         self.ff_rt_valgus_int = "+" + "{:.2f}".format(float(self.ff_rt_valgus_int))
    #     elif self.ff_rt_valgus_int:
    #         if '-' in self.ff_rt_valgus_int:
    #             self.ff_rt_valgus_int = "{:.2f}".format(float(self.ff_rt_valgus_int))
    #     if self.ff_lt_valgus_int and self.ff_lt_valgus_int.isdigit():
    #         self.ff_lt_valgus_int = "+" + "{:.2f}".format(float(self.ff_lt_valgus_int))
    #     elif self.ff_lt_valgus_int:
    #         if '-' in self.ff_lt_valgus_int:
    #             self.ff_lt_valgus_int = "{:.2f}".format(float(self.ff_lt_valgus_int))
    
    # forefoot valgus extrinsic values
    # ff_rt_valgus_ext = fields.char()
    # ff_lt_valgus_ext = fields.char()
    
    # @api.onchange('ff_rt_valgus_ext', 'ff_lt_valgus_ext')
    # def onchange_ff_varus_int(self):
    
    #     if self.ff_rt_valgus_ext and self.ff_rt_valgus_ext.isdigit():
    #         self.ff_rt_valgus_ext = "+" + "{:.2f}".format(float(self.ff_rt_valgus_ext))
    #     elif self.ff_rt_valgus_ext:
    #         if '-' in self.ff_rt_valgus_ext:
    #             self.ff_rt_valgus_ext = "{:.2f}".format(float(self.ff_rt_valgus_ext))
    #     if self.ff_lt_valgus_ext and self.ff_lt_valgus_ext.isdigit():
    #         self.ff_lt_valgus_ext = "+" + "{:.2f}".format(float(self.ff_lt_valgus_ext))
    #     elif self.ff_lt_valgus_ext:
    #         if '-' in self.ff_lt_valgus_ext:
    #             self.ff_lt_valgus_ext = "{:.2f}".format(float(self.ff_lt_valgus_ext))
    
    
class RearfootCorrection(models.Model):
    _name = 'podiatry.rearfoot.correction'
    _rec_name = 'name'
    _description = 'Podiatry Rearfoot Correction'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")
    
    # forefoot varus values
    # ff_rt_varus = fields.char()
    # ff_lt_varus = fields.char()
    
    # forefoot valgus values
    # ff_rt_valgus = fields.char()
    # ff_lt_valgus = fields.char()
    
    # forefoot netural values
    # ff_rt_neutral = fields.char()
    # ff_lt_neutral = fields.char()
    

class OrthoticMeasure(models.Model):
    _name = 'podiatry.orthotic.measure'
    _rec_name = 'name'
    _description = 'Podiatry Orthotic Measure'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")
    
    # forefoot width values
    # ff_rt_width = fields.char()
    # ff_lt_width = fields.char()
    
    # heel depth values
    # heel_depth_rt = fields.char()
    # heel_depth_lt = fields.char()
    
    # length values
    # rt_length = fields.char()
    # lt_length = fields.char()
    
    # cap size values
    # rt_cap_size = fields.char()
    # lt_cap_size = fields.char()