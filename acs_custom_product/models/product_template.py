
from odoo import api, fields, models, tools, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    health_register = fields.Char('Registro sanitario')
    digemit_code = fields.Char('Código DIGEMID')
    therapeutic_ids = fields.Many2many('product.therapeutic.action', string='Acción Farmacológica')
    pathology_ids = fields.Many2many('product.pathology', string='Patología')
    active_principle_ids = fields.Many2many('product.active.principle', string='Principio activo')
    laboratory_id = fields.Many2one('product.laboratory', string='Laboratorio')
    unit_box = fields.Float('Precio #2')
    blister_box = fields.Float('Precio #3')
    unit_blister = fields.Float('Unidades x blister')
    alert_cant_stock = fields.Float('Alerta cant. de stock')
    udm_unit_box = fields.Many2one('uom.uom', string='Udm #2')
    udm_blister_box = fields.Many2one('uom.uom', string='Udm #3')
    type_cost = fields.Char('Tipo de costo')
    utility = fields.Float(string='Utilidad', compute="_compute_utility")
    incentive = fields.Float('Incentivo')

    unit_for_box = fields.Float('Unidad x caja')
    blister_for_box = fields.Float('Blister x caja')
    unit_for_blister = fields.Float('Unidades x blister', compute="_compute_unit_for_blister")
    
    margin = fields.Float(string='Margen', compute="_compute_margin")
    is_prescription = fields.Boolean("Receta Medica") 
    is_incentive = fields.Boolean("Aplicar Incentivo") 

    @api.depends('utility')
    def _compute_margin(self):
        for rec in self:
            if rec.utility and rec.standard_price:
                rec.margin = rec.utility * 100 / rec.standard_price
            else:
                rec.margin = False

    def _compute_unit_for_blister(self):
        for template in self:
            template.unit_for_blister = 0.0
            if template.blister_for_box:
                template.unit_for_blister = template.unit_for_box / template.blister_for_box

    def _compute_utility(self):
        for template in self:
            template.utility = template.list_price - template.standard_price
