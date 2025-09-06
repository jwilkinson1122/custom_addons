import logging
import json
from lxml import etree
from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from odoo.tools import frozendict
from odoo.tools.misc import OrderedSet
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base.models.ir_model import FIELD_TYPES

_logger = logging.getLogger(__name__)

LATERALITY_OPTIONS = [
    ("left", "Left Only"),
    ("right", "Right Only"),
    ("bilateral", "Bilateral"),
]

class Base(models.AbstractModel):
    _inherit = "base"

    def onchange(self, values: dict, field_names: list, fields_spec: dict):
        _logger.warning("[onchange] Fields: %s", field_names)
        _logger.warning("[onchange] Fields Spec Keys: %s", list(fields_spec.keys()))
        _logger.warning("[onchange] Values: %s", values)
        
        fields_spec = self.env["product.configurator"]._remove_dynamic_fields(
            fields_spec
        )
        return super().onchange(values, field_names, fields_spec)


class FreeSelection(fields.Selection):
    def convert_to_cache(self, value, record, validate=True):
        return super().convert_to_cache(value=value, record=record, validate=False)


class ProductConfigurator(models.Model): 
    _name = "product.configurator"
    _inherits = {"product.config.session": "config_session_id"}
    _description = "Product configuration Wizard"
    # _auto = True   

    # product_tmpl_id = fields.Many2one("product.template", string="Product Template")

    laterality = fields.Selection(
        selection=LATERALITY_OPTIONS,
        string="Laterality",
        required=True,
        default="bilateral",
    )

    is_bilateral = fields.Boolean(
        compute="_compute_is_bilateral", store=False
    )

    custom_laterality = fields.Boolean(
        string="Customize Laterality",
        help="Enable laterality customization when selected.",
        default=False,
    )

    laterality_config_ids = fields.One2many(
        "product.configurator.laterality.line",  
        "configurator_id",  
        string="Laterality",
    )

    laterality_comparison = fields.Text(compute="_compute_laterality_comparison", store=False)

    quantity = fields.Integer(
        string="Quantity",
        default=1,
        required=True,
        help="Number of devices to manufacture",
    )

    @api.depends("laterality")
    def _compute_is_bilateral(self):
        for record in self:
            record.is_bilateral = record.laterality == "bilateral"

    def action_customize_laterality(self):
        """Toggle Laterality Configuration and safely reset selections for a new step."""

        _logger.info(f"[CUSTOMIZE] Toggling Customize Section: Configurator ID = {self.id}, Custom Laterality = {self.custom_laterality}")

        # Ensure configurator exists before proceeding
        if not self.exists():
            _logger.error(f"[CUSTOMIZE] Configurator {self.id} is missing! Restoring session...")
            return self._handle_missing_configurator()

        # Preserve session while ensuring a clean slate for selections
        session = self.config_session_id
        if not session or not session.exists():
            _logger.warning(f"No active session found for Configurator ID = {self.id}. Searching for draft session.")
            session = self._get_active_session()

            if not session:
                return {"warning": {"title": "Session Error", "message": "Configuration session lost. Please restart."}}

        _logger.info(f"Using Session ID = {session.id} for Configurator ID = {self.id}")

        # SAFELY CLEAR EXISTING SELECTIONS WITHOUT BREAKING CONSTRAINTS
        _logger.info(f"[CUSTOMIZE] Resetting Laterality Configs for Configurator ID {self.id}")
        self.write({"laterality_config_ids": [(5, 0, 0)]})  # SAFE CLEAR

        # Toggle Laterality
        self.write({"custom_laterality": not self.custom_laterality})
        _logger.info(f"[CUSTOMIZE] Laterality Updated: Configurator ID = {self.id}, Custom Laterality = {self.custom_laterality}")

        # Commit changes to ensure data consistency
        self.env.cr.commit()

        return self._return_configurator_window()


    def _handle_missing_configurator(self):
        """Handle the case where the configurator record no longer exists."""
        _logger.error(f"[CUSTOMIZE] Configurator {self.id} is missing! Searching for active session.")

        session = self._get_active_session()

        if not session:
            return {"warning": {"title": "Session Error", "message": "Configuration session lost. Please restart."}}

        return self._restore_or_create_configurator(session)

    def _get_active_session(self):
        """Retrieve an active draft configuration session if available."""
        return self.env["product.config.session"].search(
            [("id", "=", self.config_session_id.id), ("state", "=", "draft")], limit=1
        ) if self.config_session_id else None

    def _restore_or_create_configurator(self, session):
        """Restore or create a new configurator for the active session."""
        
        configurator_model = "product.configurator.sale" if self._name == "product.configurator.sale" else "product.configurator"

        restored_configurator = self.env[configurator_model].search(
            [("config_session_id", "=", session.id)], limit=1
        )

        if not restored_configurator:
            _logger.info(f"[CUSTOMIZE] No existing configurator found for session {session.id}. Creating a new one.")

            restored_configurator = self.env[configurator_model].create({
                "config_session_id": session.id,
                "product_tmpl_id": session.product_tmpl_id.id,
                "laterality": session.laterality or "bilateral",
                "order_id": self.order_id.id if self._name == "product.configurator.sale" else False,
            })

            _logger.info(f"[CUSTOMIZE] New configurator created: ID = {restored_configurator.id} from session {session.id}")

        return {
            "type": "ir.actions.act_window",
            "res_model": configurator_model,
            "view_mode": "form",
            "res_id": restored_configurator.id,
            "target": "new",
            "context": dict(self.env.context, default_config_session_id=session.id),
        }

    def _return_configurator_window(self):
        """Return the current configurator window after updating laterality."""
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
            "context": self.env.context,
        }

    @api.depends("product_tmpl_id", "laterality", "quantity")
    def _compute_price(self):
        """Dynamically calculate price based on laterality and quantity."""
        for configurator in self:
            if not configurator.product_tmpl_id:
                configurator.price = 0.0
                continue

            base_price = configurator.product_tmpl_id.list_price or 0.0

            if configurator.laterality == "bilateral":
                configurator.price = base_price * 2 * configurator.quantity
            else:
                configurator.price = base_price * configurator.quantity

    def _find_wizard_context(self):
        # TODO: For more ref. https://github.com/odoo/odoo/pull/135145
        wizard_id = (
            self.env.context.get("wizard_id_view_ref")
            or self.env.context.get("wizard_id")
            or False
        )
        return wizard_id

    @property
    def _prefixes(self):
        """Return a dictionary with all dynamic field prefixes used to generate
        fields in the wizard. We add separate prefixes for left and right attributes
        when custom laterality is enabled."""
        return {
            "field_prefix": "__attribute_",
            "left_field_prefix": "__left_attribute_",
            "right_field_prefix": "__right_attribute_",
            "custom_field_prefix": "__custom_",
        }

    # TODO: Remove _prefix suffix as this is implied by the class property name
    @api.model
    def _remove_dynamic_fields(self, fields):
        """Remove elements from the fields dictionary/list that begin with any
        prefix from the _prefixes property
            :param fields: list or dict of the form [fn1, fn2] / {fn1: val}
        """

        prefixes = self._prefixes.values()

        field_type = type(fields)

        if field_type == list:
            static_fields = []
        elif field_type == dict:
            static_fields = {}

        for field_name in fields:
            if any(prefix in field_name for prefix in prefixes):
                continue
            if field_type == list:
                static_fields.append(field_name)
            elif field_type == dict:
                static_fields[field_name] = fields[field_name]
        return static_fields

    @api.depends("product_tmpl_id", "value_ids", "custom_value_ids")
    def _compute_cfg_image(self):
        # TODO: Update when allowing custom values to influence image
        for configurator in self:
            cfg_sessions = configurator.config_session_id.with_context(bin_size=False)
            image = cfg_sessions.get_config_image()
            configurator.product_img = image

    @api.depends("product_tmpl_id", "state", "product_tmpl_id.attribute_line_ids")
    def _compute_attr_lines(self):
        """Ensure only attributes related to the current step are shown."""
        for configurator in self:
            if not configurator.product_tmpl_id:
                configurator.attribute_line_ids = False
                continue

            # Handle case where state is "select"
            if configurator.state == "select":
                _logger.info(f"[ATTRIBUTE UPDATE] Configurator {configurator.id} is in 'select' state, displaying all attributes.")
                configurator.attribute_line_ids = configurator.product_tmpl_id.attribute_line_ids
                continue  # Skip step-based filtering

            # Convert state to step ID, handling invalid cases
            try:
                step_id = int(configurator.state)  # Convert to integer
            except (ValueError, TypeError):
                _logger.warning(f"Invalid state: '{configurator.state}' for Configurator {configurator.id}")
                configurator.attribute_line_ids = False
                continue

            # Fetch step lines related to this step ID
            step_lines = self.env["product.config.step.line"].search([("config_step_id", "=", step_id)])

            if not step_lines:
                configurator.attribute_line_ids = False
                continue

            valid_attr_lines = step_lines.mapped("attribute_line_ids")

            # Apply step-based attribute filtering
            configurator.attribute_line_ids = configurator.product_tmpl_id.attribute_line_ids.filtered(
                lambda line: line in valid_attr_lines
            )

    def _compute_laterality_comparison(self):
        """Compute a structured comparison between left and right configurations."""
        for record in self:
            comparison = []
            left_config = {line.attribute_id.id: line.value_id.name for line in record.laterality_config_ids.filtered(lambda x: x.side == "left")}
            right_config = {line.attribute_id.id: line.value_id.name for line in record.laterality_config_ids.filtered(lambda x: x.side == "right")}

            all_attributes = set(left_config.keys()).union(set(right_config.keys()))

            for attr_id in all_attributes:
                comparison.append({
                    "attribute": self.env["product.attribute"].browse(attr_id).name,
                    "left_value": left_config.get(attr_id, "Not Set"),
                    "right_value": right_config.get(attr_id, "Not Set"),
                    "difference": left_config.get(attr_id) != right_config.get(attr_id),
                })

            record.laterality_comparison = json.dumps(comparison)

    def action_review_differences(self):
        """Show a popup to review differences before proceeding."""
        self.ensure_one()
        comparison_data = json.loads(self.laterality_comparison or "[]")
        differences = [row for row in comparison_data if row["difference"]]

        if not differences:
            return {"warning": {"title": "No Differences", "message": "Both sides have identical configurations."}}

        message = "<b>Differences detected:</b><br/><ul>"
        for diff in differences:
            message += f"<li><b>{diff['attribute']}:</b> Left: {diff['left_value']} | Right: {diff['right_value']}</li>"
        message += "</ul>"

        return {
            "type": "ir.actions.act_window",
            "name": "Review Configuration Differences",
            "res_model": "ir.actions.server",
            "view_mode": "form",
            "views": [(False, "form")],
            "target": "new",
            "context": {"default_message": message},
        }

    def get_state_selection(self):
        """Get the states of the wizard using standard values and optional configuration steps."""
        steps = [("select", "Select Template")]
        wizard_id = self._find_wizard_context()
        wiz = self.browse(wizard_id).exists()
        if wiz:
            open_lines = wiz.config_session_id.get_open_step_lines()
            open_steps = open_lines.mapped(lambda x: (str(x.id), x.config_step_id.name))
            steps += open_steps if wiz.product_id else open_steps
        else:
            steps.append(("configure", "Configure"))
        return steps

    # TODO: Add confirmation button and delete cfg session

    @api.onchange("product_tmpl_id")
    def onchange_product_tmpl_id(self):
        """Ensure configurator updates correctly when selecting a product template, 
        preventing data loss and ensuring attributes, configuration steps, and presets are correctly updated.
        """

        if not self.product_tmpl_id:
            _logger.warning("No product template selected. Clearing attributes, steps, and preset.")
            self.attribute_line_ids = False
            self.config_step_ids = False
            self.product_preset_id = False
            return

        template = self.product_tmpl_id
        _logger.info(f"Updating configurator for Product Template: {template.name} (ID {template.id})")

        # Load attribute lines for the selected template
        self.attribute_line_ids = template.attribute_line_ids
        _logger.info(f"Loaded {len(self.attribute_line_ids)} attributes for {template.name}")

        # Load configuration steps for the selected template
        self.config_step_ids = template.config_step_line_ids.mapped("config_step_id")
        _logger.info(f"Loaded {len(self.config_step_ids)} configuration steps for {template.name}")

        # If a session exists, link to the preset (if any)
        session = self.env["product.config.session"].search_session(product_tmpl_id=template.id)
        self.product_preset_id = session.product_preset_id if session else False
        _logger.info(f"Product preset set: {self.product_preset_id.name if self.product_preset_id else 'None'}")

        # Prevent configuration loss when switching templates
        if self.value_ids:
            _logger.warning("Changing the product template will erase/reset the active configuration.")
            raise UserError(
                _("Changing the product template while having an active configuration will erase/reset all values.")
            )

    def get_onchange_domains(
        self,
        values,
        cfg_val_ids,
        product_tmpl_id=False,
        config_session_id=False,
    ):
        """Generate domains to be returned by onchange method in order
        to restrict the availble values of dynamically inserted fields

        :param values: values argument passed to onchance wrapper
        :cfg_val_ids: current configuration passed as a list of value_ids
        (usually in the form of db value_ids + interface value_ids)

        :returns: a dictionary of domains returned by onchance method
        """
        field_prefix = self._prefixes.get("field_prefix")
        if not product_tmpl_id:
            product_tmpl_id = self.product_tmpl_id
        if not config_session_id:
            config_session_id = self.config_session_id

        domains = {}
        check_avail_ids = cfg_val_ids[:]
        for line in product_tmpl_id.attribute_line_ids.sorted():
            field_name = field_prefix + str(line.attribute_id.id)

            if field_name not in values:
                continue

            vals = values[field_name]

            # get available values

            avail_ids = config_session_id.values_available(
                check_val_ids=line.value_ids.ids, value_ids=check_avail_ids
            )

            domains[field_name] = [("id", "in", avail_ids)]
            check_avail_ids = list(
                set(check_avail_ids) - (set(line.value_ids.ids) - set(avail_ids))
            )
            # Include custom value in the domain if attr line permits it
            if line.custom:
                custom_val = config_session_id.get_custom_value_id()
                domains[field_name][0][2].append(custom_val.id)
                if line.multi and vals and custom_val.id in vals[0][2]:
                    continue
        return domains

    def get_onchange_vals(self, cfg_val_ids, config_session_id=None):
        """Onchange hook to add / modify returned values by onchange method"""
        if not config_session_id:
            config_session_id = self.config_session_id

        # Remove None from cfg_val_ids if exist
        cfg_val_ids = [val for val in cfg_val_ids if val]
        tobe_remove_attr = self.env.context.get("tobe_remove_attr", [])
        product_img = config_session_id.get_config_image(cfg_val_ids)
        price = config_session_id.with_context(
            tobe_remove_attr=tobe_remove_attr
        ).get_cfg_price(cfg_val_ids)
        weight = config_session_id.get_cfg_weight(value_ids=cfg_val_ids)
        return {
            "product_img": product_img,
            "value_ids": [(6, 0, cfg_val_ids)],
            "weight": weight,
            "price": price,
        }

    def get_form_vals(
        self,
        dynamic_fields,
        domains,
        cfg_val_ids=None,
        product_tmpl_id=None,
        config_session_id=None,
    ):
        """Generate a dictionary to return new values via onchange method.
        Domains hold the values available, this method enforces these values
        if a selection exists in the view that is not available anymore.

        :param dynamic_fields: Dictionary with the current {dynamic_field: val}
        :param domains: Odoo domains restricting attribute values

        :returns vals: Dictionary passed to {'value': vals} by onchange method
        """
        vals = {}
        dynamic_fields = {k: v for k, v in dynamic_fields.items() if v}
        tobe_remove_attr = []
        available_val_ids_m2m = []
        for k, v in dynamic_fields.items():
            if not v:
                continue
            available_val_ids = domains[k][0][2]
            value_ids = self.config_session_id.value_ids
            attribute_line_ids = self.product_tmpl_id.attribute_line_ids.filtered(
                lambda line: line.multi
                and line.attribute_id.id in value_ids.mapped("attribute_id").ids
            )
            multi_value_ids = self.config_session_id.value_ids.filtered(
                lambda value: value.attribute_id.id
                in attribute_line_ids.mapped("attribute_id").ids
            )
            available_val_ids_m2m = multi_value_ids.ids
            tobe_remove_attr_m2m = []
            if isinstance(v, list) or self.env.context.get("is_m2m"):
                if isinstance(v, list):
                    for sub_value in v:
                        if sub_value[0] == 3:
                            tobe_remove_attr_m2m.append(sub_value[1])
                            available_val_ids_m2m.remove(sub_value[1])
                        if sub_value[0] == 4:
                            available_val_ids_m2m.append(sub_value[1])
                    dynamic_fields.update({k: available_val_ids_m2m})
                    vals[k] = [[6, 0, available_val_ids_m2m]]
            elif v not in available_val_ids:
                dynamic_fields.update({k: []})
                vals[k] = []

            else:
                vals[k] = v
        if (
            (
                self.env.context.get("is_action_previous")
                or self.env.context.get("is_preset")
                or self.env.context.get("is_m2m")
            )
            and config_session_id
            and config_session_id.value_ids
        ):
            session_attrb_values = config_session_id.value_ids
            tmpl_config_lines = (
                config_session_id.product_tmpl_id.config_line_ids.mapped(
                    "attribute_line_id.attribute_id"
                )
            )
            domain_line_attrbs = (
                config_session_id.product_tmpl_id.config_line_ids.mapped(
                    "domain_id.domain_line_ids.attribute_id"
                )
            )
            dynamic_fields2 = {}
            restricted_attrs = list(set(tmpl_config_lines.ids + domain_line_attrbs.ids))
            field_prefix = self._prefixes.get("field_prefix")
            if (
                self.env.context.get("is_action_previous")
                or self.env.context.get("is_preset")
                or self._context.get("is_m2m", False)
            ):
                for attrb_value in session_attrb_values:
                    dyn_key = field_prefix + str(attrb_value.attribute_id.id)
                    if not self._context.get("is_m2m", False):
                        if (
                            dynamic_fields.get(dyn_key)
                            and dynamic_fields.get(dyn_key)
                            not in session_attrb_values.ids
                        ):
                            tobe_remove_attr.append(attrb_value.id)
                            if attrb_value.attribute_id.id in restricted_attrs:
                                local_attrb_value = attrb_value
                                for i in range(len(restricted_attrs)):
                                    valve_ids = product_tmpl_id.config_line_ids.filtered(
                                        lambda line: int(local_attrb_value.id)
                                        in line.domain_id.domain_line_ids.value_ids.ids
                                    ).mapped(
                                        "value_ids"
                                    )
                                    local_attrb_value = session_attrb_values.filtered(
                                        lambda lk: lk.id in valve_ids.ids
                                    )
                                    if local_attrb_value:
                                        tobe_remove_attr.append(local_attrb_value.id)
                                        dynamic_fields2.update(
                                            {
                                                field_prefix
                                                + str(
                                                    local_attrb_value.attribute_id.id
                                                ): local_attrb_value.id
                                            }
                                        )
                    elif (
                        self._context.get("is_m2m", False) and dyn_key in dynamic_fields
                    ):
                        tobe_remove_attr_m2m = set(tobe_remove_attr_m2m) - set(
                            available_val_ids_m2m
                        )
                        tobe_remove_attr.extend(list(tobe_remove_attr_m2m))
            origin_updated_fields = set(dynamic_fields)
            to_updated_fields = set(dynamic_fields2)
            updated_fields = to_updated_fields - origin_updated_fields
            for fi in updated_fields:
                dynamic_fields.update({fi: None})
                vals.update({fi: None})
        final_cfg_val_ids = list(dynamic_fields.values())
        vals.update(
            self.with_context(tobe_remove_attr=tobe_remove_attr).get_onchange_vals(
                final_cfg_val_ids, config_session_id
            )
        )
        # To solve the Multi selection problem removing extra []
        if "value_ids" in vals:
            val_ids = vals["value_ids"][0]
            vals["value_ids"] = [[val_ids[0], val_ids[1], tools.flatten(val_ids[2])]]
        return vals

    def apply_onchange_values(self, values, field_name, field_onchange):
        """Called from web-controller
        - original onchage return M2o values in formate
        (attr-value.id, attr-value.name) but on website
        we need only attr-value.id"""
        product_tmpl_id = self.env["product.template"].browse(
            values.get("product_tmpl_id", [])
        )
        if not product_tmpl_id:
            product_tmpl_id = self.product_tmpl_id

        config_session_id = self.env["product.config.session"].browse(
            values.get("config_session_id", [])
        )
        if not config_session_id:
            config_session_id = self.config_session_id

        state = values.get("state", False)
        if not state:
            state = self.state

        cfg_vals = self.env["product.attribute.value"]
        config_line_ids = product_tmpl_id.config_line_ids

        if not cfg_vals:
            cfg_vals = self.value_ids

        field_type = type(field_name)
        field_prefix = self._prefixes.get("field_prefix")
        custom_field_prefix = self._prefixes.get("custom_field_prefix")
        local_field_name = field_name and field_name[0].startswith(field_prefix)
        local_custom_field = field_name and field_name[0].startswith(
            custom_field_prefix
        )
        if field_type == list and (not local_field_name and not local_custom_field):
            values = self._remove_dynamic_fields(values)
            res = super().onchange(values, field_name, field_onchange)
            return res

        view_val_ids = set()
        view_attribute_ids = set()

        try:
            cfg_step_id = int(state)
            cfg_step = product_tmpl_id.config_step_line_ids.filtered(
                lambda x: x.id == cfg_step_id
            )
        except Exception:
            cfg_step = self.env["product.config.step.line"]

        dynamic_fields = {k: v for k, v in values.items() if k.startswith(field_prefix)}
        # Get the unstored values from the client view
        for k, v in dynamic_fields.items():
            attr_id = int(k.split(field_prefix)[1])
            valve_ids = self.env["product.attribute.value"]
            if isinstance(v, list):
                for att in v:
                    valve_ids |= product_tmpl_id.config_line_ids.filtered(
                        lambda line: int(att[1])
                        in line.domain_id.domain_line_ids.value_ids.ids
                    ).mapped("value_ids")
            else:
                valve_ids = product_tmpl_id.config_line_ids.filtered(
                    lambda line: int(v) in line.domain_id.domain_line_ids.value_ids.ids
                ).mapped("value_ids")
                dyn_restricted_attrs_dicts = (
                    self.dyn_restricted_attrs_dicts
                    and json.loads(self.dyn_restricted_attrs_dicts)
                    or {}
                )
                field_name = field_prefix + str(valve_ids.mapped("attribute_id").id)
                if attr_id and valve_ids.filtered(
                    lambda value: value.attribute_id.id != attr_id
                ):
                    if field_name in dyn_restricted_attrs_dicts:
                        dyn_restricted_attrs_dicts[field_name] = valve_ids.ids
                    else:
                        dyn_restricted_attrs_dicts.update({field_name: valve_ids.ids})
                self.dyn_restricted_attrs_dicts = json.dumps(dyn_restricted_attrs_dicts)
            is_custom = self.product_tmpl_id.attribute_line_ids.filtered(
                lambda l: l.attribute_id.id == valve_ids.mapped("attribute_id").id
                and l.custom
            )
            non_custom = self.product_tmpl_id.attribute_line_ids - is_custom
            self.domain_attr_2_ids = [(6, 0, valve_ids.ids)]
            if valve_ids.mapped("attribute_id").id in is_custom.ids:
                self.dyn_field_2_value = custom_field_prefix + str(
                    valve_ids.mapped("attribute_id").id
                )
            if valve_ids.mapped("attribute_id").id in non_custom.ids:
                self.dyn_field_2_value = field_prefix + str(
                    valve_ids.mapped("attribute_id").id
                )

            line_attributes = cfg_step.attribute_line_ids.mapped("attribute_id")

            if not cfg_step or attr_id in line_attributes.ids:
                view_attribute_ids.add(attr_id)
            else:
                continue
            if not v:
                continue
            if isinstance(v, list):
                for a in v:
                    view_val_ids.add(a[1])
            elif isinstance(v, int):
                view_val_ids.add(v)

        # Clear all DB values belonging to attributes changed in the wizard
        cfg_vals = cfg_vals.filtered(
            lambda v: v.attribute_id.id not in view_attribute_ids
        )
        # Combine database values with wizard values_available
        cfg_val_ids = cfg_vals.ids + list(view_val_ids)

        domains = self.get_onchange_domains(
            values, cfg_val_ids, product_tmpl_id, config_session_id
        )
        if domains:
            for key, value in domains.items():
                if [key] == field_name:
                    if len(domains) == 1:
                        self.dyn_field_value = key
                        self.domain_attr_ids = [(6, 0, value[0][2])]
                    else:
                        self.dyn_field_2_value = key
                        self.domain_attr_2_ids = [(6, 0, value[0][2])]

                    continue
                elif values and value[0][2]:
                    self.dyn_field_2_value = key
                    self.domain_attr_2_ids = [(6, 0, value[0][2])]
        if self.dyn_field_value == self.dyn_field_2_value and dynamic_fields.get(
            self.dyn_field_value
        ):
            value_to_remove = dynamic_fields.get(self.dyn_field_value)
            if value_to_remove in self.domain_attr_ids.ids:
                self.domain_attr_ids = False
            if value_to_remove in self.domain_attr_2_ids.ids:
                self.domain_attr_2_ids = False
        vals = self.get_form_vals(
            dynamic_fields=dynamic_fields,
            domains=domains,
            product_tmpl_id=product_tmpl_id,
            config_session_id=config_session_id,
        )
        return {"value": vals, "domain": domains}

    def onchange(self, values, field_name, field_onchange):
        """Override the onchange wrapper to return domains to dynamic
        fields as onchange isn't triggered for non-db fields
        """
        onchange_values = self.apply_onchange_values(
            values=values, field_name=field_name, field_onchange=field_onchange
        )
        field_prefix = self._prefixes.get("field_prefix")
        vals = onchange_values.get("value", {})
        for key, val in vals.items():
            if isinstance(val, int) and key.startswith(field_prefix):
                att_val = self.env["product.attribute.value"].browse(val)
                vals[key] = (att_val.id, att_val.name)
        return onchange_values

    config_session_id = fields.Many2one(
        required=True,
        comodel_name="product.config.session",
        string="Configuration Session",
        ondelete="restrict", 
    )

    attribute_line_ids = fields.One2many(
        comodel_name="product.template.attribute.line",
        compute="_compute_attr_lines",
        string="Attributes",
        readonly=True,
        store=False,
    )

    config_step_ids = fields.Many2many(
        comodel_name="product.config.step",
        relation="product_config_config_steps_rel",
        column1="config_wiz_id",
        column2="config_step_id",
        string="Configuration Steps",
        readonly=True,
        store=False,
    )

    product_tmpl_id = fields.Many2one(
        "product.template",
        string="Product Template",
        required=False,  # Remove any forced requirement at creation
        default=None,  # Ensure no product is preselected
        domain="[('config_ok', '=', True)]",
    )

    product_id = fields.Many2one(
        comodel_name="product.product",
        readonly=True,
        string="Product Variant",
        help="Set only when re-configuring a existing variant",
    )

    product_img = fields.Binary(compute="_compute_cfg_image", readonly=True)

    state = FreeSelection(
        selection="get_state_selection", default="select", string="State"
    )

    domain_attr_ids = fields.Many2many(
        "product.attribute.value",
        "domain_attrs_values_rel",
        "wiz_id",
        "attribute_id",
        string="Domain",
    )

    dyn_field_value = fields.Char()

    domain_attr_2_ids = fields.Many2many(
        "product.attribute.value",
        "domain_attrs_2_values_rel",
        "wiz_id",
        "attribute_id",
        string="Domain",
    )

    dyn_field_2_value = fields.Char()

    dyn_restricted_attrs_dicts = fields.Text()

    @api.onchange("state")
    def _onchange_state(self):
        """Save values when change state of wizard by clicking on statusbar"""
        if self.env.context.get("allow_preset_selection"):
            self = self.with_context(allow_preset_selection=False)
        if self.config_session_id:
            self.config_session_id._origin.write(
                {
                    "value_ids": [[6, 0, self.value_ids.ids]],
                    "config_step": self.state,
                }
            )

    @api.onchange("product_preset_id")
    def _onchange_product_preset(self):
        """Set value ids as from product preset"""
        preset_id = self.product_preset_id
        if not preset_id and self.env.context.get("preset_values"):
            preset_id = self.env.context.get("preset_values").get("product_preset_id")
            preset_id = self.env["product.product"].browse(preset_id)
        pta_value_ids = preset_id.product_template_attribute_value_ids
        attr_value_ids = pta_value_ids.mapped("product_attribute_value_id")
        self._origin.value_ids = attr_value_ids
        self._origin.price = (
            preset_id and preset_id.lst_price or self.product_tmpl_id.list_price
        )

    @api.model
    def get_field_default_attrs(self):
        return {
            "company_dependent": False,
            "depends": (),
            "groups": False,
            "readonly": False,
            "manual": False,
            "required": False,
            "searchable": False,
            "store": False,
            "translate": False,
        }
    
    def fields_get(self, allfields=None, attributes=None):
        """Dynamically inject attributes for the product configurator, considering both template selection and step-based configuration."""

        field_prefix = self._prefixes.get("field_prefix")
        left_field_prefix = self._prefixes.get("left_field_prefix")
        right_field_prefix = self._prefixes.get("right_field_prefix")

        res = super().fields_get(allfields=allfields, attributes=attributes)

        wizard_id = self._find_wizard_context()
        if not wizard_id:
            _logger.warning("[FIELDS_GET] No wizard ID found, skipping field injection.")
            return res

        wiz = self.browse(wizard_id)

        if not wiz.product_tmpl_id:
            _logger.warning("[FIELDS_GET] No product template found, skipping field injection.")
            return res

        # **Inject attribute_line_ids during Select Template phase**
        if wiz.state == "select":
            res["attribute_line_ids"] = {
                "type": "one2many",
                "relation": "product.template.attribute.line",
                "string": "Available Attributes",
            }
            _logger.info(f"[FIELDS_GET] Injected {len(wiz.product_tmpl_id.attribute_line_ids)} attributes for Select Template.")
            return res

        # **Retrieve current step**
        step_id = int(wiz.state) if wiz.state.isdigit() else None
        step = self.env["product.config.step"].browse(step_id) if step_id else None

        if not step:
            _logger.warning(f"[FIELDS_GET] Step ID '{step_id}' does not exist, skipping field injection.")
            return res

        _logger.info(f"[FIELDS_GET] Processing Step: {step.id}")

        step_lines = self.env["product.config.step.line"].search([("config_step_id", "=", step.id)])
        applicable_attr_lines = wiz.product_tmpl_id.attribute_line_ids.filtered(lambda l: l in step_lines.mapped("attribute_line_ids"))

        for line in applicable_attr_lines:
            attribute = line.attribute_id
            value_ids = wiz.config_session_id.values_available(check_val_ids=line.value_ids.ids)

            field_name = field_prefix + str(attribute.id)
            res[field_name] = {
                "type": "many2one",
                "domain": [("id", "in", value_ids)],
                "string": attribute.name,
                "relation": "product.attribute.value",
            }

            # **Handle bilateral customization**
            if wiz.laterality == "bilateral" and wiz.custom_laterality:
                res[left_field_prefix + str(attribute.id)] = {
                    "type": "many2one",
                    "domain": [("id", "in", value_ids)],
                    "string": f"{attribute.name} (Left)",
                    "relation": "product.attribute.value",
                }
                res[right_field_prefix + str(attribute.id)] = {
                    "type": "many2one",
                    "domain": [("id", "in", value_ids)],
                    "string": f"{attribute.name} (Right)",
                    "relation": "product.attribute.value",
                }
                res.pop(field_name, None)  # Remove the single field since we now have left/right options

        _logger.info(f"[FIELDS_GET] Injected dynamic fields: {list(res.keys())}")
        return res

    def get_view(self, view_id=None, view_type="form", **options):
        """Ensure dynamic fields load correctly and fix step validation issues."""

        if view_type == "form" and not view_id:
            view_ext_id = "pod_odoo_master.product_configurator_form"
            view_id = self.env.ref(view_ext_id).id

        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        wizard_id = self._find_wizard_context()

        if not wizard_id:
            _logger.warning(" [GET_VIEW] No wizard ID found, skipping view update.")
            return res

        wiz = self.browse(wizard_id)

        # Fix Issue: Ensure state is not None
        if not wiz.state:
            _logger.warning(f" [GET_VIEW] Invalid Step ID 'None' detected, defaulting to 'select'.")
            wiz.write({"state": "select"})

        if not wiz.product_tmpl_id:
            _logger.warning(" [GET_VIEW] No product template found, skipping view update.")
            return res

        step_id = int(wiz.state) if wiz.state.isdigit() else None
        step = self.env["product.config.step"].browse(step_id) if step_id else None

        if not step:
            _logger.warning(f" [GET_VIEW] Step ID '{step_id}' does not exist, skipping view update.")
            return res

        _logger.info(f" [GET_VIEW] Processing Step in get_view: {step.id}")

        try:
            xml_view = etree.fromstring(res["arch"])
            xml_dynamic_form = xml_view.xpath("//group[@name='dynamic_form']")
            if not xml_dynamic_form:
                _logger.warning(" [GET_VIEW] 'dynamic_form' group not found in XML view.")
                return res
            xml_dynamic_form = xml_dynamic_form[0]
            xml_dynamic_form.clear()
        except Exception as e:
            _logger.error(f" [GET_VIEW ERROR] Unable to parse XML view: {str(e)}")
            return res

        step_lines = self.env["product.config.step.line"].search([("config_step_id", "=", step.id)])
        applicable_attr_lines = wiz.product_tmpl_id.attribute_line_ids.filtered(
            lambda l: l in step_lines.mapped("attribute_line_ids")
        )

        field_prefix = self._prefixes.get("field_prefix")
        left_field_prefix = self._prefixes.get("left_field_prefix")
        right_field_prefix = self._prefixes.get("right_field_prefix")

        for attr_line in applicable_attr_lines:
            attr_id = attr_line.attribute_id.id

            if wiz.laterality == "bilateral" and wiz.custom_laterality:
                left_node = etree.Element("field", name=f"{left_field_prefix}{attr_id}", string=f"{attr_line.attribute_id.name} (Left)")
                right_node = etree.Element("field", name=f"{right_field_prefix}{attr_id}", string=f"{attr_line.attribute_id.name} (Right)")
                xml_dynamic_form.append(left_node)
                xml_dynamic_form.append(right_node)
            else:
                node = etree.Element("field", name=f"{field_prefix}{attr_id}", string=attr_line.attribute_id.name)
                xml_dynamic_form.append(node)

        res["arch"] = etree.tostring(xml_view, encoding="utf-8").decode("utf-8")
        _logger.info(f" [GET_VIEW] Updated XML View for Step {step.id}")
        
        return res

    def prepare_attrs_initial(
        self, attr_lines, field_prefix, custom_field_prefix, dynamic_fields, wiz
    ):
        cfg_step_ids = []
        for attr_line in attr_lines:
            attribute_id = attr_line.attribute_id.id
            field_name = field_prefix + str(attribute_id)
            custom_field = custom_field_prefix + str(attribute_id)

            # Check if the attribute line has been added to the db fields
            if field_name not in dynamic_fields:
                continue

            config_steps = wiz.product_tmpl_id.config_step_line_ids.filtered(
                lambda x: attr_line in x.attribute_line_ids
            )

            # attrs property for dynamic fields
            attrs = {"readonly": "", "required": "", "invisible": ""}
            invisible_str = ""
            readonly_str = ""
            required_str = ""

            if config_steps:
                cfg_step_ids = [str(id) for id in config_steps.ids]
                invisible_str = f"state not in {cfg_step_ids}"
                readonly_str = f"state not in {cfg_step_ids}"
                # If attribute is required make it so only in the proper step
                if attr_line.required:
                    required_str = f"state in {cfg_step_ids}"
            else:
                invisible_str = "state not in {}".format(["configure"])
                readonly_str = "state not in {}".format(["configure"])
                # If attribute is required make it so only in the proper step
                if attr_line.required:
                    required_str = "state in {}".format(["configure"])

            if attr_line.custom:
                pass
                # TODO: Implement restrictions for ranges

            config_lines = wiz.product_tmpl_id.config_line_ids
            dependencies = config_lines.filtered(
                lambda cl: cl.attribute_line_id == attr_line
            )

            # If an attribute field depends on another field from the same
            # configuration step then we must use attrs to enable/disable the
            # required and readonly depending on the value entered in the
            # dependee

            if attr_line.value_ids <= dependencies.mapped("value_ids"):
                attr_depends = {}
                domain_lines = dependencies.mapped("domain_id.domain_line_ids")
                for domain_line in domain_lines:
                    attr_id = domain_line.attribute_id.id
                    attr_field = field_prefix + str(attr_id)
                    attr_lines = wiz.product_tmpl_id.attribute_line_ids
                    # If the fields it depends on are not in the config step
                    # allow to update attrs for all attribute.\ otherwise
                    # required will not work with stepchange using statusbar.
                    # if config_steps and wiz.state not in cfg_step_ids:
                    #     continue
                    if attr_field not in attr_depends:
                        attr_depends[attr_field] = set()
                    if domain_line.condition == "in":
                        attr_depends[attr_field] |= set(domain_line.value_ids.ids)
                    elif domain_line.condition == "not in":
                        val_ids = attr_lines.filtered(
                            lambda line: line.attribute_id.id == attr_id
                        ).value_ids
                        val_ids = val_ids - domain_line.value_ids
                        attr_depends[attr_field] |= set(val_ids.ids)

                for dependee_field, val_ids in attr_depends.items():
                    if not val_ids:
                        continue

                    # if not attr_line.custom:
                    #     readonly_str = f"{dependee_field} not in {list(val_ids)}"
                    if attr_line.required and not attr_line.custom:
                        required_str += f" and {dependee_field} in {list(val_ids)}"

            attrs.update(
                {
                    "readonly": readonly_str,
                    "required": required_str,
                    "invisible": invisible_str,
                }
            )
        return attrs, field_name, custom_field, config_steps, cfg_step_ids

    @api.model
    def add_dynamic_fields(self, res, dynamic_fields, wiz):
        """Create the configuration view using the dynamically generated
        fields in fields_get()
        """

        field_prefix = self._prefixes.get("field_prefix")
        custom_field_prefix = self._prefixes.get("custom_field_prefix")

        try:
            # Search for view container hook and add dynamic view and fields
            xml_view = etree.fromstring(res["arch"])
            xml_static_form = xml_view.xpath("//group[@name='static_form']")[0]
            xml_dynamic_form = etree.Element("group", colspan="2", name="dynamic_form")
            xml_parent = xml_static_form.getparent()
            xml_parent.insert(xml_parent.index(xml_static_form) + 1, xml_dynamic_form)
            xml_dynamic_form = xml_view.xpath("//group[@name='dynamic_form']")[0]
        except Exception as exc:
            raise UserError(
                _("There was a problem rendering the view " "(dynamic_form not found)")
            ) from exc

        # Get all dynamic fields inserted via fields_get method
        attr_lines = wiz.product_tmpl_id.attribute_line_ids.sorted()

        # Loop over the dynamic fields and add them to the view one by one
        for attr_line in attr_lines:  # TODO: NC: Added a filter for multi
            (
                attrs,
                field_name,
                custom_field,
                config_steps,
                cfg_step_ids,
            ) = self.prepare_attrs_initial(
                attr_line, field_prefix, custom_field_prefix, dynamic_fields, wiz
            )

            # Create the new field in the view
            node = etree.Element(
                "field",
                name=field_name,
                on_change="1",
                default_focus="1" if attr_line == attr_lines[0] else "0",
                attrib=attrs,
                context=str(
                    {
                        "show_attribute": False,
                        "show_price_extra": True,
                        "active_id": wiz.product_tmpl_id.id,
                        "wizard_id": wiz.id,
                        "field_name": field_name,
                        "is_m2m": attr_line.multi,
                        "value_ids": attr_line.value_ids.ids,
                        "active_model": self._name,
                    }
                ),
                options=str(
                    {
                        "no_create": True,
                        "no_create_edit": True,
                        "no_open": True,
                    }
                ),
            )

            field_type = dynamic_fields[field_name].get("type")
            if field_type == "many2many":
                node.attrib["widget"] = "many2many_tags"
            # Apply the modifiers (attrs) on the newly inserted field in the
            # arch and add it to the view
            # self.setup_modifiers(node) # TODO: NC: Need to improve this method
            xml_dynamic_form.append(node)

            if attr_line.custom and custom_field in dynamic_fields:
                widget = ""
                config_session_obj = self.env["product.config.session"]
                custom_option_id = config_session_obj.get_custom_value_id().id

                if field_type == "many2many":
                    field_val = [(6, False, [custom_option_id])]
                else:
                    field_val = custom_option_id

                attrs.update(
                    {
                        "readonly": attrs.get("readonly")
                        + f" and {field_name} != {field_val}"
                    }
                )
                attrs.update(
                    {
                        "invisible": attrs.get("invisible")
                        + f" and {field_name} != {field_val}"
                    }
                )
                attrs.update(
                    {
                        "required": attrs.get("required")
                        + f" and {field_name} != {field_val}"
                    }
                )

                if config_steps:
                    attrs.update(
                        {
                            "required": attrs.get("required")
                            + f" and 'state' in {cfg_step_ids}"
                        }
                    )

                # TODO: Add a field2widget mapper
                if attr_line.attribute_id.custom_type == "color":
                    widget = "color"

                node = etree.Element(
                    "field", name=custom_field, attrib=attrs, widget=widget
                )
                # self.setup_modifiers(node) # TODO: NC: Need to improve this method
                xml_dynamic_form.append(node)
        return xml_view

    @api.model_create_multi
    def create(self, vals_list):
        """Ensures configurator is fully created, committed, and properly initialized."""

        for vals in vals_list:
            product_tmpl_id = vals.get("product_tmpl_id")

            # If product_id is provided, infer product_tmpl_id
            if "product_id" in vals and not product_tmpl_id:
                product = self.env["product.product"].browse(vals["product_id"])
                vals["product_tmpl_id"] = product.product_tmpl_id.id
                attr_value_ids = product.product_template_attribute_value_ids.mapped("product_attribute_value_id")
                vals["value_ids"] = [(6, 0, attr_value_ids.ids)]

            # Ensure configurator can be created without a product template
            if not vals.get("product_tmpl_id"):
                _logger.warning("Creating configurator without a product template. Defaulting to 'select' state.")
                vals["state"] = "select"  # Ensure configurator starts in 'select' step
                vals["product_tmpl_id"] = False  # Explicitly set template to False

            # Only create a session if a product template is provided
            if vals.get("product_tmpl_id"):
                session = self.env["product.config.session"].sudo().create_get_session(
                    product_tmpl_id=vals["product_tmpl_id"]
                )
                vals["config_session_id"] = session.id

                # Assign session values if available
                if session.value_ids:
                    vals["value_ids"] = [(6, 0, session.value_ids.ids)]
            else:
                _logger.info("ℹ Skipping session creation as no product template is selected.")

            vals["user_id"] = self.env.uid  # Ensure user ID is set

        # Create the configurator record
        records = super().create(vals_list)

        # Flush and commit to ensure database consistency
        self.env.cr.flush()
        self.env.cr.commit()

        _logger.info(f"Configurator Created and Committed: {records.ids}")

        return records

    def read(self, fields=None, load="_classic_read"):
        """Remove dynamic fields from the fields list and update the
        returned values with the dynamic data stored in value_ids"""

        field_prefix = self._prefixes.get("field_prefix")
        custom_field_prefix = self._prefixes.get("custom_field_prefix")
        attr_vals = [f for f in fields if f.startswith(field_prefix)]
        custom_attr_vals = [f for f in fields if f.startswith(custom_field_prefix)]

        dynamic_fields = attr_vals + custom_attr_vals
        fields = self._remove_dynamic_fields(fields)

        custom_val = self.env["product.config.session"].get_custom_value_id()
        dynamic_vals = {}

        res = super().read(fields=fields, load=load)

        if not load:
            load = "_classic_read"

        if not dynamic_fields:
            return res

        for attr_line in self.product_tmpl_id.attribute_line_ids:
            attr_id = attr_line.attribute_id.id
            field_name = field_prefix + str(attr_id)
            if field_name not in dynamic_fields:
                continue

            custom_field_name = custom_field_prefix + str(attr_id)

            # Handle default values for dynamic fields on Odoo frontend
            res[0].update({field_name: False, custom_field_name: False})

            custom_vals = self.custom_value_ids.filtered(
                lambda x: x.attribute_id.id == attr_id
            ).with_context(show_attribute=False)
            vals = attr_line.value_ids.filtered(
                lambda v: v in self.value_ids
            ).with_context(
                show_attribute=False,
                show_price_extra=True,
                active_id=self.product_tmpl_id.id,
            )

            if not attr_line.custom and not vals:
                continue

            if attr_line.custom and custom_vals:
                custom_field_val = custom_val.id
                if load == "_classic_read":
                    # custom_field_val = custom_val.name_get()[0]
                    custom_field_val = (custom_val.id, custom_val.display_name or "")
                dynamic_vals.update(
                    {
                        field_name: custom_field_val,
                        custom_field_name: custom_vals.eval(),
                    }
                )
            elif attr_line.multi:
                dynamic_vals = {field_name: vals.ids}
            else:
                try:
                    vals.ensure_one()
                    field_value = vals.id
                    if load == "_classic_read":
                        # field_value = vals.name_get()[0]
                        field_value = (vals.id, vals.display_name or "")
                    dynamic_vals = {field_name: field_value}
                except Exception:
                    continue
            res[0].update(dynamic_vals)
        return res
    
    def _merge_or_reset(self, existing_ids, new_vals, field_name):
        """Merge existing selections with new ones unless explicitly cleared."""
        
        if not new_vals:
            _logger.warning(f"Resetting {field_name} selections for Configurator ID {self.id}")
            return [(5, 0, 0)]  # Explicitly clear

        # Extract new IDs from format [(6, 0, [ids])]
        if isinstance(new_vals, list) and new_vals and isinstance(new_vals[0], tuple):
            new_vals = new_vals[0][2] if isinstance(new_vals[0][2], list) else []

        merged_values = list(set(existing_ids + new_vals))
        _logger.info(f"Merging {field_name}: Old={existing_ids}, New={new_vals}, Merged={merged_values}")
        
        return [(6, 0, merged_values)]
    
    def write(self, vals):
        """Ensure values and laterality settings persist correctly across steps while referencing the correct configurator."""
        
        _logger.info(f"[WRITE] Called with vals: {vals} on Configurator ID {self.id}")

        # Ensure pending transactions are flushed before querying the database
        self.env.cr.flush()

        # Validate the configurator exists in the database
        self.env.cr.execute("SELECT id FROM product_configurator_sale WHERE id = %s", (self.id,))
        configurator_exists = self.env.cr.fetchone()

        _logger.info(f"Query Result for ID {self.id}: {configurator_exists}")

        if configurator_exists is None:
            _logger.error(f"Configurator ID {self.id} STILL does not exist in DB! Aborting write.")
            return False

        _logger.info(f"Configurator ID {self.id} confirmed in database.")

        # Determine the correct configurator_id for laterality updates
        correct_configurator_id = self.id  

        if self._name == "product.configurator":
            sale_configurator = self.env["product.configurator.sale"].search(
                [("config_session_id", "=", self.config_session_id.id)], limit=1
            )
            if sale_configurator:
                correct_configurator_id = sale_configurator.id
                _logger.info(f"Mapping laterality updates to sale configurator ID: {correct_configurator_id}")
            else:
                _logger.warning(f"No corresponding product.configurator.sale found! Retaining configurator_id {self.id}.")

        # Process session updates before modifying values
        self.config_session_id.update_session_configuration_value(
            vals=vals, product_tmpl_id=self.product_tmpl_id
        )

        vals = self._remove_dynamic_fields(vals)

        # Preserve existing value_ids and prevent unwanted resets
        if "value_ids" in vals:
            existing_values = self.value_ids.ids or []
            new_values = vals.get("value_ids", [(6, 0, [])])

            if isinstance(new_values, list) and new_values and isinstance(new_values[0], tuple):
                new_values = new_values[0][2] if isinstance(new_values[0][2], list) else []
            else:
                new_values = []

            merged_values = list(set(existing_values + new_values))

            _logger.info(f"Merging value_ids: Old={existing_values}, New={new_values}, Merged={merged_values}")
            vals["value_ids"] = [(6, 0, merged_values)]

        # Ensure laterality updates reference the correct configurator
        if "laterality_config_ids" in vals:
            existing_laterality = self.laterality_config_ids.ids or []
            new_laterality_values = vals.get("laterality_config_ids", [])

            # Safely extract `value_id` from valid tuples
            new_ids = [
                x[2]["value_id"] for x in new_laterality_values
                if isinstance(x, tuple) and len(x) > 2 and isinstance(x[2], dict) and x[2].get("value_id")
            ]

            merged_values = list(set(existing_laterality + new_ids))

            if not merged_values:
                _logger.warning(f"Preventing laterality reset! Retaining existing selections: {existing_laterality}")
                vals["laterality_config_ids"] = [(6, 0, existing_laterality)]
            else:
                _logger.info(f"Merging laterality_config_ids: Old={existing_laterality}, New={new_ids}, Merged={merged_values}")
                vals["laterality_config_ids"] = [(6, 0, merged_values)]

                # Ensure correct configurator ID references in laterality records
                for laterality in new_laterality_values:
                    if isinstance(laterality, tuple) and len(laterality) > 2 and isinstance(laterality[2], dict):
                        laterality[2]["configurator_id"] = correct_configurator_id  
                        laterality[2]["config_session_id"] = self.config_session_id.id  

                _logger.info(f"Corrected laterality_config_ids before writing: {vals['laterality_config_ids']}")

        _logger.info(f"[WRITE] Final processed vals before saving: {vals}")

        # Perform the actual write operation
        result = super().write(vals)
        _logger.info(f"[WRITE] Successfully saved values.")

        return result

    def action_next_step(self):
        """Proceed to the next step, ensuring the configurator still exists and attributes persist correctly."""

        _logger.info(f"[NEXT STEP] Attempting to proceed from Step: {self.state} (Configurator ID: {self.id})")

        # **Ensure the configurator still exists before proceeding**
        if not self.exists():
            _logger.error(f"[NEXT STEP] Configurator {self.id} is missing or was deleted! Attempting to restore session...")
            
            # Attempt to recover a session if one exists
            session = self.env["product.config.session"].search([("user_id", "=", self.env.uid)], limit=1)
            if session and session.configurator_id:
                self = session.configurator_id
                _logger.info(f"Restored Configurator ID: {self.id} from Session ID: {session.id}")
            else:
                raise ValidationError(_("The configurator session has been lost. Please restart the configuration."))

        wizard_action = self.with_context(allow_preset_selection=False).get_wizard_action(wizard=self)

        # **Ensure product template is set**
        if not self.product_tmpl_id:
            _logger.warning("No product template selected. Returning to wizard.")
            return wizard_action

        # **Ensure valid attributes are selected**
        if not self.config_session_id.value_ids:
            _logger.warning("No attributes selected! Assigning default values.")

            default_values = []
            for attr_line in self.product_tmpl_id.attribute_line_ids:
                if attr_line.value_ids:
                    if attr_line.multi:
                        default_values.extend(attr_line.value_ids.ids)  # Allow multiple selection
                    else:
                        default_values.append(attr_line.value_ids[0].id)  # Select only the first valid option

            if default_values:
                self.config_session_id.write({"value_ids": [(6, 0, list(set(default_values)))]})
                _logger.info(f"Assigned default attribute values: {default_values}")
            else:
                raise ValidationError(_("You must select at least one valid attribute to proceed."))

        # **Get Next Step**
        next_step_id = self.config_session_id.get_next_step(
            state=self.state,
            product_tmpl_id=self.product_tmpl_id,
            value_ids=self.config_session_id.value_ids,
            custom_value_ids=self.config_session_id.custom_value_ids,
        )

        if not next_step_id:
            return self.action_config_done()

        if isinstance(next_step_id, str):  # Convert string to record
            next_step = self.env["product.config.step"].search([("id", "=", int(next_step_id))], limit=1)
        else:
            next_step = next_step_id

        if not next_step.exists():
            raise ValidationError(_("The next configuration step is invalid or missing."))

        return self.open_step(next_step)

    def action_previous_step(self):
        """Moves back to the previous step in the configuration wizard."""
        
        _logger.info(f"[PREVIOUS STEP] Attempting to go back from Step: {self.state} (Configurator ID: {self.id})")

        wizard_action = self.with_context(
            wizard_id=self.id, view_cache=False, allow_preset_selection=False
        ).get_wizard_action(wizard=self)

        if wizard_action.get("context") and "is_action_previous" in wizard_action.get("context"):
            wizard_action["context"]["is_action_previous"] = True

        if not self.product_tmpl_id:
            _logger.warning(f"[PREVIOUS STEP] No product template associated with Configurator ID {self.id}. Returning to Select Template.")
            self.state = "select"
            return wizard_action

        cfg_step_lines = self.product_tmpl_id.config_step_line_ids

        if not cfg_step_lines:
            _logger.info(f"[PREVIOUS STEP] No defined steps in product template. Returning to Select Template.")
            self.state = "select"
            return wizard_action

        try:
            cfg_step_line_id = int(self.state)
            active_cfg_line = cfg_step_lines.filtered(lambda x: x.id == cfg_step_line_id)
        except ValueError:
            _logger.error(f"[PREVIOUS STEP] Invalid state '{self.state}'. Returning to Select Template.")
            self.state = "select"
            return wizard_action

        if not active_cfg_line:
            _logger.warning(f"[PREVIOUS STEP] No matching configuration step found for ID: {self.state}. Returning to Select Template.")
            self.state = "select"
            return wizard_action

        if not hasattr(self.config_session_id, "get_adjacent_steps"):
            _logger.error(f"[PREVIOUS STEP] `get_adjacent_steps()` is missing in `product.config.session`. Please define it.")
            return wizard_action

        adjacent_steps = self.config_session_id.get_adjacent_steps(active_step_line_id=active_cfg_line.id)

        if not adjacent_steps:
            _logger.warning(f"[PREVIOUS STEP] `get_adjacent_steps()` returned None. Returning to Select Template.")
            self.state = "select"
            return wizard_action

        previous_step = adjacent_steps.get("previous_step")

        if previous_step:
            _logger.info(f"[PREVIOUS STEP] Moving to previous step: {previous_step.id}")
            self.state = str(previous_step.id)
        else:
            _logger.info(f"[PREVIOUS STEP] No previous step found. Returning to Select Template.")
            self.state = "select"

        self.config_session_id.config_step = self.state
        return wizard_action

    def action_reset(self):
        """Reset the configurator by clearing selections and reloading."""
        _logger.info(f"[RESET] Resetting configurator: ID = {self.id}")

        session = self.config_session_id
        if not session.exists():
            _logger.warning(f"[RESET] Session {session.id} does not exist. Creating a new one.")
            session = self.env["product.config.session"].sudo().create_get_session(
                product_tmpl_id=self.product_tmpl_id.id
            )
            self.config_session_id = session.id

        _logger.info(f"[RESET] Using session ID: {session.id}")

        new_session = self.env["product.config.session"].sudo().create_get_session(
            product_tmpl_id=self.product_tmpl_id.id
        )
        _logger.info(f"[RESET] New session assigned: ID = {new_session.id}")

        sale_config_refs = self.env["product.configurator.sale"].search([("config_session_id", "=", session.id)])
        for sale_config in sale_config_refs:
            _logger.info(f"[RESET] Updating session reference for Configurator ID: {sale_config.id}")
            sale_config.sudo().write({"config_session_id": new_session.id})  

        if not self.env["product.configurator.sale"].search([("config_session_id", "=", session.id)]):
            try:
                session.unlink()
                _logger.info(f"[RESET] Successfully deleted session {session.id}")
            except Exception as e:
                _logger.error(f"[RESET ERROR] Failed to delete session {session.id}: {str(e)}")
                _logger.warning(f"[RESET] Keeping session {session.id} but resetting it instead.")
                session.write({"state": "draft"})  

        laterality = self.laterality or "bilateral"

        new_configurator = self.create({
            "config_session_id": new_session.id,
            "product_tmpl_id": self.product_tmpl_id.id,
            "laterality": laterality,
        })

        _logger.info(f"[RESET] New configurator created: ID = {new_configurator.id}")

        return {
            "type": "ir.actions.act_window",
            "res_model": "product.configurator",
            "view_mode": "form",
            "res_id": new_configurator.id,
            "target": "new",
            "context": self.env.context,
        }

    def action_copy_left_to_right(self):
        """Copy all left-side configurations to the right side in bilateral mode."""
        if self.laterality != "bilateral":
            raise ValidationError(_("This action is only available for Bilateral products."))

        left_side_values = self.laterality_config_ids.filtered(lambda x: x.side == "left")
        
        # Delete any existing right-side values
        self.laterality_config_ids = self.laterality_config_ids.filtered(lambda x: x.side != "right")

        # Copy left-side values to right-side
        copied_values = []
        for line in left_side_values:
            copied_values.append((0, 0, {
                "side": "right",
                "attribute_id": line.attribute_id.id,
                "value_id": line.value_id.id,
            }))

        self.write({
            "value_ids": [(6, 0, self.value_ids.ids)],
            "laterality_config_ids": [(6, 0, self.laterality_config_ids.ids)],"laterality_config_ids": copied_values})

    def action_copy_right_to_left(self):
        """Copy all right-side configurations to the left side in bilateral mode."""
        if self.laterality != "bilateral":
            raise ValidationError(_("This action is only available for Bilateral products."))

        right_side_values = self.laterality_config_ids.filtered(lambda x: x.side == "right")
        
        # Delete any existing left-side values
        self.laterality_config_ids = self.laterality_config_ids.filtered(lambda x: x.side != "left")

        # Copy right-side values to left-side
        copied_values = []
        for line in right_side_values:
            copied_values.append((0, 0, {
                "side": "left",
                "attribute_id": line.attribute_id.id,
                "value_id": line.value_id.id,
            }))

        self.write({
            "value_ids": [(6, 0, self.value_ids.ids)],
            "laterality_config_ids": [(6, 0, self.laterality_config_ids.ids)],"laterality_config_ids": copied_values})

    def get_wizard_action(self, view_cache=False, wizard=None):
        """Return action of wizard
        :param view_cache: Boolean (True/False)
        :param wizard: recordset of product.configurator
        :returns : dictionary
        """
        ctx = self.env.context.copy()
        ctx.update(
            {
                "view_cache": view_cache,
                "differentiator": ctx.get("differentiator", 1) + 1,
                "is_product_configurator": True,
                "is_action_previous": False,
                "is_preset": self.product_preset_id and True or False,
            }
        )
        if wizard:
            ctx.update({"wizard_id": wizard.id, "wizard_id_view_ref": wizard.id})
        wizard_action = {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "name": "Configure Product",
            "views": [
                [
                    self.env.ref("pod_odoo_master.product_configurator_form").id,
                    "form",
                ]
            ],
            "view_mode": "form",
            "context": ctx,
            "target": "new",
        }
        if wizard:
            wizard_action.update({"res_id": wizard.id})
        if self and not self.state:
            self.state = "select"
        return wizard_action
    
    def open_step(self, step):
        """Open wizard step `step` and ensure UI updates correctly."""
        _logger.info(f"[OPEN STEP] Transitioning to Step: {step}")

        # Ensure step is an object
        if isinstance(step, str):
            step = self.env["product.config.step"].search([("id", "=", int(step))], limit=1)

        if not step.exists():
            _logger.warning(f" [OPEN STEP ERROR] Invalid Step ID: {step}")
            return self.with_context(allow_preset_selection=False).get_wizard_action(wizard=self)

        _logger.info(f" [OPEN STEP] Successfully transitioning to Step: {step.id}")

        #  Save the new step to session and wizard state
        self.write({"state": str(step.id)})
        self.config_session_id.config_step = str(step.id)

        #  Force a UI refresh and reload the wizard view
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
            "context": dict(self.env.context, allow_preset_selection=False, view_cache=False, wizard_id_view_ref=self.id),
        }

    def web_save(self, vals, specification=None):
        """Ensure laterality selections persist and prevent duplicate laterality values."""

        _logger.info(f"🛠 [WEB_SAVE] Called with vals: {vals} | specification: {specification}")

        # **Ensure configurator exists**
        if not self.exists():
            _logger.error(f"[WEB_SAVE] Configurator {self.id} is missing! Attempting to restore session...")
            return self._handle_missing_configurator()

        # **Prevent automatic product template selection**
        if "product_tmpl_id" in vals and not vals["product_tmpl_id"]:
            _logger.warning("Preventing automatic product template selection.")
            del vals["product_tmpl_id"]

        # **Ensure valid fields are passed**
        valid_fields = self.fields_get().keys()
        invalid_fields = [key for key in vals if key not in valid_fields]

        if invalid_fields:
            _logger.warning(f"[WEB_SAVE] Removing invalid fields before saving: {invalid_fields}")
            for field in invalid_fields:
                del vals[field]

        # **Remove dynamically injected bilateral fields**
        dynamic_fields_to_remove = [key for key in vals if key.startswith("__left_attribute_") or key.startswith("__right_attribute_")]
        for field in dynamic_fields_to_remove:
            vals.pop(field, None)

        if dynamic_fields_to_remove:
            _logger.info(f"[WEB_SAVE] Removed dynamic fields before saving: {dynamic_fields_to_remove}")

        # **Ensure Laterality is Handled Properly**
        if "laterality_config_ids" in vals:
            new_laterality_entries = vals["laterality_config_ids"]

            # Extract only new values
            new_laterality_dict = {
                (entry[2]["side"], entry[2]["attribute_id"]): entry[2]["value_id"]
                for entry in new_laterality_entries if entry[0] == 0
            }

            # Fetch existing laterality records
            existing_laterality = {
                (line.side, line.attribute_id.id): line.value_id.id
                for line in self.laterality_config_ids
            }

            # Find duplicates (same side + attribute)
            duplicate_entries = set(existing_laterality.keys()) & set(new_laterality_dict.keys())

            if duplicate_entries:
                _logger.warning(f"Removing duplicate laterality entries: {duplicate_entries}")

                # Remove conflicting laterality values before inserting new ones
                vals["laterality_config_ids"] = [(3, line.id, 0) for line in self.laterality_config_ids
                                                if (line.side, line.attribute_id.id) in duplicate_entries]

            # Add new laterality values
            vals["laterality_config_ids"] += new_laterality_entries

        elif self.laterality_config_ids:
            _logger.info("[WEB_SAVE] Retaining existing laterality configuration.")
            vals["laterality_config_ids"] = [(6, 0, self.laterality_config_ids.ids)]

        else:
            _logger.warning("No laterality values found. Applying default selections.")
            vals["laterality_config_ids"] = self._get_default_laterality_values()

        # **Save data**
        self.write(vals)
        _logger.info(f"[WEB_SAVE] Successfully saved values: {vals}")

        return super().web_save(vals, specification)

    def web_read(self, specification):
        values_list = super().web_read(specification)
        for field_name, field_spec in specification.items():
            field = self._fields.get(field_name)
            if field is None:
                if (
                    field_spec.get("context")
                    and "is_m2m" in field_spec.get("context")
                    and field_spec.get("context").get("is_m2m")
                ):
                    if not field_spec:
                        continue

                    co_records = self.env["product.attribute.value"]
                    if "order" in field_spec and field_spec["order"]:
                        co_records = co_records.search(
                            [("id", "in", co_records.ids)], order=field_spec["order"]
                        )
                        order_key = {
                            co_record.id: index
                            for index, co_record in enumerate(co_records)
                        }
                        for values in values_list:
                            # filter out inaccessible corecords in case of "cache pollution"
                            values[field_name] = [
                                id_ for id_ in values[field_name] if id_ in order_key
                            ]
                            values[field_name] = sorted(
                                values[field_name], key=order_key.__getitem__
                            )

                    if "context" in field_spec:
                        co_records = co_records.with_context(**field_spec["context"])
                    if "fields" in field_spec:
                        if field_spec.get("limit") is not None:
                            limit = field_spec["limit"]
                            ids_to_read = OrderedSet(
                                id_
                                for values in values_list
                                for id_ in values[field_name][:limit]
                            )
                            co_records = co_records.browse(ids_to_read)
                        x2many_data = {
                            vals["id"]: vals
                            for vals in co_records.web_read(field_spec["fields"])
                        }
                        for values in values_list:
                            if values[field_name]:
                                attribute_ids = self.env[
                                    "product.attribute.value"
                                ].browse(values[field_name])
                                x2many_data = {
                                    vals["id"]: vals
                                    for vals in attribute_ids.web_read(
                                        field_spec["fields"]
                                    )
                                }
                                values[field_name] = [
                                    x2many_data.get(id_) or {"id": id_}
                                    for id_ in x2many_data
                                ]
                            else:
                                values[field_name] = [
                                    x2many_data.get(id_) or {"id": id_}
                                    for id_ in x2many_data
                                ]
        return values_list

    def action_config_done(self):
        """Finalize the configuration, ensuring all selections persist."""
        
        _logger.info(f"[ACTION_CONFIG_DONE] Finalizing configuration for Configurator ID {self.id}")

        # Log Bilateral Attribute Selections Before Saving
        _logger.info(f"[ACTION_CONFIG_DONE] Checking Bilateral Attributes: {self.laterality_config_ids}")

        # Identify Missing Left/Right Attributes
        missing_left = not self.laterality_config_ids.filtered(lambda x: x.side == "left")
        missing_right = not self.laterality_config_ids.filtered(lambda x: x.side == "right")

        if missing_left or missing_right:
            _logger.warning(f"[ACTION_CONFIG_DONE] Missing Laterality Selections: "
                            f"{'Left' if missing_left else ''} {'Right' if missing_right else ''}")

        if not self.laterality_config_ids:
            _logger.warning("[ACTION_CONFIG_DONE] No laterality selections found! They might have been removed.")

            # Ensure Default Laterality Selections are Added
            default_laterality_values = self._get_default_laterality_values()

            if default_laterality_values:
                _logger.info(f"[ACTION_CONFIG_DONE] Assigning Default Laterality Values: {default_laterality_values}")
                self.write({"laterality_config_ids": default_laterality_values})
            else:
                _logger.error("[ACTION_CONFIG_DONE] No valid laterality values found. Cannot proceed.")
                raise ValidationError("Cannot finalize configuration without laterality selections.")

        # Ensure all values are properly saved before finalizing
        _logger.info("[ACTION_CONFIG_DONE] Saving current selections before finalizing...")
        self.web_save(self.read())  # Save all current data

        # Check if Any Incomplete Steps Need to be Opened
        step_to_open = self.config_session_id.check_and_open_incomplete_step()
        if step_to_open:
            return self.open_step(step_to_open)

        # Ensure Product Selection Before Finalizing
        product_id = self.product_id or self._derive_product_from_laterality()
        if not product_id:
            _logger.error("[ACTION_CONFIG_DONE] No product found. Cannot finalize.")
            raise ValidationError("Cannot finalize configuration without a product.")

        _logger.info(f"[ACTION_CONFIG_DONE] Derived Product: {product_id} ({self.env['product.product'].browse(product_id).display_name})")

        # Assign Product and Confirm Session
        self.write({"product_id": product_id})
        self.config_session_id.action_confirm()

        _logger.info(f"[ACTION_CONFIG_DONE] Configuration finalized successfully!")

        return {"type": "ir.actions.act_window_close"}

    def _derive_product_from_laterality(self):
        """Derive a product from laterality selections if product_id is missing."""
        _logger.info("Deriving product from laterality configurations...")

        left_values = self.laterality_config_ids.filtered(lambda x: x.side == "left").mapped("value_id")
        right_values = self.laterality_config_ids.filtered(lambda x: x.side == "right").mapped("value_id")

        if not left_values and not right_values:
            _logger.warning(" No laterality configurations found. Cannot derive product.")
            return None

        _logger.info(f" Left Values: {left_values.ids} | Right Values: {right_values.ids}")

        if not self.product_tmpl_id:
            _logger.error(" Product Template is missing. Cannot derive product.")
            return None

        _logger.info(f" Using Product Template: {self.product_tmpl_id.id} ({self.product_tmpl_id.name})")

        product_domain = [
            ("product_tmpl_id", "=", self.product_tmpl_id.id),
            ("attribute_value_ids", "in", left_values.ids + right_values.ids)
        ]
        matching_products = self.env["product.product"].search(product_domain, limit=1)

        if matching_products:
            _logger.info(f" Derived Product: {matching_products.id} ({matching_products.display_name})")
            return matching_products.id

        _logger.warning(" No matching product found for given laterality configuration.")

        if self.product_tmpl_id.product_variant_id:
            _logger.info(f" Using Default Product Variant: {self.product_tmpl_id.product_variant_id.id}")
            return self.product_tmpl_id.product_variant_id.id

        return None


