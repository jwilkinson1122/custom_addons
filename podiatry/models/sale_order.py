
import ast
from datetime import datetime, timedelta

from odoo import _, api, fields, exceptions, models, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError, ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    helpdesk_tickets_ids = fields.Many2many('helpdesk.ticket',string='Helpdesk Tickets')
    helpdesk_tickets_count = fields.Integer(string='# of Delivery Order', compute='_get_helpdesk_tickets_count')
    clinic_id = fields.Many2one(comodel_name='podiatry.podiatry', string='Clinic')
    is_clinic = fields.Boolean(string='Is Clinic')
    is_joint_venture = fields.Boolean(string='Is Joint Venture')
    order_start = fields.Datetime(string='Order Start')
    order_end = fields.Datetime(string='Order End')
    tax_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    clinic_id = fields.Many2one('podiatry.podiatry', 
                                string='Clinic', 
                                readonly=True, 
                                states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, 
                                domain="[('is_clinic', '=', 'True')]")

    type_id = fields.Many2one(
        comodel_name="sale.order.type",
        string="Type",
        compute="_compute_sale_type_id",
        store=True,
        readonly=False,
        states={
            "sale": [("readonly", True)],
            "done": [("readonly", True)],
            "cancel": [("readonly", True)],
        },
        default=lambda so: so._default_type_id(),
        ondelete="restrict",
        copy=True,
        check_company=True,
    )

    @api.model
    def _default_type_id(self):
        return self.env["sale.order.type"].search(
            [("company_id", "in", [self.env.company.id, False])], limit=1
        )

    @api.model
    def _default_sequence_id(self):
        """We get the sequence in same way the core next_by_code method does so we can
        get the proper default sequence"""
        force_company = self.company_id.id or self.env.company.id
        return self.env["ir.sequence"].search(
            [
                ("code", "=", "sale.order"),
                "|",
                ("company_id", "=", force_company),
                ("company_id", "=", False),
            ],
            order="company_id",
            limit=1,
        )

    @api.depends("partner_id", "company_id")
    @api.depends_context("partner_id", "company_id", "company")
    def _compute_sale_type_id(self):
        for record in self:
            if not record.partner_id:
                record.type_id = self.env["sale.order.type"].search(
                    [("company_id", "in", [self.env.company.id, False])], limit=1
                )
            else:
                sale_type = (
                    record.partner_id.with_company(record.company_id).sale_type
                    or record.partner_id.commercial_partner_id.with_company(
                        record.company_id
                    ).sale_type
                )
                if sale_type:
                    record.type_id = sale_type

    @api.onchange("type_id")
    def onchange_type_id(self):
        # TODO: To be changed to computed stored readonly=False if possible in v14?
        vals = {}
        for order in self:
            order_type = order.type_id
            # Order values
            vals = {}
            if order_type.warehouse_id:
                vals.update({"warehouse_id": order_type.warehouse_id})
            if order_type.picking_policy:
                vals.update({"picking_policy": order_type.picking_policy})
            if order_type.payment_term_id:
                vals.update({"payment_term_id": order_type.payment_term_id})
            if order_type.pricelist_id:
                vals.update({"pricelist_id": order_type.pricelist_id})
            if order_type.incoterm_id:
                vals.update({"incoterm": order_type.incoterm_id})
            if order_type.analytic_account_id:
                vals.update({"analytic_account_id": order_type.analytic_account_id})
            if order_type.quotation_validity_days:
                vals.update(
                    {
                        "validity_date": fields.Date.to_string(
                            datetime.now()
                            + timedelta(order_type.quotation_validity_days)
                        )
                    }
                )
            if vals:
                order.update(vals)
            # Order line values
            line_vals = {}
            line_vals.update({"route_id": order_type.route_id.id})
            order.order_line.update(line_vals)


    @api.onchange('tax_id')
    def on_change_tax_id(self):
        for rec in self.order_line:
            rec.tax_id = self.tax_id

    @api.depends('helpdesk_tickets_ids')
    def _get_helpdesk_tickets_count(self):
        for rec in self:
            rec.helpdesk_tickets_count = len(rec.helpdesk_tickets_ids)

    def helpdesk_ticket(self):
        action = self.env.ref('helpdesk.helpdesk_ticket_action_main_tree').read()[0]
        tickets = self.order_line.mapped('helpdesk_description_id')
        if len(tickets) > 1:
            action['domain'] = [('id', 'in', tickets.ids)]
        elif tickets:
            action['views'] = [(self.env.ref('helpdesk.helpdesk_ticket_view_form').id, 'form')]
            action['res_id'] = tickets.id
        return action
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New") and vals.get("type_id"):
                sale_type = self.env["sale.order.type"].browse(vals["type_id"])
                if sale_type.sequence_id:
                    vals["name"] = sale_type.sequence_id.next_by_id(
                        sequence_date=vals.get("date_order"))
        result = super(SaleOrder, self).create(vals_list)
        if not vals.get('is_joint_venture') or vals.get('is_joint_venture') == False:
            result.copy({'is_joint_venture': True})
        return result      
        # return super().create(vals_list)
    
    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         if vals.get("name", _("New")) == _("New") and vals.get("type_id"):
    #             sale_type = self.env["sale.order.type"].browse(vals["type_id"])
    #             if sale_type.sequence_id:
    #                 vals["name"] = sale_type.sequence_id.next_by_id(
    #                     sequence_date=vals.get("date_order")
    #                 )
    #     return super().create(vals_list)
    
    #  @api.model
    # def create(self, vals):
    #     result = super(SaleOrder, self).create(vals)
    #     if not vals.get('is_joint_venture') or vals.get('is_joint_venture') == False:
    #         result.copy({'is_joint_venture': True})
    #     return result

    def write(self, vals):
        """A sale type could have a different order sequence, so we could
        need to change it accordingly"""
        default_sequence = self._default_sequence_id()
        if vals.get("type_id"):
            sale_type = self.env["sale.order.type"].browse(vals["type_id"])
            if sale_type.sequence_id:
                for record in self:
                    # An order with a type without sequence would get the default one.
                    # We want to avoid changing the order reference when the new
                    # sequence has the same default sequence.
                    ignore_default_sequence = (
                        not record.type_id.sequence_id
                        and sale_type.sequence_id == default_sequence
                    )
                    if (
                        record.state in {"draft", "sent"}
                        and record.type_id.sequence_id != sale_type.sequence_id
                        and not ignore_default_sequence
                    ):
                        new_vals = vals.copy()
                        new_vals["name"] = sale_type.sequence_id.next_by_id(
                            sequence_date=vals.get("date_order")
                        )
                        super(SaleOrder, record).write(new_vals)
                    else:
                        super(SaleOrder, record).write(vals)
                return True
        return super().write(vals)

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.type_id.journal_id:
            res["journal_id"] = self.type_id.journal_id.id
        if self.type_id:
            res["sale_type_id"] = self.type_id.id
        return res
    
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




