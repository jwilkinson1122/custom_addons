from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
 
class BookingOrder(models.Model):
    _inherit = 'sale.order'
    
    is_booking_order = fields.Boolean(string='Is Booking Order')

    practice_id = fields.Many2one(comodel_name='practice', string='Practice')
    practice_name = fields.Char(string='Practice', related='practice_id.name')
    practitioner_id = fields.Many2one(comodel_name='practitioner', string='Practitioner')
    practitioner_name = fields.Char(string='Practitioner', related='practitioner_id.name')
    patient_id = fields.Many2one(comodel_name='patient', string='Patient')
    patient_name = fields.Char(string='Patient', related='patient_id.name')
 

    booking_start = fields.Datetime(
        string='Booking Start')
    booking_end = fields.Datetime(
        string='Booking End')
    
    wo_count = fields.Integer(
        string='Work Order',
        compute='_compute_wo_count')
    

    def _compute_wo_count(self):
        wo_data = self.env['work.order'].sudo().read_group([('bo_reference', 'in', self.ids)], ['bo_reference'],
                                                                   ['bo_reference'])
        result = {
            data['bo_reference'][0]: data['bo_reference_count'] for data in wo_data
        }

        for wo in self:
            wo.wo_count = result.get(wo.id, 0)
            
    def action_confirm(self):
        res = super(BookingOrder, self).action_confirm()
        for order in self:
            wo = self.env['work.order'].search(
                ['|', '|', '|',
                 ('practitioner_id', 'in', [g.id for g in self.patient_id]),
                 ('patient_id', 'in', [self.practitioner_id.id]),
                 ('practitioner_id', '=', self.practitioner_id.id),
                 ('patient_id', 'in', [g.id for g in self.patient_id]),
                 ('state', '!=', 'cancelled'),
                 ('planned_start', '<=', self.booking_end),
                 ('planned_end', '>=', self.booking_start)], limit=1)
            if wo:
                raise ValidationError('Please book on another date.')
            order.action_work_order_create()
        return res

    def action_work_order_create(self):
        wo_obj = self.env['work.order']
        for order in self:
            wo_obj.create([{'bo_reference': order.id,
                            'practice_id': order.practice_id.id,
                            'practitioner_id': order.practitioner_id.id,
                            'patient_id': order.patient_id.ids,
                            'planned_start': order.booking_start,
                            'planned_end': order.booking_end}])
            


class BookingOrderLine(models.Model):
    _inherit = "sale.order.line"

    