class ProductConfigurationTemplate(models.Model):
    _name = "product.configurator.template"
    _description = "Saved Product Configuration Template"

    name = fields.Char("Template Name", required=True)
    product_id = fields.Many2one("product.product", string="Product", required=True)
    laterality = fields.Selection(selection=LATERALITY_OPTIONS, string="Laterality", required=True)
    laterality_config_ids = fields.One2many("product.configurator.laterality.line", "template_id", string="Configuration Details")

    def action_save_template(self):
        self.ensure_one()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Success",
                "message": "Configuration template saved successfully.",
                "sticky": False,
            },
        }


class ConfiguratorLateralityLine(models.Model):
    _name = "product.configurator.laterality.line"
    _description = "Laterality Configurations"
    _order = "configurator_id, side"
    _sql_constraints = [
        ("unique_config_laterality", "unique(configurator_id, side, attribute_id)", "Each attribute can only have one laterality value per side.")
    ]

    configurator_id = fields.Many2one(
        "product.configurator.sale",  # Ensure laterality is tied to sales
        string="Sale Configurator",
        required=True,
        ondelete="cascade",
        index=True,
    )


    config_session_id = fields.Many2one( 
        "product.config.session",
        string="Configuration Session",
        ondelete="cascade",
        index=True,  # Index for better query performance
    )

    sale_order_line_id = fields.Many2one(
        "sale.order.line",
        string="Sale Order Line",
        ondelete="cascade",
        index=True,
    )

    template_id = fields.Many2one(
        "product.configurator.template",
        string="Configuration Template",
        ondelete="set null"
    )

    side = fields.Selection([("left", "Left"), ("right", "Right")], required=True)
    attribute_id = fields.Many2one("product.attribute", required=True, index=True)
    value_id = fields.Many2one("product.attribute.value", required=True, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure configurator ID is set before creating records."""
        for vals in vals_list:
            if not vals.get("configurator_id"):
                _logger.error(f"[LATERALITY] Attempted to create a record with NULL configurator_id! Vals: {vals}")
                raise ValidationError("Laterality record must have a valid Configurator ID.")

        _logger.info(f"[LATERALITY] Creating laterality records: {vals_list}")
        return super().create(vals_list)
    
    def write(self, vals):
        """Log updates to laterality selections."""
        _logger.info(f"[LATERALITY] Updating Laterality Config ID {self.ids} with {vals}")
        return super().write(vals)

    def unlink(self):
        """Prevent accidental deletion if linked to an order or template."""
        if self.filtered(lambda r: r.sale_order_line_id or r.template_id):
            raise ValidationError("Cannot delete laterality configurations linked to an order or template.")
        return super().unlink()


class ProductConfiguratorSale(models.Model):
    _name = "product.configurator.sale"
    _inherit = "product.configurator"
    _description = "Product Configurator Sale"

    order_id = fields.Many2one(comodel_name="sale.order", required=True, readonly=True)
    order_line_id = fields.Many2one(comodel_name="sale.order.line", readonly=True)

    domain_attr_ids = fields.Many2many(
        "product.attribute.value",
        "domain_attrs_values_sale_rel",
        "wiz_id",
        "attribute_id",
        string="Domain",
    )

    domain_attr_2_ids = fields.Many2many(
        "product.attribute.value",
        "domain_attrs_2_values_sale_rel",
        "wiz_id",
        "attribute_id",
        string="Domain",
    )

    def _get_order_line_vals(self):
        """Prepare order line values before adding/updating sale order."""
        product = self.env["product.product"].browse(self.product_id.id)
        line_vals = {
            "product_id": self.product_id.id,
            "order_id": self.order_id.id,
            "config_session_id": self.config_session_id.id,
            "name": product._get_mako_tmpl_name(),
            "customer_lead": product.sale_delay,
        }

        line = self.env["sale.order.line"].new(line_vals)
        onchange_fields = ["price_unit", "product_uom", "tax_id"]
        for field in onchange_fields:
            line_vals[field] = line._fields[field].convert_to_write(line[field], line)

        return line_vals

    def action_config_done(self):
        """Finalize Sale Order Configuration and Update Order Line."""
        _logger.info(f"Finalizing Configuration for Order ID {self.order_id.id}")

        if not self.product_id:
            _logger.warning("No product found, deriving from laterality configuration.")
            product_id = self._derive_product_from_laterality()

            if not product_id:
                _logger.error("Product derivation failed. Cannot finalize configuration.")
                raise ValidationError(_("Cannot finalize configuration without a product."))

            _logger.info(f"Assigning Derived Product: {product_id}")
            self.write({"product_id": product_id})

        if not self.laterality_config_ids:
            _logger.warning("No laterality configurations found. Assigning defaults.")
            default_laterality_values = self._get_default_laterality_values()
            self.write({"laterality_config_ids": default_laterality_values})

        # Call parent method to handle confirmation
        res = super().action_config_done()
        if res.get("res_model") == self._name:
            return res

        # Prepare sale order line updates
        order_line_vals = self._get_order_line_vals()
        order_line_obj = self.env["sale.order.line"]
        cfg_session = self.config_session_id
        fields_spec = cfg_session.get_onchange_specifications(model="sale.order.line")
        fields_spec = {k: v for k, v in fields_spec.items() if k in order_line_vals and k != "tax_id"}

        # Apply onchange updates
        updates = order_line_obj.onchange(order_line_vals, ["product_id"], fields_spec)
        values = updates.get("value", {})
        values = cfg_session.get_vals_to_write(values=values, model="sale.order.line")
        values.update(order_line_vals)

        # Create or update sale order line
        if self.order_line_id:
            self.order_line_id.write(values)
        else:
            self.order_id.write({"order_line": [(0, 0, values)]})

        return res
    
    @api.model_create_multi
    def create(self, vals_list):
        """Ensure configurator is fully created, properly initialized, and linked to a sale order."""
        
        for vals in vals_list:
            product_tmpl_id = vals.get("product_tmpl_id")

            # Ensure `order_id` is set
            order_id = vals.get("order_id") or self.env.context.get("default_order_id")
            if not order_id:
                raise ValidationError(_("A sale order must be linked to the configurator."))

            vals["order_id"] = order_id  # Assign the order ID

            # Allow configurator to be created without a product template
            if not product_tmpl_id:
                _logger.warning("Creating configurator without a product template. Defaulting to 'select' state.")
                vals["state"] = "select"  # Ensure configurator starts in 'select' step
                vals["product_tmpl_id"] = False  # Explicitly set template to False
                vals["attribute_line_ids"] = []  # Ensure no attributes are assigned
            else:
                # Fetch product template
                product_template = self.env["product.template"].browse(product_tmpl_id)

                # Assign attributes from product template
                vals["attribute_line_ids"] = [(6, 0, product_template.attribute_line_ids.ids)]

                # Ensure configurator session exists
                session = self.env["product.config.session"].sudo().create_get_session(product_tmpl_id=product_tmpl_id)
                vals["config_session_id"] = session.id

                # Assign values from session if available
                if session.value_ids:
                    vals["value_ids"] = [(6, 0, session.value_ids.ids)]

            vals["user_id"] = self.env.uid  # Ensure user ID is set

            # Handle custom values if creating from a sale order line
            if self.env.context.get("default_order_line_id"):
                sale_line = self.env["sale.order.line"].browse(self.env.context["default_order_line_id"])
                if sale_line.custom_value_ids:
                    vals["custom_value_ids"] = self._get_custom_values(sale_line.config_session_id)

        records = super().create(vals_list)

        _logger.info(f"Configurator Created: {records.ids} with Order ID {order_id}")
        _logger.info(f"Configurator Created: {records.ids} with Attributes: {records.attribute_line_ids}")

        return records

    def _get_default_laterality_values(self):
        """Generate default laterality values based on the selected product template and laterality setting."""
        _logger.info("[DEFAULT LATERALITY] Generating default laterality values...")

        if not self.product_tmpl_id:
            _logger.warning("No product template found! Cannot generate laterality values.")
            return []

        default_laterality_values = []

        for attr in self.product_tmpl_id.attribute_line_ids:
            if attr.value_ids:
                if self.laterality == "bilateral":
                    # Create both left & right values
                    default_laterality_values.extend([
                        (0, 0, {"side": "left", "attribute_id": attr.id, "value_id": attr.value_ids[0].id}),
                        (0, 0, {"side": "right", "attribute_id": attr.id, "value_id": attr.value_ids[0].id}),
                    ])
                else:
                    # Single entry for unilateral (left or right)
                    default_laterality_values.append(
                        (0, 0, {"side": self.laterality, "attribute_id": attr.id, "value_id": attr.value_ids[0].id})
                    )

        if default_laterality_values:
            _logger.info(f"[DEFAULT LATERALITY] Assigned: {default_laterality_values}")
        else:
            _logger.warning("No default laterality values could be assigned.")

        return default_laterality_values

    def _get_custom_values(self, session):
        """Extract custom values for configurator persistence."""
        return [(5,)] + [
            (0, 0, {
                "attribute_id": value_custom.attribute_id.id,
                "value": value_custom.value,
                "attachment_ids": [(4, attach.id) for attach in value_custom.attachment_ids],
            })
            for value_custom in session.custom_value_ids
        ]



class ProductConfiguratorMrp(models.Model):
    _name = "product.configurator.mrp"
    _inherit = "product.configurator"
    _description = "Product Configurator MRP"

    order_id = fields.Many2one(comodel_name="mrp.production", required=True, ondelete="cascade")

    custom_laterality_step_ids = fields.Many2many(
        "product.config.step",
        relation="custom_laterality_step_mrp_rel",
        column1="mrp_configurator_id",
        column2="step_id",
        string="Custom Laterality Steps",
    )

    domain_attr_ids = fields.Many2many(
        "product.attribute.value",
        "domain_attrs_mrp_configurator_rel",
        "wiz_id",
        "attribute_id",
        string="Domain",
    )

    domain_attr_2_ids = fields.Many2many(
        "product.attribute.value",
        "domain_attrs_mrp_configurator_2_rel",
        "wiz_id",
        "attribute_id",
        string="Domain 2",
    )

    def action_config_done(self):
        """Finalize the MRP configuration and create product variants."""
        _logger.info(f"🛠 Finalizing MRP Configuration for Order ID {self.order_id.id}")

        step_to_open = self.config_session_id.check_and_open_incomplete_step()
        if step_to_open:
            return self.open_step(step_to_open)

        self.config_session_id.action_confirm()

        # **Handle Bilateral Laterality Separately**
        if self.laterality == "bilateral":
            return self._handle_bilateral_configuration()

        # **Handle Single-Side Laterality**
        return self._finalize_single_side_configuration()

    def _handle_bilateral_configuration(self):
        """Create separate product variants for left and right sides in a bilateral configuration."""
        _logger.info("Processing Bilateral Configuration")

        left_values = self.laterality_config_ids.filtered(lambda x: x.side == "left").mapped("value_id").ids
        right_values = self.laterality_config_ids.filtered(lambda x: x.side == "right").mapped("value_id").ids

        product_left = self.config_session_id.create_get_variant(left_values, laterality="left")
        product_right = self.config_session_id.create_get_variant(right_values, laterality="right")

        if not product_left or not product_right:
            _logger.error("Bilateral Product Configuration Failed. Could not generate product variants.")
            raise ValidationError(_("Bilateral configuration failed: Could not generate product variants."))

        _logger.info(f"Created Bilateral Products: Left - {product_left.id}, Right - {product_right.id}")

        return {
            "type": "ir.actions.act_window",
            "name": _("Bilateral Configuration"),
            "res_model": "product.product",
            "view_mode": "form",
            "res_ids": [product_left.id, product_right.id],
        }

    def _finalize_single_side_configuration(self):
        """Create a product variant for single-side laterality."""
        _logger.info(f"Finalizing Single-Side Configuration for Laterality: {self.laterality}")

        variant = self.config_session_id.create_get_variant(self.value_ids.ids, laterality=self.laterality)

        if variant and variant.exists():
            _logger.info(f"Created Product Variant: {variant.id} ({variant.display_name})")
            return {
                "type": "ir.actions.act_window",
                "res_model": "product.product",
                "name": _("Product Variant"),
                "view_mode": "form",
                "res_id": variant.id,
            }

        _logger.error("Configuration Failed: Could Not Generate Product.")
        raise ValidationError(_("Configuration failed: Could not generate product."))

    def action_previous_step(self):
        """Navigate back while preserving selections."""
        _logger.info(f"Moving to Previous Step from: {self.state}")

        wizard_action = self.get_wizard_action()
        cfg_step_lines = self.product_tmpl_id.config_step_line_ids

        if not cfg_step_lines:
            self.state = "select"
            return wizard_action

        try:
            cfg_step_line_id = int(self.state)
            active_cfg_line_id = cfg_step_lines.filtered(lambda x: x.id == cfg_step_line_id).id
        except ValueError:
            active_cfg_line_id = None

        previous_step = self.config_session_id.get_adjacent_steps(active_step_line_id=active_cfg_line_id).get("previous_step")
        self.state = str(previous_step.id) if previous_step else "select"
        self.config_session_id.config_step = self.state

        return wizard_action