class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    order_line_image = fields.Binary(string="Image", related="product_id.image_1920")
    product_line_image = fields.Binary(string="Image", related="product_id.image_1920")
    product_custom_attribute_value_ids = fields.One2many('product.attribute.custom.value', 'sale_order_line_id', string="Custom Values", copy=True)
    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value', string="Extra Values", ondelete='restrict')
    helpdesk_description_id = fields.Many2one('helpdesk.ticket',string='Helpdesk')
    remark = fields.Text(string='Remark')
    
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
        essentially a shortcut to pre-fill configuration data of a variant"""
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
            super(SaleOrderLine, self).product_uom_change()

   
class SaleOrderStage(models.Model):
    """ Model for case stages. This models the main stages of a Sale Order Request management flow. """
    _name = 'sale.order.stage'
    _description = 'Sale Order Stage'
    _order = 'sequence, id'

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=20)
    fold = fields.Boolean('Folded in Sale Order Pipe')
    done = fields.Boolean('Request Done')


class SaleOrderRequest(models.Model):
    _name = 'sale.order.request'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Sale Order Request'
    _order = "id desc"
    _check_company_auto = True

    @api.returns('self')
    def _default_stage(self):
        return self.env['sale.order.stage'].search([], limit=1)

    def _creation_subtype(self):
        return self.env.ref('sale.order.ord_req_created')

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'stage_id' in init_values:
            return self.env.ref('sale.order.ord_req_status')
        return super(SaleOrderRequest, self)._track_subtype(init_values)

    def _get_default_team_id(self):
        MT = self.env['sale.order.team']
        team = MT.search([('company_id', '=', self.env.company.id)], limit=1)
        if not team:
            team = MT.search([], limit=1)
        return team.id

    name = fields.Char('Subjects', required=True)
    company_id = fields.Many2one('res.company', string='Company',
        default=lambda self: self.env.company)
    description = fields.Html('Description')
    request_date = fields.Date('Request Date', tracking=True, default=fields.Date.context_today,
                               help="Date requested for the sale order to happen")
    owner_user_id = fields.Many2one('res.users', string='Created by User', default=lambda s: s.env.uid)
    category_id = fields.Many2one('sale.order.product.category', related='product_id.category_id', string='Category', store=True, readonly=True)
    product_id = fields.Many2one('sale.order.product', string='Product',
                                   ondelete='restrict', index=True, check_company=True)
    user_id = fields.Many2one('res.users', string='Technician', tracking=True)
    stage_id = fields.Many2one('sale.order.stage', string='Stage', ondelete='restrict', tracking=True,
                               group_expand='_read_group_stage_ids', default=_default_stage, copy=False)
    priority = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')], string='Priority')
    color = fields.Integer('Color Index')
    close_date = fields.Date('Close Date', help="Date the sale order was finished. ")
    kanban_state = fields.Selection([('normal', 'In Progress'), ('blocked', 'Blocked'), ('done', 'Ready for next stage')],
                                    string='Kanban State', required=True, default='normal', tracking=True)
    # active = fields.Boolean(default=True, help="Set active to false to hide the sale order request without deleting it.")
    archive = fields.Boolean(default=False, help="Set archive to true to hide the sale order request without deleting it.")
    
    # laterality_type = fields.Selection([
    #     ('lt', 'Left'), 
    #     ('rt', 'Right'),
    #     ('bl', 'Bilateral')
    #     ], string='Laterality Type', default="laterality")
    
    # sale_order_type = fields.Selection([
    #     ('correctice', 'Corrective'), 
    #     ('preventive', 'Preventive')
    #     ], string='Sale Order Type', default="corrective")
    
    sale_order_type = fields.Selection([
        ('rush', 'Rush Order'), 
        ('normal', 'Normal')
        ], string='Sale Order Type', default="normal")
    
    schedule_date = fields.Datetime('Scheduled Date', help="Date the sale order team plans the sale.order  It should not differ much from the Request Date. ")
    sale_order_team_id = fields.Many2one('sale.order.team', string='Team', required=True, default=_get_default_team_id, check_company=True)
    duration = fields.Float(help="Duration in hours.")
    done = fields.Boolean(related='stage_id.done')

    def archive_product_request(self):
        self.write({'archive': True})

    def reset_product_request(self):
        """ Reinsert the sale order request into the sale order pipe in the first stage"""
        first_stage_obj = self.env['sale.order.stage'].search([], order="sequence asc", limit=1)
        # self.write({'active': True, 'stage_id': first_stage_obj.id})
        self.write({'archive': False, 'stage_id': first_stage_obj.id})

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.sale_order_team_id:
            if self.sale_order_team_id.company_id and not self.sale_order_team_id.company_id.id == self.company_id.id:
                self.sale_order_team_id = False

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.user_id = self.product_id.tech_user_id if self.product_id.tech_user_id else self.product_id.category_id.tech_user_id
            self.category_id = self.product_id.category_id
            if self.product_id.sale_order_team_id:
                self.sale_order_team_id = self.product_id.sale_order_team_id.id

    @api.onchange('category_id')
    def onchange_category_id(self):
        if not self.user_id or not self.product_id or (self.user_id and not self.product_id.tech_user_id):
            self.user_id = self.category_id.tech_user_id

    @api.model
    def create(self, vals):
        # context: no_log, because subtype already handle this
        request = super(SaleOrderRequest, self).create(vals)
        if request.owner_user_id or request.user_id:
            request._add_followers()
        if request.product_id and not request.sale_order_team_id:
            request.sale_order_team_id = request.product_id.sale_order_team_id
        if not request.stage_id.done:
            request.close_date = False
        elif request.stage_id.done and not request.close_date:
            request.close_date = fields.Date.today()
        request.activity_update()
        return request

    def write(self, vals):
        # Overridden to reset the kanban_state to normal whenever
        # the stage (stage_id) of the Sale Order Request changes.
        if vals and 'kanban_state' not in vals and 'stage_id' in vals:
            vals['kanban_state'] = 'normal'
        res = super(SaleOrderRequest, self).write(vals)
        if vals.get('owner_user_id') or vals.get('user_id'):
            self._add_followers()
        if 'stage_id' in vals:
            self.filtered(lambda m: m.stage_id.done).write({'close_date': fields.Date.today()})
            self.filtered(lambda m: not m.stage_id.done).write({'close_date': False})
            self.activity_feedback(['sale.ordermail_act_sale_order_request'])
            self.activity_update()
        if vals.get('user_id') or vals.get('schedule_date'):
            self.activity_update()
        if vals.get('product_id'):
            # need to change description of activity also so unlink old and create new activity
            self.activity_unlink(['sale.ordermail_act_sale_order_request'])
            self.activity_update()
        return res

    def activity_update(self):
        """ Update sale order activities based on current record set state.
        It reschedule, unlink or create sale order request activities. """
        self.filtered(lambda request: not request.schedule_date).activity_unlink(['sale.ordermail_act_sale_order_request'])
        for request in self.filtered(lambda request: request.schedule_date):
            date_dl = fields.Datetime.from_string(request.schedule_date).date()
            updated = request.activity_reschedule(
                ['sale.ordermail_act_sale_order_request'],
                date_deadline=date_dl,
                new_user_id=request.user_id.id or request.owner_user_id.id or self.env.uid)
            if not updated:
                if request.product_id:
                    note = _('Request planned for <a href="#" data-oe-model="%s" data-oe-id="%s">%s</a>') % (
                        request.product_id._name, request.product_id.id, request.product_id.display_name)
                else:
                    note = False
                request.activity_schedule(
                    'sale.ordermail_act_sale_order_request',
                    fields.Datetime.from_string(request.schedule_date).date(),
                    note=note, user_id=request.user_id.id or request.owner_user_id.id or self.env.uid)

    def _add_followers(self):
        for request in self:
            partner_ids = (request.owner_user_id.partner_id + request.user_id.partner_id).ids
            request.message_subscribe(partner_ids=partner_ids)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Read group customization in order to display all the stages in the
            kanban view, even if they are empty
        """
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)


