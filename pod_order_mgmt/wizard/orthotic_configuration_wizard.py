from odoo import models, fields, api

class OrthoticConfiguratorWizard(models.TransientModel):
    _name = 'orthotic.configurator.wizard'
    _inherit = ['multi.step.wizard.mixin', 'product.configurator']
    _description = 'Orthotic Configurator Wizard'
    
    # Define fields here that you want to display in the wizard, like:
    configuration_data = fields.Text(string='Configuration Data')


    prescription_order_id = fields.Many2one(
        comodel_name='pod.prescription.order', 
        name="Prescription", 
        required=True, 
        ondelete='cascade', 
        default=lambda self: self._default_prescription_order_id(),
    )
    laterality = fields.Selection([
        ('lt_single', 'Left'),
        ('rt_single', 'Right'),
        ('bl_pair', 'Bilateral')
    ], string='Laterality', required=True, default='bl_pair')
    product_tmpl_id = fields.Many2one('product.template', string='Product Template')

    # product_tmpl_id = fields.Many2one('product.template', string='Product Template', required=True)
    product_id = fields.Many2one('product.product', string='Product')
    attribute_value_ids = fields.Many2many('product.attribute.value', string='Attribute Values')
    total_price = fields.Float(string='Total Price', compute='_compute_total_price', readonly=True)
    
    @api.model
    def _default_prescription_order_id(self):
        return self.env.context.get('active_id')
      
    @api.depends('product_id', 'attribute_value_ids', 'laterality')
    def _compute_total_price(self):
        for wizard in self:
            price = wizard.product_id.lst_price
            for value in wizard.attribute_value_ids:
                price += value.price_extra
            if wizard.laterality == 'bl_pair':
                price *= 2
            wizard.total_price = price
            

    # def action_confirm(self):
    #     self.ensure_one()
    #     self.prescription_order_id.write({
    #         'product_id': self.product_id.id,
    #         'attribute_value_ids': [(6, 0, self.attribute_value_ids.ids)],
    #         'laterality': self.laterality,
    #         'total_price': self.total_price
    #     })
        
    def action_confirm(self):
        self.ensure_one()
        prescription_order = self.prescription_order_id

        for wizard_line in self.prescription_order_lines:
            # Try to find an existing line to update
            existing_line = prescription_order.prescription_order_line_ids.filtered(
                lambda line: line.product_id == wizard_line.product_id
            )

            values = {
                'name': wizard_line.description,
                'product_id': wizard_line.product_id.id,
                'quantity': wizard_line.quantity,
                'laterality': wizard_line.laterality,
                'price': wizard_line.total_price,
            }

            if existing_line:
                # Update the existing line if found
                existing_line.write(values)
            else:
                # Otherwise, create a new line and link it to the prescription order
                values['prescription_order_id'] = prescription_order.id
                self.env['pod.prescription.order.line'].create(values)

        # Close the wizard
        return {'type': 'ir.actions.act_window_close'}

        
    @api.model
    def _selection_state(self):
        return [
            ('start', 'Start'),
            ('configure', 'Configure'),
            ('custom', 'Customize'),
            ('final', 'Final'),
            ]

    def state_exit_start(self):
        self.state = 'configure'

    def state_exit_configure(self):
        self.state = 'custom'

    def state_exit_custom(self):
        self.state = 'final'
        
    def button_save(self):
        self.ensure_one()

        prescription_order = self.prescription_order_id

        for wizard_line in self.prescription_order_lines:
            # Try to find an existing line to update
            existing_line = prescription_order.prescription_order_line_ids.filtered(
                lambda line: line.product_id == wizard_line.product_id
            )

            values = {
                'name': wizard_line.description,
                'product_id': wizard_line.product_id.id,
                'quantity': wizard_line.quantity,
                'price': wizard_line.price,
            }

            if existing_line:
                # Update the existing line if found
                existing_line.write(values)
            else:
                # Otherwise, create a new line and link it to the prescription order
                values['prescription_order_id'] = prescription_order.id
                self.env['pod.prescription.order.line'].create(values)

        # Close the wizard
        return {'type': 'ir.actions.act_window_close'}
    

    