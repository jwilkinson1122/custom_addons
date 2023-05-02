# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.
 
from odoo import api, fields, models, _
 
class patient_rounding(models.Model):
    _name = "podiatry.patient.rounding"
    _description ='Podiatry patient rounding'
    _rec_name = 'patient_id'

    @api.onchange('right_pupil','left_pupil')
    def onchange_duration(self):
        if self.left_pupil == self.right_pupil:
            self.anisocoria = False
        else:
            self.anisocoria = True
     
    health_physician_id = fields.Many2one('podiatry.physician',string="Health Professional",readonly=True)
    patient_id = fields.Many2one('podiatry.patient',string="Patient",required=True)
    details_start = fields.Datetime(string="Start",required=True)
    details_end = fields.Datetime(string="End",required=True)
    warning = fields.Boolean(string='Warning')
    pain = fields.Boolean(string='Pain')
    evolution = fields.Selection([('n','Status Quo'),
                                  ('i','Improving'),
                                  ('w','Worsening')],
                                 string="Evolution")
    round_summary = fields.Text(string="Round Summary")
    right_pupil = fields.Integer(string="R")
    pupillary_reactivity = fields.Selection([('brisk','Brisk'),
                                             ('sluggish','Sluggish'),
                                             ('nonreactive','Nonreactive')],
                                            string="Pupillary_Reactivity")
    pupil_dilation = fields.Selection([('normal','Normanl'),
                                       ('miosis','Miosis'),
                                       ('mydriasis','Mydriasis')],
                                      string="Pupil Dilation")
    left_pupil = fields.Integer(string="l")
    practice_location_id = fields.Many2one('stock.location',string='Activity Location')
    orthotics_ids = fields.One2many('podiatry.patient.rounding.orthotic','patient_rounding_orthotic_id',string="Orthotics")
    supplies_ids = fields.One2many('podiatry.patient.rounding.supply','patient_rounding_supply_id',string='Podiatry Supplier')
    state = fields.Selection([('draft','Draft'),
                              ('done','Done')],
                             string="Status")

    # move_ids = fields.One2many(
    #     'stock.move', string="Stock moves", compute='_compute_move_ids')
    
    # @api.depends('picking_ids', 'picking_ids.move_line_ids', 'picking_ids.move_lines', 'picking_ids.move_lines.state')
    # def _compute_move_ids(self):
    #     for batch in self:
    #         batch.move_ids = batch.picking_ids.move_lines
    #         batch.move_line_ids = batch.picking_ids.move_line_ids
    #         batch.show_check_availability = any(m.state not in ['assigned', 'done'] for m in batch.move_ids)

    # -------------------------------------------------------------------------
    # Action methods
    # -------------------------------------------------------------------------
    # def action_confirm(self):
    #     """Sanity checks, confirm the pickings and mark the batch as confirmed."""
    #     self.ensure_one()
    #     if not self.picking_ids:
    #         raise UserError(_("You have to set some pickings to batch."))
    #     self.picking_ids.action_confirm()
    #     self._check_company()
    #     self.state = 'in_progress'
    #     return True

    # def action_cancel(self):
    #     self.state = 'cancel'
    #     self.picking_ids = False
    #     return True

    # def action_print(self):
    #     self.ensure_one()
    #     return self.env.ref('stock_picking_batch.action_report_picking_batch').report_action(self)
