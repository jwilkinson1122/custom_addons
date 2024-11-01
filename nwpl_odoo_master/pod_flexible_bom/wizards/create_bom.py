from odoo import fields, models, api, _


class CreateMRPBOMWizard(models.TransientModel):
    _name = "create.mrp.bom.wizard"
    _description = "Create MRP BOM Wizard"

    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id

    # Add other fields as needed for creating the MRP BOM
    bom_template_id = fields.Many2one("mrp.bom", string="BOM Template")
    code = fields.Char('Reference')
    active = fields.Boolean('Active', default=True)
    type = fields.Selection([
        ('normal', 'Manufacture this product'),
        ('phantom', 'Kit')], 'BoM Type', default='normal', required=True)
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product', check_company=True, index=True, domain="[('type', 'in', ['product', 'consu'])]", required=True)
    product_id = fields.Many2one(
        'product.product', 'Product Variant', check_company=True, index=True, domain="['&', ('product_tmpl_id', '=', product_tmpl_id), ('type', 'in', ['product', 'consu'])]", help="If a product variant is defined the BOM is available only for this product.")
    bom_line_ids = fields.One2many('create.mrp.bom.wizard.line', 'bom_id', 'BoM Lines', copy=True)
    product_qty = fields.Float(
        'Quantity', default=1.0, digits='Product Unit of Measure', required=True, help="This should be the smallest quantity that this product can be produced in. If the BOM contains operations, make sure the work center capacity is accurate.")
    product_uom_id = fields.Many2one(
        'uom.uom', 'Unit of Measure', default=_get_default_product_uom_id, required=True, help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control", domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_tmpl_id.uom_id.category_id')
    sequence = fields.Integer('Sequence')
    ready_to_produce = fields.Selection([
        ('all_available', ' When all components are available'),
        ('asap', 'When components for 1st operation are available')], string='Manufacturing Readiness', default='all_available', required=True)
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type', domain="[('code', '=', 'mrp_operation')]", check_company=True, help=u"When a procurement has a ‘produce’ route with a operation type set, it will try to create "
             "a Manufacturing Order for that product using a BoM of the same operation type. That allows "
             "to define stock rules which trigger different manufacturing orders with different BoMs.")
    company_id = fields.Many2one(
        'res.company', 'Company', index=True, default=lambda self: self.env.company)
    consumption = fields.Selection([
        ('flexible', 'Allowed'),
        ('warning', 'Allowed with warning'),
        ('strict', 'Blocked')], help="Defines if you can consume more or less components than the quantity defined on the BoM:\n"
             "  * Allowed: allowed for all manufacturing users.\n"
             "  * Allowed with warning: allowed for all manufacturing users with summary of consumption differences when closing the manufacturing order.\n"
             "  Note that in the case of component Manual Consumption, where consumption is registered manually exclusively, consumption warnings will still be issued when appropriate also.\n"
             "  * Blocked: only a manager can close a manufacturing order when the BoM consumption is not respected.", default='warning', string='Flexible Consumption', required=True
    )
    possible_product_template_attribute_value_ids = fields.Many2many(
        'product.template.attribute.value', compute='_compute_possible_product_template_attribute_value_ids')
    allow_operation_dependencies = fields.Boolean('Operation Dependencies', help="Create operation level dependencies that will influence both planning and the status of work orders upon MO confirmation. If this feature is ticked, and nothing is specified, Odoo will assume that all operations can be started simultaneously."
    )
    produce_delay = fields.Integer(
        'Manufacturing Lead Time', default=0, help="Average lead time in days to manufacture this product. In the case of multi-level BOM, the manufacturing lead times of the components will be added. In case the product is subcontracted, this can be used to determine the date at which components should be sent to the subcontractor.")
    days_to_prepare_mo = fields.Integer( string="Days to prepare Manufacturing Order", default=0, help="Create and confirm Manufacturing Orders this many days in advance, to have enough time to replenish components or manufacture semi-finished products.\n"
             "Note that security lead times will also be considered when appropriate.")
    operation_ids = fields.One2many('mrp.routing.workcenter.wizard', 'wizard_id', 'Operations', copy=True)


    def create_bom(self):
        active_id = self._context.get('active_id')
        sale_order_line = self.env['sale.order.line'].browse(active_id)

        # Create the MRP BOM

        bom_values = {
            "product_tmpl_id": self.product_tmpl_id.id,
            "bom_template_id": self.bom_template_id.id,
            "type": self.type,
            "code": self.code,
            "company_id": self.company_id.id,
            "ready_to_produce": self.ready_to_produce,
            "consumption": self.consumption,
            "produce_delay": self.produce_delay,
            "days_to_prepare_mo": self.days_to_prepare_mo,
        }
        bom_lines = []
        for line in self.bom_line_ids:
            bom_line = {
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'product_uom_id': 1,
            }
            bom_lines.append((0, 0, bom_line))
        bom_values["bom_line_ids"] = bom_lines

        operation_lines = []
        for operation in self.operation_ids:
            operation_line = {
                'name': operation.name,
                'workcenter_id': operation.workcenter_id.id,
                'time_mode': operation.time_mode,
                'time_cycle': operation.time_cycle,
                'company_id': operation.company_id.id,
                'employee_ratio': operation.employee_ratio,
            }
            operation_lines.append((0, 0, operation_line))
        bom_values["operation_ids"] = operation_lines

        new_bom = self.env["mrp.bom"].create(bom_values)

        # Assign the newly created BOM to the sale order line
        sale_order_line.bom_id = new_bom.id
        total_cost = line.product_id._compute_bom_price(new_bom)
        # total_cost = 0.0
        # for line in sale_order_line.bom_id.bom_line_ids:
        #     total_cost += line.product_id.standard_price * line.product_qty
        if total_cost:
            sale_order_line.purchase_price = total_cost
        if sale_order_line.product_id.product_tmpl_id.margin:
            sale_order_line.price_unit = total_cost / (1 - sale_order_line.product_id.product_tmpl_id.margin)
        return {'type': 'ir.actions.act_window_close'}

    @api.onchange('bom_template_id')
    def _onchange_bom_template_id(self):
        if self.bom_template_id:
            # Clear existing lines
            self.bom_line_ids = [(5, 0, 0)]

            # Add lines from the template
            new_lines = []
            for line in self.bom_template_id.bom_line_ids:
                new_line_vals = {
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                    'product_uom_id': line.product_uom_id.id,
                    'product_tmpl_id': line.product_id.product_tmpl_id.id, # Assuming you need to link to product template as well
                }
                new_lines.append((0, 0, new_line_vals))
            self.bom_line_ids = new_lines
            operation_lines = []
            self.operation_ids = [(5,0,0)]

            for line in self.bom_template_id.operation_ids:
                new_line_vals = {
                    'wizard_id': self.id,
                    'name': line.name,
                    'workcenter_id': line.workcenter_id.id,
                    'company_id': line.company_id.id,
                    'time_mode': line.time_mode,
                    'employee_ratio': line.employee_ratio,
                    'time_cycle': line.time_cycle,
                }
                operation_lines.append((0, 0, new_line_vals))
            self.operation_ids = operation_lines

    @api.depends(
        'product_tmpl_id.attribute_line_ids.value_ids',
        'product_tmpl_id.attribute_line_ids.attribute_id.create_variant',
        'product_tmpl_id.attribute_line_ids.product_template_value_ids.ptav_active',
    )
    def _compute_possible_product_template_attribute_value_ids(self):
        for bom in self:
            bom.possible_product_template_attribute_value_ids = bom.product_tmpl_id.valid_product_template_attribute_line_ids._without_no_variant_attributes().product_template_value_ids._only_active()

