import logging
import json
import base64
from io import BytesIO
import hashlib
from urllib.parse import quote_plus
from datetime import datetime
from datetime import date, timedelta
# from odoo.tools import formatLang, float_compare
from odoo.tools import (
    float_compare, 
    formatLang,
    )
from odoo.fields import Field
from odoo import _, api, fields, models
from odoo.models import NewId
from odoo.exceptions import UserError, ValidationError
from ...cpq.helpers.summary_helper import (
    render_summary_html, 
    compute_cpq_price_breakdown, 
    generate_cpq_order_qr_payload,
    flatten_grouped_selection,
    canonicalize_cpq_config,
    parse_cpq_json,
    env_with_context,
    ensure_env,
    )

try:
    import qrcode
except ImportError:
    qrcode = None

_logger = logging.getLogger(__name__)

class CPQMrpComponentUtils(models.AbstractModel):
    _name = 'cpq.mrp.component.utils'
    _description = 'CPQ → MRP Component Resolver'
    
    @api.model
    def get_components_from_cpq_config(self, cpq_config_json):
        component_lines = []
        try:
            cfg = json.loads(cpq_config_json) if isinstance(cpq_config_json, str) else (cpq_config_json or {})
        except Exception:
            return []

        # 1) flatten bucketed selected → set of CPQ value ids (strings)
        sel = cfg.get("selected") or {}
        if {"left","right","shared"} & set(sel.keys()):
            ids = set()
            for side in ("left","right","shared"):
                for k in (sel.get(side) or {}):
                    if str(k).isdigit():
                        ids.add(str(k))
        else:
            ids = {k for k in sel.keys() if str(k).isdigit()}

        # 2) turn each CPQ value → component product via linked_product_id
        CPQVal = self.env["cpq.attribute.value"].sudo()
        for key in ids:
            cpq_val = CPQVal.browse(int(key)).exists()
            if not cpq_val or not cpq_val.linked_product_id:
                continue
            prod = cpq_val.linked_product_id
            component_lines.append((0, 0, {
                "product_id": prod.id,
                "product_uom_id": prod.uom_id.id,
                "product_qty": 1.0,  # adjust if you need per-side/per-length quantities
                "name": cpq_val.name or prod.display_name,
            }))
        return component_lines

class SaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Sales Orders"
    
    partner_id = fields.Many2one(
        "res.partner",
        domain="[('is_account', '=', True)]",
        string="Account",
        required=True,
    )

    affiliate_id = fields.Many2one(
        "res.partner",
        domain="[('is_affiliate', '=', True)]",
        string="Affiliate",
    )

    contact_id = fields.Many2one(
        "res.partner",
        domain="[('is_contact', '=', True)]",
        string="Contact",
    )

    patient_id = fields.Many2one(
        "res.partner",
        domain="[('is_patient', '=', True)]",
        string="Patient",
    )
    
    ship_to_patient = fields.Boolean(string="Ship to Patient")

    rush_3day = fields.Boolean(string="3‑Day Rush", help="Ship to customer within 3 days.")
    
    rush_due_date = fields.Datetime(string="Due Date", readonly=True, copy=False)

    # onChange methods
    @api.onchange("ship_to_patient", "patient_id", "partner_id", "affiliate_id")
    def _onchange_ship_to_patient(self):
        for order in self:
            # Ship directly to the patient
            if order.ship_to_patient and order.patient_id:
                order.partner_shipping_id = order.patient_id
                continue

            # Fallback: affiliate’s delivery address, else partner’s delivery, else the base record
            ship_base = order.affiliate_id or order.partner_id
            if not ship_base:
                order.partner_shipping_id = False
                continue

            # Prefer a dedicated delivery child
            delivery = ship_base.child_ids.filtered(lambda p: p.type == "delivery")[:1]
            order.partner_shipping_id = delivery or ship_base
   
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.affiliate_id = False
        self.contact_id = False
        self.patient_id = False
        self.ship_to_patient = False

    @api.onchange('affiliate_id')
    def _onchange_affiliate_id(self):
        self.contact_id = False
        self.patient_id = False
        self.ship_to_patient = False

    @api.onchange('contact_id')
    def _onchange_contact_id(self):
        self.patient_id = False
        self.ship_to_patient = False

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if not self.patient_id:
            self.ship_to_patient = False

    cpq_order_qr_image = fields.Binary(
        string='',
        compute='_compute_cpq_order_qr',
        store=True,
        readonly=True,
    )

    quotation_seq_used = fields.Boolean(
        string="Quotation Sequence Used", default=False, copy=False, readonly=True
    )
    
    @api.depends("order_line", "order_line.cpq_config_hash", "order_line.product_template_id")
    def _compute_cpq_order_qr(self):
        for order in self:
            if not qrcode:
                order.cpq_order_qr_image = False
                continue

            uri = generate_cpq_order_qr_payload(order)
            if not uri:
                order.cpq_order_qr_image = False
                continue

            qr = qrcode.QRCode(
                version=2,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=3,
                border=4,
            )
            qr.add_data(uri)
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            order.cpq_order_qr_image = base64.b64encode(temp.getvalue())

    def action_regenerate_order_qr(self):
        for order in self:
            order._compute_cpq_order_qr()
        return self.env["ir.actions.client"].sudo().with_context(self.env.context).create({
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Order QR",
                "message": "Regenerated QR for order.",
                "type": "success",
            },
        })

    # sale order revision
    # === Revision core ===
    revision_number = fields.Integer(string="Revision", copy=False, default=0)
    unrevisioned_name = fields.Char(string="Original Reference", copy=True, readonly=True)
    active = fields.Boolean(default=True)

    # links to other revisions of *sale.order*
    current_revision_id = fields.Many2one(
        'sale.order', string="Current revision", readonly=True, copy=True
    )
    old_revision_ids = fields.One2many(
        'sale.order', 'current_revision_id',
        string="Old revisions",
        readonly=True,
        context={'active_test': False},
        domain=["|", ("active", "=", False), ("active", "=", True)],
    )

    has_old_revisions = fields.Boolean(compute="_compute_has_old_revisions")
    revision_count = fields.Integer(
        compute="_compute_revision_count", string="Previous versions count"
    )

    _sql_constraints = [
        # keep uniqueness per company to avoid cross‑company collisions
        (
            "revision_unique",
            "unique(unrevisioned_name, revision_number, company_id)",
            "Order Reference and revision must be unique per Company.",
        )
    ]

    @api.depends("old_revision_ids")
    def _compute_has_old_revisions(self):
        for rec in self:
            rec.has_old_revisions = bool(rec.with_context(active_test=False).old_revision_ids)

    @api.depends("old_revision_ids")
    def _compute_revision_count(self):
        # same read_group logic, but scoped to sale.order
        res = self.with_context(active_test=False).read_group(
            domain=[("current_revision_id", "in", self.ids)],
            fields=["current_revision_id"],
            groupby=["current_revision_id"],
        )
        counts = {x["current_revision_id"][0]: x["current_revision_id_count"] for x in res}
        for rec in self:
            rec.revision_count = counts.get(rec.id, 0)

    # --- Helpers you had in the mixin, adapted for SaleOrder ---
    def _get_new_rev_data(self, new_rev_number):
        self.ensure_one()
        # build a new external name like "SO0001-01"
        return {
            "revision_number": new_rev_number,
            "unrevisioned_name": self.unrevisioned_name,
            "name": "%s-%02d" % (self.unrevisioned_name, new_rev_number),
            "old_revision_ids": [(4, self.id, False)],
        }

    def _prepare_revision_data(self, new_revision):
        """Called on the *old* record to retire it when a new revision is made."""
        # keep your custom tweak: cancel old revision automatically
        return {"active": False, "current_revision_id": new_revision.id, "state": "cancel"}
    
    def action_view_revisions(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id("sale.action_orders")
        result["domain"] = ["|", ("active", "=", False), ("active", "=", True)]
        result["context"] = {
            "active_test": 0,
            "search_default_current_revision_id": self.id,
            "default_current_revision_id": self.id,
        }
        return result

    def copy_revision_with_context(self):
        """Create a new revision (a new sale.order row) and retire the current one."""
        self.ensure_one()

        # defaults for copy() – keep your quotation logic elsewhere unchanged
        default_data = self.default_get([])
        new_rev_number = self.revision_number + 1
        vals = self._get_new_rev_data(new_rev_number)
        default_data.update(vals)

        # make the copy
        new_revision = self.copy(default_data)

        # wire up links both ways
        self.old_revision_ids.write({"current_revision_id": new_revision.id})
        self.write(self._prepare_revision_data(new_revision))

        # optionally post chatter messages if mail.thread is enabled on sale.order
        if hasattr(self, "message_post"):
            msg = _("New revision created: %s") % new_revision.name
            new_revision.message_post(body=msg)
            self.message_post(body=msg)

        return new_revision

    def create_revision(self):
        """Multi create + return an action on the new records (as your original did)."""
        revision_ids = []
        for rec in self:
            copied_rec = rec.copy_revision_with_context()
            revision_ids.append(copied_rec.id)
        return {
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "name": _("New Revisions"),
            "res_model": self._name,
            "domain": [("id", "in", revision_ids)],
            "target": "current",
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Determine company
            company = self.env['res.company'].browse(vals.get('company_id')) if vals.get('company_id') else self.env.company

            # Always assign a real name on create (never leave '/')
            if not vals.get('name') or vals['name'] in ('/', False):
                if company.keep_name_so:
                    # give final SO number at quotation stage
                    vals['name'] = self.env['sale.order'].get_sale_order_seq(company) or '/'
                    # OR call ir.sequence directly (also fine)
                    # # vals['name'] = self.env['ir.sequence'].with_company(company).next_by_code('sale.order') or '/'
                    vals['quotation_seq_used'] = False
                else:
                    # use quotation sequence; will be swapped on confirm
                    vals['name'] = self.with_company(company).get_quotation_seq() or '/'
                    vals['quotation_seq_used'] = True

            # Mirror base name into unrevisioned_name if missing or placeholder
            if not vals.get('unrevisioned_name') or vals['unrevisioned_name'] in ('/', False):
                vals['unrevisioned_name'] = vals['name']

            vals.setdefault('revision_number', 0)

        return super().create(vals_list)


    # @api.model
    # def is_using_quotation_number(self, vals):
    #     company = False
    #     if vals.get("company_id"):
    #         company = self.env["res.company"].browse(vals.get("company_id"))
    #     else:
    #         company = self.env.company
    #     return not company.keep_name_so

    def copy(self, default=None):
        """Keep your origin behavior AND preserve unrevisioned_name when duplicating."""
        self.ensure_one()
        default = dict(default or {})
        # your existing origin handling
        default["origin"] = f"{self.origin}, {self.name}" if self.origin else self.name
        # if you duplicate *not* as a revision, keep base reference consistent
        if "unrevisioned_name" not in default:
            # use current 'name' as original reference when first duplicated
            default["unrevisioned_name"] = self.unrevisioned_name or self.name
        return super().copy(default)

    def unlink(self):
        for order in self:
            # Only allow delete if the order is a cancelled quotation or cancelled draft
            if order.state != "cancel":
                raise UserError(_("Only cancelled quotations can be deleted. Please archive instead."))
        return super().unlink()

    @api.model
    def get_quotation_seq(self):
        return self.env["ir.sequence"].next_by_code("sale.quotation")

    @api.model
    def get_sale_order_seq(self, company=None):
        """Company-aware SO sequence getter usable from model or record."""
        company = company or self.env.company
        return self.env["ir.sequence"].with_company(company).next_by_code("sale.order")
    
    @api.onchange("rush_3day", "date_order")
    def _onchange_rush_3day(self):
        for order in self:
            if order.rush_3day:
                base = order.date_order or fields.Datetime.now()
                # timezone-aware, uses server utils
                due = fields.Datetime.add(base, days=3)
                order.rush_due_date = due
                order.commitment_date = due
            else:
                order.rush_due_date = False
                # leave commitment_date as-is (as you intended)

    def action_confirm(self):
        # --- PRE-CONFIRM: handle quotation sequence renaming ---
        for order in self:
            # Only when we used the quotation sequence and are still a quotation,
            # and the company doesn't keep the original name on SO confirmation.
            if (
                order.quotation_seq_used
                and order.state in ("draft", "sent")
                and not order.company_id.keep_name_so
            ):
                old_name = order.name
                quo = f"{order.origin}, {old_name}" if order.origin else old_name
                new_seq = order.get_sale_order_seq()

                write_vals = {
                    "origin": quo,
                    "name": new_seq,
                    "quotation_seq_used": False,
                }
                # Restore the base (unrevisioned) name if it was cleared.
                if not order.unrevisioned_name or order.unrevisioned_name == "/":
                    write_vals["unrevisioned_name"] = quo or new_seq

                order.write(write_vals)

        # --- CONFIRM ---
        res = super().action_confirm()

        # --- POST-CONFIRM: schedule activity for 3‑day rush orders ---
        rush_orders = self.filtered(lambda so: getattr(so, "rush_3day", False))
        if rush_orders:
            # Try to get a generic TODO activity; if not found, skip quietly.
            activity_type = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
            if activity_type:
                today = fields.Date.today()
                for so in rush_orders:
                    so.activity_schedule(
                        activity_type_id=activity_type.id,
                        summary=_("RUSH: Ship within 3 days"),
                        date_deadline=getattr(so, "rush_due_date", False) or today,
                        user_id=so.user_id.id or self.env.user.id,
                    )

        return res

    def _create_cpq_mrp_productions(self):
        Production = self.env['mrp.production'].sudo()
        CPQUtils   = self.env['cpq.mrp.component.utils'].sudo()

        for order in self:
            for line in order.order_line:
                if not getattr(line.product_template_id, "cpq_ok", False):
                    continue
                if not line.cpq_configuration_summary:
                    raise UserError(_("Missing CPQ configuration summary for line: %s") % line.name)
                # Find the dynamic BoM for this template
                dyn_bom = line.product_template_id.cpq_dynamic_bom_ids[:1]
                components = CPQUtils.get_components_from_cpq_config(line.cpq_configuration_json)

                mo = Production.create({
                    "origin":            order.name,
                    "product_id":        line.product_id.id,
                    "product_uom_id":    line.product_uom.id,
                    "product_qty":       line.product_uom_qty,
                    "sale_line_id":      line.id,  # useful, but we’ll also set it on finished moves after confirm
                    "company_id":        order.company_id.id,
                    "cpq_configuration_json":     line.cpq_configuration_json,
                    "cpq_configuration_summary":  line.cpq_configuration_summary,
                    "cpq_config_hash":            line.cpq_config_hash,
                    "move_raw_ids":      components,
                    "picking_type_id": dyn_bom.picking_type_id.id if dyn_bom else False,

                })

                # ensure finished moves exist
                mo.action_confirm()
                
                # Create work orders from dynamic operations
                if dyn_bom and dyn_bom.operation_ids:
                    WO = self.env['mrp.workorder'].sudo()
                    seq = 1
                    for op in dyn_bom.operation_ids:
                        WO.create({
                            "name": op.name,
                            "production_id": mo.id,
                            "workcenter_id": op.workcenter_id.id,
                            "sequence": op.sequence or seq,
                            "duration_expected": op.duration_expected or 0.0,
                        })
                        seq += 1

                # link finished moves back to SOL and copy snapshot (so MO computes will pick it up)
                mo.move_finished_ids.write({
                    "sale_line_id":               line.id,
                    "cpq_configuration_json":     line.cpq_configuration_json or False,
                    "cpq_configuration_summary":  line.cpq_configuration_summary or False,
                    "cpq_config_hash":            line.cpq_config_hash or False,
                })

                line.write({"cpq_product_created": True})


    picking_note = fields.Html(
        string="Picking Internal Note",
        compute="_compute_picking_notes",
        store=True,
        readonly=False,
    )
    
    picking_customer_note = fields.Text(
        string="Picking Customer Comments",
        compute="_compute_picking_notes",
        store=True,
        readonly=False,
    )

    @api.depends("partner_id", "partner_shipping_id")
    def _compute_picking_notes(self):
        for order in self:
            if order.state not in {"sale", "cancel"}:
                order.picking_note = (
                    order.partner_shipping_id.picking_note
                    or order.partner_id.picking_note
                )
                order.picking_customer_note = (
                    order.partner_shipping_id.picking_customer_note
                    or order.partner_id.picking_customer_note
                )

    display_discount_with_tax = fields.Boolean(
        name="Show the Discount with TAX",
        help="Check this field to show the Discount with TAX",
        related="company_id.display_discount_with_tax",
    )

    discount_total = fields.Monetary(
        compute="_compute_discount_total",
        name="Discount total",
        currency_field="currency_id",
        store=True,
    )

    discount_subtotal = fields.Monetary(
        compute="_compute_discount_total",
        name="Discount Subtotal",
        currency_field="currency_id",
        store=True,
    )

    price_subtotal_no_discount = fields.Monetary(
        compute="_compute_discount_total",
        name="Subtotal Without Discount",
        currency_field="currency_id",
        store=True,
    )

    price_total_no_discount = fields.Monetary(
        compute="_compute_discount_total",
        name="Total Without Discount",
        currency_field="currency_id",
        store=True,
    )

    @api.model
    def _get_compute_discount_total_depends(self):
        return [
            "order_line.discount_total",
            "order_line.discount_subtotal",
            "order_line.price_subtotal_no_discount",
            "order_line.price_total_no_discount",
        ]

    @api.depends(lambda self: self._get_compute_discount_total_depends())
    def _compute_discount_total(self):
        for order in self:
            discount_total = sum(order.order_line.mapped("discount_total"))
            discount_subtotal = sum(order.order_line.mapped("discount_subtotal"))
            price_subtotal_no_discount = sum(
                order.order_line.mapped("price_subtotal_no_discount")
            )
            price_total_no_discount = sum(
                order.order_line.mapped("price_total_no_discount")
            )
            order.update(
                {
                    "discount_total": discount_total,
                    "discount_subtotal": discount_subtotal,
                    "price_subtotal_no_discount": price_subtotal_no_discount,
                    "price_total_no_discount": price_total_no_discount,
                }
            )

    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total')
    def _compute_amounts(self):
        for order in self:
            order.amount_untaxed = sum(line.price_subtotal for line in order.order_line)
            order.amount_tax = sum(line.price_tax for line in order.order_line)
            order.amount_total = order.amount_untaxed + order.amount_tax
            _logger.info(
                "[_compute_amounts] Order %s: untaxed=%.2f tax=%.2f total=%.2f lines=%s",
                order.id,
                order.amount_untaxed,
                order.amount_tax,
                order.amount_total,
                [(l.id, l.price_subtotal, l.price_tax, l.price_total) for l in order.order_line]
            )

    invoiced_amount = fields.Monetary(
        compute="_compute_invoice_amount",
        store=True,
        help="Order amount already invoiced.",
    )

    uninvoiced_amount = fields.Monetary(
        compute="_compute_invoice_amount",
        store=True,
        help="Order amount to be invoiced",
    )

    @api.depends(
        "state",
        "invoice_ids",
        "invoice_ids.amount_total_in_currency_signed",
        "amount_total",
        "invoice_ids.state",
    )
    def _compute_invoice_amount(self):
        for rec in self:
            if rec.state != "cancel" and rec.invoice_ids:
                rec.invoiced_amount = 0.0
                for invoice in rec.invoice_ids:
                    if invoice.state != "cancel":
                        if (
                            invoice.currency_id != rec.currency_id
                            and rec.currency_id != invoice.company_currency_id
                        ):
                            rec.invoiced_amount += invoice.currency_id._convert(
                                invoice.amount_total_signed,
                                rec.currency_id,
                                invoice.company_id,
                                invoice.invoice_date or fields.Date.today(),
                            )
                        else:
                            rec.invoiced_amount += invoice.amount_total_signed
                # Uninvoiced amount could not be equal to total - invoiced amount.
                # For example if the amount invoiced does not match with the price unit.
                rec.uninvoiced_amount = max(
                    0,
                    sum(
                        (line.product_uom_qty - line.qty_invoiced)
                        * (line.price_total / line.product_uom_qty)
                        for line in rec.order_line.filtered(
                            lambda sl: sl.product_uom_qty > 0
                        )
                    ),
                )
            else:
                rec.invoiced_amount = 0.0
                if rec.state in ["draft", "sent", "cancel"]:
                    rec.uninvoiced_amount = 0.0
                else:
                    rec.uninvoiced_amount = rec.amount_total

    @api.depends_context('lang')
    @api.depends(
        'order_line.tax_id',
        'order_line.price_unit',
        'amount_total',
        'amount_untaxed',
        'currency_id',
        'state',
        'invoice_ids',
        'invoice_ids.amount_total_in_currency_signed',
        'invoice_ids.state',
    )
    def _compute_tax_totals(self):
        super()._compute_tax_totals()
        for order in self:
            lang_env = order.with_context(lang=order.partner_id.lang).env
            tax_totals = order.tax_totals
            if isinstance(tax_totals, str):
                try:
                    tax_totals = json.loads(tax_totals)
                except Exception:
                    tax_totals = {}
            elif tax_totals is None:
                tax_totals = {}

            tax_totals.update({
                # === Main SO Amounts ===
                "amount_total": order.amount_total,
                "amount_untaxed": order.amount_untaxed,
                "amount_tax": order.amount_tax,
                "formatted_amount_total": formatLang(lang_env, order.amount_total, currency_obj=order.currency_id),
                "formatted_amount_untaxed": formatLang(lang_env, order.amount_untaxed, currency_obj=order.currency_id),
                "formatted_amount_tax": formatLang(lang_env, order.amount_tax, currency_obj=order.currency_id),

                # === CPQ/Custom: Invoicing Fields ===
                "invoiced_amount": order.invoiced_amount,
                "uninvoiced_amount": order.uninvoiced_amount,
                "formatted_invoiced_amount": formatLang(lang_env, order.invoiced_amount, currency_obj=order.currency_id),
                "formatted_uninvoiced_amount": formatLang(lang_env, order.uninvoiced_amount, currency_obj=order.currency_id),

                # === CPQ/Custom: Discount and No-Discount Totals (optional) ===
                "discount_total": getattr(order, "discount_total", 0.0),
                "discount_subtotal": getattr(order, "discount_subtotal", 0.0),
                "price_subtotal_no_discount": getattr(order, "price_subtotal_no_discount", 0.0),
                "price_total_no_discount": getattr(order, "price_total_no_discount", 0.0),
                "formatted_discount_total": formatLang(lang_env, getattr(order, "discount_total", 0.0), currency_obj=order.currency_id),
                "formatted_price_total_no_discount": formatLang(lang_env, getattr(order, "price_total_no_discount", 0.0), currency_obj=order.currency_id),
            })

            order.tax_totals = tax_totals
   
   
class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "mail.thread"]
    _name = "sale.order.line"

    product_template_id_cpq_ok = fields.Boolean(related="product_template_id.cpq_ok")

    linked_option_ids = fields.Many2many(
        "product.options",
        string="Linked Options",
        help="Linked options for Custom products.",
        domain="[('is_leaf', '=', True)]",
        )

    cpq_laterality = fields.Selection(
        selection=[
            ('left', 'Left Only'),
            ('right', 'Right Only'),
            ('bilateral', 'Bilateral'),
        ],
        string="Laterality",
        compute='_compute_cpq_laterality',
        store=True
    )

    cpq_configuration_summary = fields.Html(
        string="Custom Summary",
        compute="_compute_cpq_configuration_summary",
        store=True,
        sanitize=False,    
    )
    
    cpq_configuration_json = fields.Json(
        string="Custom Configuration",
        help="Stores selected laterality and option data for Custom products."
    )

    cpq_quantity_to_make = fields.Integer(
        string="Pairs to Make",
        compute="_compute_cpq_quantity_to_make",
        store=True
    )

    cpq_product_created = fields.Boolean(
        string="Custom Product Created",
        compute="_compute_cpq_product_created",
        store=True
    )

    cpq_total_price = fields.Monetary(
        string="Custom Total Price",
        compute="_compute_cpq_total_price",
        currency_field="currency_id",
        store=True
    )

    cpq_config_hash = fields.Char(
        string="CPQ Config Hash",
        compute="_compute_cpq_config_hash",
        store=True,
        help="Hash of the CPQ configuration, used for QR code payloads."
    )

    cpq_summary_printable = fields.Html("Printable Custom Summary")

    cpq_unconfigured = fields.Boolean(
        string="Missing Custom Config",
        compute="_compute_cpq_unconfigured",
        store=False,
    )

    price_unit = fields.Float(
        compute="_compute_price_unit",
        store=True,
        readonly=False, 
    )

    price_unit_display = fields.Char(
        string="Display Price",
        compute="_compute_price_unit_display",
        store=False,
    )

    cpq_qr_code_image = fields.Binary(
        string='QR Code',
        compute='_compute_cpq_qr_code_image',
        store=True,
        readonly=True,
    )

    computed_amount = fields.Float(
        string="Amount", 
        compute="_compute_amount", 
        store=True, 
        precompute=True
    )

    discount_total = fields.Monetary(
        compute="_compute_amount",
        store=True,
        precompute=True,
    )

    discount_subtotal = fields.Monetary(
        compute="_compute_amount",
        store=True,
        precompute=True,
    )

    price_subtotal_no_discount = fields.Monetary(
        compute="_compute_amount",
        string="Subtotal Without Discount",
        store=True,
        precompute=True,
    )

    price_total_no_discount = fields.Monetary(
        compute="_compute_amount",
        string="Total Without Discount",
        store=True,
        precompute=True,
    )

    def _parse_config(self):
        cfg = parse_cpq_json(self.cpq_configuration_json) or {}
        cfg = canonicalize_cpq_config(cfg) 
        # guarantee both shapes exist
        grouped = cfg.get("grouped") or {"left":{}, "right":{}, "shared":{}}
        selected = cfg.get("selected") or {}
        if not selected or all(not (selected.get(s) or {}) for s in ("left","right","shared")):
            cfg["selected"] = flatten_grouped_selection(grouped)
        return cfg

    def toggle_debug_cpq_json(self):
        # Placeholder logic: in real use, you'd probably use context or a transient field to show/hide.
        raise UserError("This would show/hide Custom JSON — placeholder.")
    
    @api.onchange("cpq_configuration_json", "product_id")
    def _onchange_cpq_configuration(self):
        for line in self:
            if not line.product_id.cpq_ok:
                line.cpq_configuration_json = False
                continue
            if not line.cpq_configuration_json:
                continue
            try:
                config = canonicalize_cpq_config(line.cpq_configuration_json)
                line.name = config.get("name") or line.name
                line.product_uom_qty = config.get("quantity_to_make", line.product_uom_qty)
                # summary_html = render_summary_html(self.env, line, config, mode="chatter")
                summary_html = render_summary_html(self.env, line, config)

                line.cpq_configuration_summary = summary_html
                line.message_post(
                    body=f"""
                        <b>Custom Configuration Applied:</b><br/>
                        {summary_html}
                    """,
                    subtype_xmlid="mail.mt_note",
                )
            except Exception as e:
                _logger.warning(f"Failed to parse Custom config JSON: {e}")

    @api.onchange("product_id")
    def _onchange_product_id_warning(self):
        res = super()._onchange_product_id_warning()

        for line in self:
            if not line.product_id:
                continue  # 🟡 No product selected → nothing to do

            if line.product_id.cpq_ok:
                # Custom Product → skip price/UoM, configurator will handle this later
                partner_lang = line.order_id.partner_id.lang if line.order_id.partner_id else self.env.user.lang
                if line.product_id.cpq_description_sale_tmpl:
                    product = line.product_id.with_context(lang=partner_lang)
                    name = product.product_tmpl_id._cpq_render_inline_template(
                        product.cpq_description_sale_tmpl,
                        extras={"record": product, "tmpl": line},
                    )
                    if name:
                        line.name = name
                # 🛑 Do NOT set price_unit or product_uom here — handled by CPQ.
            else:
                # 🟢 Non-Custom Product → force apply Odoo pricing & UoM behavior:
                product = line.product_id.with_company(line.company_id)
                partner = line.order_id.partner_id
                pricelist = line.order_id.pricelist_id

                # 🟢 Use Odoo's native price logic:
                product_context = dict(self.env.context, partner_id=partner.id, quantity=1, uom=product.uom_id.id)
                price = pricelist._get_product_price(product.with_context(product_context), 1.0, partner)

                line.price_unit = price or product.lst_price or 0.0
                line.product_uom = product.uom_id
                line.name = product.get_product_multiline_description_sale() or product.name
                line.cpq_configuration_json = False  # Clear Custom config if it was hanging around.

        return res

    @api.onchange("cpq_configuration_json", "product_id")
    def _onchange_cpq_pricing(self):
        for line in self:
            if not line.product_id.cpq_ok:
                continue
            cfg = line._parse_config()
            bd = compute_cpq_price_breakdown(self.env, line, cfg) or {}
            qty = bd.get("quantity") or 1
            total = bd.get("final_price") or bd.get("total") or bd.get("subtotal") or 0.0
            line.price_unit = (total / qty) if qty else 0.0
            line.product_uom_qty = qty

    # crud methods
    def _canonicalize_json_str(self, raw):
        """Return canonicalized JSON string or False."""
        if raw in (False, None, "", {}):
            return False
        try:
            cfg = parse_cpq_json(raw)
            cfg = canonicalize_cpq_config(cfg)
            return json.dumps(cfg)
        except Exception:
            return False

    def _ensure_cpq_product_in_vals(self, vals):
        """If the template is CPQ and product_id is missing, inject the shell product."""
        if vals.get("display_type"):
            return vals
        tmpl_id = vals.get("product_template_id")
        if not tmpl_id or vals.get("product_id"):
            return vals
        tmpl = self.env["product.template"].browse(tmpl_id)
        if tmpl and tmpl.cpq_ok:
            product = tmpl._ensure_configurator_product()
            vals["product_id"] = product.id
        return vals

    def _maybe_generate_qr(self, line, changed_fields):
        if line.display_type or not line.product_template_id.cpq_ok:
            return
        if {"cpq_configuration_json", "product_template_id"} & set(changed_fields):
            try:
                line.cpq_qr_code_image = line.generate_configuration_qr(line.id)
            except Exception as e:
                _logger.warning("Failed to (re)generate QR for line %s: %s", line.id, e)

    def _maybe_update_summary(self, line, raw_json_in_write=None):
        """Use explicit incoming JSON in write when provided; otherwise use the stored field."""
        raw = raw_json_in_write if raw_json_in_write is not None else line.cpq_configuration_json
        if not raw:
            line.cpq_configuration_summary = ""
            return
        self._compute_and_assign_summary(line, raw)

    def _cpq_normalize_config(self, raw):
        """
        Parse → canonicalize once → return dict and JSON string.
        """
        try:
            cfg = parse_cpq_json(raw) if isinstance(raw, (str, bytes)) else (raw or {})
            # cfg = canonicalize_cpq_config(cfg or {})
            cfg = canonicalize_cpq_config(cfg) 
            return cfg, json.dumps(cfg)
        except Exception as e:
            _logger.warning("[CPQ] Failed to normalize config: %s", e)
            return {}, json.dumps({})

    def _apply_cpq_price(self):
        # hard guard: if a caller explicitly said “don’t bounce writes”, bail
        if self.env.context.get("cpq_skip_apply_price"):
            return
        for line in self:
            if not getattr(line.product_template_id, "cpq_ok", False):
                continue
            cfg = line._parse_config()
            bd = compute_cpq_price_breakdown(self.env, line, cfg) or {}
            qty = bd.get("quantity") or 1.0
            final = bd.get("final_price") or bd.get("total") or bd.get("subtotal") or 0.0
            unit = (final / qty) if qty else 0.0

            # skip no-op writes using currency precision
            if float_compare(line.price_unit or 0.0, unit, precision_rounding=line.currency_id.rounding) == 0:
                continue

            # IMPORTANT: prevent write() → _apply_cpq_price() loop
            line.with_context(skip_pricelist=True, cpq_skip_apply_price=True).write({"price_unit": unit})
            _logger.info("[CPQ] Applied unit price %.2f on SOL %s (final %.2f / qty %.2f)", unit, line.id, final, qty)

    # Overrides
    @api.model_create_multi
    def create(self, vals_list):
        # Normalize config in vals BEFORE create so computed fields see canonical structure
        for vals in vals_list:
            if "cpq_configuration_json" in vals:
                raw = vals.get("cpq_configuration_json")
                cfg, cfg_json = self._cpq_normalize_config(raw)
                vals["cpq_configuration_json"] = cfg_json
                _logger.info("[CPQ][create] canonicalized config to be saved: %s", cfg_json)

        lines = super().create(vals_list)

        # Post-create enrichments
        for line, vals in zip(lines, vals_list):
            # Fallback product for CPQ templates
            if not vals.get("product_id") and not vals.get("display_type"):
                tmpl_id = vals.get("product_template_id")
                if tmpl_id:
                    tmpl = self.env["product.template"].browse(tmpl_id)
                    if tmpl and getattr(tmpl, "cpq_ok", False):
                        product = tmpl._ensure_configurator_product()
                        line.product_id = product.id
                        _logger.info("[CPQ] Fallback product_id=%s injected for template_id=%s", product.id, tmpl.id)

            # QR & summary (use the canonicalized config we just stored)
            if not line.display_type and getattr(line.product_template_id, "cpq_ok", False):
                try:
                    line.cpq_qr_code_image = line.generate_configuration_qr(line.id)
                except Exception as e:
                    _logger.warning("[CPQ] QR generation failed for line %s: %s", line.id, e)

                cfg = line._parse_config()
                try:
                    line.cpq_configuration_summary = render_summary_html(self.env, line, cfg)
                except Exception as e:
                    _logger.warning("[CPQ] Summary render failed for line %s: %s", line.id, e)
                    line.cpq_configuration_summary = ""
            try:
                lines._apply_cpq_price()

                # lines.with_context(cpq_skip_apply_price=True)._apply_cpq_price()
            except Exception as e:
                _logger.warning("[CPQ] Failed to apply CPQ price on create: %s", e)
                
        return lines

    # ---------- Write ----------
    def write(self, vals):
        # normalize JSON first (unchanged)
        if "cpq_configuration_json" in vals:
            raw = vals.get("cpq_configuration_json")
            cfg, cfg_json = self._cpq_normalize_config(raw)
            vals["cpq_configuration_json"] = cfg_json
            _logger.info("[CPQ][write] canonicalized config to be saved: %s", cfg_json)

        result = super().write(vals)

        # ---- Prevent recursion: if we are inside our own price write, bail
        if self.env.context.get("cpq_skip_apply_price"):
            return result

        needs_qr = {"cpq_configuration_json", "product_template_id"} & set(vals.keys())
        has_config = "cpq_configuration_json" in vals

        for line in self:
            if line.display_type or not getattr(line.product_template_id, "cpq_ok", False):
                continue

            if needs_qr:
                try:
                    line.cpq_qr_code_image = line.generate_configuration_qr(line.id)
                except Exception as e:
                    _logger.warning("[CPQ] QR regeneration failed for line %s: %s", line.id, e)

            if has_config:
                cfg = line._parse_config()
                try:
                    line.cpq_configuration_summary = render_summary_html(self.env, line, cfg)
                except Exception as e:
                    _logger.warning("[CPQ] Summary render failed for line %s: %s", line.id, e)
                    line.cpq_configuration_summary = ""

        # ---- Only re-apply price when CPQ-relevant fields changed
        trigger_fields = {"cpq_configuration_json", "product_template_id", "product_id"}
        if trigger_fields & set(vals.keys()):
            try:
                self._apply_cpq_price()
                # self.with_context(cpq_skip_apply_price=True)._apply_cpq_price()
            except Exception as e:
                _logger.warning("[CPQ] Failed to apply CPQ price on write: %s", e)

        return result

    # compute methods
    @api.depends("product_template_id.cpq_ok", "cpq_configuration_json")
    def _compute_cpq_unconfigured(self):
        for line in self:
            line.cpq_unconfigured = bool(line.product_template_id.cpq_ok and not line.cpq_configuration_json)

    @api.depends("cpq_configuration_json") 
    def _compute_cpq_config_hash(self):
        for line in self:
            config = line._parse_config()
            sel = config.get("selected") or {}
            if {"left","right","shared"} <= set(sel.keys()):
                flat = {}
                for side in ("left","right","shared"):
                    for k, v in (sel.get(side) or {}).items():
                        flat[str(k)] = v
                selected = flat
            else:
                selected = sel
                # then build `enriched` from `selected` (flat) as you do now

            # Normalize selected before hashing (remove random metadata)
            # selected = config.get("selected", {})
            enriched = {
                k: {
                    "value": v.get("value", k) if isinstance(v, dict) else v,
                    "note": v.get("note") if isinstance(v, dict) else None,
                    "isPreferred": v.get("isPreferred", False) if isinstance(v, dict) else False,
                    "isPreferredLeft": v.get("isPreferredLeft", False) if isinstance(v, dict) else False,
                    "isPreferredRight": v.get("isPreferredRight", False) if isinstance(v, dict) else False,
                }
                for k, v in selected.items()
            }
            config["selected"] = enriched
            serialized = json.dumps(config, sort_keys=True)
            line.cpq_config_hash = hashlib.md5(serialized.encode("utf-8")).hexdigest()
            # try:
            #     serialized = json.dumps(config, sort_keys=True)
            #     line.cpq_config_hash = hashlib.md5(serialized.encode("utf-8")).hexdigest()
            # except Exception as e:
            #     _logger.warning("Failed to hash configuration for line %s: %s", line.id, e)
            #     line.cpq_config_hash = False

    @api.depends("cpq_configuration_json", "product_template_id.cpq_ok")
    def _compute_price_unit(self):
        for line in self:
            if line.product_template_id.cpq_ok:
                config = line._parse_config()
                breakdown = compute_cpq_price_breakdown(self.env, line, config) or {}
                qty = breakdown.get("quantity") or 1.0
                final = breakdown.get("final_price") or breakdown.get("total") or breakdown.get("subtotal") or 0.0
                line.price_unit = (final / qty) if qty else 0.0
            else:
                super(SaleOrderLine, line)._compute_price_unit()

    @api.depends("price_unit", "cpq_configuration_json", "product_template_id.cpq_ok")
    def _compute_price_unit_display(self):
        for line in self:
            if not line.product_template_id.cpq_ok:
                line.price_unit_display = f"{line.price_unit:.2f}"
                continue

            config = line._parse_config()
            laterality = config.get("laterality")
            qty_to_make = config.get("quantity_to_make", 1)
            base_price = line.product_template_id.list_price or 0

            # Show $100.00 ($50.00 x 2)
            if laterality == "bilateral" and qty_to_make == 1:
                total_base = base_price * 2
                line.price_unit_display = f"${total_base:.2f} (${base_price:.2f} x 2)"
            else:
                total_base = base_price * qty_to_make
                line.price_unit_display = f"${total_base:.2f}"

    @api.depends("cpq_configuration_json", "product_id.cpq_ok")
    def _compute_cpq_name_suffix(self):
        for line in self:
            if not line.product_id.cpq_ok:
                line.cpq_laterality = False
                continue  # Skip non-Custom lines!
            # config = self._parse_config(line.cpq_configuration_json)
            config = line._parse_config()

            if not config:
                line.name = line.product_id.display_name or line.product_id.name
                continue

            selections = config.get("selected", {})
            side = config.get("laterality", "").capitalize()
            summary = ", ".join(str(v) for v in selections.values()) if isinstance(selections, dict) else ""

            if side and summary:
                line.name = f"{line.product_id.name} - {side} ({summary})"
            elif side:
                line.name = f"{line.product_id.name} - {side}"
            else:
                line.name = line.product_id.name if line.product_id else line.product_template_id.name or "Custom Product"

    @api.depends("cpq_configuration_json", "product_id.cpq_ok")
    def _compute_cpq_laterality(self):
        for line in self:
            config = line._parse_config() if line.product_id.cpq_ok else {}
            line.cpq_laterality = config.get("laterality")

    @api.depends("cpq_configuration_json", "product_id.cpq_ok")
    def _compute_cpq_quantity_to_make(self):
        for line in self:
            config = line._parse_config() if line.product_id.cpq_ok else {}
            line.cpq_quantity_to_make = config.get("quantity_to_make", 1)

    def _compute_cpq_product_created(self):
        for line in self:
            line.cpq_product_created = bool(
                line.product_id and line.product_id.default_code and line.product_id.default_code.startswith("CFG-")
            )

    def _compute_and_assign_summary(self, line, raw_json):
        try:
            config = canonicalize_cpq_config(parse_cpq_json(raw_json))
            line.cpq_configuration_summary = render_summary_html(self.env, line, config)
        except Exception as e:
            _logger.warning("Failed to render summary for line %s: %s", line.id, e)
            line.cpq_configuration_summary = ""

    @api.depends("cpq_configuration_json", "product_id.cpq_ok")
    def _compute_cpq_configuration_summary(self):
        for line in self:
            summary_html = ""
            try:
                config = canonicalize_cpq_config(line.cpq_configuration_json)
                summary_html = render_summary_html(self.env, line, config)
            except Exception:
                _logger.exception("Failed to compute CPQ summary for line %s", line.id)
            line.cpq_configuration_summary = summary_html or ""

    @api.depends("cpq_configuration_json", "product_id.cpq_ok")
    def _compute_cpq_total_price(self):
        for line in self:
            config = line._parse_config() if line.product_id.cpq_ok else {}
            breakdown = compute_cpq_price_breakdown(self.env, line, config)
            line.cpq_total_price = breakdown.get("total", 0.0)

    def _calculate_total_extras(self, config):
        selected = config.get('selected', {})
        if not selected:
            return 0

        ptav_ids = [int(k) for k in selected if k.isdigit()]
        ptavs = self.env['product.template.attribute.value'].browse(ptav_ids)

        total_extra = sum(ptav.price_extra for ptav in ptavs)
        _logger.info(f"Total extras calculated: {total_extra}")
        return total_extra

    def _update_discount_display_fields(self):
        for line in self:
            line.price_subtotal_no_discount = 0
            line.price_total_no_discount = 0
            line.discount_total = 0
            if not line.discount:
                line.price_subtotal_no_discount = line.price_subtotal
                line.price_total_no_discount = line.price_total
                continue
            price = line.price_unit
            taxes = line.tax_id.compute_all(
                price,
                line.order_id.currency_id,
                line.product_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id,
            )

            price_subtotal_no_discount = taxes["total_excluded"]
            price_total_no_discount = taxes["total_included"]
            discount_total = price_total_no_discount - line.price_total
            discount_subtotal = price_subtotal_no_discount - line.price_subtotal

            line.update(
                {
                    "discount_total": discount_total,
                    "discount_subtotal": discount_subtotal,
                    "price_subtotal_no_discount": price_subtotal_no_discount,
                    "price_total_no_discount": price_total_no_discount,
                }
            )

    @api.depends("product_uom_qty", "discount", "price_unit", "tax_id", "cpq_configuration_json")
    def _compute_amount(self):
        for line in self:
            if line.product_template_id.cpq_ok:
                config = line._parse_config()
                breakdown = compute_cpq_price_breakdown(self.env, line, config)
                subtotal = breakdown.get("total", 0.0)
                tax = 0.0
                # Calculate tax if needed:
                if line.tax_id:
                    tax_result = line.tax_id.compute_all(
                        subtotal,  # use your computed subtotal!
                        line.order_id.currency_id,
                        quantity=1,  # CPQ lines are typically 1 per config
                        product=line.product_id,
                        partner=line.order_id.partner_shipping_id,
                    )
                    tax = tax_result["total_included"] - tax_result["total_excluded"]
                line.price_subtotal = subtotal
                line.price_tax = tax
                line.price_total = subtotal + tax
                line.computed_amount = subtotal + tax
            else:
                super(SaleOrderLine, line)._compute_amount()

    @api.model
    def _generate_cpq_description(self, config, total_extra):
        parts = [
            f"Laterality: {config.get('laterality', '').capitalize()}",
            f"Quantity: {config.get('quantity_to_make', 1)}",
        ]

        selected = config.get("selected", {})
        if selected:
            parts.append("Selected Options:")
            for _, value in selected.items():
                parts.append(f"• {value}")

        if total_extra:
            parts.append(f"💰 Total Extras: {total_extra:.2f}")

        total_price = config.get('total_price')
        if total_price:
            parts.append(f"📊 Total Price: {total_price:.2f}")

        return "\n".join(parts)

    @api.model
    def _apply_cpq_attributes_to_product(self, config, product):
        selected = config.get('selected', {})
        if not selected:
            return

        ptav_ids = [int(k) for k in selected if k.isdigit()]
        ptav_records = self.env['product.template.attribute.value'].browse(ptav_ids)

        if not ptav_records:
            return

        product.write({
            'product_template_attribute_value_ids': [(6, 0, ptav_records.ids)],
        })

        _logger.info(f"Applied Custom attributes to product {product.display_name}: {ptav_records.mapped('name')}")

    # actions
    def action_create_product_from_configuration(self):
        self.ensure_one()

        config = canonicalize_cpq_config(self.cpq_configuration_json)

        if not config:
            raise UserError("No Custom configuration found or it could not be parsed.")

        _logger.info("[Custom] Creating product from configuration: %s", json.dumps(config, indent=2))

        # Safety check: prevent duplicate Custom product creation
        if self.product_id and self.product_id.default_code and self.product_id.default_code.startswith("CFG-"):
            raise UserError("This line is already linked to a custom Custom product.")

        product_tmpl = self.product_template_id
        if not product_tmpl:
            raise UserError("No product template linked to this order line.")

        today_str = datetime.today().strftime("%Y%m%d")
        customer_initials = ''.join(word[0].upper() for word in (self.order_id.partner_id.name or "").split() if word)
        internal_ref = f"CFG-{today_str}-{self.id}-{customer_initials or 'CUST'}"

        product_name = config.get('name') or f"{product_tmpl.name} Custom"
        total_extra = self._calculate_total_extras(config)
        description_sale = self._generate_cpq_description(config, total_extra)
        image = product_tmpl.image_1920

        new_product = self.env['product.product'].create({
            'product_tmpl_id': product_tmpl.id,
            'default_code': internal_ref,
            'name': product_name,
            'lst_price': total_extra or self.price_unit,
            'description_sale': description_sale,
            'description_purchase': description_sale,
            'image_1920': image,
        })

        _logger.info(f"Created product {new_product.display_name} ({new_product.id}) from Custom config.")

        self._apply_cpq_attributes_to_product(config, new_product)

        self.message_post(body=_(
            f"Product <b>{new_product.display_name}</b> created from Custom configuration."
        ))
        new_product.message_post(body=_(
            f"Created from Custom configuration on Sale Order <b>{self.order_id.name}</b>."
        ))

        self.product_id = new_product.id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'res_id': new_product.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def edit_cpq_configuration(self):
        self.ensure_one()

        # 🛑 Ensure line is saved (no virtual/unsaved IDs)
        if not self.id or isinstance(self.id, NewId):
            raise UserError("Please save the order before editing this configuration.")

        # Validate template
        tmpl = self.product_template_id or self.product_id.product_tmpl_id
        if not tmpl:
            raise UserError("No product template linked to this line.")

        # Validate order context
        if not self.order_id or not self.order_id.id:
            raise UserError("This line is not linked to a valid order.")
        if not self.order_id.currency_id:
            raise UserError("Missing currency on the order.")
        
        cpq_config_json = self.cpq_configuration_json
        cpq_initial_config = json.loads(cpq_config_json) if cpq_config_json else {}
        # Optionally extract these to pass through, if present
        split_by_attr_map = cpq_initial_config.get("splitByAttrMap", {})
        laterality = cpq_initial_config.get("laterality", "bilateral")
        # If you have a method for preloading PTAL, add:
        # ptal_ids = self.product_template_id.get_cpq_ptal_ids() if hasattr(self.product_template_id, 'get_cpq_ptal_ids') else []

        # Compose safe JS context
        return {
            "type": "ir.actions.client",
            "tag": "cpq.ConfigureDialogAction",
            "context": {
                "active_model": "sale.order.line",
                "active_id": self.id,
                "cpq_product_template_id": tmpl.id,
                "cpq_initial_config": cpq_initial_config,
                "splitByAttrMap": split_by_attr_map,
                "laterality": laterality,
                # "ptal_ids": ptal_ids,  # optional, for perf if easy
                "from_sale_order": True,
                "redirect_to_line": True,
                "edit": not isinstance(self.id, NewId),
                "orderId": self.order_id.id,
                "currencyId": self.order_id.currency_id.id,
                "soDate": str(self.order_id.date_order or fields.Date.today()),
                "companyId": self.order_id.company_id.id,
                "quantity": self.product_uom_qty or 1,
                "partner_id": self.order_id.partner_id.id,
            },
        }

    def action_open_create_product_wizard(self):
        self.ensure_one()

        if not self.cpq_configuration_json:
            raise UserError("No Custom configuration found on this line.")

        return {
            'name': _("Confirm Product Creation"),
            'type': 'ir.actions.act_window',
            'res_model': 'create.product.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_line_id': self.id,
                'default_configuration_summary': self.cpq_configuration_summary,
            },
        }

    # qr code methods
    def generate_configuration_qr(self, val_id):
        """Generate QR code for this configuration."""
        if not qrcode or not base64:
            return

        line = self.browse(val_id)
        order_id = line.order_id.id
        line_id = line.id
        template_id = line.product_template_id.id
        config_hash = line.cpq_config_hash

        payload = f"cpq://order/{order_id}/line/{line_id}/template/{template_id}?config={config_hash}"
        # _logger.info("Generated QR payload: %s", payload)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=3,
            border=4,
        )
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        return base64.b64encode(temp.getvalue())

    @api.depends("cpq_configuration_json", "cpq_config_hash")
    def _compute_cpq_qr_code_image(self):
        for line in self:
            line.cpq_qr_code_image = line.generate_configuration_qr(line.id)

    # cleaning methods
    def cpq_clean_broken_pav_links(self):
        """
        Clean up cpq_configuration_json by removing references to deleted product.attribute.value IDs.
        """
        cleaned = 0
        broken_refs = {}

        for line in self:
            raw = line.cpq_configuration_json
            try:
                config = json.loads(raw or "{}")
            except Exception as e:
                # _logger.warning("Skipping line %s due to JSON error: %s", line.id, e)
                continue
            
            sel = config.get("selected") or {}
            if {"left","right","shared"} <= set(sel.keys()):
                flat = {}
                for side in ("left","right","shared"):
                    for k, v in (sel.get(side) or {}).items():
                        flat[str(k)] = v
                selected = flat
            else:
                selected = sel
            # selected = config.get("selected")
            if not isinstance(selected, dict):
                continue

            removed_keys = []
            for key in list(selected.keys()):
                try:
                    pav_id = int(key)
                    if not self.env["product.attribute.value"].browse(pav_id).exists():
                        selected.pop(key)
                        removed_keys.append(pav_id)
                except Exception:
                    continue

            if removed_keys:
                line.cpq_configuration_json = json.dumps(config)
                line._compute_cpq_configuration_summary()
                cleaned += 1
                broken_refs[line.id] = removed_keys

        return {
            "cleaned": cleaned,
            "details": broken_refs,
        }

    def cpq_clean_broken_pav_links_ui(self):
        """
        UI wrapper to run cpq_clean_broken_pav_links and return a notification.
        """
        result = self.cpq_clean_broken_pav_links()
        message = f"Custom cleanup completed:\n- Lines cleaned: {result['cleaned']}"
        if result["details"]:
            for line_id, keys in result["details"].items():
                message += f"\n  • Line {line_id}: removed {keys}"
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Custom Cleanup",
                "message": message,
                "type": "success",
                "sticky": False,
            },
        }
    