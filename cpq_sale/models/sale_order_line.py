import logging
import json
from datetime import datetime
from datetime import date, timedelta
from odoo.fields import Field
from odoo import _, api, fields, models
from odoo.tools import image_process
import qrcode
import base64
import hashlib
from io import BytesIO
from odoo.exceptions import UserError, ValidationError
from odoo.addons.cpq.helpers.summary_helper import render_summary_html, compute_cpq_price_breakdown, get_cpq_config_dict, generate_cpq_qr_payload, get_partner_discount

_logger = logging.getLogger(__name__)

# class SaleOrder(models.Model):
#     _inherit = "sale.order"

class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "mail.thread"]
    _name = "sale.order.line"

    product_template_id_cpq_ok = fields.Boolean(related="product_template_id.cpq_ok")

    # order_line_image = fields.Binary(string="Image",
    #                                  related="product_id.image_128",
    #                                  help="This field represents the image "
    #                                       "associated with the product on the "
    #                                       "sale order line."
    #                                  )

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
        string="CPQ Summary",
        compute="_compute_cpq_configuration_summary",
        store=True,
    )

    cpq_configuration_json = fields.Json(
        string="CPQ Configuration",
        help="Stores selected laterality and option data for CPQ products."
    )

    cpq_quantity_to_make = fields.Integer(
        string="Pairs to Make",
        compute="_compute_cpq_quantity_to_make",
        store=True
    )

    cpq_product_created = fields.Boolean(
        string="CPQ Product Created",
        compute="_compute_cpq_product_created",
        store=True
    )

    cpq_total_price = fields.Monetary(
        string="CPQ Total Price",
        compute="_compute_cpq_total_price",
        currency_field="currency_id",
        store=True
    )

    cpq_summary_printable = fields.Html("Printable CPQ Summary")

    cpq_qr_image = fields.Binary("CPQ QR Code", compute='_compute_cpq_qr_code', store=False)
    
    cpq_configuration_hash = fields.Char(
        string="CPQ Configuration Hash",
        compute="_compute_cpq_configuration_hash",
        store=True
    )

    @api.depends('order_id', 'product_template_id', 'cpq_configuration_json')
    def _compute_cpq_qr_code(self):
        for line in self:
            if line.product_template_id and line.order_id:
                config_hash = None
                if line.cpq_configuration_json:
                    config_hash = line._get_configuration_hash(line.cpq_configuration_json)

                payload = generate_cpq_qr_payload(
                    order_id=line.order_id.id,
                    line_id=line.id,
                    template_id=line.product_template_id.id,
                    config_hash=config_hash,
                )

                qr = qrcode.make(payload)
                buffer = BytesIO()
                qr.save(buffer, format="PNG")
                line.cpq_qr_image = base64.b64encode(buffer.getvalue())
            else:
                line.cpq_qr_image = False

    qr_uri = fields.Char(string="CPQ QR URI", compute="_compute_qr_uri")

    def _compute_qr_uri(self):
        for line in self:
            config_data = line.cpq_configuration_json
            config_hash = None
            if config_data:
                config_hash = line._get_configuration_hash(config_data)
            line.qr_uri = generate_cpq_qr_payload(
                order_id=line.order_id.id,
                line_id=line.id,
                template_id=line.product_template_id.id,
                config_hash=config_hash,
            )

    @api.depends('cpq_configuration_json')
    def _compute_cpq_configuration_hash(self):
        for line in self:
            if line.cpq_configuration_json:
                line.cpq_configuration_hash = line._get_configuration_hash(line.cpq_configuration_json)
            else:
                line.cpq_configuration_hash = False

    # def _get_configuration_hash(self, config_data):
    #     if isinstance(config_data, dict):
    #         config_data = json.dumps(config_data, sort_keys=True)
    #     elif not isinstance(config_data, str):
    #         config_data = str(config_data)
    #     return hashlib.sha256(config_data.encode("utf-8")).hexdigest()[:16]

    def _get_configuration_hash(self, config_data):
        """
        Generates a consistent SHA256 hash for the given CPQ configuration data.

        Handles dict, str, and other data types safely with sorted keys for consistency.
        """
        def default_serializer(obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            return str(obj)

        try:
            if isinstance(config_data, dict):
                # Safe JSON serialization with stable key order
                config_str = json.dumps(config_data, sort_keys=True, default=default_serializer)
            elif isinstance(config_data, str):
                config_str = config_data
            else:
                # Fallback: try to serialize other types safely
                config_str = json.dumps(config_data, default=default_serializer)
        except Exception as e:
            _logger.warning(f"⚠️ [CPQ] Failed to serialize config for hashing: {e}. Falling back to string conversion.")
            config_str = str(config_data)

        return hashlib.sha256(config_str.encode("utf-8")).hexdigest()[:16]


    def toggle_debug_cpq_json(self):
        # Placeholder logic: in real use, you'd probably use context or a transient field to show/hide.
        raise UserError("This would show/hide CPQ JSON — placeholder.")
    
    @api.onchange('cpq_configuration_json')
    def _onchange_cpq_configuration(self):
        for line in self:
            if not line.product_id.cpq_ok:
                line.cpq_configuration_json = False  # 💯 Non-CPQ? Kill any stray config.
                continue
            if not line.cpq_configuration_json:
                continue
            try:
                config = get_cpq_config_dict(line)  # ✅ Cleaner and safe

                _logger.info("🧩 [CPQ] Applying configuration to order line: %s", json.dumps(config, indent=2))

                line.name = config.get("name") or line.name
                line.product_uom_qty = config.get("quantity_to_make", line.product_uom_qty)

                # Optional: add to chatter only after save
                summary_html = render_summary_html(self.env, line.order_id, config, mode="chatter")

                _logger.info("🖨️ [CPQ] Generated Summary HTML:\n%s", summary_html)

                line.message_post(
                    body=f"""
                        <b>🛠️ CPQ Configuration Applied:</b><br/>
                        {summary_html}
                    """,
                    subtype_xmlid="mail.mt_note",
                )

            except Exception as e:
                _logger.warning(f"⚠️ Failed to parse CPQ config JSON: {e}")

    @api.depends('cpq_configuration_json')
    def _compute_cpq_laterality(self):
        for line in self:
            if not line.product_id.cpq_ok:
                line.cpq_laterality = False
                continue  # ✅ Skip non-CPQ lines!
            config = get_cpq_config_dict(line.cpq_configuration_json)
            line.cpq_laterality = config.get('laterality')
            
    @api.depends("cpq_configuration_json")
    def _compute_cpq_quantity_to_make(self):
        for line in self:
            if not line.product_id.cpq_ok:
                line.cpq_laterality = False
                continue  # ✅ Skip non-CPQ lines!
            config = get_cpq_config_dict(line.cpq_configuration_json)
            line.cpq_quantity_to_make = config.get("quantity_to_make", 1)

    @api.onchange("product_id")
    def _onchange_product_id_warning(self):
        res = super()._onchange_product_id_warning()

        for line in self:
            if not line.product_id:
                continue  # 🟡 No product selected → nothing to do

            if line.product_id.cpq_ok:
                # ✅ CPQ Product → skip price/UoM, configurator will handle this later
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
                # 🟢 Non-CPQ Product → force apply Odoo pricing & UoM behavior:
                product = line.product_id.with_company(line.company_id)
                partner = line.order_id.partner_id
                pricelist = line.order_id.pricelist_id

                # 🟢 Use Odoo's native price logic:
                product_context = dict(self.env.context, partner_id=partner.id, quantity=1, uom=product.uom_id.id)
                price = pricelist._get_product_price(product.with_context(product_context), 1.0, partner)

                line.price_unit = price or product.lst_price or 0.0
                line.product_uom = product.uom_id
                line.name = product.get_product_multiline_description_sale() or product.name
                line.cpq_configuration_json = False  # 🚫 Clear CPQ config if it was hanging around.

        return res

    @api.depends("cpq_configuration_json")
    def _compute_cpq_name_suffix(self):
        for line in self:
            if not line.product_id.cpq_ok:
                line.cpq_laterality = False
                continue  # ✅ Skip non-CPQ lines!
            config = self._parse_json_field(line.cpq_configuration_json)
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

    @api.onchange('cpq_configuration_json')
    def _onchange_cpq_pricing(self):
        for line in self:
            if not line.product_id.cpq_ok:
                # 🚫 Skip pricing logic entirely for non-CPQ products
                return

            config = get_cpq_config_dict(line.cpq_configuration_json)
            result = compute_cpq_price_breakdown(self.env, line, config) or {}
            quantity = result.get("quantity", 1)
            total = result.get("total")
            subtotal = result.get("subtotal")

            line.price_unit = total / quantity if total and quantity else subtotal or 0.0
            line.product_uom_qty = quantity

    @api.depends('cpq_configuration_json')
    def _compute_cpq_configuration_summary(self):
        for line in self:
            if not line.product_id.cpq_ok:
                line.cpq_laterality = False
                continue  # ✅ Skip non-CPQ lines!
            config = line._parse_config()
            if not config:
                line.cpq_configuration_summary = "No configuration available."
                continue
            try:
                config = line._parse_config()
                _logger.info(f"🧩 Generating summary for Sale Order Line {line.id}")
                _logger.info(f"Config Data: {config}")

                summary_html = render_summary_html(self.env, line.order_id, config)

                line.cpq_configuration_summary = summary_html

            except Exception as e:
                _logger.warning(f"⚠️ Failed to generate summary HTML: {e}")
                config = line._parse_config()

    def _parse_config(self):
        try:
            return json.loads(self.cpq_configuration_json) if isinstance(self.cpq_configuration_json, str) else self.cpq_configuration_json or {}
        except Exception as e:
            _logger.warning(f"[CPQ] JSON parse error: {e}")
            return {}

    def edit_cpq_configuration(self):
        self.ensure_one()
        
        # tmpl = self.product_template_id
        # if not tmpl:
        #     raise UserError("No product template linked to this line.")

        tmpl = self.product_template_id or self.product_id.product_tmpl_id
        if not tmpl:
            raise UserError("No product template linked to this line.")

        return {
            "type": "ir.actions.client",
            "tag": "cpq.ConfigureDialogAction",
            "context": {
                "active_model": "sale.order.line",
                "active_id": self.id,
                "cpq_product_template_id": tmpl.id,
                "cpq_initial_config": self.cpq_configuration_json,
                "from_sale_order": True,
                "redirect_to_line": True,
                "orderId": self.order_id.id,
                "currencyId": self.order_id.currency_id.id,
                "soDate": str(self.order_id.date_order),
                "companyId": self.order_id.company_id.id,
            },
            
        }
    
    def _compute_cpq_product_created(self):
        for line in self:
            line.cpq_product_created = bool(
                line.product_id and line.product_id.default_code and line.product_id.default_code.startswith("CFG-")
            )

    def action_open_create_product_wizard(self):
        self.ensure_one()

        if not self.cpq_configuration_json:
            raise UserError("No CPQ configuration found on this line.")

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

    def action_create_product_from_configuration(self):
        self.ensure_one()

        config = get_cpq_config_dict(self)
        if not config:
            raise UserError("No CPQ configuration found or it could not be parsed.")

        _logger.info("🧩 [CPQ] Creating product from configuration: %s", json.dumps(config, indent=2))

        # ✅ Safety check: prevent duplicate CPQ product creation
        if self.product_id and self.product_id.default_code and self.product_id.default_code.startswith("CFG-"):
            raise UserError("This line is already linked to a custom CPQ product.")

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

        _logger.info(f"🆕 Created product {new_product.display_name} ({new_product.id}) from CPQ config.")

        self._apply_cpq_attributes_to_product(config, new_product)

        self.message_post(body=_(
            f"🧩 Product <b>{new_product.display_name}</b> created from CPQ configuration."
        ))
        new_product.message_post(body=_(
            f"🧩 Created from CPQ configuration on Sale Order <b>{self.order_id.name}</b>."
        ))

        self.product_id = new_product.id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'res_id': new_product.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _calculate_total_extras(self, config):
        selected = config.get('selected', {})
        if not selected:
            return 0

        ptav_ids = [int(k) for k in selected if k.isdigit()]
        ptavs = self.env['product.template.attribute.value'].browse(ptav_ids)

        total_extra = sum(ptav.price_extra for ptav in ptavs)
        _logger.info(f"🧩 Total extras calculated: {total_extra}")
        return total_extra
    

    @api.model
    def _generate_cpq_description(self, config, total_extra):
        parts = [
            f"🦶 Laterality: {config.get('laterality', '').capitalize()}",
            f"📦 Quantity: {config.get('quantity_to_make', 1)}",
        ]

        selected = config.get("selected", {})
        if selected:
            parts.append("🧩 Selected Options:")
            for _, value in selected.items():
                parts.append(f"• {value}")

        if total_extra:
            parts.append(f"💰 Total Extras: {total_extra:.2f}")

        total_price = config.get('total_price')
        if total_price:
            parts.append(f"📊 Total Price: {total_price:.2f}")

        return "\n".join(parts)

    @api.depends("cpq_configuration_json")
    def _compute_cpq_total_price(self):
        for line in self:
            if not line.product_id.cpq_ok:
                line.cpq_laterality = False
                continue  # ✅ Skip non-CPQ lines!
            config = get_cpq_config_dict(line.cpq_configuration_json)
            breakdown = compute_cpq_price_breakdown(self.env, line, config)
            line.cpq_total_price = breakdown.get("total", 0.0)

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

        _logger.info(f"🧩 Applied CPQ attributes to product {product.display_name}: {ptav_records.mapped('name')}")
