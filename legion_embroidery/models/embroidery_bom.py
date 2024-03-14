from datetime import time, date

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, float_compare

from itertools import groupby
from collections import defaultdict


class EmbroideryScarp(models.Model):
    _name = 'embroidery.bom'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'
    _description = 'embroidery Bill Of material'

    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id

    partner_id = fields.Many2one('res.partner', string="CUSTOMER")
    employee_id = fields.Many2one('hr.employee', string="EMPLOYEE", )
    product_tmpl_id = fields.Many2one('product.product', 'PRODUCT', required=True, store=True, )

    default_code = fields.Char(related='product_tmpl_id.default_code', string='PRODUCT NUMBER', readonly=True,
                               store=True, )

    # test_001 = fields.Float(string="Test 001", required=False)

    fabric_height = fields.Float(string="FABRIC HEIGHT", required=False)
    design_height = fields.Float(string="DESIGN HEIGHT", required=False)
    code = fields.Char('REFERENCE')
    active = fields.Boolean('Active', default=True)
    type = fields.Selection([
        ('normal', 'Manufacture this product'),
        ('phantom', 'Subcontracting'),
        ('Embroidery', 'Embroidery')], 'BOM TYPE',
        default='normal', required=True)
    product_id = fields.Many2one('product.product', 'PRODUCT',
                                 domain="['&', ('product_tmpl_id', '=', product_tmpl_id), ('type', 'in', ['product', "
                                        "'consu']),  '|', ('company_id', '=', False), ('company_id', '=', "
                                        "company_id)]", )
    bom_line_ids = fields.One2many('embroidery.bom.line', 'bom_id', 'BOM LINES', copy=True)
    net_ordering_lines = fields.One2many('embroidery.net.ordering.line', 'net_ordering_id', 'NET ORDERING LINES',
                                         copy=True)

    product_qty = fields.Float('REPEATS', default=1.0, required=True)
    ready_to_produce = fields.Selection([
        ('all_available', ' When all components are available'),
        ('asap', 'When components for 1st operation are available')], string='Manufacturing Readiness',
        default='asap', required=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'OPERATION TYPE',
                                      domain="[('code', '=', 'mrp_operation'), ('company_id', '=', company_id)]")
    company_id = fields.Many2one(
        'res.company', 'COMPANY', index=True,
        default=lambda self: self.env.company)
    consumption = fields.Selection([('strict', 'STRICT'), ('flexible', 'FLEXIBLE')], default='strict',
                                   string='CONSUMPTION')
    total_repeats = fields.Float(string="TOTAL REPEATS", required=False)
    total_head = fields.Float(string="HEAD", required=False, readonly=False, default=24)
    plotters_stitch = fields.Float(string="PLOTTERS STITCH", readonly=False, required=False, )
    total_fabric = fields.Float(string="TOTAL FABRIC", required=False, readonly=True)
    production_stitches = fields.Float(string="PRODUCTION STITCHES", required=False,
                                       compute='_compute_total_production_stitches')
    total_stitch = fields.Float(string="TOTAL STITCHES", required=False, readonly=True)
    total_cones = fields.Float(string="TOTAL CONES", required=False)
    po_bol = fields.Boolean(string="po boolean", default=False)
    complete_po = fields.Boolean(string="complete po", default=True)

    # def name_get(self):
    #     return [(bom.id, '%s%s' % (bom.code and '%s: ' % bom.code or '', bom.product_tmpl_id.display_name)) for bom in
    #             self]

    display_name = fields.Char(compute='_compute_display_name')

    @api.depends('code', 'product_tmpl_id')
    def _compute_display_name(self):
        for trace in self:
            trace.display_name = '%s: %s' % (trace.code, trace.product_tmpl_id.display_name)

    """COMPUTE METHOD FOR FORM FIELDS COMPUTATION"""

    @api.depends('production_stitches', 'total_head', 'plotters_stitch', 'total_stitch', 'total_repeats',
                 'total_fabric')
    def _compute_total_production_stitches(self):
        for rec in self:
            rec.production_stitches = rec.total_repeats * rec.plotters_stitch
            print('total production stitches : ', rec.production_stitches)
            rec.total_stitch = rec.plotters_stitch * (rec.total_repeats * rec.total_head)
            print('total stitches : ', rec.total_stitch)
            if rec.total_head == 24:
                rec.total_fabric = rec.total_repeats * 8.5
                print('total fabric if head 24 : ', rec.total_fabric)
            if rec.total_head == 8:
                rec.total_fabric = rec.total_repeats * 2.9
                print('total fabric if head 8 : ', rec.total_fabric)

    """API CONSTRAINTS FOR FABRIC AND DESIGN WIDTH"""

    @api.constrains('design_height')
    def _check_design_height(self):
        for rec in self:
            if rec.design_height > rec.fabric_height:
                raise ValidationError("Design Height Should be 4 Inch Less Than Fabric Height.")

    """ONCHANGE METHOD FOR EMBROIDERY COMPONENTS"""

    @api.onchange('bom_line_ids')
    def onchange_method(self):
        print('onchange method')
        data = []
        for rec in self.bom_line_ids:
            rec.total_stitches = rec.stitches * (self.total_repeats * self.total_head)
            print('stitches', rec.stitches)
            print('total stitches', rec.total_stitches)
            rec.total_cones = rec.total_stitches / rec.consumption
            print('total cones', rec.total_cones)
            if rec.total_cones < 0.5:
                rec.total_cones = 1
                print('total cones if less than 0.5', rec.total_cones)
            rec.total_yard = rec.total_cones * 30000
            print('total yards', rec.total_yard)
            product = self.env['product.product'].search([('id', '=', rec.product_id.id)], limit=1)
            rec.available_stock = product.qty_available
            print('Product matched available quantity', product.qty_available)
            rec.net_cones = rec.total_cones - rec.available_stock
            print('Net cones', rec.net_cones)
            rec.lot_size = self.total_head
            print('Lot Size', rec.lot_size)
            rec.factor = rec.net_cones / rec.lot_size
            print('Factor with float', rec.factor)
            rec.real_factor = round(rec.net_cones / rec.lot_size + 0.10)
            print('Factor if float digit greater than 0.4 : ', rec.real_factor)
            if rec.real_factor < 0:
                rec.net_ordering = 0
                print('If Factor in Minus')
            else:
                rec.net_ordering = rec.lot_size * rec.real_factor
                print('If Factor In Plus', rec.net_ordering)

        # this work for ordering line model
        for line in self.bom_line_ids:
            data.append((0, 0, {
                'id': line.id,
                'product_id': line.product_id.id,
                'stitches': line.stitches,
                'attach': line.attach,
                'consumption': line.consumption,
                'total_stitches': line.total_stitches,
                'total_yard': line.total_yard,
                'total_cones': line.total_cones,
                'available_stock': line.available_stock,
                'lot_size': line.lot_size,
                'factor': line.factor,
                'real_factor': line.real_factor,
                'net_cones': abs(line.net_cones),
                'net_ordering': line.net_ordering
            }))
        self.net_ordering_lines = False
        self.net_ordering_lines = data

    """FUNCTION FOR PURCHASE ORDER NET ORDERING"""

    def action_to_purchase_order(self):
        print('Purchase Order Function')
        for product in self.net_ordering_lines:
            if product.net_ordering > 0:
                self.complete_po = True  # default true for complete po for every product line
                purchase_id = 0
                partner_id = product.product_id.partner_id
                po_id = self.env['purchase.order'].search([])

                for po in po_id:
                    if partner_id == po.partner_id:
                        purchase_id = po
                        self.complete_po = False  # if current partner matched we don't need to complete po
                        self.po_bol = True  # true and we need to add product in line
                        print('Already Partner There : po.partner_id', po.partner_id.name, 'partner_id',
                              partner_id.name)
                        for lines in po.order_line:
                            if lines.product_id == product.product_id and lines.product_qty == product.net_ordering:
                                print('Product Already There')
                                self.po_bol = False  # if product already in po then we don't need to create product
                                self.complete_po = False  # if partner and line matched we don't need to complete po

                if self.po_bol:
                    data = []
                    data.append((0, 0, {
                        'id': purchase_id,
                        'name': 'purchase order from Embroidery',
                        'product_id': product.product_id.id,
                        'product_qty': product.net_ordering,
                        'product_uom': product.product_id.uom_id.id,
                        'price_unit': False,
                        'date_planned': date.today(),
                    }))
                    purchase_id.order_line = data
                    data.clear()
                    self.po_bol = False
                    self.complete_po = False  # if line added for current partner we don't need for complete po
                    print('Added lines For this partner_id : ', partner_id.name, 'id is ', purchase_id)

                if self.complete_po:
                    new_po = self.env['purchase.order'].create({
                        'partner_id': partner_id.id,
                        'company_id': self.env.company.id,
                        'date_order': date.today(),
                    })
                    data = []
                    data.append((0, 0, {
                        'id': new_po,
                        'name': 'purchase order from Embroidery',
                        'product_id': product.product_id.id,
                        'product_qty': product.net_ordering,
                        'product_uom': product.product_id.uom_id.id,
                        'price_unit': False,
                        'date_planned': date.today(),
                    }))
                    new_po.order_line = data
                    print('purchase order created for ', partner_id.name, 'purchase order number', new_po)
                    self.complete_po = False  # if line added for current partner we don't need for complete po