class SaleOrderTeam(models.Model):
    _name = 'sale.order.team'
    _description = 'Sale Order Teams'

    name = fields.Char('Team Name', required=True, translate=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company',
        default=lambda self: self.env.company)
    member_ids = fields.Many2many(
        'res.users', 'sale_order_team_users_rel', string="Team Members",
        domain="[('company_ids', 'in', company_id)]")
    color = fields.Integer("Color Index", default=0)
    request_ids = fields.One2many('sale.order.request', 'sale_order_team_id', copy=False)
    product_ids = fields.One2many('sale.order.product', 'sale_order_team_id', copy=False)

    # For the dashboard only
    todo_request_ids = fields.One2many('sale.order.request', string="Requests", copy=False, compute='_compute_todo_requests')
    todo_request_count = fields.Integer(string="Number of Requests", compute='_compute_todo_requests')
    todo_request_count_date = fields.Integer(string="Number of Requests Scheduled", compute='_compute_todo_requests')
    todo_request_count_high_priority = fields.Integer(string="Number of Requests in High Priority", compute='_compute_todo_requests')
    todo_request_count_block = fields.Integer(string="Number of Requests Blocked", compute='_compute_todo_requests')
    todo_request_count_unscheduled = fields.Integer(string="Number of Requests Unscheduled", compute='_compute_todo_requests')

    @api.depends('request_ids.stage_id.done')
    def _compute_todo_requests(self):
        for team in self:
            team.todo_request_ids = self.env['sale.order.request'].search([('sale_order_team_id', '=', team.id), ('stage_id.done', '=', False)])
            team.todo_request_count = len(team.todo_request_ids)
            team.todo_request_count_date = self.env['sale.order.request'].search_count([('sale_order_team_id', '=', team.id), ('schedule_date', '!=', False)])
            team.todo_request_count_high_priority = self.env['sale.order.request'].search_count([('sale_order_team_id', '=', team.id), ('priority', '=', '3')])
            team.todo_request_count_block = self.env['sale.order.request'].search_count([('sale_order_team_id', '=', team.id), ('kanban_state', '=', 'blocked')])
            team.todo_request_count_unscheduled = self.env['sale.order.request'].search_count([('sale_order_team_id', '=', team.id), ('schedule_date', '=', False)])

    @api.depends('product_ids')
    def _compute_product(self):
        for team in self:
            team.product_count = len(team.product_ids)


