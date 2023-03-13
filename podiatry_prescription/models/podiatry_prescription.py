from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
 
class PrescriptionOrder(models.Model):
    # _name = "podiatry.prescription.order"
    _description = "Podiatry Prescription Order"
    _inherit = 'sale.order'
    

    internal_identifier = fields.Char(string="Rx Order")
    
    is_prescription_order = fields.Boolean(string='Is Prescription Order')
   
    service_id = fields.Many2one(
        string="Service",
        comodel_name="product.product",
        ondelete="cascade",
        index=True,
        domain="[('type', '=', 'service')]",
    )  # Field: code
    
    partner_id = fields.Many2one(
        string="Practice",
        comodel_name="res.partner",
        ondelete="cascade",
        index=True,
        tracking=True,
        domain=[("is_location", "=", True)],
        help="Practice associated with Practitioner",
    )  # Field : clinic
    
    practice_id = fields.Many2one(
        string="Practice",
        comodel_name="res.partner",
        ondelete="cascade",
        index=True,
        tracking=True,
        domain=[("is_location", "=", True)],
        help="Practice associated with Practitioner",
    )  
     
    practitioner_id = fields.Many2one(
        string="Practitioner",
        comodel_name="res.partner",
        ondelete="cascade",
        index=True,
        tracking=True,
        domain=[("is_practitioner", "=", True)],
        help="Who is responsible for prescription/patient",
    )   
    
    patient_id = fields.Many2one(
        string="Patient",
        comodel_name="podiatry.patient",
        required=True,
        tracking=True,
        ondelete="cascade",
        index=True,
        help="Patient Name",
    )  
    
    order_by_id = fields.Many2one(
        string="Submitted by",
        comodel_name="res.partner",
        tracking=True,
        help="Person who has initiated the order.",
        ondelete="cascade",
        index=True,
    )  # Field: requester/agent
   
    priority = fields.Selection(
        [("low", "Low"), ("normal", "Normal"), ("high", "High")],
        required=True,
        default="normal",
    )  # Field: priority
   
    prescription_date = fields.Datetime(
        string="Submitted date", help="Date prescription created."
    )  # Field: authoredOn
    
    prescription_start = fields.Datetime(
        string='Prescription Start')
    
    prescription_end = fields.Datetime(
        string='Prescription End')
    
    wo_count = fields.Integer(
        string='Work Order',
        compute='_compute_wo_count')
    
    @api.depends("name", "internal_identifier")
    def name_get(self):
        result = []
        for record in self:
            name = "[%s]" % record.internal_identifier
            if record.name:
                name = "{} {}".format(name, record.name)
            result.append((record.id, name))
        return result
    
    
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
        wo_data = self.env['prescription.work_order'].sudo().read_group([('bo_reference', 'in', self.ids)], ['bo_reference'],
                                                                   ['bo_reference'])
        result = {
            data['bo_reference'][0]: data['bo_reference_count'] for data in wo_data
        }

        for wo in self:
            wo.wo_count = result.get(wo.id, 0)
            

    def action_confirm(self):
        res = super(PrescriptionOrder, self).action_confirm()
        for order in self:
            wo = self.env['prescription.work_order'].search(
                ['|', '|', '|',
                 ('practitioner_id', 'in', [g.id for g in self.patient_id]),
                 ('patient_id', 'in', [self.practitioner_id.id]),
                 ('practitioner_id', '=', self.practitioner_id.id),
                 ('patient_id', 'in', [g.id for g in self.patient_id]),
                 ('state', '!=', 'cancelled')], limit=1)
            if wo:
                raise ValidationError(' Please book on another date.')
            order.action_work_order_create()
        return res

    def action_work_order_create(self):
        wo_obj = self.env['prescription.work_order']
        for order in self:
            wo_obj.create([{'bo_reference': order.id,
                            'partner_id': order.partner_id.id,
                            'practitioner_id': order.practitioner_id.id,
                            'patient_id': order.patient_id.id,
                            'planned_start': order.prescription_start,
                            'planned_end': order.prescription_end}])


class PrescriptionOrderLine(models.Model):
    _inherit = "sale.order.line"

   