class CreateMRPBOMWizardLine(models.TransientModel):
    _name = "create.mrp.bom.wizard.line"
    _description = "Temporary BoM Lines"

    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id

    product_id = fields.Many2one('product.product', 'Component', required=True, check_company=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', related='product_id.product_tmpl_id', store=True, index=True)
    company_id = fields.Many2one( related='bom_id.company_id', store=True, index=True, readonly=True)
    product_qty = fields.Float(
        'Quantity', default=1.0, digits='Product Unit of Measure', required=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure', default=_get_default_product_uom_id, required=True, help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control", domain="[('category_id', '=', product_uom_category_id)]")
    product_cost = fields.Float(string="Unit cost", related="product_id.product_tmpl_id.standard_price")
    product_total_cost = fields.Float(string="Total cost", compute="_compute_product_total_cost")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    sequence = fields.Integer(
        'Sequence', default=1, help="Gives the sequence order when displaying.")
    bom_id = fields.Many2one(
        'create.mrp.bom.wizard', 'Parent BoM', index=True, ondelete='cascade', required=True)
    parent_product_tmpl_id = fields.Many2one('product.template', 'Parent Product Template', related='bom_id.product_tmpl_id')
    possible_bom_product_template_attribute_value_ids = fields.Many2many(related='bom_id.possible_product_template_attribute_value_ids')
    bom_product_template_attribute_value_ids = fields.Many2many(
        'product.template.attribute.value', string="Apply on Variants", ondelete='restrict', domain="[('id', 'in', possible_bom_product_template_attribute_value_ids)]", help="BOM Product Variants needed to apply this line.")
    allowed_operation_ids = fields.One2many('mrp.routing.workcenter.wizard', related='bom_id.operation_ids')
    operation_id = fields.Many2one(
        'mrp.routing.workcenter.wizard', 'Consumed in Operation', check_company=True, domain="[('id', 'in', allowed_operation_ids)]", help="The operation where the components are consumed, or the finished products created.")
    child_bom_id = fields.Many2one(
        'mrp.bom', 'Sub BoM', compute='_compute_child_bom_id')
    child_line_ids = fields.One2many(
        'mrp.bom.line', string="BOM lines of the referred bom", compute='_compute_child_line_ids')
    attachments_count = fields.Integer('Attachments Count', compute='_compute_attachments_count')
    tracking = fields.Selection(related='product_id.tracking')
    manual_consumption = fields.Boolean(
        'Manual Consumption', default=False, compute='_compute_manual_consumption', readonly=False, store=True, copy=True, help="When activated, then the registration of consumption for that component is recorded manually exclusively.\n"
             "If not activated, and any of the components consumption is edited manually on the manufacturing order, Odoo assumes manual consumption also.")
    manual_consumption_readonly = fields.Boolean(
        'Manual Consumption Readonly', compute='_compute_manual_consumption_readonly')

    @api.depends("product_cost", "product_qty")
    def _compute_product_total_cost(self):
        for record_id in self:
            record_id.product_total_cost = record_id.product_qty * record_id.product_cost

    def _compute_attachments_count(self):
        for line in self:
            line.attachments_count = len(line.attachment_ids)

    attachment_ids = fields.Many2many('ir.attachment', string="Attachments")


    @api.depends('product_id', 'tracking', 'operation_id')
    def _compute_manual_consumption(self):
        for line in self:
            line.manual_consumption = (line.tracking != 'none' or line.operation_id)

    @api.depends('tracking', 'operation_id')
    def _compute_manual_consumption_readonly(self):
        for line in self:
            line.manual_consumption_readonly = (line.tracking != 'none' or line.operation_id)

    @api.depends('product_id', 'bom_id')
    def _compute_child_bom_id(self):
        products = self.product_id
        bom_by_product = self.env['mrp.bom']._bom_find(products)
        for line in self:
            if not line.product_id:
                line.child_bom_id = False
            else:
                line.child_bom_id = bom_by_product.get(line.product_id, False)

    @api.depends('product_id')
    def _compute_attachments_count(self):
        for line in self:
            nbr_attach = self.env['mrp.document'].search_count([
                '|',
                '&', ('res_model', '=', 'product.product'), ('res_id', '=', line.product_id.id),
                '&', ('res_model', '=', 'product.template'), ('res_id', '=', line.product_id.product_tmpl_id.id)])
            line.attachments_count = nbr_attach

    @api.depends('child_bom_id')
    def _compute_child_line_ids(self):
        """ If the BOM line refers to a BOM, return the ids of the child BOM lines """
        for line in self:
            line.child_line_ids = line.child_bom_id.bom_line_ids.ids or False

    @api.onchange('product_uom_id')
    def onchange_product_uom_id(self):
        res = {}
        if not self.product_uom_id or not self.product_id:
            return res
        if self.product_uom_id.category_id != self.product_id.uom_id.category_id:
            self.product_uom_id = self.product_id.uom_id.id
            res['warning'] = {'title': _('Warning'), 'message': _('The Product Unit of Measure you chose has a different category than in the product form.')}
        return res

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if 'product_id' in values and 'product_uom_id' not in values:
                values['product_uom_id'] = self.env['product.product'].browse(values['product_id']).uom_id.id
        return super().create(vals_list)

    def _skip_bom_line(self, product):
        """ Control if a BoM line should be produced, can be inherited to add
        custom control.
        """
        self.ensure_one()
        if product._name == 'product.template':
            return False
        return not product._match_all_variant_values(self.bom_product_template_attribute_value_ids)

    def action_see_attachments(self):
        domain = [
            '|',
            '&', ('res_model', '=', 'product.product'), ('res_id', '=', self.product_id.id),
            '&', ('res_model', '=', 'product.template'), ('res_id', '=', self.product_id.product_tmpl_id.id)]
        attachment_view = self.env.ref('mrp.view_document_file_kanban_mrp')
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'mrp.document',
            'type': 'ir.actions.act_window',
            'view_id': attachment_view.id,
            'views': [(attachment_view.id, 'kanban'), (False, 'form')],
            'view_mode': 'kanban,tree,form',
            'help': _('''<p class="o_view_nocontent_smiling_face">
                        Upload files to your product
</p>
<p>
                        Use this feature to store any files, like drawings or specifications.
</p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d, 'default_company_id': %s}" % ('product.product', self.product_id.id, self.company_id.id)
        }


class MrpRoutingWorkcenterWizard(models.TransientModel):
    _name = "mrp.routing.workcenter.wizard"

    name = fields.Char(string="name")
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company)
    time_mode = fields.Selection([
        ('auto', 'Compute based on tracked time'),
        ('manual', 'Set duration manually')], string='Duration Computation', default='manual')
    time_cycle = fields.Float(string="Duration", default=1.00)
    wizard_id = fields.Many2one("create.mrp.bom.wizard", string="Wizzard-o")
    employee_ratio = fields.Float("Employee Capacity", default=1, help="Number of employees needed to complete operation.")
    workcenter_id = fields.Many2one('mrp.workcenter', 'Work Center', required=True)
