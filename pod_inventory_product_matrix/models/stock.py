# -*- coding: utf-8 -*-
import json
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, float_compare, float_round, format_date, groupby


class StockMove(models.Model):
    _inherit = 'stock.move'

    """ Matrix loading and update: fields and methods :

    NOTE: The matrix functionality was done in python, server side, to avoid js
        restriction.  Indeed, the js framework only loads the x first lines displayed
        in the client, which means in case of big matrices and lots of po_lines,
        the js doesn't have access to the 41st and following lines.

        To force the loading, a 'hack' of the js framework would have been needed...
    """
    product_template_id = fields.Many2one('product.template',
                                          compute='_compute_product_template_id',
                                          readonly=False,
                                          search='_search_product_template_id')
    is_configurable_product = fields.Boolean('Is the product configurable?',
                                             related="product_template_id.has_configurable_attributes")
    product_template_attribute_value_ids = fields.Many2many(related='product_id.product_template_attribute_value_ids',
                                                            readonly=True)
    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value',
                                                              string='Product attribute values that do not create '
                                                                     'variants',
                                                              ondelete='restrict')
    inventory_product_add_mode = fields.Selection(related='product_template_id.inventory_product_add_mode', depends=['product_template_id'])

    @api.depends('product_id')
    def _compute_product_template_id(self):
        for line in self:
            line.product_template_id = line.product_id.product_tmpl_id

    @staticmethod
    def _search_product_template_id(operator, value):
        return [('product_id.product_tmpl_id', operator, value)]

    @api.onchange('product_template_id')
    def onchange_invoice_product_id(self):
        for line in self:
            if len(line.product_template_id.product_variant_ids) > 1:
                line.write(
                    {'product_template_id': line.product_template_id, 'product_id': False, 'description_picking': False,
                     'quantity': 0.0, 'product_uom_qty': 0.0})
            else:
                line.write({'quantity': 0.0, 'product_uom_qty': 0.0})


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    report_grids = fields.Boolean(string="Print Variant Grids", default=True)
    grid_product_tmpl_id = fields.Many2one('product.template', store=False,
                                           help="Technical field for product_matrix functionalities.")
    grid_update = fields.Boolean(default=False, store=False,
                                 help="Whether the grid field contains a new matrix to apply or not.")
    grid = fields.Char(store=False,
                       help="Technical storage of grid. \nIf grid_update, will be loaded on the PO. \nIf not, represents the matrix to open.")

    @api.onchange('move_ids_without_package')
    def _move_onchange_product_id(self):
        for line in self.move_ids_without_package:
            if line.product_template_id:
                product = line.product_id.with_context(lang=line._get_lang())
                line.name = product.partner_ref
                line.location_id = line.picking_id.location_id.id
                line.location_dest_id = line.picking_id.location_dest_id.id
                if product:
                    line.description_picking = product._get_description(line.picking_type_id)

    @api.onchange('grid_product_tmpl_id')
    def _set_grid_up(self):
        if self.grid_product_tmpl_id:
            self.grid_update = False
            self.grid = json.dumps(self._get_matrix(self.grid_product_tmpl_id))

    def _must_delete_date_planned(self, field_name):
        return super()._must_delete_date_planned(field_name) or field_name == "grid"

    @api.onchange('grid')
    def _apply_grid(self):
        """Apply the given list of changed matrix cells to the current move."""
        if self.grid and self.grid_update:
            grid = json.loads(self.grid)
            product_template = self.env['product.template'].browse(grid['product_template_id'])
            dirty_cells = grid['changes']
            Attrib = self.env['product.template.attribute.value']
            default_stock_move_line_vals = {}
            new_lines = []
            for cell in dirty_cells:
                combination = Attrib.browse(cell['ptav_ids'])
                no_variant_attribute_values = combination - combination._without_no_variant_attributes()

                # create or find product variant from combination
                product = product_template._create_product_variant(combination)
                move_line_ids_without_package_lines = self.move_ids_without_package.filtered(
                    lambda line: line.product_id.id == product.id
                                 and line.product_no_variant_attribute_value_ids.ids == no_variant_attribute_values.ids
                )

                # if product variant already exist in move lines
                old_qty = sum(move_line_ids_without_package_lines.mapped('product_uom_qty'))
                qty = cell['qty']
                diff = qty - old_qty

                if not diff:
                    continue

                # TODO keep qty check? cannot be 0 because we only get cell changes ...
                if move_line_ids_without_package_lines:
                    if qty == 0:
                        if self.state in ['draft', 'done']:
                            # Remove lines if qty was set to 0 in matrix
                            self.move_ids_without_package -= move_line_ids_without_package_lines
                        else:
                            move_line_ids_without_package_lines.update({'product_uom_qty': 0.0})
                    else:
                        """
                        When there are multiple lines for same product and its quantity was changed in the matrix,
                        An error is raised.

                        A 'good' strategy would be to:
                            * Sets the quantity of the first found line to the cell value
                            * Remove the other lines.

                        But this would remove all business logic linked to the other lines...
                        Therefore, it only raises an Error for now.
                        """
                        if len(move_line_ids_without_package_lines) > 1:
                            raise ValidationError(
                                _("You cannot change the quantity of a product present in multiple move lines."))
                        else:
                            move_line_ids_without_package_lines[0].product_uom_qty = qty
                else:
                    if not default_stock_move_line_vals:
                        StockMoveObj = self.env['stock.move']
                        default_stock_move_line_vals = StockMoveObj.default_get(StockMoveObj._fields.keys())
                    last_sequence = self.move_ids_without_package[-1:].sequence
                    if last_sequence:
                        default_stock_move_line_vals['sequence'] = last_sequence
                    new_lines.append((0, 0, dict(
                        default_stock_move_line_vals,
                        product_id=product.id,
                        product_uom_qty=qty,
                        product_no_variant_attribute_value_ids=no_variant_attribute_values.ids)
                                      ))
            if new_lines:
                # Add new move lines
                self.update(dict(move_ids_without_package=new_lines))

    def _get_matrix(self, product_template):
        """Return the matrix of the given product, updated with current SOLines quantities.
            :param product.template product_template:
            :return: matrix to display
        """
        def has_ptavs(line, sorted_attr_ids):
            ptav = line.product_template_attribute_value_ids.ids
            pnav = line.product_no_variant_attribute_value_ids.ids
            pav = pnav + ptav
            pav.sort()
            return pav == sorted_attr_ids

        matrix = product_template.with_context(res_model=self._name)._get_template_matrix(
            company_id=self.company_id,
            currency_id=self.company_id.currency_id)
        if self.move_ids_without_package:
            lines = matrix['matrix']
            if product_template.inventory_product_add_mode == 'product_configurator':
                lines = matrix['matrix']
            move_ids_without_package_line = self.move_ids_without_package.filtered(
                lambda line: line.product_template_id == product_template)
            for line in lines:
                for cell in line:
                    if not cell.get('name', False):
                        line = move_ids_without_package_line.filtered(lambda line: has_ptavs(line, cell['ptav_ids']))
                        if line:
                            cell.update({
                                'qty': sum(line.mapped('product_qty'))
                            })
        return matrix

    def get_report_matrixes(self):
        """Reporting method."""
        matrixes = []
        if self.report_grids:
            grid_configured_templates = self.move_ids_without_package.filtered(
                'is_configurable_product').product_template_id
            # TODO is configurable product and product_variant_count > 1
            for template in grid_configured_templates:
                if len(self.move_ids_without_package.filtered(lambda line: line.product_template_id == template)) > 1:
                    matrix = self._get_matrix(template)
                    matrix_data = []
                    for row in matrix['matrix']:
                        if any(column['qty'] != 0 for column in row[1:]):
                            matrix_data.append(row)
                    matrix['matrix'] = matrix_data
                    matrixes.append(matrix)
        return matrixes