class SaleOrderProductCategory(models.Model):
    _name = 'sale.order.product.category'
    _inherit = ['mail.alias.mixin', 'mail.thread']
    _description = 'Sale Order Product Category'

    @api.depends('product_ids')
    def _compute_fold(self):
        # fix mutual dependency: 'fold' depends on 'product_count', which is
        # computed with a read_group(), which retrieves 'fold'!
        self.fold = False
        for category in self:
            category.fold = False if category.product_count else True

    name = fields.Char('Category Name', required=True, translate=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    tech_user_id = fields.Many2one('res.users', 'Responsible', tracking=True, default=lambda self: self.env.uid)
    color = fields.Integer('Color Index')
    note = fields.Html('Comments', translate=True)
    product_ids = fields.One2many('sale.order.product', 'category_id', string='Products', copy=False)
    product_count = fields.Integer(string="Product", compute='_compute_product_count')
    sale_order_ids = fields.One2many('sale.order.request', 'category_id', copy=False)
    sale_order_count = fields.Integer(string="Sale Order Count", compute='_compute_sale_order_count')
    alias_id = fields.Many2one(
        'mail.alias', 'Alias', ondelete='restrict', required=True,
        help="Email alias for this product category. New emails will automatically "
        "create a new product under this category.")
    fold = fields.Boolean(string='Folded in Sale Order Pipe', compute='_compute_fold', store=True)

    def _compute_product_count(self):
        product_data = self.env['sale.order.product'].read_group([('category_id', 'in', self.ids)], ['category_id'], ['category_id'])
        mapped_data = dict([(m['category_id'][0], m['category_id_count']) for m in product_data])
        for category in self:
            category.product_count = mapped_data.get(category.id, 0)

    def _compute_sale_order_count(self):
        sale_order_data = self.env['sale.order.request'].read_group([('category_id', 'in', self.ids)], ['category_id'], ['category_id'])
        mapped_data = dict([(m['category_id'][0], m['category_id_count']) for m in sale_order_data])
        for category in self:
            category.sale_order_count = mapped_data.get(category.id, 0)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_contains_sale_order_requests(self):
        for category in self:
            if category.product_ids or category.sale_order_ids:
                raise UserError(_("You cannot delete an product category containing products or order requests."))

    def _alias_get_creation_values(self):
        values = super(SaleOrderProductCategory, self)._alias_get_creation_values()
        values['alias_model_id'] = self.env['ir.model']._get('sale.order.request').id
        if self.id:
            values['alias_defaults'] = defaults = ast.literal_eval(self.alias_defaults or "{}")
            defaults['category_id'] = self.id
        return values


class SaleOrderProduct(models.Model):
    _name = 'sale.order.product'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sale Order Product'
    _check_company_auto = True

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'owner_user_id' in init_values and self.owner_user_id:
            return self.env.ref('podiatry.ord_mat_assign')
        return super(SaleOrderProduct, self)._track_subtype(init_values)

    def name_get(self):
        result = []
        for record in self:
            if record.name and record.serial_no:
                result.append((record.id, record.name + '/' + record.serial_no))
            if record.name and not record.serial_no:
                result.append((record.id, record.name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        product_ids = []
        if name:
            product_ids = self._search([('name', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid)
        if not product_ids:
            product_ids = self._search([('name', operator, name)] + args, limit=limit, access_rights_uid=name_get_uid)
        return product_ids

    name = fields.Char('Product Name', required=True, translate=True)
    company_id = fields.Many2one('res.company', string='Company',
        default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    tech_user_id = fields.Many2one('res.users', string='Technician', tracking=True)
    owner_user_id = fields.Many2one('res.users', string='Owner', tracking=True)
    category_id = fields.Many2one('sale.order.product.category', string='Product Category',
                                  tracking=True, group_expand='_read_group_category_ids')
    partner_id = fields.Many2one('res.partner', string='Vendor', check_company=True)
    partner_ref = fields.Char('Vendor Reference')
    location = fields.Char('Location')
    model = fields.Char('Model')
    serial_no = fields.Char('Serial Number', copy=False)
    quantity = fields.Integer('Quantity', default="1")
    color = fields.Char(string='Color')
    laterality = fields.Selection([
        ('lt_only', 'Left Only'),
        ('rt_only', 'Right Only'),
        ('bl_pair', 'Bilateral')], default='bl_pair')
    tc_length = fields.Selection([
        ('none', 'No Top Cover'),
        ('3_4', '3/4'),
        ('to_sulcus', 'To Sulcus'),
        ('heel_to_toe', 'Heel-to-Toe')], default='heel_to_toe')

   
    assign_date = fields.Date('Assigned Date', tracking=True)
    effective_date = fields.Date('Effective Date', default=fields.Date.context_today, required=True, help="Date at which the product became effective. This date will be used to compute the Mean Time Between Failure.")
    cost = fields.Float('Cost')
    note = fields.Html('Note')
    warranty_date = fields.Date('Warranty Expiration Date')
    color = fields.Integer('Color Index')
    scrap_date = fields.Date('Scrap Date')
    sale_order_ids = fields.One2many('sale.order.request', 'product_id')
    sale_order_count = fields.Integer(compute='_compute_sale_order_count', string="Sale Order Count", store=True)
    sale_order_open_count = fields.Integer(compute='_compute_sale_order_count', string="Current Sale Order", store=True)
    period = fields.Integer('Days between each preventive sale order')
    next_action_date = fields.Date(compute='_compute_next_sale_order', string='Date of the next sale order', store=True)

    sale_order_team_id = fields.Many2one('sale.order.team', string='Sale Order Team', check_company=True)
    sale_order_duration = fields.Float(help="Sale Order Duration in hours.")
    
    
    # @api.depends('quantity')
    # def _compute_amount(self):
    #     for record in self:
    #         unit_price = 15
    #         if record.size == 's':
    #             unit_price = 12
    #         elif record.size in ['xl', 'xxl']:
    #             unit_price = 18
    #         if record.quantity > 5:
    #             unit_price = unit_price * 0.9
    #         record.amount = record.quantity * unit_price
    
    @api.depends('quantity')
    def _compute_amount(self):
        for record in self:
            unit_price = 15
            unit_quant = 1
            if record.tc_length == 'none':
                unit_price = 0
            elif record.tc_length == '3_4':
                unit_price = 12
            elif record.tc_length in ['to_sulcus', 'heel_to_toe']:
                unit_price = 18
            if record.laterality == 'lt_only':
                record.quantity = unit_quant
            elif record.laterality == 'rt_only':
                record.quantity = unit_quant
            elif record.laterality == 'bl_pair':
                record.quantity = unit_quant + 1
            record.amount = record.quantity * unit_price

    @api.depends('effective_date', 'period', 'sale_order_ids.request_date', 'sale_order_ids.close_date')
    def _compute_next_sale_order(self):
        date_now = fields.Date.context_today(self)
        products = self.filtered(lambda x: x.period > 0)
        for product in products:
            next_sale_order_todo = self.env['sale.order.request'].search([
                ('product_id', '=', product.id),
                ('sale_order_type', '=', 'normal'),
                ('stage_id.done', '!=', True),
                ('close_date', '=', False)], order="request_date asc", limit=1)
            last_sale_order_done = self.env['sale.order.request'].search([
                ('product_id', '=', product.id),
                ('sale_order_type', '=', 'normal'),
                ('stage_id.done', '=', True),
                ('close_date', '!=', False)], order="close_date desc", limit=1)
            if next_sale_order_todo and last_sale_order_done:
                next_date = next_sale_order_todo.request_date
                date_gap = next_sale_order_todo.request_date - last_sale_order_done.close_date
                # If the gap between the last_sale_order_done and the next_sale_order_todo one is bigger than 2 times the period and next request is in the future
                # We use 2 times the period to avoid creation too closed request from a manually one created
                if date_gap > timedelta(0) and date_gap > timedelta(days=product.period) * 2 and next_sale_order_todo.request_date > date_now:
                    # If the new date still in the past, we set it for today
                    if last_sale_order_done.close_date + timedelta(days=product.period) < date_now:
                        next_date = date_now
                    else:
                        next_date = last_sale_order_done.close_date + timedelta(days=product.period)
            elif next_sale_order_todo:
                next_date = next_sale_order_todo.request_date
                date_gap = next_sale_order_todo.request_date - date_now
                # If next sale order to do is in the future, and in more than 2 times the period, we insert an new request
                # We use 2 times the period to avoid creation too closed request from a manually one created
                if date_gap > timedelta(0) and date_gap > timedelta(days=product.period) * 2:
                    next_date = date_now + timedelta(days=product.period)
            elif last_sale_order_done:
                next_date = last_sale_order_done.close_date + timedelta(days=product.period)
                # If when we add the period to the last sale order done and we still in past, we plan it for today
                if next_date < date_now:
                    next_date = date_now
            else:
                next_date = product.effective_date + timedelta(days=product.period)
            product.next_action_date = next_date
        (self - products).next_action_date = False

    @api.depends('sale_order_ids.stage_id.done')
    def _compute_sale_order_count(self):
        for product in self:
            product.sale_order_count = len(product.sale_order_ids)
            product.sale_order_open_count = len(product.sale_order_ids.filtered(lambda x: not x.stage_id.done))

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.sale_order_team_id:
            if self.sale_order_team_id.company_id and not self.sale_order_team_id.company_id.id == self.company_id.id:
                self.sale_order_team_id = False

    @api.onchange('category_id')
    def _onchange_category_id(self):
        self.tech_user_id = self.category_id.tech_user_id

    _sql_constraints = [
        ('serial_no', 'unique(serial_no)', "Another asset already exists with this serial number!"),
    ]

    @api.model
    def create(self, vals):
        product = super(SaleOrderProduct, self).create(vals)
        if product.owner_user_id:
            product.message_subscribe(partner_ids=[product.owner_user_id.partner_id.id])
        return product

    def write(self, vals):
        if vals.get('owner_user_id'):
            self.message_subscribe(partner_ids=self.env['res.users'].browse(vals['owner_user_id']).partner_id.ids)
        return super(SaleOrderProduct, self).write(vals)

    @api.model
    def _read_group_category_ids(self, categories, domain, order):
        """ Read group customization in order to display all the categories in
            the kanban view, even if they are empty.
        """
        category_ids = categories._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return categories.browse(category_ids)

    def _prepare_sale_order_request_vals(self, date):
        self.ensure_one()
        return {
            'name': _('Standard Sale Order - %s', self.name),
            'request_date': date,
            'schedule_date': date,
            'category_id': self.category_id.id,
            'product_id': self.id,
            'sale_order_type': 'normal',
            'owner_user_id': self.owner_user_id.id,
            'user_id': self.tech_user_id.id,
            'sale_order_team_id': self.sale_order_team_id.id,
            'duration': self.sale_order_duration,
            'company_id': self.company_id.id or self.env.company.id
        }

    def _create_new_request(self, date):
        self.ensure_one()
        vals = self._prepare_sale_order_request_vals(date)
        sale_order_requests = self.env['sale.order.request'].create(vals)
        return sale_order_requests

    @api.model
    def _cron_generate_requests(self):
        """
            Generates sale order request on the next_action_date or today if none exists
        """
        for product in self.search([('period', '>', 0)]):
            next_requests = self.env['sale.order.request'].search([('stage_id.done', '=', False),
                                                    ('product_id', '=', product.id),
                                                    ('sale_order_type', '=', 'normal'),
                                                    ('request_date', '=', product.next_action_date)])
            if not next_requests:
                product._create_new_request(product.next_action_date)


