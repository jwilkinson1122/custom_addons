# -*- coding: utf-8 -*-


import time

from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PickingType(models.Model):
    _inherit = 'stock.picking.type'

    code = fields.Selection(selection_add=[
        ('prescription_operation', 'Prescription')
    ], ondelete={'prescription_operation': 'cascade'})

    count_prescription_confirmed = fields.Integer(
        string="Number of Prescription Orders Confirmed", compute='_compute_count_prescription')
    count_prescription_in_progress = fields.Integer(
        string="Number of Prescription Orders In Progress", compute='_compute_count_prescription')
    count_prescription_ready = fields.Integer(
        string="Number of Prescription Orders to Process", compute='_compute_count_prescription')

    default_remove_location_dest_id = fields.Many2one(
        'stock.location', 'Default Remove Destination Location', compute='_compute_default_remove_location_dest_id',
        check_company=True, store=True, readonly=False, precompute=True,
        help="This is the default remove destination location when you create a prescription order with this operation type.")

    default_recycle_location_dest_id = fields.Many2one(
        'stock.location', 'Default Recycle Destination Location', compute='_compute_default_recycle_location_dest_id',
        check_company=True, store=True, readonly=False, precompute=True,
        help="This is the default recycle destination location when you create a prescription order with this operation type.")

    is_prescriptionable = fields.Boolean(
        'Create Prescription Orders from Returns',
        compute='_compute_is_prescriptionable', store=True, readonly=False, default=False,
        help="If ticked, you will be able to directly create prescription orders from a return.")
    return_type_of_ids = fields.One2many('stock.picking.type', 'return_picking_type_id')

    def _compute_count_prescription(self):
        prescription_picking_types = self.filtered(lambda picking: picking.code == 'prescription_operation')

        # By default, set count_prescription_xxx to False
        self.count_prescription_ready = False
        self.count_prescription_confirmed = False
        self.count_prescription_in_progress = False

        # shortcut
        if not prescription_picking_types:
            return

        picking_types = self.env['prescription.order']._read_group(
            [
                ('picking_type_id', 'in', prescription_picking_types.ids),
                ('state', 'in', ('confirmed', 'in_progress')),
            ],
            groupby=['picking_type_id', 'is_parts_available', 'state'],
            aggregates=['id:count']
        )

        counts = {}
        for pt in picking_types:
            pt_count = counts.setdefault(pt[0].id, {})
            if pt[1]:
                pt_count.setdefault('ready', 0)
                pt_count['ready'] += pt[3]
            pt_count.setdefault(pt[2], 0)
            pt_count[pt[2]] += pt[3]

        for pt in prescription_picking_types:
            if pt.id not in counts:
                continue
            pt.count_prescription_ready = counts[pt.id].get('ready')
            pt.count_prescription_confirmed = counts[pt.id].get('confirmed')
            pt.count_prescription_in_progress = counts[pt.id].get('in_progress')

    @api.depends('return_type_of_ids', 'code')
    def _compute_is_prescriptionable(self):
        for picking_type in self:
            if not picking_type.return_type_of_ids:
                picking_type.is_prescriptionable = False  # Reset the user choice as it's no more available.

    def _compute_default_location_src_id(self):
        remaining_picking_type = self.env['stock.picking.type']
        for picking_type in self:
            if picking_type.code != 'prescription_operation':
                remaining_picking_type |= picking_type
                continue
            stock_location = picking_type.warehouse_id.lot_stock_id
            picking_type.default_location_src_id = stock_location.id
        super(PickingType, remaining_picking_type)._compute_default_location_src_id()

    def _compute_default_location_dest_id(self):
        prescription_picking_type = self.filtered(lambda pt: pt.code == 'prescription_operation')
        prod_locations = self.env['stock.location']._read_group(
            [('usage', '=', 'production'), ('company_id', 'in', prescription_picking_type.company_id.ids)],
            ['company_id'],
            ['id:min'],
        )
        prod_locations = {l[0].id: l[1] for l in prod_locations}
        for picking_type in prescription_picking_type:
            picking_type.default_location_dest_id = prod_locations.get(picking_type.company_id.id)
        super(PickingType, (self - prescription_picking_type))._compute_default_location_dest_id()

    @api.depends('code')
    def _compute_default_remove_location_dest_id(self):
        prescription_picking_type = self.filtered(lambda pt: pt.code == 'prescription_operation')
        company_ids = prescription_picking_type.company_id.ids
        company_ids.append(False)
        scrap_locations = self.env['stock.location']._read_group(
            [('scrap_location', '=', True), ('company_id', 'in', company_ids)],
            ['company_id'],
            ['id:min'],
        )
        scrap_locations = {l[0].id: l[1] for l in scrap_locations}
        for picking_type in prescription_picking_type:
            picking_type.default_remove_location_dest_id = scrap_locations.get(picking_type.company_id.id)

    @api.depends('code')
    def _compute_default_recycle_location_dest_id(self):
        for picking_type in self:
            if picking_type.code == 'prescription_operation':
                stock_location = picking_type.warehouse_id.lot_stock_id
                picking_type.default_recycle_location_dest_id = stock_location.id

    def get_prescription_stock_picking_action_picking_type(self):
        action = self.env["ir.actions.actions"]._for_xml_id('prescription.action_picking_prescription')
        if self:
            action['display_name'] = self.display_name
        return action


class Picking(models.Model):
    _inherit = 'stock.picking'

    is_prescriptionable = fields.Boolean(compute='_compute_is_prescriptionable')
    prescription_ids = fields.One2many('prescription.order', 'picking_id')
    nbr_prescriptions = fields.Integer('Number of prescriptions linked to this picking', compute='_compute_nbr_prescriptions')

    @api.depends('picking_type_id.is_prescriptionable', 'return_id')
    def _compute_is_prescriptionable(self):
        for picking in self:
            picking.is_prescriptionable = picking.picking_type_id.is_prescriptionable and picking.return_id

    @api.depends('prescription_ids')
    def _compute_nbr_prescriptions(self):
        for picking in self:
            picking.nbr_prescriptions = len(picking.prescription_ids)

    def action_prescription_return(self):
        self.ensure_one()
        ctx = self.env.context.copy()
        ctx.update({
            'default_location_id': self.location_dest_id.id,
            'default_picking_id': self.id,
            'default_picking_type_id': self.picking_type_id.warehouse_id.prescription_type_id.id,
            'default_partner_id': self.partner_id and self.partner_id.id or False,
        })
        return {
            'name': _('Create Prescription'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'prescription.order',
            'view_id': self.env.ref('prescription.view_prescription_order_form').id,
            'context': ctx,
        }

    def action_view_prescriptions(self):
        if self.prescription_ids:
            action = {
                'res_model': 'prescription.order',
                'type': 'ir.actions.act_window',
            }
            if len(self.prescription_ids) == 1:
                action.update({
                    'view_mode': 'form',
                    'res_id': self.prescription_ids[0].id,
                })
            else:
                action.update({
                    'name': _('Prescription Orders'),
                    'view_mode': 'tree,form',
                    'domain': [('id', 'in', self.prescription_ids.ids)],
                })
            return action
