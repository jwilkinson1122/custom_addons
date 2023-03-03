from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

# class BookingOrderProductReConfigurator(models.TransientModel):
#     _inherit = 'sale.product.configurator'

#     product_id = fields.Many2one('product.product')
#     order_line_id = fields.Many2one('sale.order.line')
#     order_id = fields.Many2one('sale.order')

class BookingOrder(models.Model):
    _inherit = 'sale.order'
    
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        domain=[("is_practice", "=", True)]
    )
   
    practice_id = fields.Many2one(comodel_name='practice', string='Practice')
    practice_name = fields.Char(string='Practitioner', related='practice_id.name')
    practitioner_id = fields.Many2one(comodel_name='practitioner', string='Practitioner')
    practitioner_name = fields.Char(string='Practitioner', related='practitioner_id.name')
    patient_id = fields.Many2one(comodel_name='patient', string='Patient')
    patient_name = fields.Char(string='Practitioner', related='patient_id.name')

    is_booking_order = fields.Boolean(
        string='Is Booking Order')
    team = fields.Many2one(
        comodel_name='booking.service_team',
        string='Team')
    team_leader = fields.Many2one(
        comodel_name='res.users',
        string='Team Leader')
    team_members = fields.Many2many(
        comodel_name='res.users',
        string='Team Members')
    booking_start = fields.Datetime(
        string='Booking Start')
    booking_end = fields.Datetime(
        string='Booking End')
    wo_count = fields.Integer(
        string='Work Order',
        compute='_compute_wo_count')

    def _compute_wo_count(self):
        wo_data = self.env['booking.work_order'].sudo().read_group([('bo_reference', 'in', self.ids)], ['bo_reference'],
                                                                   ['bo_reference'])
        result = {
            data['bo_reference'][0]: data['bo_reference_count'] for data in wo_data
        }

        for wo in self:
            wo.wo_count = result.get(wo.id, 0)
            
    @api.onchange('practice_id')
    def onchange_practice_id(self):
        for rec in self:
            return {'domain': {'practitioner_id': [('practice_id', '=', rec.practice_id.id)]}}
    @api.onchange('practitioner_id')
    def onchange_practitioner_id(self):
        for rec in self:
            return {'domain': {'patient_id': [('practitioner_id', '=', rec.practitioner_id.id)]}}
            
    # @api.onchange("partner_id")
    # def _onchange_partner_id(self):
    #     """
    #     When you change partner_id it will update the partner_invoice_id,
    #     partner_shipping_id and pricelist_id of the podiatry prescription as well
    #     ---------------------------------------------------------------
    #     @param self: object pointer
    #     """
    #     if self.partner_id:
    #         self.update(
    #             {
    #                 "partner_invoice_id": self.partner_id.id,
    #                 "partner_shipping_id": self.partner_id.id,
    #                 "pricelist_id": self.partner_id.property_product_pricelist.id,
    #             }
    #         )

    @api.onchange('team')
    def _onchange_team(self):
        search = self.env['booking.service_team'].search([('id', '=', self.team.id)])
        team_members = []
        for team in search:
            team_members.extend(members.id for members in team.team_members)
            self.team_leader = team.team_leader.id
            self.team_members = team_members

    # def action_check(self):
    #     for check in self:
    #         wo = self.env['booking.work_order'].search(
    #             ['|', '|', '|',
    #              ('team_leader', 'in', [g.id for g in self.team_members]),
    #              ('team_members', 'in', [self.team_leader.id]),
    #              ('team_leader', '=', self.team_leader.id),
    #              ('team_members', 'in', [g.id for g in self.team_members]),
    #              ('state', '!=', 'cancelled'),
    #              ('planned_start', '<=', self.booking_end),
    #              ('planned_end', '>=', self.booking_start)], limit=1)
    #         if wo:
    #             raise ValidationError('Team already has work order during that period on SOXX')
    #         else:
    #             raise ValidationError('Team is available for booking')

    def action_confirm(self):
        res = super(BookingOrder, self).action_confirm()
        for order in self:
            wo = self.env['booking.work_order'].search(
                ['|', '|', '|',
                 ('team_leader', 'in', [g.id for g in self.team_members]),
                 ('team_members', 'in', [self.team_leader.id]),
                 ('team_leader', '=', self.team_leader.id),
                 ('team_members', 'in', [g.id for g in self.team_members]),
                 ('state', '!=', 'cancelled'),
                 ('planned_start', '<=', self.booking_end),
                 ('planned_end', '>=', self.booking_start)], limit=1)
            if wo:
                raise ValidationError('Team is not available during this period, already booked on '
                                      'SOXX. Please book on another date.')
            order.action_work_order_create()
        return res

    def action_work_order_create(self):
        wo_obj = self.env['booking.work_order']
        for order in self:
            wo_obj.create([{'bo_reference': order.id,
                            'team': order.team.id,
                            'team_leader': order.team_leader.id,
                            'team_members': order.team_members.ids,
                            'planned_start': order.booking_start,
                            'planned_end': order.booking_end}])
            
    # @api.model
    # def update_order_line(self, order_line_id, params):
    #     product_id = params['product_id']
    #     qty = params['quantity']
    #     order_line = self.env['sale.order.line']
    #     old_order_line = self.env['sale.order.line'].browse(order_line_id)
    #     variant_attribute_values = params['no_variant_attribute_values']
    #     product_custom_attribute_values = params['product_custom_attribute_values']
    #     custom_attribute_ids = self.env['product.attribute.custom.value']
    #     if product_custom_attribute_values:
    #         for custom_attribute in product_custom_attribute_values:
    #             custom_attribute_ids += self.env['product.attribute.custom.value'].new({
    #                 'custom_value': custom_attribute['custom_value'],
    #                 'attribute_value_id': custom_attribute['attribute_value_id'],
    #                 'attribute_value_name': custom_attribute['attribute_value_name']
    #             })
    #     default_values = order_line.default_get(order_line._fields.keys())
    #     new_order_line = order_line.new(dict(default_values,
    #         product_id=product_id,
    #         product_uom_qty=qty,
    #         order_id=self,
    #         sequence=old_order_line.sequence,
    #         product_custom_attribute_value_ids=custom_attribute_ids,
    #         product_no_variant_attribute_value_ids=list(map(lambda x: int(x['value']), variant_attribute_values)),
    #     ))
    #     new_order_line.product_id_change()
    #     new_order_line.sequence = old_order_line.sequence

    #     self.order_line += new_order_line
    #     self.order_line -= old_order_line


# class BookingOrderLine(models.Model):
#     _inherit = 'sale.order.line'

#     def open_product_configurator(self):
#         form_view = self.env.ref('booking_order.booking_order_product_reconfigurator_view_form')
#         return {
#             'name': _('Configure a product'),
#             'type': 'ir.actions.act_window',
#             'res_model': 'sale.product.configurator',
#             'views': [[form_view.id, 'form']],
#             'target': 'new',
#             'context': {
#                 'default_product_template_id': self.product_id.product_tmpl_id.id,
#                 'default_product_id': self.product_id.id,
#                 'default_order_line_id': self.id,
#                 'default_order_id': self.order_id.id
#             }
#         }

