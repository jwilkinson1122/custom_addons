from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class EmbroideryEmbroidery(models.Model):
    _name = 'embroidery.embroidery'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'embroidery Manufacturing Orders'

    name = fields.Char('REFERENCE', copy=False, readonly=True, default=lambda x: _('New'))
    company_id = fields.Many2one(
        'res.company', 'COMPANY', index=True,
        default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string="CUSTOMER")
    product_id = fields.Many2one(
        'product.product', 'PRODUCT',
        readonly=False, required=False, check_company=True,
        states={'draft': [('readonly', False)]})

    product_tmpl_id = fields.Many2one('product.product', 'PRODUCT', readonly=True)

    # test_001 = fields.Float(related='bom_id.test_001', store=True, index=True, readonly=True)

    avg_prod_stch = fields.Float(string="AVERAGE PS", required=False, )
    days_plan = fields.Float(string="DAYS PLAN", required=False, )

    @api.onchange('days_plan', 'production_stitches', 'avg_prod_stch')
    def onchange_days_plan(self):
        if self.stitched == 0:
            self.days_plan = self.avg_prod_stch

        elif self.stitched != 0:
            self.days_plan = self.production_stitches / self.avg_prod_stch

    @api.onchange('flow')
    def onchange_flow(self):
        if self.flow == 'flow_one':
            self.avg_prod_stch = 980000
            # self.days_plan = self.production_stitches / self.avg_prod_stch

        elif self.flow == 'flow_two':
            self.avg_prod_stch = 800000
            # self.days_plan = self.production_stitches / self.avg_prod_stch

        else:
            self.avg_prod_stch = 0

        # self.days_plan = self.production_stitches / self.avg_prod_stch

    product_qty = fields.Float(related='bom_id.total_repeats', default=1.0, required=True, tracking=True,
                               states={'draft': [('readonly', False)]})
    # stitched = fields.Float(string="STITCHES", required=False, )

    stitched = fields.Float(related='bom_id.total_stitch', required=False, )

    total_head = fields.Float(related='bom_id.total_head', required=False, default=24.0)
    total_stitches = fields.Float(string="TOTAL STITCHES", required=False, readonly=True,
                                  compute='_compute_total_production_stitches')

    # total_stitches = fields.Float(related='bom_id.total_stitches', required=False, readonly=True,
    #                               compute='_compute_total_production_stitches')

    total_fabric = fields.Float(related='bom_id.total_fabric', required=False, readonly=True)
    production_stitches = fields.Float(string="PRODUCTION STITCHES", required=False, readonly=True)
    machine = fields.Selection(string="MACHINE",
                               selection=[('product_one', 'Production-M-01'), ('production_two', 'Production-M-02'),
                                          ('production_three', 'Production-M-03'),
                                          ('production_sampling', 'Sampling-M-04'),
                                          ], required=False, default='product_one')
    date_deadline = fields.Datetime('DATE DEADLINE', copy=False, index=True)
    date_planned = fields.Datetime(
        'PLANNED DATE', copy=False, default=fields.Datetime.now,
        help="Date at which you plan to start the production.",
        index=True, required=True, store=True)
    date_planned_finished = fields.Datetime(
        'Planned End Date',
        help="Date at which you plan to finish the production.",
        copy=False, store=True)
    date_start = fields.Datetime('Start Date', copy=False, index=True, readonly=True)
    date_finished = fields.Datetime('End Date', copy=False, index=True, readonly=True)
    date_start_wo = fields.Datetime(
        'Plan From', copy=False, readonly=True,
        help="Work orders will be planned based on the availability of the work centers\
                 starting from this date. If empty, the work orders will be planned as soon as possible.",
    )
    bom_id = fields.Many2one(
        'embroidery.bom', 'BILL OF MATERIALS', readonly=False)

    state = fields.Selection([
        ('draft', 'FABRIC QUALITY'),
        ('thread_store', 'THREAD STORE'),
        ('emb_production', 'PRODUCTION'),
        ('hand_work', 'HAND WORK'),
        ('emb_finishing', 'FINISHING'),
        ('internal_audit', 'INTERNAL AUDIT'),
        ('external_audit', 'EXTERNAL AUDIT'),
        ('dispatch', 'DISPATCH'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled')], string='STATE',
        compute='_compute_state', copy=False, index=True, readonly=True,
        store=True, tracking=True, default='draft')

    draft_stage = fields.Char(string="Stage", default='FABRIC QUALITY', readonly=True)
    thread_stage = fields.Char(string="Stage", default='THREAD STORE', readonly=True)
    production_stage = fields.Char(string="Stage", default='PRODUCTION', readonly=True)
    clipping_stage = fields.Char(string="Stage", default='HANDWORK', readonly=True)
    finishing_stage = fields.Char(string="Stage", default='FINISHING', readonly=True)
    internal_audit = fields.Char(string="Stage", default='INTERNAL AUDIT', readonly=True)
    external_audit = fields.Char(string="Stage", default='EXTERNAL AUDIT', readonly=True)
    dispatch_stage = fields.Char(string="Stage", default='DISPATCH', readonly=True)
    confirmed_stage = fields.Char(string="Stage", default='CONFIRMED', readonly=True)

    flow = fields.Selection(string="FLOW", selection=[('flow_one', 'PRODUCTION'), ('flow_two', 'SAMPLING'), ],
                            required=False,
                            default='flow_one')
    flow_one_string = fields.Char(string="PRODUCTION     : ",
                                  default='FABRIC QUALITY, THREAD STORE, PRODUCTION, HANDWORK, FINISHING, INTERNAL AUDIT, EXTERNAL AUDIT, DISPATCH ,DISPATCH',
                                  readonly=True)
    flow_two_string = fields.Char(string="SAMPLING : ",
                                  default='FABRIC QUALITY, THREAD STORE, PRODUCTION, HANDWORK, FINISHING, INTERNAL AUDIT, DISPATCH ,DISPATCH',
                                  readonly=True)

    production_qty_update = fields.Boolean(string="production_qty_update", default=True)
    components_qty_update = fields.Boolean(string="components_qty_update", default=True)
    entry = fields.Boolean(string="Entry", default=True)
    internal_layout = fields.Boolean(string="internal layout", default=True)
    back_internal_layout = fields.Boolean(string="Back internal layout", default=False)
    external_layout = fields.Boolean(string="external layout", default=True)
    dispatch_button = fields.Boolean(string="dispatch", default=True)
    user_id = fields.Many2one(
        'res.users', 'RESPONSIBLE', default=lambda self: self.env.user,
        states={'confirmed': [('readonly', True)], 'cancel': [('readonly', True)]})

    is_locked = fields.Boolean('Is Locked', default=True, copy=False)
    fabric_height = fields.Float(related='bom_id.fabric_height', required=False)
    design_height = fields.Float(related='bom_id.design_height', required=False)
    # designed_head = fields.Float(string="DESIGN HEAD", required=False)
    designed_head = fields.Selection(string="DESIGN HEAD",
                                     selection=[('single_head', 'Single Head'), ('double_head', 'Double Head'),
                                                ('triple_head', 'Triple Head')],
                                     required=False, default='single_head')

    embroidery_line_ids = fields.One2many('embroidery.lines', 'bom_id', 'BoM Lines', copy=True)
    fabric_quality_line_ids = fields.One2many('fabric.quality.lines', 'fabric_id', 'Fabric Quality', copy=True)
    result_embroidery_line_ids = fields.One2many('result.embroidery.lines', 'result_id', 'RESULT LINE', copy=True)

    thread_employee_ids = fields.One2many('thread.store.lines', 'thread_id', 'Fabric Quality', copy=True)
    production_employee_ids = fields.One2many('production.employee.lines', 'production_id', 'Fabric Quality', copy=True)
    handwork_employee_ids = fields.One2many('clipping.employee.lines', 'handwork_id', 'Fabric Quality', copy=True)
    finishing_employee_ids = fields.One2many('finishing.employee.lines', 'finishing_id', 'Fabric Quality', copy=True)
    audit_employee_ids = fields.One2many('audit.employee.lines', 'audit_id', 'Fabric Quality', copy=True)
    ex_audit_employee_ids = fields.One2many('external.audit.lines', 'ex_audit_id', 'External Audit', copy=True)
    disp_audit_employee_ids = fields.One2many('disp.employee.lines', 'disp_id', 'External Audit', copy=True)
    dispatch_employee_ids = fields.One2many('dispatch.employee.lines', 'dispatch_id', 'Fabric Quality', copy=True)

    # brand_id = fields.Many2one('product.template', readonly=True)
    # batch_no = fields.Char('product.template', readonly=True)
    # taxes_id = fields.Char('product.template', readonly=True)

    # brand_id = fields.Many2one('product.template',  readonly=True)
    # batch_no = fields.Char('product.template',  readonly=True)

    """COMPUTE METHOD FOR FORM FIELDS COMPUTATION"""

    @api.depends('stitched', 'total_head', 'product_qty', 'total_stitches', 'total_fabric', 'design_height',
                 'production_stitches')
    def _compute_total_production_stitches(self):
        # print('compute function')
        for rec in self:
            # print("stitched", rec.stitched)
            rec.total_stitches = rec.stitched * (rec.product_qty * rec.total_head)
            rec.production_stitches = rec.stitched * rec.product_qty
            # print('total stitches : ', rec.total_stitches)
            if rec.total_head == 24:
                rec.total_fabric = rec.product_qty * 8.5
                # print('total fabric if head 24 : ', rec.total_fabric)
            if rec.total_head == 8:
                rec.total_fabric = rec.product_qty * 2.9
                # print('total fabric if head 8 : ', rec.total_fabric)

            # designed head and width
            # if rec.design_height > 13:
            #     rec.designed_head = rec.design_height * 2
            # if rec.design_height > 25:
            #     rec.designed_head = rec.design_height * 2

    """THIS PART FOR AUTO GETTING COMPONENTS OF SELECTED BOM"""

    @api.onchange('bom_id')
    def onchange_method(self):
        print('onchange on bill of materials')
        self.product_tmpl_id = self.bom_id.product_tmpl_id
        # self.product_id = self.bom_id.product_tmpl_id
        data = []
        for line in self.bom_id.bom_line_ids:
            data.append((0, 0, {
                'id': line.id,
                'product_id': line.product_id.id,
                'stitches': line.stitches,
                'attach': line.attach,
                'total_stitches': line.total_stitches,
                'total_yard': line.total_yard,
                'total_cones': line.total_cones,
                'available_stock': line.available_stock,
                'lot_size': line.lot_size,
                'factor': line.factor,
                'real_factor': line.real_factor,
                'net_cones': abs(line.net_cones),
                'net_ordering': line.net_ordering
            }))
        self.embroidery_line_ids = False
        self.embroidery_line_ids = data

    """API CONSTRAINTS FOR FABRIC AND DESIGN WIDTH"""

    @api.constrains('design_height')
    def _check_design_height_method(self):
        for rec in self:
            if rec.design_height > rec.fabric_height:
                raise ValidationError("Design Height Should be 4 Inch Less Than Fabric Height.")

    """THIS PART FOR SEQUENCE OF ORDER"""

    @api.model
    def create(self, vals):
        # overriding the create method to add the sequence
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('embroidery.embroidery') or _('New')
        result = super(EmbroideryEmbroidery, self).create(vals)
        return result

    """FABRIC BALANCE PART"""

    @api.onchange('fabric_quality_line_ids')
    def fabric_balance(self):
        print('ONCHANGE FOR FABRIC LINE')
        for rec in self.fabric_quality_line_ids:
            total = rec.a_grade_fabric + rec.b_grade_fabric + rec.reject_fabric
            rem_fabric = total - rec.total_fabric
            rec.balance_fabric = abs(rem_fabric)

    """STEP PROCEED BUTTON"""

    def action_emb_production(self):
        print('emb production')
        # MANUFACTURING QUANTITY UPDATING PART
        if self.production_qty_update:
            location = self.env.ref('stock.stock_location_stock')
            product = self.product_tmpl_id
            qty = self.product_qty
            updated_qty = self.env['stock.quant']._update_available_quantity(product, location, qty)
            print('Updated Plus Quantity', updated_qty)
            self.production_qty_update = False
        # COMPONENT QUANTITY DECREASING PART
        if self.components_qty_update:
            for line in self.embroidery_line_ids:
                product = line.product_id
                qty = line.total_cones
                updated_qty = self.env['stock.quant']._update_available_quantity(product, location, -qty)
                print('Updated Subtract Quantity', updated_qty)
            self.components_qty_update = False

        self.state = 'emb_production'

    def action_thread_store(self):
        print('Production')
        self.state = 'thread_store'

    def action_hand_work(self):
        print('emb hand_work')
        self.state = 'hand_work'

    def action_emb_finishing(self):
        print('emb finishing')
        self.state = 'emb_finishing'

    def action_internal_audit(self):
        print('internal_audit')
        if self.flow == 'flow_two':
            self.dispatch_button = True
        if self.flow == 'flow_one':
            self.external_layout = True
            self.dispatch_button = False
        self.state = 'internal_audit'

    def action_external_audit(self):
        print('action external_audit')
        self.state = 'external_audit'

    def action_emb_dispatch(self):
        print('emb_dispatch')
        if self.flow == 'flow_two':
            self.back_internal_layout = True
        if self.flow == 'flow_one':
            self.back_internal_layout = False
        self.state = 'dispatch'

    def action_confirm(self):
        print('emb_dispatch')
        self.state = 'confirmed'

    @api.onchange('flow')
    def onchange_on_flow(self):
        print('onchange on flow')
        if self.flow == 'flow_two':
            self.external_layout = False
            self.internal_layout = True
        else:
            self.external_layout = True
            self.internal_layout = True

    # reverse button

    def action_to_cancel(self):
        print('Back cancel')
        self.state = 'cancel'

    def action_back_draft(self):
        print('emb draft back')
        self.state = 'draft'

    def action_back_thread_store(self):
        print('emb thread store back')
        self.state = 'thread_store'

    def action_back_production(self):
        print('emb production back')
        self.state = 'emb_production'

    def action_back_hand_work(self):
        print('emb hand_work back')
        self.state = 'hand_work'

    def action_back_finishing(self):
        print('emb finishing back')
        self.state = 'emb_finishing'

    def action_back_internal_audit(self):
        print('internal_audit back')
        self.state = 'internal_audit'

    def action_back_external_audit(self):
        print('action_back_external_audit back')
        self.state = 'external_audit'

    def action_back_dispatch(self):
        print('action_back_dispatch back')
        self.state = 'dispatch'

    """THREAD STORE UPDATE ACTION"""

    def thread_store_update_action(self):
        # self.thread_employee_ids.check = True
        if self.product_qty > 0:
            # print('action thread store')
            print('action thread store 1111111111111111111111111')
            data = []
            result_repeats = 0
            result_stitches = 0
            result_reject_stitches = 0
            result_reject_repeats = 0

            total_repeats_closed = 0
            total_stitches_closed = 0
            total_reject_repeats = 0
            total_reject_stitches = 0
            for line in self.thread_employee_ids:
                line.check_new = False
                print("Check Value: ", line.check_new)

                total_repeats_closed = total_repeats_closed + line.closed_repeats
                total_stitches_closed = total_stitches_closed + line.closed_stitches
                total_reject_repeats = total_reject_repeats + line.reject_repeats
                if line.line_readonly == 1:
                    result_repeats = result_repeats + line.closed_repeats
                    result_stitches = result_stitches + line.closed_stitches
                    result_reject_stitches = result_reject_stitches + line.reject_stitches
                    result_reject_repeats = result_reject_repeats + line.reject_repeats

                data.append((0, 0, {
                    'id': self.id,
                    'employee_id': line.employee_id.id,
                    'rate': line.rate,
                    'line_readonly': 1,
                    'shift': line.shift,
                    'reject_repeats': line.reject_repeats,
                    'reject_stitches': line.reject_stitches,
                    'closed_repeats': line.closed_repeats,
                    'closed_stitches': line.closed_stitches,
                }))

                # line.check = False

            if total_repeats_closed <= self.product_qty:
                print('total_repeats_closed : ', total_repeats_closed)
                if total_stitches_closed <= self.total_stitches:
                    print('total_stitches_closed : ', total_stitches_closed)
                    if total_reject_repeats <= self.product_qty:
                        print('total_reject_repeats : ', total_reject_repeats)
                        if total_reject_stitches <= self.total_stitches:
                            print('total_reject_stitches : ', total_reject_stitches)
                            # reject repeats and closed repeats
                            all_repeats = total_repeats_closed + total_reject_repeats
                            if all_repeats <= self.product_qty:
                                # reject stitches and closed stitches
                                all_stitches = total_stitches_closed + total_reject_stitches
                                if all_stitches <= self.total_stitches:
                                    self.thread_employee_ids = False
                                    self.thread_employee_ids = data
                                    print('DATA IS : ', data)

                                    """STAGE RESULT"""
                                    for result in self.result_embroidery_line_ids:
                                        if self.state == 'thread_store':
                                            result.total_repeats = self.product_qty
                                            result.total_stitches = self.total_stitches
                                            result.closed_repeats = result_repeats
                                            result.closed_stitches = result_stitches
                                            result.pending_repeats = self.product_qty - result_repeats
                                            result.pending_stitches = self.total_stitches - result_stitches

                                    """PART FOR CREATING INVOICE OF EMPLOYEE"""
                                    account_id = self.env['account.account'].search(
                                        [('name', '=', 'Salary Expenses'), ('user_type_id', '=', 'Expenses')])

                                    for emp_line in self.thread_employee_ids:
                                        if emp_line.line_readonly:
                                            inv_id = self.env['account.move'].search([])
                                            for inv_emp in inv_id:
                                                for inv_emp_line in inv_emp.invoice_line_ids:
                                                    if inv_emp.amount_total > 0:
                                                        if inv_emp.partner_id.id == emp_line.employee_id.user_partner_id.id:
                                                            print('employee is : ',
                                                                  emp_line.employee_id.user_partner_id.name,
                                                                  ' : partner is : ', inv_emp.partner_id.name)
                                                            if inv_emp.amount_total == emp_line.rate:
                                                                print('already amount ', inv_emp.amount_total,
                                                                      'total rate ', emp_line.rate)
                                                                if inv_emp_line.quantity == emp_line.closed_repeats:
                                                                    print('already quantity', inv_emp_line.quantity,
                                                                          'Closed Repeats ', emp_line.closed_repeats)
                                                                    print('Record Not Created for ',
                                                                          emp_line.employee_id.user_partner_id.name)
                                                                    self.entry = False

                                            if self.entry:
                                                print('record created for : ',
                                                      emp_line.employee_id.user_partner_id.name)
                                                invoice = self.env['account.move'].create({
                                                    'type': 'out_invoice',
                                                    'partner_id': emp_line.employee_id.user_partner_id.id,
                                                    'company_id': self.env.company.id,
                                                    'ref': self.name,
                                                    'invoice_user_id': self.user_id.id,
                                                    'invoice_date': self.date_planned,
                                                    'invoice_line_ids': [(0, 0, {
                                                        'product_id': self.product_tmpl_id.id,
                                                        'account_id': account_id,
                                                        'name': self.product_tmpl_id.default_code,
                                                        'quantity': emp_line.closed_repeats,
                                                        'price_unit': emp_line.rate,
                                                    })]
                                                })
                                        self.entry = True
                                        """PART END CREATING  EMPLOYEE INVOICE"""

                                else:
                                    print('all stitches', all_stitches)
                                    raise UserError(
                                        _('Your Reject stitches and Closed stitches Cannot More than Total stitches'))
                            else:
                                print('all repeats', all_repeats)
                                raise UserError(
                                    _('Your Reject Repeats and Closed repeats Cannot More than Total Repeats'))

                        else:
                            print('total_reject_stitches : ', total_reject_stitches)
                            raise UserError(_('YOU CANNOT REJECT STITCHES QUANTITY MORE THAN TOTAL STITCHES'))
                    else:
                        print('total_reject_repeats : ', total_reject_repeats)
                        raise UserError(_('YOU CANNOT REJECT REPEATS QUANTITY MORE THAN TOTAL REPEATS'))
                else:
                    print('total_stitches_closed : ', total_stitches_closed)
                    raise UserError(_('YOU CANNOT CLOSE STITCHES QUANTITY MORE THAN TOTAL STITCHES'))
            else:
                print('total_repeats_closed : ', total_repeats_closed)
                raise UserError(_('YOU CANNOT CLOSE REPEATS MORE THAN TOTAL REPEATS'))

        else:
            raise UserError(_('YOU DONE HAVE QUANTITY'))

    """PRODUCTION UPDATE ACTION"""

    def production_update_action(self):
        if self.product_qty > 0:
            print('action production store')
            data = []
            result_repeats = 0
            result_stitches = 0
            result_reject_stitches = 0
            result_reject_repeats = 0

            total_repeats_closed = 0
            total_stitches_closed = 0
            total_reject_repeats = 0
            total_reject_stitches = 0
            for line in self.production_employee_ids:
                total_repeats_closed = total_repeats_closed + line.closed_repeats
                total_stitches_closed = total_stitches_closed + line.closed_stitches
                total_reject_repeats = total_reject_repeats + line.reject_repeats
                if line.line_readonly == 1:
                    result_repeats = result_repeats + line.closed_repeats
                    result_stitches = result_stitches + line.closed_stitches
                    result_reject_stitches = result_reject_stitches + line.reject_stitches
                    result_reject_repeats = result_reject_repeats + line.reject_repeats

                data.append((0, 0, {
                    'id': self.id,
                    'employee_id': line.employee_id.id,
                    'rate': line.rate,
                    'line_readonly': 1,
                    'shift': line.shift,
                    'reject_repeats': line.reject_repeats,
                    'reject_stitches': line.reject_stitches,
                    'closed_repeats': line.closed_repeats,
                    'closed_stitches': line.closed_stitches,
                }))

            if total_repeats_closed <= self.product_qty:
                print('total_repeats_closed : ', total_repeats_closed)
                if total_stitches_closed <= self.total_stitches:
                    print('total_stitches_closed : ', total_stitches_closed)
                    if total_reject_repeats <= self.product_qty:
                        print('total_reject_repeats : ', total_reject_repeats)
                        if total_reject_stitches <= self.total_stitches:
                            print('total_reject_stitches : ', total_reject_stitches)
                            # reject repeats and closed repeats
                            all_repeats = total_repeats_closed + total_reject_repeats
                            if all_repeats <= self.product_qty:
                                # reject stitches and closed stitches
                                all_stitches = total_stitches_closed + total_reject_stitches
                                if all_stitches <= self.total_stitches:
                                    self.production_employee_ids = False
                                    self.production_employee_ids = data
                                    print('DATA IS : ', data)

                                    """STAGE RESULT"""
                                    for result in self.result_embroidery_line_ids:
                                        if self.state == 'emb_production':
                                            result.total_repeats = self.product_qty
                                            result.total_stitches = self.total_stitches
                                            result.closed_repeats = result_repeats
                                            result.closed_stitches = result_stitches
                                            result.pending_repeats = self.product_qty - result_repeats
                                            result.pending_stitches = self.total_stitches - result_stitches

                                    """PART FOR CREATING INVOICE OF EMPLOYEE"""
                                    account_id = self.env['account.account'].search(
                                        [('name', '=', 'Salary Expenses'), ('user_type_id', '=', 'Expenses')])

                                    for emp_line in self.production_employee_ids:
                                        if emp_line.line_readonly:
                                            inv_id = self.env['account.move'].search([])
                                            for inv_emp in inv_id:
                                                for inv_emp_line in inv_emp.invoice_line_ids:
                                                    if inv_emp.amount_total > 0:
                                                        if inv_emp.partner_id.id == emp_line.employee_id.user_partner_id.id:
                                                            print('employee is : ',
                                                                  emp_line.employee_id.user_partner_id.name,
                                                                  ' : partner is : ', inv_emp.partner_id.name)
                                                            if inv_emp.amount_total == emp_line.rate:
                                                                print('already amount ', inv_emp.amount_total,
                                                                      'total rate ', emp_line.rate)
                                                                if inv_emp_line.quantity == emp_line.closed_repeats:
                                                                    print('already quantity', inv_emp_line.quantity,
                                                                          'Closed Repeats ', emp_line.closed_repeats)
                                                                    print('Record Not Created for ',
                                                                          emp_line.employee_id.user_partner_id.name)
                                                                    self.entry = False

                                            if self.entry:
                                                print('record created for : ',
                                                      emp_line.employee_id.user_partner_id.name)
                                                invoice = self.env['account.move'].create({
                                                    'type': 'out_invoice',
                                                    'partner_id': emp_line.employee_id.user_partner_id.id,
                                                    'company_id': self.env.company.id,
                                                    'ref': self.name,
                                                    'invoice_user_id': self.user_id.id,
                                                    'invoice_date': self.date_planned,
                                                    'invoice_line_ids': [(0, 0, {
                                                        'product_id': self.product_tmpl_id.id,
                                                        'account_id': account_id,
                                                        'name': self.product_tmpl_id.default_code,
                                                        'quantity': emp_line.closed_repeats,
                                                        'price_unit': emp_line.rate,
                                                    })]
                                                })
                                        self.entry = True
                                        """PART END CREATING  EMPLOYEE INVOICE"""

                                else:
                                    print('all stitches', all_stitches)
                                    raise UserError(
                                        _('Your Reject stitches and Closed stitches Cannot More than Total stitches'))
                            else:
                                print('all repeats', all_repeats)
                                raise UserError(
                                    _('Your Reject Repeats and Closed repeats Cannot More than Total Repeats'))

                        else:
                            print('total_reject_stitches : ', total_reject_stitches)
                            raise UserError(_('YOU CANNOT REJECT STITCHES QUANTITY MORE THAN TOTAL STITCHES'))
                    else:
                        print('total_reject_repeats : ', total_reject_repeats)
                        raise UserError(_('YOU CANNOT REJECT REPEATS QUANTITY MORE THAN TOTAL REPEATS'))
                else:
                    print('total_stitches_closed : ', total_stitches_closed)
                    raise UserError(_('YOU CANNOT CLOSE STITCHES QUANTITY MORE THAN TOTAL STITCHES'))
            else:
                print('total_repeats_closed : ', total_repeats_closed)
                raise UserError(_('YOU CANNOT CLOSE REPEATS MORE THAN TOTAL REPEATS'))

        else:
            raise UserError(_('YOU DONE HAVE QUANTITY'))

    """HANDWORK UPDATE ACTION"""

    def handwork_update_action(self):
        if self.product_qty > 0:
            print('action handwork store')
            data = []
            result_repeats = 0
            result_stitches = 0
            result_reject_stitches = 0
            result_reject_repeats = 0

            total_repeats_closed = 0
            total_stitches_closed = 0
            total_reject_repeats = 0
            total_reject_stitches = 0
            for line in self.handwork_employee_ids:
                total_repeats_closed = total_repeats_closed + line.closed_repeats
                total_stitches_closed = total_stitches_closed + line.closed_stitches
                total_reject_repeats = total_reject_repeats + line.reject_repeats
                if line.line_readonly == 1:
                    result_repeats = result_repeats + line.closed_repeats
                    result_stitches = result_stitches + line.closed_stitches
                    result_reject_stitches = result_reject_stitches + line.reject_stitches
                    result_reject_repeats = result_reject_repeats + line.reject_repeats

                data.append((0, 0, {
                    'id': self.id,
                    'employee_id': line.employee_id.id,
                    'rate': line.rate,
                    'line_readonly': 1,
                    'shift': line.shift,
                    'reject_repeats': line.reject_repeats,
                    'reject_stitches': line.reject_stitches,
                    'closed_repeats': line.closed_repeats,
                    'closed_stitches': line.closed_stitches,
                }))
            if total_repeats_closed <= self.product_qty:
                print('total_repeats_closed : ', total_repeats_closed)
                if total_stitches_closed <= self.total_stitches:
                    print('total_stitches_closed : ', total_stitches_closed)
                    if total_reject_repeats <= self.product_qty:
                        print('total_reject_repeats : ', total_reject_repeats)
                        if total_reject_stitches <= self.total_stitches:
                            print('total_reject_stitches : ', total_reject_stitches)
                            # reject repeats and closed repeats
                            all_repeats = total_repeats_closed + total_reject_repeats
                            if all_repeats <= self.product_qty:
                                # reject stitches and closed stitches
                                all_stitches = total_stitches_closed + total_reject_stitches
                                if all_stitches <= self.total_stitches:
                                    self.handwork_employee_ids = False
                                    self.handwork_employee_ids = data
                                    print('DATA IS : ', data)

                                    """STAGE RESULT"""
                                    for result in self.result_embroidery_line_ids:
                                        if self.state == 'emb_finishing':
                                            result.total_repeats = self.product_qty
                                            result.total_stitches = self.total_stitches
                                            result.closed_repeats = result_repeats
                                            result.closed_stitches = result_stitches
                                            result.pending_repeats = self.product_qty - result_repeats
                                            result.pending_stitches = self.total_stitches - result_stitches

                                    """PART FOR CREATING INVOICE OF EMPLOYEE"""
                                    account_id = self.env['account.account'].search(
                                        [('name', '=', 'Salary Expenses'), ('user_type_id', '=', 'Expenses')])

                                    for emp_line in self.handwork_employee_ids:
                                        if emp_line.line_readonly:
                                            inv_id = self.env['account.move'].search([])
                                            for inv_emp in inv_id:
                                                for inv_emp_line in inv_emp.invoice_line_ids:
                                                    if inv_emp.amount_total > 0:
                                                        if inv_emp.partner_id.id == emp_line.employee_id.user_partner_id.id:
                                                            print('employee is : ',
                                                                  emp_line.employee_id.user_partner_id.name,
                                                                  ' : partner is : ', inv_emp.partner_id.name)
                                                            if inv_emp.amount_total == emp_line.rate:
                                                                print('already amount ', inv_emp.amount_total,
                                                                      'total rate ', emp_line.rate)
                                                                if inv_emp_line.quantity == emp_line.closed_repeats:
                                                                    print('already quantity', inv_emp_line.quantity,
                                                                          'Closed Repeats ', emp_line.closed_repeats)
                                                                    print('Record Not Created for ',
                                                                          emp_line.employee_id.user_partner_id.name)
                                                                    self.entry = False

                                            if self.entry:
                                                print('record created for : ',
                                                      emp_line.employee_id.user_partner_id.name)
                                                invoice = self.env['account.move'].create({
                                                    'type': 'out_invoice',
                                                    'partner_id': emp_line.employee_id.user_partner_id.id,
                                                    'company_id': self.env.company.id,
                                                    'ref': self.name,
                                                    'invoice_user_id': self.user_id.id,
                                                    'invoice_date': self.date_planned,
                                                    'invoice_line_ids': [(0, 0, {
                                                        'product_id': self.product_tmpl_id.id,
                                                        'account_id': account_id,
                                                        'name': self.product_tmpl_id.default_code,
                                                        'quantity': emp_line.closed_repeats,
                                                        'price_unit': emp_line.rate,
                                                    })]
                                                })
                                        self.entry = True
                                        """PART END CREATING  EMPLOYEE INVOICE"""

                                else:
                                    print('all stitches', all_stitches)
                                    raise UserError(
                                        _('Your Reject stitches and Closed stitches Cannot More than Total stitches'))
                            else:
                                print('all repeats', all_repeats)
                                raise UserError(
                                    _('Your Reject Repeats and Closed repeats Cannot More than Total Repeats'))

                        else:
                            print('total_reject_stitches : ', total_reject_stitches)
                            raise UserError(_('YOU CANNOT REJECT STITCHES QUANTITY MORE THAN TOTAL STITCHES'))
                    else:
                        print('total_reject_repeats : ', total_reject_repeats)
                        raise UserError(_('YOU CANNOT REJECT REPEATS QUANTITY MORE THAN TOTAL REPEATS'))
                else:
                    print('total_stitches_closed : ', total_stitches_closed)
                    raise UserError(_('YOU CANNOT CLOSE STITCHES QUANTITY MORE THAN TOTAL STITCHES'))
            else:
                print('total_repeats_closed : ', total_repeats_closed)
                raise UserError(_('YOU CANNOT CLOSE REPEATS MORE THAN TOTAL REPEATS'))

        else:
            raise UserError(_('YOU DONE HAVE QUANTITY'))

    """FINISHING UPDATE ACTION"""

    def finishing_update_action(self):
        if self.product_qty > 0:
            print('action finishing store')
            data = []
            result_repeats = 0
            result_stitches = 0
            result_reject_stitches = 0
            result_reject_repeats = 0

            total_repeats_closed = 0
            total_stitches_closed = 0
            total_reject_repeats = 0
            total_reject_stitches = 0
            for line in self.finishing_employee_ids:
                total_repeats_closed = total_repeats_closed + line.closed_repeats
                total_stitches_closed = total_stitches_closed + line.closed_stitches
                total_reject_repeats = total_reject_repeats + line.reject_repeats
                if line.line_readonly == 1:
                    result_repeats = result_repeats + line.closed_repeats
                    result_stitches = result_stitches + line.closed_stitches
                    result_reject_stitches = result_reject_stitches + line.reject_stitches
                    result_reject_repeats = result_reject_repeats + line.reject_repeats

                data.append((0, 0, {
                    'id': self.id,
                    'employee_id': line.employee_id.id,
                    'rate': line.rate,
                    'line_readonly': 1,
                    'shift': line.shift,
                    'reject_repeats': line.reject_repeats,
                    'reject_stitches': line.reject_stitches,
                    'closed_repeats': line.closed_repeats,
                    'closed_stitches': line.closed_stitches,
                }))
            if total_repeats_closed <= self.product_qty:
                print('total_repeats_closed : ', total_repeats_closed)
                if total_stitches_closed <= self.total_stitches:
                    print('total_stitches_closed : ', total_stitches_closed)
                    if total_reject_repeats <= self.product_qty:
                        print('total_reject_repeats : ', total_reject_repeats)
                        if total_reject_stitches <= self.total_stitches:
                            print('total_reject_stitches : ', total_reject_stitches)
                            # reject repeats and closed repeats
                            all_repeats = total_repeats_closed + total_reject_repeats
                            if all_repeats <= self.product_qty:
                                # reject stitches and closed stitches
                                all_stitches = total_stitches_closed + total_reject_stitches
                                if all_stitches <= self.total_stitches:
                                    self.finishing_employee_ids = False
                                    self.finishing_employee_ids = data
                                    print('DATA IS : ', data)

                                    """STAGE RESULT"""
                                    for result in self.result_embroidery_line_ids:
                                        if self.state == 'hand_work':
                                            result.total_repeats = self.product_qty
                                            result.total_stitches = self.total_stitches
                                            result.closed_repeats = result_repeats
                                            result.closed_stitches = result_stitches
                                            result.pending_repeats = self.product_qty - result_repeats
                                            result.pending_stitches = self.total_stitches - result_stitches

                                    """PART FOR CREATING INVOICE OF EMPLOYEE"""
                                    account_id = self.env['account.account'].search(
                                        [('name', '=', 'Salary Expenses'), ('user_type_id', '=', 'Expenses')])

                                    for emp_line in self.finishing_employee_ids:
                                        if emp_line.line_readonly:
                                            inv_id = self.env['account.move'].search([])
                                            for inv_emp in inv_id:
                                                for inv_emp_line in inv_emp.invoice_line_ids:
                                                    if inv_emp.amount_total > 0:
                                                        if inv_emp.partner_id.id == emp_line.employee_id.user_partner_id.id:
                                                            print('employee is : ',
                                                                  emp_line.employee_id.user_partner_id.name,
                                                                  ' : partner is : ', inv_emp.partner_id.name)
                                                            if inv_emp.amount_total == emp_line.rate:
                                                                print('already amount ', inv_emp.amount_total,
                                                                      'total rate ', emp_line.rate)
                                                                if inv_emp_line.quantity == emp_line.closed_repeats:
                                                                    print('already quantity', inv_emp_line.quantity,
                                                                          'Closed Repeats ', emp_line.closed_repeats)
                                                                    print('Record Not Created for ',
                                                                          emp_line.employee_id.user_partner_id.name)
                                                                    self.entry = False

                                            if self.entry:
                                                print('record created for : ',
                                                      emp_line.employee_id.user_partner_id.name)
                                                invoice = self.env['account.move'].create({
                                                    'type': 'out_invoice',
                                                    'partner_id': emp_line.employee_id.user_partner_id.id,
                                                    'company_id': self.env.company.id,
                                                    'ref': self.name,
                                                    'invoice_user_id': self.user_id.id,
                                                    'invoice_date': self.date_planned,
                                                    'invoice_line_ids': [(0, 0, {
                                                        'product_id': self.product_tmpl_id.id,
                                                        'account_id': account_id,
                                                        'name': self.product_tmpl_id.default_code,
                                                        'quantity': emp_line.closed_repeats,
                                                        'price_unit': emp_line.rate,
                                                    })]
                                                })
                                        self.entry = True
                                        """PART END CREATING  EMPLOYEE INVOICE"""

                                else:
                                    print('all stitches', all_stitches)
                                    raise UserError(
                                        _('Your Reject stitches and Closed stitches Cannot More than Total stitches'))
                            else:
                                print('all repeats', all_repeats)
                                raise UserError(
                                    _('Your Reject Repeats and Closed repeats Cannot More than Total Repeats'))

                        else:
                            print('total_reject_stitches : ', total_reject_stitches)
                            raise UserError(_('YOU CANNOT REJECT STITCHES QUANTITY MORE THAN TOTAL STITCHES'))
                    else:
                        print('total_reject_repeats : ', total_reject_repeats)
                        raise UserError(_('YOU CANNOT REJECT REPEATS QUANTITY MORE THAN TOTAL REPEATS'))
                else:
                    print('total_stitches_closed : ', total_stitches_closed)
                    raise UserError(_('YOU CANNOT CLOSE STITCHES QUANTITY MORE THAN TOTAL STITCHES'))
            else:
                print('total_repeats_closed : ', total_repeats_closed)
                raise UserError(_('YOU CANNOT CLOSE REPEATS MORE THAN TOTAL REPEATS'))

        else:
            raise UserError(_('YOU DONE HAVE QUANTITY'))

    """INTERNAL AUDIT UPDATE ACTION"""

    def int_audit_update_action(self):
        if self.product_qty > 0:
            print('action Internal Audit store')
            data = []
            result_repeats = 0
            result_stitches = 0
            result_reject_stitches = 0
            result_reject_repeats = 0

            total_repeats_closed = 0
            total_stitches_closed = 0
            total_reject_repeats = 0
            total_reject_stitches = 0
            for line in self.audit_employee_ids:
                total_repeats_closed = total_repeats_closed + line.closed_repeats
                total_stitches_closed = total_stitches_closed + line.closed_stitches
                total_reject_repeats = total_reject_repeats + line.reject_repeats
                if line.line_readonly == 1:
                    result_repeats = result_repeats + line.closed_repeats
                    result_stitches = result_stitches + line.closed_stitches
                    result_reject_stitches = result_reject_stitches + line.reject_stitches
                    result_reject_repeats = result_reject_repeats + line.reject_repeats

                data.append((0, 0, {
                    'id': self.id,
                    'employee_id': line.employee_id.id,
                    'rate': line.rate,
                    'line_readonly': 1,
                    'shift': line.shift,
                    'reject_repeats': line.reject_repeats,
                    'reject_stitches': line.reject_stitches,
                    'closed_repeats': line.closed_repeats,
                    'closed_stitches': line.closed_stitches,
                }))
            if total_repeats_closed <= self.product_qty:
                print('total_repeats_closed : ', total_repeats_closed)
                if total_stitches_closed <= self.total_stitches:
                    print('total_stitches_closed : ', total_stitches_closed)
                    if total_reject_repeats <= self.product_qty:
                        print('total_reject_repeats : ', total_reject_repeats)
                        if total_reject_stitches <= self.total_stitches:
                            print('total_reject_stitches : ', total_reject_stitches)
                            # reject repeats and closed repeats
                            all_repeats = total_repeats_closed + total_reject_repeats
                            if all_repeats <= self.product_qty:
                                # reject stitches and closed stitches
                                all_stitches = total_stitches_closed + total_reject_stitches
                                if all_stitches <= self.total_stitches:
                                    self.audit_employee_ids = False
                                    self.audit_employee_ids = data
                                    print('DATA IS : ', data)

                                    """STAGE RESULT"""
                                    for result in self.result_embroidery_line_ids:
                                        if self.state == 'internal_audit':
                                            result.total_repeats = self.product_qty
                                            result.total_stitches = self.total_stitches
                                            result.closed_repeats = result_repeats
                                            result.closed_stitches = result_stitches
                                            result.pending_repeats = self.product_qty - result_repeats
                                            result.pending_stitches = self.total_stitches - result_stitches

                                    """PART FOR CREATING INVOICE OF EMPLOYEE"""
                                    account_id = self.env['account.account'].search(
                                        [('name', '=', 'Salary Expenses'), ('user_type_id', '=', 'Expenses')])

                                    for emp_line in self.audit_employee_ids:
                                        if emp_line.line_readonly:
                                            inv_id = self.env['account.move'].search([])
                                            for inv_emp in inv_id:
                                                for inv_emp_line in inv_emp.invoice_line_ids:
                                                    if inv_emp.amount_total > 0:
                                                        if inv_emp.partner_id.id == emp_line.employee_id.user_partner_id.id:
                                                            print('employee is : ',
                                                                  emp_line.employee_id.user_partner_id.name,
                                                                  ' : partner is : ', inv_emp.partner_id.name)
                                                            if inv_emp.amount_total == emp_line.rate:
                                                                print('already amount ', inv_emp.amount_total,
                                                                      'total rate ', emp_line.rate)
                                                                if inv_emp_line.quantity == emp_line.closed_repeats:
                                                                    print('already quantity', inv_emp_line.quantity,
                                                                          'Closed Repeats ', emp_line.closed_repeats)
                                                                    print('Record Not Created for ',
                                                                          emp_line.employee_id.user_partner_id.name)
                                                                    self.entry = False

                                            if self.entry:
                                                print('record created for : ',
                                                      emp_line.employee_id.user_partner_id.name)
                                                invoice = self.env['account.move'].create({
                                                    'type': 'out_invoice',
                                                    'partner_id': emp_line.employee_id.user_partner_id.id,
                                                    'company_id': self.env.company.id,
                                                    'ref': self.name,
                                                    'invoice_user_id': self.user_id.id,
                                                    'invoice_date': self.date_planned,
                                                    'invoice_line_ids': [(0, 0, {
                                                        'product_id': self.product_tmpl_id.id,
                                                        'account_id': account_id,
                                                        'name': self.product_tmpl_id.default_code,
                                                        'quantity': emp_line.closed_repeats,
                                                        'price_unit': emp_line.rate,
                                                    })]
                                                })
                                        self.entry = True
                                        """PART END CREATING  EMPLOYEE INVOICE"""

                                else:
                                    print('all stitches', all_stitches)
                                    raise UserError(
                                        _('Your Reject stitches and Closed stitches Cannot More than Total stitches'))
                            else:
                                print('all repeats', all_repeats)
                                raise UserError(
                                    _('Your Reject Repeats and Closed repeats Cannot More than Total Repeats'))

                        else:
                            print('total_reject_stitches : ', total_reject_stitches)
                            raise UserError(_('YOU CANNOT REJECT STITCHES QUANTITY MORE THAN TOTAL STITCHES'))
                    else:
                        print('total_reject_repeats : ', total_reject_repeats)
                        raise UserError(_('YOU CANNOT REJECT REPEATS QUANTITY MORE THAN TOTAL REPEATS'))
                else:
                    print('total_stitches_closed : ', total_stitches_closed)
                    raise UserError(_('YOU CANNOT CLOSE STITCHES QUANTITY MORE THAN TOTAL STITCHES'))
            else:
                print('total_repeats_closed : ', total_repeats_closed)
                raise UserError(_('YOU CANNOT CLOSE REPEATS MORE THAN TOTAL REPEATS'))

        else:
            raise UserError(_('YOU DONE HAVE QUANTITY'))

    """EXTERNAL AUDIT UPDATE ACTION"""

    def ext_audit_update_action(self):
        if self.product_qty > 0:
            print('action External Audit store')
            data = []
            result_repeats = 0
            result_stitches = 0
            result_reject_stitches = 0
            result_reject_repeats = 0

            total_repeats_closed = 0
            total_stitches_closed = 0
            total_reject_repeats = 0
            total_reject_stitches = 0
            for line in self.ex_audit_employee_ids:
                total_repeats_closed = total_repeats_closed + line.closed_repeats
                total_stitches_closed = total_stitches_closed + line.closed_stitches
                total_reject_repeats = total_reject_repeats + line.reject_repeats
                if line.line_readonly == 1:
                    result_repeats = result_repeats + line.closed_repeats
                    result_stitches = result_stitches + line.closed_stitches
                    result_reject_stitches = result_reject_stitches + line.reject_stitches
                    result_reject_repeats = result_reject_repeats + line.reject_repeats

                data.append((0, 0, {
                    'id': self.id,
                    'employee_id': line.employee_id.id,
                    'rate': line.rate,
                    'line_readonly': 1,
                    'shift': line.shift,
                    'reject_repeats': line.reject_repeats,
                    'reject_stitches': line.reject_stitches,
                    'closed_repeats': line.closed_repeats,
                    'closed_stitches': line.closed_stitches,
                }))
            if total_repeats_closed <= self.product_qty:
                print('total_repeats_closed : ', total_repeats_closed)
                if total_stitches_closed <= self.total_stitches:
                    print('total_stitches_closed : ', total_stitches_closed)
                    if total_reject_repeats <= self.product_qty:
                        print('total_reject_repeats : ', total_reject_repeats)
                        if total_reject_stitches <= self.total_stitches:
                            print('total_reject_stitches : ', total_reject_stitches)
                            # reject repeats and closed repeats
                            all_repeats = total_repeats_closed + total_reject_repeats
                            if all_repeats <= self.product_qty:
                                # reject stitches and closed stitches
                                all_stitches = total_stitches_closed + total_reject_stitches
                                if all_stitches <= self.total_stitches:
                                    self.ex_audit_employee_ids = False
                                    self.ex_audit_employee_ids = data
                                    print('DATA IS : ', data)

                                    """STAGE RESULT"""
                                    for result in self.result_embroidery_line_ids:
                                        if self.state == 'external_audit':
                                            result.total_repeats = self.product_qty
                                            result.total_stitches = self.total_stitches
                                            result.closed_repeats = result_repeats
                                            result.closed_stitches = result_stitches
                                            result.pending_repeats = self.product_qty - result_repeats
                                            result.pending_stitches = self.total_stitches - result_stitches

                                    """PART FOR CREATING INVOICE OF EMPLOYEE"""
                                    account_id = self.env['account.account'].search(
                                        [('name', '=', 'Salary Expenses'), ('user_type_id', '=', 'Expenses')])

                                    for emp_line in self.ex_audit_employee_ids:
                                        if emp_line.line_readonly:
                                            inv_id = self.env['account.move'].search([])
                                            for inv_emp in inv_id:
                                                for inv_emp_line in inv_emp.invoice_line_ids:
                                                    if inv_emp.amount_total > 0:
                                                        if inv_emp.partner_id.id == emp_line.employee_id.user_partner_id.id:
                                                            print('employee is : ',
                                                                  emp_line.employee_id.user_partner_id.name,
                                                                  ' : partner is : ', inv_emp.partner_id.name)
                                                            if inv_emp.amount_total == emp_line.rate:
                                                                print('already amount ', inv_emp.amount_total,
                                                                      'total rate ', emp_line.rate)
                                                                if inv_emp_line.quantity == emp_line.closed_repeats:
                                                                    print('already quantity', inv_emp_line.quantity,
                                                                          'Closed Repeats ', emp_line.closed_repeats)
                                                                    print('Record Not Created for ',
                                                                          emp_line.employee_id.user_partner_id.name)
                                                                    self.entry = False

                                            if self.entry:
                                                print('record created for : ',
                                                      emp_line.employee_id.user_partner_id.name)
                                                invoice = self.env['account.move'].create({
                                                    'type': 'out_invoice',
                                                    'partner_id': emp_line.employee_id.user_partner_id.id,
                                                    'company_id': self.env.company.id,
                                                    'ref': self.name,
                                                    'invoice_user_id': self.user_id.id,
                                                    'invoice_date': self.date_planned,
                                                    'invoice_line_ids': [(0, 0, {
                                                        'product_id': self.product_tmpl_id.id,
                                                        'account_id': account_id,
                                                        'name': self.product_tmpl_id.default_code,
                                                        'quantity': emp_line.closed_repeats,
                                                        'price_unit': emp_line.rate,
                                                    })]
                                                })
                                        self.entry = True
                                        """PART END CREATING  EMPLOYEE INVOICE"""

                                else:
                                    print('all stitches', all_stitches)
                                    raise UserError(
                                        _('Your Reject stitches and Closed stitches Cannot More than Total stitches'))
                            else:
                                print('all repeats', all_repeats)
                                raise UserError(
                                    _('Your Reject Repeats and Closed repeats Cannot More than Total Repeats'))

                        else:
                            print('total_reject_stitches : ', total_reject_stitches)
                            raise UserError(_('YOU CANNOT REJECT STITCHES QUANTITY MORE THAN TOTAL STITCHES'))
                    else:
                        print('total_reject_repeats : ', total_reject_repeats)
                        raise UserError(_('YOU CANNOT REJECT REPEATS QUANTITY MORE THAN TOTAL REPEATS'))
                else:
                    print('total_stitches_closed : ', total_stitches_closed)
                    raise UserError(_('YOU CANNOT CLOSE STITCHES QUANTITY MORE THAN TOTAL STITCHES'))
            else:
                print('total_repeats_closed : ', total_repeats_closed)
                raise UserError(_('YOU CANNOT CLOSE REPEATS MORE THAN TOTAL REPEATS'))

        else:
            raise UserError(_('YOU DONE HAVE QUANTITY'))

    """DISPATCH AUDIT UPDATE ACTION"""

    def dispatch_update_action(self):
        if self.product_qty > 0:
            print('action Dispatch Audit store')
            data = []
            result_repeats = 0
            result_stitches = 0
            result_reject_stitches = 0
            result_reject_repeats = 0

            total_repeats_closed = 0
            total_stitches_closed = 0
            total_reject_repeats = 0
            total_reject_stitches = 0
            for line in self.disp_audit_employee_ids:
                total_repeats_closed = total_repeats_closed + line.closed_repeats
                total_stitches_closed = total_stitches_closed + line.closed_stitches
                total_reject_repeats = total_reject_repeats + line.reject_repeats
                if line.line_readonly == 1:
                    result_repeats = result_repeats + line.closed_repeats
                    result_stitches = result_stitches + line.closed_stitches
                    result_reject_stitches = result_reject_stitches + line.reject_stitches
                    result_reject_repeats = result_reject_repeats + line.reject_repeats

                data.append((0, 0, {
                    'id': self.id,
                    'employee_id': line.employee_id.id,
                    'rate': line.rate,
                    'line_readonly': 1,
                    'shift': line.shift,
                    'reject_repeats': line.reject_repeats,
                    'reject_stitches': line.reject_stitches,
                    'closed_repeats': line.closed_repeats,
                    'closed_stitches': line.closed_stitches,
                }))
            if total_repeats_closed <= self.product_qty:
                print('total_repeats_closed : ', total_repeats_closed)
                if total_stitches_closed <= self.total_stitches:
                    print('total_stitches_closed : ', total_stitches_closed)
                    if total_reject_repeats <= self.product_qty:
                        print('total_reject_repeats : ', total_reject_repeats)
                        if total_reject_stitches <= self.total_stitches:
                            print('total_reject_stitches : ', total_reject_stitches)
                            # reject repeats and closed repeats
                            all_repeats = total_repeats_closed + total_reject_repeats
                            if all_repeats <= self.product_qty:
                                # reject stitches and closed stitches
                                all_stitches = total_stitches_closed + total_reject_stitches
                                if all_stitches <= self.total_stitches:
                                    self.disp_audit_employee_ids = False
                                    self.disp_audit_employee_ids = data
                                    print('DATA IS : ', data)

                                    """STAGE RESULT"""
                                    for result in self.result_embroidery_line_ids:
                                        if self.state == 'external_audit':
                                            result.total_repeats = self.product_qty
                                            result.total_stitches = self.total_stitches
                                            result.closed_repeats = result_repeats
                                            result.closed_stitches = result_stitches
                                            result.pending_repeats = self.product_qty - result_repeats
                                            result.pending_stitches = self.total_stitches - result_stitches

                                    """PART FOR CREATING INVOICE OF EMPLOYEE"""
                                    account_id = self.env['account.account'].search(
                                        [('name', '=', 'Salary Expenses'), ('user_type_id', '=', 'Expenses')])

                                    for emp_line in self.disp_audit_employee_ids:
                                        if emp_line.line_readonly:
                                            inv_id = self.env['account.move'].search([])
                                            for inv_emp in inv_id:
                                                for inv_emp_line in inv_emp.invoice_line_ids:
                                                    if inv_emp.amount_total > 0:
                                                        if inv_emp.partner_id.id == emp_line.employee_id.user_partner_id.id:
                                                            print('employee is : ',
                                                                  emp_line.employee_id.user_partner_id.name,
                                                                  ' : partner is : ', inv_emp.partner_id.name)
                                                            if inv_emp.amount_total == emp_line.rate:
                                                                print('already amount ', inv_emp.amount_total,
                                                                      'total rate ', emp_line.rate)
                                                                if inv_emp_line.quantity == emp_line.closed_repeats:
                                                                    print('already quantity', inv_emp_line.quantity,
                                                                          'Closed Repeats ', emp_line.closed_repeats)
                                                                    print('Record Not Created for ',
                                                                          emp_line.employee_id.user_partner_id.name)
                                                                    self.entry = False

                                            if self.entry:
                                                print('record created for : ',
                                                      emp_line.employee_id.user_partner_id.name)
                                                invoice = self.env['account.move'].create({
                                                    'type': 'out_invoice',
                                                    'partner_id': emp_line.employee_id.user_partner_id.id,
                                                    'company_id': self.env.company.id,
                                                    'ref': self.name,
                                                    'invoice_user_id': self.user_id.id,
                                                    'invoice_date': self.date_planned,
                                                    'invoice_line_ids': [(0, 0, {
                                                        'product_id': self.product_tmpl_id.id,
                                                        'account_id': account_id,
                                                        'name': self.product_tmpl_id.default_code,
                                                        'quantity': emp_line.closed_repeats,
                                                        'price_unit': emp_line.rate,
                                                    })]
                                                })
                                        self.entry = True
                                        """PART END CREATING  EMPLOYEE INVOICE"""

                                else:
                                    print('all stitches', all_stitches)
                                    raise UserError(
                                        _('Your Reject stitches and Closed stitches Cannot More than Total stitches'))
                            else:
                                print('all repeats', all_repeats)
                                raise UserError(
                                    _('Your Reject Repeats and Closed repeats Cannot More than Total Repeats'))

                        else:
                            print('total_reject_stitches : ', total_reject_stitches)
                            raise UserError(_('YOU CANNOT REJECT STITCHES QUANTITY MORE THAN TOTAL STITCHES'))
                    else:
                        print('total_reject_repeats : ', total_reject_repeats)
                        raise UserError(_('YOU CANNOT REJECT REPEATS QUANTITY MORE THAN TOTAL REPEATS'))
                else:
                    print('total_stitches_closed : ', total_stitches_closed)
                    raise UserError(_('YOU CANNOT CLOSE STITCHES QUANTITY MORE THAN TOTAL STITCHES'))
            else:
                print('total_repeats_closed : ', total_repeats_closed)
                raise UserError(_('YOU CANNOT CLOSE REPEATS MORE THAN TOTAL REPEATS'))

        else:
            raise UserError(_('YOU DONE HAVE QUANTITY'))


class FabricQualityLines(models.Model):
    _name = 'fabric.quality.lines'
    _description = 'Embroidery Bill of Material Line'
    _check_company_auto = True

    fabric_id = fields.Many2one('embroidery.embroidery', ondelete='cascade')
    total_fabric = fields.Float(string="TOTAL FABRIC", required=False)
    a_grade_fabric = fields.Float(string="A GRADE FABRIC", required=False)
    b_grade_fabric = fields.Float(string="B GRADE FABRIC", required=False)
    reject_fabric = fields.Float(string="REJECT FABRIC", required=False)
    balance_fabric = fields.Float(string="BALANCE FABRIC", required=False)


class EmbroideryBomLine(models.Model):
    _name = 'embroidery.lines'
    _description = 'Embroidery Bill of Material Line'

    bom_id = fields.Many2one('embroidery.embroidery', 'BoM', ondelete='cascade')
    company_id = fields.Many2one(related='bom_id.company_id', store=True, index=True, readonly=True)
    product_id = fields.Many2one('product.product', 'COMPONENTS', required=True, check_company=True)
    attach = fields.Char(string="ATTACH", required=False, )
    stitches = fields.Float(string="STITCHES", required=False)
    total_stitches = fields.Float(string="TOTAL STITCHES", required=False, readonly=True)
    total_yard = fields.Float(string="TOTAL YARD", required=False, readonly=True)
    total_cones = fields.Float(string="TOTAL CONES", required=False, readonly=True)
    available_stock = fields.Float(string="INVENTORY", required=False, readonly=True)
    net_cones = fields.Float(string="NET CONE", required=False)
    lot_size = fields.Float(string="LOT SIZE", required=False)
    factor = fields.Float(string="FACTOR", required=False)
    real_factor = fields.Float(string="FACTOR", required=False)
    net_ordering = fields.Float(string="NET ORDERING", required=False)


class ResultEmbroideryLine(models.Model):
    _name = 'result.embroidery.lines'
    _description = 'Embroidery Bill of Material Line'

    result_id = fields.Many2one('embroidery.embroidery', 'BoM', ondelete='cascade')
    company_id = fields.Many2one(store=True, index=True, readonly=True, default=lambda self: self.env.company)
    total_repeats = fields.Float(string="TOTAL REPEATS", required=False, )
    closed_repeats = fields.Float(string="CLOSED REPEATS", required=False, )
    pending_repeats = fields.Float(string="PENDING REPEATS", required=False, )
    total_stitches = fields.Float(string="TOTAL STITCHES", required=False, )
    closed_stitches = fields.Float(string="CLOSED STITCHES", required=False, )
    pending_stitches = fields.Float(string="PENDING STITCHES", required=False, )


class ThreadStoreEmployeeLines(models.Model):
    _name = 'thread.store.lines'
    _description = 'Embroidery Production Line'

    thread_id = fields.Many2one('embroidery.embroidery', ondelete='cascade')
    company_id = fields.Many2one(store=True, index=True, readonly=True, default=lambda self: self.env.company)
    employee_id = fields.Many2one('hr.employee', 'EMPLOYEE', required=True, check_company=True)
    rate = fields.Float(string="RATE", required=False)
    shift = fields.Selection(string="SHIFT", selection=[('day', 'MORNING'), ('night', 'NIGHT'), ], required=False,
                             default='day')
    closed_repeats = fields.Float(string="NO.OF REPEATS CLOSED", required=False)
    closed_stitches = fields.Float(string="NO.OF STITCHES CLOSED", required=False)
    reject_repeats = fields.Float(string="NO.OF REPEATS REJECT", required=False)
    reject_stitches = fields.Float(string="NO.OF STITCHES REJECT", required=False)
    work_done = fields.Float(string="WORK DONE", required=False)
    line_readonly = fields.Boolean(string="READONLY", default=False)

    check_new = fields.Boolean(string="Check New", default=True)

    # def unlink(self):
    #     if self.check == 'True':
    #         raise ValidationError(_("You Cannot Edite until it is in Done State"))
    #     return super(ThreadStoreEmployeeLines, self).unlink()


class ProductEmployeeLines(models.Model):
    _name = 'production.employee.lines'
    _description = 'Embroidery Production Line'

    production_id = fields.Many2one('embroidery.embroidery', ondelete='cascade')
    company_id = fields.Many2one(store=True, index=True, readonly=True, default=lambda self: self.env.company)
    employee_id = fields.Many2one('hr.employee', 'EMPLOYEE', required=True, check_company=True)
    rate = fields.Float(string="RATE", required=False)
    shift = fields.Selection(string="SHIFT", selection=[('day', 'MORNING'), ('night', 'NIGHT'), ], required=False,
                             default='day')
    closed_repeats = fields.Float(string="NO.OF REPEATS CLOSED", required=False)
    closed_stitches = fields.Float(string="NO.OF STITCHES CLOSED", required=False)
    reject_repeats = fields.Float(string="NO.OF REPEATS REJECT", required=False)
    reject_stitches = fields.Float(string="NO.OF STITCHES REJECT", required=False)
    work_done = fields.Float(string="WORK DONE", required=False)
    line_readonly = fields.Boolean(string="READONLY", default=False)


class ClippingEmployeeLines(models.Model):
    _name = 'clipping.employee.lines'
    _description = 'Embroidery Production Line'

    handwork_id = fields.Many2one('embroidery.embroidery', 'BoM', ondelete='cascade')
    company_id = fields.Many2one(store=True, index=True, readonly=True, default=lambda self: self.env.company)
    employee_id = fields.Many2one('hr.employee', 'EMPLOYEE', required=True, check_company=True)
    rate = fields.Float(string="RATE", required=False)
    shift = fields.Selection(string="SHIFT", selection=[('day', 'MORNING'), ('night', 'NIGHT'), ], required=False,
                             default='day')
    closed_repeats = fields.Float(string="NO.OF REPEATS CLOSED", required=False)
    closed_stitches = fields.Float(string="NO.OF STITCHES CLOSED", required=False)
    reject_repeats = fields.Float(string="NO.OF REPEATS REJECT", required=False)
    reject_stitches = fields.Float(string="NO.OF STITCHES REJECT", required=False)
    work_done = fields.Float(string="WORK DONE", required=False)
    line_readonly = fields.Boolean(string="READONLY", default=False)


class FinishingEmployeeLines(models.Model):
    _name = 'finishing.employee.lines'
    _description = 'Embroidery Production Line'

    finishing_id = fields.Many2one('embroidery.embroidery', ondelete='cascade')
    company_id = fields.Many2one(store=True, index=True, readonly=True, default=lambda self: self.env.company)
    employee_id = fields.Many2one('hr.employee', 'EMPLOYEE', required=True, check_company=True)
    rate = fields.Float(string="RATE", required=False)
    shift = fields.Selection(string="SHIFT", selection=[('day', 'MORNING'), ('night', 'NIGHT'), ], required=False,
                             default='day')
    closed_repeats = fields.Float(string="NO.OF REPEATS CLOSED", required=False)
    closed_stitches = fields.Float(string="NO.OF STITCHES CLOSED", required=False)
    reject_repeats = fields.Float(string="NO.OF REPEATS REJECT", required=False)
    reject_stitches = fields.Float(string="NO.OF STITCHES REJECT", required=False)
    work_done = fields.Float(string="WORK DONE", required=False)
    line_readonly = fields.Boolean(string="READONLY", default=False)


class AuditEmployeeLines(models.Model):
    _name = 'audit.employee.lines'
    _description = 'Embroidery Production Line'

    audit_id = fields.Many2one('embroidery.embroidery', ondelete='cascade')
    company_id = fields.Many2one(store=True, index=True, readonly=True, default=lambda self: self.env.company)
    employee_id = fields.Many2one('hr.employee', 'EMPLOYEE', required=True, check_company=True)
    rate = fields.Float(string="RATE", required=False)
    shift = fields.Selection(string="SHIFT", selection=[('day', 'MORNING'), ('night', 'NIGHT'), ], required=False,
                             default='day')
    closed_repeats = fields.Float(string="NO.OF REPEATS CLOSED", required=False)
    closed_stitches = fields.Float(string="NO.OF STITCHES CLOSED", required=False)
    reject_repeats = fields.Float(string="NO.OF REPEATS REJECT", required=False)
    reject_stitches = fields.Float(string="NO.OF STITCHES REJECT", required=False)
    work_done = fields.Float(string="WORK DONE", required=False)
    line_readonly = fields.Boolean(string="READONLY", default=False)


class ExternalAuditEmployeeLines(models.Model):
    _name = 'external.audit.lines'
    _description = 'Embroidery Production Line'

    ex_audit_id = fields.Many2one('embroidery.embroidery', ondelete='cascade')
    company_id = fields.Many2one(store=True, index=True, readonly=True, default=lambda self: self.env.company)
    employee_id = fields.Many2one('hr.employee', 'EMPLOYEE', required=True, check_company=True)
    rate = fields.Float(string="RATE", required=False)
    shift = fields.Selection(string="SHIFT", selection=[('day', 'MORNING'), ('night', 'NIGHT'), ], required=False,
                             default='day')
    closed_repeats = fields.Float(string="NO.OF REPEATS CLOSED", required=False)
    closed_stitches = fields.Float(string="NO.OF STITCHES CLOSED", required=False)
    reject_repeats = fields.Float(string="NO.OF REPEATS REJECT", required=False)
    reject_stitches = fields.Float(string="NO.OF STITCHES REJECT", required=False)
    work_done = fields.Float(string="WORK DONE", required=False)
    line_readonly = fields.Boolean(string="READONLY", default=False)


class DispatchEmployeeLines(models.Model):
    _name = 'disp.employee.lines'
    _description = 'Embroidery Production Line'

    disp_id = fields.Many2one('embroidery.embroidery', ondelete='cascade')
    company_id = fields.Many2one(store=True, index=True, readonly=True, default=lambda self: self.env.company)
    employee_id = fields.Many2one('hr.employee', 'EMPLOYEE', required=True, check_company=True)
    rate = fields.Float(string="RATE", required=False)
    shift = fields.Selection(string="SHIFT", selection=[('day', 'MORNING'), ('night', 'NIGHT'), ], required=False,
                             default='day')
    closed_repeats = fields.Float(string="NO.OF REPEATS CLOSED", required=False)
    closed_stitches = fields.Float(string="NO.OF STITCHES CLOSED", required=False)
    reject_repeats = fields.Float(string="NO.OF REPEATS REJECT", required=False)
    reject_stitches = fields.Float(string="NO.OF STITCHES REJECT", required=False)
    work_done = fields.Float(string="WORK DONE", required=False)
    line_readonly = fields.Boolean(string="READONLY", default=False)


class ConfirmedEmployeeLines(models.Model):
    _name = 'dispatch.employee.lines'
    _description = 'Embroidery Production Line'

    dispatch_id = fields.Many2one('embroidery.embroidery', ondelete='cascade')
    company_id = fields.Many2one(store=True, index=True, readonly=True, default=lambda self: self.env.company)
    employee_id = fields.Many2one('hr.employee', 'EMPLOYEE', required=True, check_company=True)
    rate = fields.Float(string="RATE", required=False)
    shift = fields.Selection(string="SHIFT", selection=[('day', 'MORNING'), ('night', 'NIGHT'), ], required=False,
                             default='day')
    closed_repeats = fields.Float(string="NO.OF REPEATS CLOSED", required=False, readonly=True)
    closed_stitches = fields.Float(string="NO.OF STITCHES CLOSED", required=False, readonly=True)
    reject_repeats = fields.Float(string="NO.OF REPEATS REJECT", required=False)
    reject_stitches = fields.Float(string="NO.OF STITCHES REJECT", required=False)
    work_done = fields.Float(string="WORK DONE", required=False)
