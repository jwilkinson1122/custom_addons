from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class BookingOrder(models.Model):
    _inherit = 'sale.order'

   
    is_booking_order = fields.Boolean(
        string='Is Booking Order')
    practice_id = fields.Many2one(
        comodel_name='practice',
        string='Practice')
    practice_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Practice Entity",
        related="partner_id.practice_id",
        store=True,
        index=True,
    )
    practitioner_id = fields.Many2one(
        comodel_name='practitioner',
        string='Practitioner')
    patient_id = fields.Many2one(
        comodel_name='patient',
        string='Patient')
    patient_ids = fields.Many2many(
        string='Patients',
        comodel_name='patient',
        compute='_compute_patient_ids',
        readonly=True,
    )
    booking_start = fields.Datetime(
        string='Booking Start')
    booking_end = fields.Datetime(
        string='Booking End')
    
    hold = fields.Boolean(
        default=False,
        copy=False,
        tracking=True,
        readonly=True,
        index=True,
    )
    hold_reason_ids = fields.Many2many(
        "booking.order.hold.reason",
        tracking=True,
    )
    
    def action_hold(self, reason_id=None, msg=None):
        for record in self.filtered(lambda s: not s.hold):
            record.hold = True
            if reason_id:
                record.hold_reason_ids = reason_id
            if msg:
                record.message_post(body=msg)

    def action_unhold(self, msg=None):
        for record in self.filtered(lambda s: s.hold):
            record.hold = False
            record.hold_reason_ids = False
            if msg:
                record.message_post(body=msg)

    def action_cancel(self):
        if not self._show_cancel_wizard():
            self.action_unhold()

        return super().action_cancel()

    def _action_cancel(self):
        self.action_unhold()
        return super()._action_cancel()
    
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
            
    def _compute_patient_ids(self):
        for record in self:
            patient_ids = []
            for line_id in record.order_line:
                patient_ids.append(line_id.patient_ids.id)
            record.patient_ids = self.env['patient'].browse(
                set(patient_ids)
            )

    # @api.onchange('practice_id')
    # def _onchange_practice_id(self):
    #     search = self.env['practice'].search([('id', '=', self.practice_id.id)])
    #     patient_ids = []
    #     for practice_id in search:
    #         patient_ids.extend(patient.id for patient in practice_id.patient_ids)
    #         self.practitioner_id = practice_id.practitioner_id.id
    #         self.patient_ids = patient_ids
            
            
    # @api.onchange('practice_id') 
    # def on_change_practice_id(self): 
    #     for record in self:
    #         if record.practice_id: 
    #             res_practice = self.env['practice'].search([('id', '=', record.practice_id)]) 
    #         if res_practice: 
    #             record.practitioner_id = res_practice.practitioner_id
    #             record.patient_id = res_practice.patient_id
            
    # @api.onchange('practice_id', 'practitioner_id')
    # def _onchange_practitioner_id(self):
    #     if self.practice_id:
    #         self.practitioner_id = self.practice_id.practitioner_id.id
    
    # @api.onchange('practice_id')
    # def onchange_practice_id(self):
    #     for rec in self:
    #         return {'domain': {'practitioner_id': [('practice_id', '=', rec.practice_id.id)]}}
            
            
    # @api.onchange('practitioner_id')
    # def onchange_practice_id(self):
    #     for rec in self:
    #         return {'domain': {'patient_id': [('practitioner_id', '=', rec.practitioner_id.id)]}}
            

    def action_check(self):
        for check in self:
            wo = self.env['work.order'].search(
                ['|', '|', '|',
                 ('practitioner_id', 'in', [g.id for g in self.patient_ids]),
                 ('patient_ids', 'in', [self.practitioner_id.id]),
                 ('practitioner_id', '=', self.practitioner_id.id),
                 ('patient_ids', 'in', [g.id for g in self.patient_ids]),
                 ('state', '!=', 'cancelled')], limit=1)
        

    def action_confirm(self):
        res = super(BookingOrder, self).action_confirm()
        for order in self:
            wo = self.env['work.order'].search(
                ['|', '|', '|',
                 ('practitioner_id', 'in', [g.id for g in self.patient_ids]),
                 ('patient_ids', 'in', [self.practitioner_id.id]),
                 ('practitioner_id', '=', self.practitioner_id.id),
                 ('patient_ids', 'in', [g.id for g in self.patient_ids]),
                 ('state', '!=', 'cancelled')], limit=1)
            order.action_work_order_create()
        return res
    
    
    # def action_confirm(self):
    #     for order in self:
    #         if order.partner_id.on_hold:
    #             raise UserError(_('This customer is on hold. Please remove it and confirm again'))
    #     super(SaleOrder, self).action_confirm()

    def action_work_order_create(self):
        wo_obj = self.env['work.order']
        for order in self:
            wo_obj.create([{'bo_reference': order.id,
                            'practice_id': order.practice_id.id,
                            'practitioner_id': order.practitioner_id.id,
                            'patient_ids': order.patient_ids.ids,
                            'planned_start': order.booking_start,
                            'planned_end': order.booking_end}])
            
    
            


class BookingOrderLine(models.Model):
    _inherit = "sale.order.line"

    