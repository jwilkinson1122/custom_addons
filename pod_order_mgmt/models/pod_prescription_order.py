import time
import json
from datetime import timedelta
from odoo import _, api, fields, models, exceptions
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import get_lang


class Prescription(models.Model):
    _name = 'pod.prescription.order'
    _description = 'Prescription Request'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"

    company_id = fields.Many2one(
        comodel_name="res.company", 
        default=lambda self: self.env.company, 
        store=True
        )

    practice_id = fields.Many2one(
        'res.partner', 
        required=True, 
        index=True, 
        domain=[('is_company','=',True)], 
        string="Practice"
        )
    
    practitioner_id = fields.Many2one(
        'res.partner', 
        required=True, 
        index=True, 
        domain=[('is_practitioner','=',True)], 
        string="Practitioner"
        )
    

    patient_id = fields.Many2one(
        "pod.patient", 
        string="Patient",
        required=True, 
        index=True, 
        states={"draft": [("readonly", False)], "done": [("readonly", True)]}
    )

    # patient_id = fields.Many2one("pod.patient", string="Patient")

    
    user_id = fields.Many2one(
        'res.users', 
        'User', readonly=True, default=lambda self: self.env.user
        )
    
    helpdesk_tickets_ids = fields.Many2many('helpdesk.ticket', string='Helpdesk Tickets')
    helpdesk_tickets_count = fields.Integer( string='# of Delivery Order', compute='_get_helpdesk_tickets_count')

    active = fields.Boolean(default=True)
    color = fields.Integer()
    date = fields.Date()
    time = fields.Datetime()
    invoice_done = fields.Boolean('Invoice Done')
    is_invoiced = fields.Boolean(copy=False, default=False)
    is_shipped = fields.Boolean(copy=False, default=False)
    is_confirmed = fields.Boolean(copy=False, default=False)
    internal_notes = fields.Text('Internal Notes')
    notes = fields.Text('Prescription Notes')
    
    name = fields.Char( string='Order Reference', required=True, copy=False, index=True, readonly=True, default=lambda self: _('New'))
    prescription = fields.Text(string="Prescription")
    prescription_order_lines = fields.One2many('pod.prescription.order.line', 'prescription_order_id', string="Products")
    test_file = fields.Binary(string='Test')
    laterality = fields.Selection([
            ('lt_single', 'Left'),
            ('rt_single', 'Right'),
            ('bl_pair', 'Bilateral')
        ], string='Laterality', required=True, default='bl_pair')
    # left_only = fields.Boolean('Left Only')
    # right_only = fields.Boolean('Right Only')

    rush_order = fields.Boolean('3-day rush')
    make_from_prior_rx = fields.Boolean('Make From Prior Rx#:')
    qty = fields.Integer('pairs to make')
    ship_to_patient = fields.Boolean('Ship to patient')
    description = fields.Text(string='Description')
    
    diagnosis_id = fields.Many2one(comodel_name='pod.diagnosis', string='diagnosis')

    attachment_ids = fields.Many2many(
        'ir.attachment', 
        'prescription_ir_attachments_rel',
        'manager_id', 
        'attachment_id', string="Attachments"
        )

    inv_state = fields.Selection([('invoiced', 'To Invoiced'), ('tobe', 'To Be Invoiced')], 'Invoice Status')
    no_invoice = fields.Boolean('Invoice exempt')
    inv_id = fields.Many2one('account.invoice', 'Invoice')
    prior_rx = fields.Boolean('Use Prior Rx#')
    product_id = fields.Many2one('product.product', 'Name')
    
    prescription_type = fields.Selection([('Custom', 'Custom'), ('OTC', 'OTC'), ('Brace', 'Brace')], default='Custom', Required=True)

    prescription_count = fields.Integer( string='Prescription Count', compute='_compute_prescription_count')

    def _compute_prescription_count_DISABLED(self):
        "Naive version, not performance optimal"
        for prescription in self:
            domain = [("practitioner_id", "=", prescription.practitioner_id.id), ("state", "not in", ["done", "cancel"])]
            prescription.prescription_count = self.search_count(domain)

    def _compute_prescription_count(self):
        "Performance optimized, to run a single database query"
        practitioners = self.mapped("practitioner_id")
        domain = [
            ("practitioner_id", "in", practitioners.ids),
            ("state", "not in", ["done", "cancel"]),
        ]
        raw = self.read_group(domain, ["id:count"], ["practitioner_id"])
        data = {x["practitioner_id"][0]: x["practitioner_id_count"]
                for x in raw}
        for prescription in self:
            prescription.prescription_count = data.get(
                prescription.practitioner_id.id, 0)

    num_prescription_items = fields.Integer( compute="_compute_num_prescription_items", store=True)

    @api.depends("prescription_order_lines")
    def _compute_num_prescription_items(self):
        for prescription in self:
            prescription.num_prescription_items = len(prescription.prescription_order_lines)
             
    # @api.constrains('company_id', 'practitioner_id', 'patient_id')
    # def _check_company_practitioner_patient(self):
    #     for record in self:
    #         if record.practitioner_id and record.company_id and record.practitioner_id.company_id != record.company_id:
    #             raise ValidationError('Practitioner does not belong to the selected company.')
    #         if record.patient_id and record.practitioner_id and record.patient_id.practitioner_id != record.practitioner_id:
    #             raise ValidationError('Patient does not belong to the selected practitioner.') 
            
    # @api.constrains('practice_id', 'practitioner_id', 'patient_id')
    # def _check_practice_practitioner_patient(self):
    #     for record in self:
    #         if record.practitioner_id and record.practice_id and record.practitioner_id.practice_id != record.practice_id:
    #             raise ValidationError('Practitioner does not belong to the selected practice.')
    #         if record.patient_id and record.practitioner_id and record.patient_id.practitioner_id != record.practitioner_id:
    #             raise ValidationError('Patient does not belong to the selected practitioner.')
            
    @api.onchange('partner_id')
    def onchange_set_domain_practitioner_id(self):
        if self.partner_id:
            # Assuming partner_id has a direct reference to the practitioner
            self.practitioner_id = self.partner_id.practitioner_id

    @api.onchange('practitioner_id')
    def onchange_set_domain_patient_id(self):
        return {
            'domain': {
                'patient_id': [('practitioner_id', '=', self.practitioner_id.id)]
            }
        }
       
            
            
    def action_config_start(self):
        """Return action to start configuration wizard"""
        configurator_obj = self.env["product.configurator.prescription"]
        return configurator_obj.with_context( default_prescription_order_id=self.id, wizard_model="product.configurator.prescription", allow_preset_selection=True).get_wizard_action()
    
    def button_launch_wizard(self):
        self.ensure_one()
        view_id = self.env.ref('pod_order_mgmt.view_orthotic_configurator_wizard_form').id
        
        default_product_tmpl_id = self.env['product.template'].search([], limit=1).id

        # Creating a new wizard, without setting product_tmpl_id here
        wizard = self.env['orthotic.configurator.wizard'].create({
            'prescription_order_id': self.id,
            'product_tmpl_id': default_product_tmpl_id,
        })
        return {
            'name': _('Orthotic Configurator'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'orthotic.configurator.wizard',
            'view_id': view_id,
            'res_id': wizard.id,
            'target': 'new',
        }

        
    # def button_launch_wizard(self):
    #     self.ensure_one()
    #     view_id = self.env.ref('pod_order_mgmt.view_orthotic_configurator_wizard_form').id
    #     wizard = self.env['orthotic.configurator.wizard'].create({
    #         'prescription_order_id': self.id,
    #         'product_tmpl_id': self.product_tmpl_id.id,  
    #     })
    #     return {
    #         'name': _('Orthotic Configurator'),
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'orthotic.configurator.wizard',
    #         'view_id': view_id,
    #         'res_id': wizard.id,
    #         'target': 'new',
    #     }

            
    @api.model
    def _default_stage(self):
        Stage = self.env["pod.prescription.order.stage"]
        return Stage.search([("state", "=", "draft")], limit=1)

    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        return stages.search([], order=order)

    stage_id = fields.Many2one(
        "pod.prescription.order.stage", default=_default_stage, copy=False, group_expand="_group_expand_stage_id"
        )

    state = fields.Selection(related="stage_id.state")

    kanban_state = fields.Selection(
        [("normal", "In Progress"),
         ("blocked", "Blocked"),
         ("done", "Ready for next stage")],
        "Kanban State", default="normal")

    priority = fields.Selection(
        [("0", "High"),
         ("1", "Very High"),
         ("2", "Critical")], default="0")
    
    request_date = fields.Date(
        default=lambda s: fields.Date.today(), 
        compute="_compute_request_date_onchange", 
        store=True, 
        readonly=False
        )
    
    @api.depends('patient_id')
    def _compute_request_date_onchange(self):
        today_date = fields.Date.today()
        if self.request_date != today_date:
            self.request_date = today_date
            return {"warning": {"title": "Changed Request Date", "message": "Request date changed to today!"}}

    @api.model
    def _get_bookin_date(self):
        self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
        checkin_date = fields.Datetime.context_timestamp(self, fields.Datetime.now())
        return fields.Datetime.to_string(checkin_date)
    
    @api.model
    def _get_bookout_date(self):
        self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
        checkout_date = fields.Datetime.context_timestamp(self, fields.Datetime.now() + timedelta(days=1))
        return fields.Datetime.to_string(checkout_date)
    
    @api.model
    def _get_hold_date(self):
        self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
        hold_date = fields.Datetime.context_timestamp(self, fields.Datetime.now() + timedelta(days=1))
        return fields.Datetime.to_string(hold_date)
    
    @api.model
    def _get_cancel_date(self):
        self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
        cancel_date = fields.Datetime.context_timestamp(self, fields.Datetime.now() + timedelta(days=1))
        return fields.Datetime.to_string(cancel_date)

    bookin_date = fields.Datetime(
        "Book In", required=True, readonly=True, states={"draft": [("readonly", False)], "done": [("readonly", True)]}, default=_get_bookin_date
    )
    
    bookout_date = fields.Datetime(
        "Book Out", required=True, readonly=True, states={"draft": [("readonly", False)], "done": [("readonly", True)]}, default=_get_bookout_date
        )

    hold_date = fields.Datetime(
        "Hold", readonly=True, default=_get_hold_date
        )
    
    cancel_date = fields.Datetime(
        "Cancel", readonly=True, default=_get_cancel_date
        )

    @api.depends('helpdesk_tickets_ids')
    def _get_helpdesk_tickets_count(self):
        for rec in self:
            rec.helpdesk_tickets_count = len(rec.helpdesk_tickets_ids)

    def helpdesk_ticket(self):
        action = self.env.ref('helpdesk.helpdesk_ticket_action_main_tree').read()[0]
        tickets = self.prescription_order_lines.mapped('helpdesk_description_id')
        if len(tickets) > 1:
            action['domain'] = [('id', 'in', tickets.ids)]
        elif tickets:
            action['views'] = [(self.env.ref('helpdesk.helpdesk_ticket_view_form').id, 'form')]
            action['res_id'] = tickets.id
        return action
    
    def action_draft(self):
        self.state = 'draft'

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'

    def action_hold(self):
        self.state = 'hold'

    def confirm_draft(self):
        for rec in self:
            rec.state = 'draft'
            
    # Overwrite Confirm Button
    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an prescription in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for prescription in self.filtered(lambda prescription: prescription.partner_id not in prescription.message_partner_ids):
            prescription.message_subscribe([prescription.partner_id.id])
        self.write({'state': 'done', 'bookin_date': fields.Datetime.now()})
        self._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        helpdesk_ticket_dict = {}
        helpdesk_ticket_list = []
        for line in self.prescription_order_lines:
            if line:
                if line.product_id.is_helpdesk:
                    helpdesk_ticket_dict = {
                                            'name' : line.product_id.name,
                                            'team_id' : line.product_id.helpdesk_team.id,
                                            'user_id' : line.product_id.helpdesk_assigned_to.id,
                                            'partner_id' : self.partner_id.id,
                                            'partner_name' : self.partner_id.name,
                                            'partner_email' : self.partner_id.email,
                                            'description' : line.name  
                                           }
                    helpdesk_ticket_id = self.env['helpdesk.ticket'].create(helpdesk_ticket_dict)
                    if helpdesk_ticket_id:
                        line.helpdesk_description_id = helpdesk_ticket_id.id
                        helpdesk_ticket_list.append(helpdesk_ticket_id.id)
                        self.helpdesk_tickets_ids = helpdesk_ticket_list
        return True
    

    # Forefoot Values
    ff_varus_lt = fields.Many2one(comodel_name='pod.forefoot.value', string='FF Varus LT', ondelete='restrict', copy=True)
    ff_varus_rt = fields.Many2one(comodel_name='pod.forefoot.value', string='FF Varus RT', ondelete='restrict', copy=True)
    ff_valgus_lt = fields.Many2one(comodel_name='pod.forefoot.value', string='FF Valgus LT', ondelete='restrict', copy=True)
    ff_valgus_rt = fields.Many2one(comodel_name='pod.forefoot.value', string='FF Valgus RT', ondelete='restrict', copy=True)
    # Forefoot Corrections
    ff_varus_intrinsic_lt = fields.Many2one(comodel_name='pod.forefoot.correction', string='FF Varus Intrinsic LT', ondelete='restrict', copy=True)
    ff_varus_intrinsic_rt = fields.Many2one(comodel_name='pod.forefoot.correction', string='FF Varus Intrinsic RT', ondelete='restrict', copy=True)
    ff_varus_extrinsic_lt = fields.Many2one(comodel_name='pod.forefoot.correction', string='FF Varus Extrinsic LT', ondelete='restrict', copy=True)
    ff_varus_extrinsic_rt = fields.Many2one(comodel_name='pod.forefoot.correction', string='FF Varus Extrinsic RT', ondelete='restrict', copy=True)
    ff_valgus_intrinsic_lt = fields.Many2one(comodel_name='pod.forefoot.correction', string='FF Valgus Intrinsic LT', ondelete='restrict', copy=True)
    ff_valgus_intrinsic_rt = fields.Many2one(comodel_name='pod.forefoot.correction', string='FF Valgus Intrinsic RT', ondelete='restrict', copy=True)
    ff_valgus_extrinsic_lt = fields.Many2one(comodel_name='pod.forefoot.correction', string='FF Valgus Extrinsic LT', ondelete='restrict', copy=True)
    ff_valgus_extrinsic_rt = fields.Many2one(comodel_name='pod.forefoot.correction', string='FF Valgus Extrinsic RT', ondelete='restrict', copy=True)

    # Rearfoot Corrections
    rf_varus_lt = fields.Many2one(comodel_name='pod.rearfoot.correction', string='RF Varus LT', ondelete='restrict', copy=True)
    rf_varus_rt = fields.Many2one(comodel_name='pod.rearfoot.correction', string='RF Varus RT', ondelete='restrict', copy=True)
    rf_valgus_lt = fields.Many2one(comodel_name='pod.rearfoot.correction', string='RF Valgus LT', ondelete='restrict', copy=True)
    rf_valgus_rt = fields.Many2one(comodel_name='pod.rearfoot.correction', string='RF Valgus RT', ondelete='restrict', copy=True)
    rf_neutral_lt = fields.Many2one(comodel_name='pod.rearfoot.correction', string='RF Neutral LT', ondelete='restrict', copy=True)
    rf_neutral_rt = fields.Many2one(comodel_name='pod.rearfoot.correction', string='RF Neutral RT', ondelete='restrict', copy=True)
 
    # Orthotic Measures
    ff_length_lt = fields.Many2one(comodel_name='pod.orthotic.measure', string='FF Length LT', ondelete='restrict', copy=True)
    ff_length_rt = fields.Many2one(comodel_name='pod.orthotic.measure', string='FF Length RT', ondelete='restrict', copy=True)
    heel_depth_lt = fields.Many2one(comodel_name='pod.orthotic.measure', string='Heel Depth LT', ondelete='restrict', copy=True)
    heel_depth_rt = fields.Many2one(comodel_name='pod.orthotic.measure', string='Heel Depth RT', ondelete='restrict', copy=True)
    orthotic_length_lt = fields.Many2one(comodel_name='pod.orthotic.measure', string='Orthotic Length LT', ondelete='restrict', copy=True)
    orthotic_length_rt = fields.Many2one(comodel_name='pod.orthotic.measure', string='Orthotic Length RT', ondelete='restrict', copy=True)
    cap_size_lt = fields.Many2one(comodel_name='pod.orthotic.measure', string='Cap Size LT', ondelete='restrict', copy=True)
    cap_size_rt = fields.Many2one(comodel_name='pod.orthotic.measure', string='Cap Size RT', ondelete='restrict', copy=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('pod.prescription.order') or _('New')
        res = super(Prescription, self).create(vals)
        if res.stage_id.state in ("done", "cancel"):
            raise exceptions.UserError("State not allowed for new prescriptions.")
        return res

    def write(self, vals):
        if "stage_id" in vals and "kanban_state" not in vals:
            vals["kanban_state"] = "normal"
        old_state = self.stage_id.state
        super().write(vals)
        new_state = self.stage_id.state
        if not self.env.context.get("_prescription_write"):
            if new_state != old_state and new_state == "draft": self.with_context(_prescription_write=True).write(
                    {"bookin_date": fields.Date.today()})
            if new_state != old_state and new_state == "done": self.with_context(_prescription_write=True).write(
                    {"bookout_date": fields.Date.today()})
            if new_state != old_state and new_state == "cancel": self.with_context(_prescription_write=True).write(
                    {"cancel_date": fields.Date.today()})
            if new_state != old_state and new_state == "hold": self.with_context(_prescription_write=True).write(
                    {"hold_date": fields.Date.today()})
        return True

    def button_done(self):
        Stage = self.env["pod_order_management.prescription.stage"]
        done_stage = Stage.search([("state", "=", "done")], limit=1)
        for prescription in self:
            prescription.stage_id = done_stage
        return True
    
    def button_cancel(self):
        Stage = self.env["pod_order_management.prescription.stage"]
        cancel_stage = Stage.search([("state", "=", "cancel")], limit=1)
        for prescription in self:
            prescription.stage_id = cancel_stage
        return True

    def button_hold(self):
        Stage = self.env["pod_order_management.prescription.stage"]
        hold_stage = Stage.search([("state", "=", "hold")], limit=1)
        for prescription in self:
            prescription.stage_id = hold_stage
        return True
    
    def unlink(self):
        if self.state == 'done':
            raise ValidationError(_("You Cannot Delete %s as it is in Done State" % self.name))
        return super(Prescription, self).unlink()

    def action_url(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'https://www.nwpodiatric.com' % self.prescription,
        }

    def create_sale_order(self):
        # Search for associated sale order
        sale_order = self.env['sale.order'].search([('prescription_order_id', '=', self.id)], limit=1)
        # If sale order exists, open its form view
        if sale_order:
            return self._prepare_action(_('Prescription order'), 'sale.order', sale_order.id)
        # If sale order doesn't exist, create a new sale order with invoice_status set to 'to_invoice'
        vals = {
            'prescription_order_id': self.id,
            'partner_id': self.practice_id.id,
            'practitioner_id': self.practitioner_id.id,
            'patient_id': self.patient_id.id,
            'invoice_status': 'to invoice',
            # 'invoice_status': 'to_invoice',  
        }
        new_sale_order = self.env['sale.order'].create(vals)
        # Create sales order lines from prescription_order_line
        for line in self.prescription_order_lines:
            line_vals = {
                'order_id': new_sale_order.id,
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'product_uom': line.product_id.uom_id.id,
                'product_uom_qty': line.quantity,
                'price_unit': line.product_id.lst_price,  
            }
            self.env['sale.order.line'].create(line_vals)
        # Return the form view of the new sales order
        return self._prepare_action(_('Prescription Order'), 'sale.order', new_sale_order.id)

    def _prepare_action(self, name, res_model, res_id=None, context=None):
        action = {
            'name': name,
            'view_type': 'form',
            'res_model': res_model,
            'view_id': False,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
        }
        if res_id:
            action['res_id'] = res_id
        if context:
            action['context'] = context
        return action

    def prescription_report(self):
        return self.env.ref('pod_order_management.report_print_prescription').report_action(self)

    def print_prescription_measure_report(self):
        return self.env.ref("pod_order_management.practitioner_prescription_ticket_size2").report_action(self)

    def print_pod_prescription_order_report(self):
        return self.env.ref("pod_order_management.practitioner_prescription_pod_ticket_size2").report_action(self)


FIELDS_PROPERTIES = {
    'pod.forefoot.value': ['ff_varus', 'ff_valgus'],
    'pod.forefoot.correction': ['ff_varus_intrinsic', 'ff_varus_extrinsic', 'ff_valgus_intrinsic', 'ff_valgus_extrinsic'],
    'pod.rearfoot.correction': ['rf_varus', 'rf_valgus', 'rf_neutral'],
    'pod.orthotic.measure': ['ff_length', 'heel_depth', 'orthotic_length', 'cap_size']
}

SIDE_SUFFIXES = ['lt', 'rt']

def add_dynamic_fields_to_class(cls):
    for model, field_names in FIELDS_PROPERTIES.items():
        for field_name in field_names:
            for side in SIDE_SUFFIXES:
                field_identifier = f"{field_name}_{side}"
                # Dynamically set the field on the class
                setattr(
                    cls,
                    field_identifier,
                    fields.Many2one( comodel_name=model, string=field_identifier.replace("_", " ").title(),
                        # relation=f"rx_{field_identifier}", ondelete='restrict', copy=True
                    )
                )

# Add the dynamic fields to the Prescription class
add_dynamic_fields_to_class(Prescription)


class PrescriptionOrderLine(models.Model):
    _name = "pod.prescription.order.line"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Prescription Order Lines'
    _rec_name = 'prescription_order_id'
    
    @api.depends('product_id')
    def onchange_product(self):
        for each in self:
            if each:
                self.qty_available = self.product_id.qty_available
                self.price = self.product_id.lst_price
            else:
                self.qty_available = 0
                self.price = 0.0

    name = fields.Text(string='Description')
    company_id = fields.Many2one(related='prescription_order_id.company_id', string='Company', store=True, index=True)
    helpdesk_description_id = fields.Many2one('helpdesk.ticket',string='Helpdesk')
    prescription_order_id = fields.Many2one('pod.prescription.order', string='Prescription')
    product_id = fields.Many2one('product.product', string='Products')
    prescription_order_line_image = fields.Binary(related="product_id.image_1920")
    uom_id = fields.Many2one('uom.uom', string='Unit')
    quantity = fields.Float(string='Quantity', digits='Product Quantity')
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]", ondelete="restrict")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_uom_readonly = fields.Boolean(compute='_compute_product_uom_readonly')
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    state = fields.Selection(related="prescription_order_id.stage_id.state", string='Status', copy=False, store=True)
    display_type = fields.Selection([('line_section', "Section"), ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    sequence = fields.Integer(string='Sequence', default=10)
    product_updatable = fields.Boolean(compute='_compute_product_updatable', string='Can Edit Product', default=True)
    remark = fields.Text(string='Remark')

    custom_value_ids = fields.One2many( comodel_name="product.config.session.custom.value", inverse_name="cfg_session_id", related="config_session_id.custom_value_ids", string="Configurator Custom Values")
    config_ok = fields.Boolean( related="product_id.config_ok", string="Configurable", readonly=True)
    config_session_id = fields.Many2one( comodel_name="product.config.session", string="Config Session")

    def reconfigure_product(self):
        """Creates and launches a product configurator wizard with a linked
        template and variant in order to re-configure a existing product. It is
        esetially a shortcut to pre-fill configuration data of a variant"""
        wizard_model = "product.configurator.prescription"

        extra_vals = {
            "prescription_order_id": self.prescription_order_id.id,
            "prescription_order_line_id": self.id,
            "product_id": self.product_id.id,
        }
        self = self.with_context( default_prescription_order_id=self.prescription_order_id.id, default_prescription_order_line_id=self.id,
        )
        return self.product_id.product_tmpl_id.create_config_wizard( model_name=wizard_model, extra_vals=extra_vals
        )
        
    @api.model
    def _prepare_add_missing_fields(self, values):
        """ Deduce missing required fields from the onchange """
        res = {}
        onchange_fields = ['name', 'price_unit', 'product_uom']
        if values.get('order_id') and values.get('product_id') and any(f not in values for f in onchange_fields):
            line = self.new(values)
            line.product_id_change()
            for field in onchange_fields:
                if field not in values:
                    res[field] = line._fields[field].convert_to_write(line[field], line)
        return res
        
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
            return

        return super(PrescriptionOrderLine, self).product_uom_change()
    
    @api.depends('state')
    def _compute_product_uom_readonly(self):
        for line in self:
            line.product_uom_readonly = line.state in ['done', 'cancel']
    
    @api.depends('product_id', 'prescription_order_id.state')
    def _compute_product_updatable(self):
        for line in self:
            if line.state in ['done', 'cancel']:
                line.product_updatable = False
            else:
                line.product_updatable = True
 
                
    # @api.onchange("product_id")
    # def onchange_product(self):
    #     res = super(PrescriptionOrderLine, self).product_id_change() if hasattr(super(), 'product_id_change') else {}
    #     for record in self:
    #         if record.product_id:
    #             record.qty_available = record.product_id.qty_available
    #             record.price = record.product_id.lst_price
    #             product_with_context = record.product_id.with_context(lang=record.prescription_order_id.partner_id.lang)
    #             if product_with_context.variant_description:
    #                 record.name = product_with_context.variant_description
    #         else:
    #             record.qty_available = 0
    #             record.price = 0.0
    #     return res
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