class MrpBomLine(models.Model):
    _name = 'embroidery.bom.line'
    _rec_name = "product_id"
    _description = 'Embroidery Bill of Material Line'

    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id

    bom_id = fields.Many2one('embroidery.bom', 'BOM', ondelete='cascade')
    company_id = fields.Many2one(related='bom_id.company_id', store=True, index=True, readonly=True)
    product_id = fields.Many2one('product.product', 'COMPONENTS', required=True, check_company=True)
    attach = fields.Char(string="ATTACH", required=False, )
    stitches = fields.Float(string="STITCHES", required=False)
    consumption = fields.Float(string="CONSUMPTION", required=False, default=300000)
    total_stitches = fields.Float(string="TOTAL STITCHES", required=False, readonly=True)
    total_yard = fields.Float(string="TOTAL YARD", required=False, readonly=True)
    total_cones = fields.Float(string="TOTAL CONES", required=False, readonly=True)
    available_stock = fields.Float(string="INVENTORY", required=False, readonly=True)
    net_cones = fields.Float(string="NET CONE", required=False)
    lot_size = fields.Float(string="LOT SIZE", required=False)
    factor = fields.Float(string="FACTOR", required=False)
    real_factor = fields.Float(string="FACTOR", required=False)
    net_ordering = fields.Float(string="NET ORDERING", required=False)


