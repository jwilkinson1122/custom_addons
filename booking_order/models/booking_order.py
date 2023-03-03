from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
 
class BookingOrder(models.Model):
    _inherit = 'sale.order'
    

    
   
    practice_id = fields.Many2one(comodel_name='practice', string='Practice')
    practice_name = fields.Char(string='Practitioner', related='practice_id.name')
    practitioner_id = fields.Many2one(comodel_name='practitioner', string='Practitioner')
    practitioner_name = fields.Char(string='Practitioner', related='practitioner_id.name')
    patient_id = fields.Many2one(comodel_name='patient', string='Patient')
    patient_name = fields.Char(string='Practitioner', related='patient_id.name')
    
        # partner_id = fields.Many2one(
    #     "res.partner",
    #     string="Practice",
    #     domain=[("is_practice", "=", True)]
    # )
    
    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=False, change_default=True, index=True, tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    partner_invoice_id = fields.Many2one(
        'res.partner', string='Invoice Address',
        readonly=False, required=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Delivery Address', readonly=True, required=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    # practitioner_id = fields.Many2one('res.partner', string='Practitioner', domain=[("is_practitioner", "=", True)], store=True)
    # patient_id = fields.Many2one('res.partner', string='Patient', domain=[("is_patient", "=", True)], store=True)

    is_booking_order = fields.Boolean(string='Is Booking Order')
    # practice_id = fields.Many2one('res.partner', string="Practice", domain=[("is_company", "=", True)])
    # practitioner_id = fields.Many2one('res.partner', 'Practitioner', domain=[("is_company", "=", False)])
    # patient_id = fields.Many2one('res.partner', 'Patient', domain=[("is_patient", "=", True)])
    # patient_name = fields.Char('Name', related='patient_id.name')
    
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
    
    def action_config_start(self):
        """Return action to start configuration wizard"""
        configurator_obj = self.env["product.configurator.sale"]
        ctx = dict(
            self.env.context,
            default_order_id=self.id,
            wizard_model="product.configurator.sale",
            allow_preset_selection=True,
        )
        return configurator_obj.with_context(ctx).get_wizard_action()

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
            


class BookingOrderLine(models.Model):
    _inherit = "sale.order.line"

    custom_value_ids = fields.One2many(
        comodel_name="product.config.session.custom.value",
        inverse_name="cfg_session_id",
        related="config_session_id.custom_value_ids",
        string="Configurator Custom Values",
    )
    config_ok = fields.Boolean(
        related="product_id.config_ok", string="Configurable", readonly=True
    )
    config_session_id = fields.Many2one(
        comodel_name="product.config.session", string="Config Session"
    )

    def reconfigure_product(self):
        """Creates and launches a product configurator wizard with a linked
        template and variant in order to re-configure a existing product. It is
        esentially a shortcut to pre-fill configuration data of a variant"""
        wizard_model = "product.configurator.sale"

        extra_vals = {
            "order_id": self.order_id.id,
            "order_line_id": self.id,
            "product_id": self.product_id.id,
        }
        self = self.with_context(
            {
                "default_order_id": self.order_id.id,
                "default_order_line_id": self.id,
            }
        )
        return self.product_id.product_tmpl_id.create_config_wizard(
            model_name=wizard_model, extra_vals=extra_vals
        )

    @api.onchange("product_uom", "product_uom_qty")
    def product_uom_change(self):
        if self.config_session_id:
            account_tax_obj = self.env["account.tax"]
            self.price_unit = account_tax_obj._fix_tax_included_price_company(
                self.config_session_id.price,
                self.product_id.taxes_id,
                self.tax_id,
                self.company_id,
            )
        else:
            super(BookingOrderLine, self).product_uom_change()