class NetOrderingLines(models.Model):
    _name = 'embroidery.net.ordering.line'
    _description = 'Embroidery net ordering lines'

    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id

    net_ordering_id = fields.Many2one('embroidery.bom', 'NET ORDERING', ondelete='cascade')
    company_id = fields.Many2one(related='net_ordering_id.company_id', store=True, index=True, readonly=True)
    product_id = fields.Many2one('product.product', 'COMPONENTS', required=True, check_company=True)
    stitches = fields.Float(string="STITCHES", required=False)
    consumption = fields.Float(string="CONSUMPTION", required=False)
    attach = fields.Char(string="ATTACH", required=False, )
    total_stitches = fields.Float(string="TOTAL STITCHES", required=False, readonly=True)
    total_yard = fields.Float(string="TOTAL YARD", required=False, readonly=True)
    total_cones = fields.Float(string="TOTAL CONES", required=False, readonly=True)
    available_stock = fields.Float(string="INVENTORY", required=False, readonly=True)
    net_cones = fields.Float(string="NET CONE", required=False)
    lot_size = fields.Float(string="LOT SIZE", required=False)
    factor = fields.Float(string="FACTOR", required=False)
    real_factor = fields.Float(string="FACTOR", required=False)
    net_ordering = fields.Float(string="NET ORDERING", required=False)
