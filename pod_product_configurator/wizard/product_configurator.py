import logging

from lxml import etree

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command
from odoo.tools import frozendict

from odoo.addons.base.models.ir_model import FIELD_TYPES

_logger = logging.getLogger(__name__)


class FreeSelection(fields.Selection):
    def convert_to_cache(self, value, record, validate=True):
        return super().convert_to_cache(value=value, record=record, validate=False)


class ProductConfigurator(models.TransientModel):
    _name = "product.configurator"
    _inherits = {"product.config.session": "config_session_id"}
    _description = "Product configuration Wizard"

    customize_step_ids = fields.Many2many(
        comodel_name="product.config.step.line",
        relation="product_configurator_customize_step_rel",
        column1="wizard_id",
        column2="step_id",
        string="Customized Steps",
        help="Steps where user opted to configure left and right independently",
    )

    def toggle_customize_step(self):
        self.ensure_one()
        step_id = int(self.env.context.get("step_id"))

        _logger.info(f"[toggle_customize_step] Step ID toggled: {step_id} | Before: {self.customize_step_ids.ids}")

        if step_id in self.customize_step_ids.ids:
            self.customize_step_ids = [(3, step_id)]  # Remove
        else:
            self.customize_step_ids = [(4, step_id)]  # Add

        _logger.info(f"[toggle_customize_step] Updated customize_step_ids: {self.customize_step_ids.ids}")
        _logger.info(f"[toggle_customize_step] Wizard {self.id} now has customize_step_ids: {self.customize_step_ids.ids}")

        # 🚨 Invalidate cached dynamic fields/view
        self.env['ir.ui.view'].clear_caches()

        # Reload view by returning the wizard action
        return self.with_context(view_cache=False).get_wizard_action(wizard=self)



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
        fields in the wizard. Any module extending this functionality should
        override this method to add all extra prefixes"""
        return {
            "field_prefix": "__attribute_",
            "custom_field_prefix": "__custom_",
            "domain_field_prefix": "__domain_",
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

    @api.depends("product_tmpl_id", "product_tmpl_id.attribute_line_ids")
    def _compute_attr_lines(self):
        """Use compute method instead of related due to increased flexibility
        and strange behavior when attempting to have a related field point
        to computed values"""
        for configurator in self:
            attribute_lines = configurator.product_tmpl_id.attribute_line_ids
            configurator.attribute_line_ids = attribute_lines

    # TODO: We could use a m2o instead of a monkeypatched select field but
    # adding new steps should be trivial via custom development
    def get_state_selection(self):
        """Get the states of the wizard using standard values and optional
        configuration steps set on the product.template via
        config_step_line_ids"""
        steps = [("select", "Select Template")]

        # Get the wizard id from context set via action_next_step method
        wizard_id = self._find_wizard_context()
        wiz = self.browse(wizard_id).exists()

        if not wiz:
            return steps

        open_lines = wiz.config_session_id.get_open_step_lines()

        if open_lines:
            open_steps = open_lines.mapped(lambda x: (str(x.id), x.config_step_id.name))
            steps = open_steps if wiz.product_id else steps + open_steps
        else:
            steps.append(("configure", "Configure"))
        return steps

    @api.onchange("product_tmpl_id")
    def onchange_product_tmpl(self):
        """set the preset_id if exist in session"""
        template = self.product_tmpl_id

        self.config_step_ids = template.config_step_line_ids.mapped("config_step_id")

        # Set product preset if exist in session
        if template:
            session = self.env["product.config.session"].search_session(
                product_tmpl_id=template.id
            )
            self.product_preset_id = session.product_preset_id

        if self.value_ids:
            # TODO: Add confirmation button an delete cfg session
            raise UserError(
                _(
                    "Changing the product template while having an active "
                    "configuration will erase reset/clear all values"
                )
            )

    def get_onchange_domains(
        self,
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

            # get available values
            attribute_line_values = line._configurator_value_ids()
            avail_ids = config_session_id.values_available(
                check_val_ids=attribute_line_values.ids,
                value_ids=check_avail_ids,
                product_template_attribute_line_id=line.id,
            )

            domains[field_name] = [("id", "in", avail_ids)]
            check_avail_ids = list(
                set(check_avail_ids) - (set(line.value_ids.ids) - set(avail_ids))
            )
        return domains

    def get_onchange_vals(self, cfg_val_ids, config_session_id=None):
        """Onchange hook to add / modify returned values by onchange method"""
        if not config_session_id:
            config_session_id = self.config_session_id

        # Remove None from cfg_val_ids if exist
        cfg_val_ids = [val for val in cfg_val_ids if val]

        product_img = config_session_id.get_config_image(cfg_val_ids)
        price = config_session_id.get_cfg_price(cfg_val_ids)
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
        values=None,
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
        # List to store multi-value IDs
        available_val_ids_m2m = []
        for k, v in dynamic_fields.items():
            if not v:
                continue
            available_val_ids = domains[k][0][2]
            # Get all value_ids linked to the current config session
            value_ids = self.config_session_id.value_ids
            # Filter attribute lines for multi-select attributes that match IDs
            # in value_ids
            attribute_line_ids = self.product_tmpl_id.attribute_line_ids.filtered(
                lambda line, value_ids=value_ids: line.multi
                and line.attribute_id.id in value_ids.mapped("attribute_id").ids
            )
            # Get multi-value IDs that match attribute lines
            # Filter the `multi_value_ids` associated with attributes in
            # `attribute_line_ids`
            multi_value_ids = value_ids.filtered(
                lambda value,
                attribute_line_ids=attribute_line_ids: value.attribute_id.id
                in attribute_line_ids.mapped("attribute_id").ids
            )

            # Retrieve IDs of available multi-value options
            available_val_ids_m2m = multi_value_ids.ids

            # Process values for the current attribute field
            if isinstance(v, list):
                for sub_value in v:
                    if sub_value[0] == Command.UNLINK:
                        if sub_value[1] in available_val_ids_m2m:
                            available_val_ids_m2m.remove(sub_value[1])
                    elif sub_value[0] == Command.LINK:
                        if sub_value[1] not in available_val_ids_m2m:
                            available_val_ids_m2m.append(sub_value[1])
                    elif sub_value[0] == Command.SET:
                        available_val_ids_m2m = sub_value[2]

                # Update dynamic fields and set `vals` with modified multi-value IDs
                dynamic_fields.update({k: available_val_ids_m2m})
                vals[k] = [[Command.SET, 0, available_val_ids_m2m]]

            elif v not in available_val_ids:
                # Handle single values not in available IDs
                dynamic_fields.update({k: None})
                vals[k] = None
            else:
                # Use the single value if it exists in available IDs
                vals[k] = v

        field_prefix = self._prefixes.get("field_prefix")
        # List of attributes to remove from value_ids as they are currently changed
        attributes_to_consider_removal = [
            int(field.split(field_prefix)[1]) for field in vals if field_prefix in field
        ]
        filtered_value_ids = self.value_ids.filtered(
            lambda val: val.attribute_id.id not in attributes_to_consider_removal
        ).ids
        final_config_values = list(filtered_value_ids + list(dynamic_fields.values()))
        vals.update(self.get_onchange_vals(final_config_values, config_session_id))
        # To solve the Multi selection problem removing extra []
        if "value_ids" in vals:
            val_ids = vals["value_ids"][0]
            vals["value_ids"] = [[val_ids[0], val_ids[1], tools.flatten(val_ids[2])]]
        return vals

    def apply_onchange_values(self, values, field_names, field_onchange):
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
        if values.get("value_ids", []):
            cfg_vals = self.env["product.attribute.value"].browse(
                values.get("value_ids", [])[0][2]
            )
        if not cfg_vals:
            cfg_vals = self.value_ids

        field_prefix = self._prefixes.get("field_prefix")
        custom_field_prefix = self._prefixes.get("custom_field_prefix")
        domain_field_prefix = self._prefixes.get("domain_field_prefix")
        local_field_name = field_names and field_names[0].startswith(field_prefix)
        local_custom_field = field_names and field_names[0].startswith(
            custom_field_prefix
        )
        local_domain_prefix = field_names and field_names[0].startswith(
            domain_field_prefix
        )
        if not local_field_name and not local_custom_field and not local_domain_prefix:
            values = self._remove_dynamic_fields(values)
            field_onchange = self._remove_dynamic_fields(field_onchange)
            res = super().onchange(values, field_names, field_onchange)
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
            # if isinstance(v, list):
            #    dynamic_fields[k] = v[0][2]

            line_attributes = cfg_step.attribute_line_ids.mapped("attribute_id")
            if not cfg_step or attr_id in line_attributes.ids:
                view_attribute_ids.add(attr_id)
            else:
                continue
            if not v:
                continue
            if isinstance(v, list):
                if v[0][0] == Command.SET:
                    view_val_ids |= set(v[0][2])
                else:
                    view_val_ids |= {a[1] for a in v}
            elif isinstance(v, int):
                view_val_ids.add(v)

        # Clear all DB values belonging to attributes changed in the wizard
        cfg_vals = cfg_vals.filtered(
            lambda v: v.attribute_id.id not in view_attribute_ids
        )
        # Combine database values with wizard values_available
        cfg_val_ids = cfg_vals.ids + list(view_val_ids)

        domains = self.get_onchange_domains(
            cfg_val_ids, product_tmpl_id, config_session_id
        )

        vals = self.get_form_vals(
            dynamic_fields=dynamic_fields,
            domains=domains,
            product_tmpl_id=product_tmpl_id,
            config_session_id=config_session_id,
            values=values,
        )
        vals.update(self._transform_onchange_domain_field_vals(domains))
        return {"value": vals, "domain": domains}

    def _transform_onchange_domain_field_vals(self, domains):
        vals = {}
        for field, value in domains.items():
            domain_field = field.replace("attribute", "domain")
            vals[domain_field] = value
        return vals

    def onchange(self, values: dict, field_names: list[str], fields_spec: dict):
        """Override the onchange wrapper to return domains to dynamic
        fields as onchange isn't triggered for non-db fields
        """
        onchange_values = self.apply_onchange_values(
            values=values, field_names=field_names, field_onchange=fields_spec
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
        ondelete="cascade",
        comodel_name="product.config.session",
        string="Configuration Session",
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
    
    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields=allfields, attributes=attributes)

        wizard_id = self._find_wizard_context()
        if not wizard_id:
            _logger.debug("[fields_get] No wizard_id found in context.")
            return res

        wiz = self.browse(wizard_id)
        wiz._invalidate_cache()  
        wiz.read()

        _logger.info(
            f"[fields_get] Generating dynamic fields for Wizard ID: {wiz.id} | "
            f"Laterality: {wiz.laterality} | Customized Step IDs: {wiz.customize_step_ids.ids}"
        )            

        laterality = wiz.laterality
        customized_step_ids = set(wiz.customize_step_ids.ids)

        _logger.info(f"[fields_get] Generating dynamic fields for Wizard ID: {wiz.id} | Laterality: {laterality} | Customized Step IDs: {customized_step_ids}")

        field_prefix = self._prefixes.get("field_prefix")
        custom_field_prefix = self._prefixes.get("custom_field_prefix")
        domain_field_prefix = self._prefixes.get("domain_field_prefix")

        default_attrs = self.get_field_default_attrs()
        config_session_obj = self.env["product.config.session"]
        custom_val = config_session_obj.get_custom_value_id()

        for line in wiz.product_tmpl_id.attribute_line_ids:
            attribute = line.attribute_id
            attr_id = attribute.id
            attr_name = attribute.name
            is_multi = line.multi
            is_custom = line.custom
            attr_values = line.value_ids.ids
            attr_values = wiz.config_session_id.values_available(check_val_ids=attr_values)

            if is_custom:
                attr_values.append(custom_val.id)

            _logger.debug(f"[fields_get] Attribute: {attr_name} (ID: {attr_id}) | Multi: {is_multi} | Custom: {is_custom} | Values: {attr_values}")

            def create_field_dict(suffix=None, domain_field=None):
                return dict(
                    default_attrs,
                    type="many2many" if is_multi else "many2one",
                    string=f"{attr_name} ({suffix})" if suffix else attr_name,
                    relation="product.attribute.value",
                    domain=f"[('id', 'in', {attr_values})]" if not domain_field else domain_field,
                )

            def create_custom_field_dict(suffix=None, custom_type=None):
                ftype = "char"
                if custom_type:
                    if custom_type == "integer":
                        ftype = "integer"
                    elif custom_type in dict(FIELD_TYPES):
                        ftype = custom_type
                return dict(
                    default_attrs,
                    string=f"Custom ({suffix})" if suffix else "Custom",
                    type=ftype,
                )

            # Add hidden domain field
            domain_field_name = f"{domain_field_prefix}{attr_id}"
            res[domain_field_name] = dict(
                default_attrs,
                type="binary",
                string=f"Domain {attr_name}",
                change_default=True,
            )

            
            step_lines = wiz.product_tmpl_id.config_step_line_ids.filtered(
                lambda step: line.id in step.attribute_line_ids.ids
            )
            step_ids = set(step_lines.mapped("id"))
            is_customized_step = bool(step_ids & customized_step_ids)

            _logger.debug(f"[fields_get] Step IDs for attr {attr_id}: {step_ids} | Customized Steps: {customized_step_ids} | Is customized: {is_customized_step}")

            if laterality in ("left", "right"):
                field_name = f"{field_prefix}{attr_id}"
                res[field_name] = create_field_dict(domain_field=domain_field_name)
                if is_custom:
                    res[f"{custom_field_prefix}{attr_id}"] = create_custom_field_dict(custom_type=attribute.custom_type)
                _logger.info(f"[fields_get] Created shared field: {field_name} (Single laterality)")

            elif laterality == "bilateral":
                if is_customized_step:
                    for side in ("left", "right"):
                        field_name = f"{field_prefix}{side}_{attr_id}"
                        res[field_name] = create_field_dict(suffix=side.capitalize(), domain_field=domain_field_name)
                        _logger.info(f"[fields_get] Created SPLIT field: {field_name} (Customized step)")

                        if is_custom:
                            custom_name = f"{custom_field_prefix}{side}_{attr_id}"
                            res[custom_name] = create_custom_field_dict(suffix=side, custom_type=attribute.custom_type)
                            _logger.info(f"[fields_get] Created custom SPLIT field: {custom_name}")
                else:
                    field_name = f"{field_prefix}{attr_id}"
                    res[field_name] = create_field_dict(domain_field=domain_field_name)
                    _logger.info(f"[fields_get] Created shared field: {field_name} (Non-customized Step)")

                    if is_custom:
                        custom_name = f"{custom_field_prefix}{attr_id}"
                        res[custom_name] = create_custom_field_dict(custom_type=attribute.custom_type)
                        _logger.info(f"[fields_get] Created custom shared field: {custom_name}")

        return res

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """Generate view dynamically using attributes stored on the product.template"""
        if view_type == "form" and not view_id:
            view_ext_id = "product_configurator.product_configurator_form"
            view_id = self.env.ref(view_ext_id).id

        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        wizard_id = self._find_wizard_context()

        wizard_model = res["model"]
        if not wizard_id or not res["models"].get(wizard_model):
            return res

        wiz = self.browse(wizard_id)
        wiz._invalidate_cache()  # ✅ Force fresh read
        wiz.read()  # ORM load

        # 🔍 Add this:
        _logger.info(f"[get_view] Loaded wizard {wiz.id} | Laterality: {wiz.laterality} | customize_step_ids: {wiz.customize_step_ids.ids}")

        if not wiz.exists():
            _logger.warning(f"[get_view] Wizard ID {wizard_id} does not exist.")
            raise UserError(_("The product configuration wizard has expired or was deleted."))

        # Get updated fields including the dynamic ones
        fields = self.fields_get()

        # Include all dynamic fields in the view
        dynamic_field_prefixes = tuple(self._prefixes.values())
        dynamic_fields = {
            k: v for k, v in fields.items() if k.startswith(dynamic_field_prefixes)
        }

        models = dict(res["models"])
        models[wizard_model] = models[wizard_model] + tuple(dynamic_fields.keys())
        res["models"] = frozendict(models)

        mod_view = self.add_dynamic_fields(res, dynamic_fields, wiz)

        # 🔍 Add this:
        _logger.info(f"[get_view] Finished building view for wizard {wiz.id} with {len(dynamic_fields)} dynamic fields")

        # Update result dict from super with modified view
        res.update({"arch": etree.tostring(mod_view)})
        return res

    def prepare_attrs_initial(self, attr_lines, field_prefix, custom_field_prefix, dynamic_fields, wiz):
        cfg_step_ids = []

        for attr_line in attr_lines:
            attribute = attr_line.attribute_id
            attribute_id = attribute.id
            field_name = f"{field_prefix}{attribute_id}"
            custom_field = f"{custom_field_prefix}{attribute_id}"
            domain_field_prefix = self._prefixes.get("domain_field_prefix")
            domain_field_name = f"{domain_field_prefix}{attribute_id}"

            if field_name not in dynamic_fields:
                _logger.debug(f"[prepare_attrs_initial] Skipping field {field_name} (not in dynamic_fields)")
                continue

            _logger.info(f"[prepare_attrs_initial] Processing attribute '{attribute.name}' (ID: {attribute_id})")

            config_steps = wiz.product_tmpl_id.config_step_line_ids.filtered(
                lambda x: attr_line in x.attribute_line_ids
            )
            step_ids = config_steps.ids
            _logger.debug(f"[prepare_attrs_initial] Related config steps: {step_ids}")

            attrs = {"readonly": "", "required": "", "invisible": ""}
            invisible_str = ""
            readonly_str = ""
            required_str = ""

            if config_steps:
                cfg_step_ids = [str(sid) for sid in config_steps.ids]
                invisible_str = f"state not in {cfg_step_ids}"
                readonly_str = f"state not in {cfg_step_ids}"
                if attr_line.required:
                    required_str = f"state in {cfg_step_ids}"
            else:
                invisible_str = "state not in ['configure']"
                readonly_str = "state not in ['configure']"
                if attr_line.required:
                    required_str = "state in ['configure']"

            _logger.debug(f"[prepare_attrs_initial] Attr visibility → invisible='{invisible_str}', readonly='{readonly_str}', required='{required_str}'")

            # Process dependencies
            config_lines = wiz.product_tmpl_id.config_line_ids
            dependencies = config_lines.filtered(lambda cl: cl.attribute_line_id == attr_line)

            if attr_line.value_ids <= dependencies.mapped("value_ids"):
                attr_depends = {}
                domain_lines = dependencies.mapped("domain_id.domain_line_ids")

                _logger.debug(f"[prepare_attrs_initial] Found {len(domain_lines)} domain lines for attribute {attribute_id}")

                for domain_line in domain_lines:
                    dependee_attr_id = domain_line.attribute_id.id
                    attr_field = f"{field_prefix}{dependee_attr_id}"
                    if attr_field not in attr_depends:
                        attr_depends[attr_field] = set()

                    if domain_line.condition == "in":
                        attr_depends[attr_field] |= set(domain_line.value_ids.ids)
                    elif domain_line.condition == "not in":
                        all_val_ids = wiz.product_tmpl_id.attribute_line_ids.filtered(
                            lambda l: l.attribute_id.id == dependee_attr_id
                        ).value_ids.ids
                        remaining_ids = set(all_val_ids) - set(domain_line.value_ids.ids)
                        attr_depends[attr_field] |= remaining_ids

                readonly_str, required_str = self._generate_dependency_attributes(
                    attr_line, attr_depends, dynamic_fields, readonly_str, required_str
                )

                _logger.debug(f"[prepare_attrs_initial] Dependencies adjusted → readonly='{readonly_str}', required='{required_str}'")

            attrs = {
                "readonly": readonly_str,
                "required": required_str,
                "invisible": invisible_str,
            }

            _logger.info(f"[prepare_attrs_initial] Final attrs for {field_name}: {attrs}")

            return (attrs, field_name, custom_field, config_steps, cfg_step_ids, domain_field_name)

    def _generate_dependency_attributes(
        self, attr_line, attr_depends, dynamic_fields, readonly_str, required_str
    ):
        """
        Applies conditions based on attribute dependencies to readonly and required
        strings.
        """
        if attr_line.custom:
            _logger.debug(
                f"[_generate_dependency_attributes] Skipping dependency logic for custom attribute: {attr_line.attribute_id.name} (ID: {attr_line.attribute_id.id})"
            )
            return readonly_str, required_str

        _logger.info(
            f"[_generate_dependency_attributes] Processing dependencies for attribute: {attr_line.attribute_id.name} (ID: {attr_line.attribute_id.id})"
        )

        for dependee_field, val_ids in attr_depends.items():
            if not val_ids:
                _logger.debug(
                    f"[_generate_dependency_attributes] No values provided for dependee field '{dependee_field}', skipping."
                )
                continue

            field_type = dynamic_fields.get(dependee_field, {}).get("type")
            _logger.debug(
                f"[_generate_dependency_attributes] Dependee: {dependee_field} | Type: {field_type} | Values: {list(val_ids)}"
            )

            if field_type != "many2many":
                readonly_cond = f"{dependee_field} not in {list(val_ids)}"
                readonly_str += f" and {readonly_cond}"
                _logger.debug(
                    f"[_generate_dependency_attributes] Adding readonly condition: {readonly_cond}"
                )

            if attr_line.required and not attr_line.custom and field_type != "many2many":
                required_cond = f"{dependee_field} in {list(val_ids)}"
                required_str += f" and {required_cond}"
                _logger.debug(
                    f"[_generate_dependency_attributes] Adding required condition: {required_cond}"
                )

        _logger.info(
            f"[_generate_dependency_attributes] Final → readonly: '{readonly_str}', required: '{required_str}'"
        )

        return readonly_str, required_str

    @api.model
    def add_dynamic_fields(self, res, dynamic_fields, wiz):
        field_prefix = self._prefixes.get("field_prefix")
        custom_field_prefix = self._prefixes.get("custom_field_prefix")
        domain_field_prefix = self._prefixes.get("domain_field_prefix")

        laterality = wiz.laterality
        customized_step_ids = set(wiz.customize_step_ids.ids)

        _logger.info(f"[add_dynamic_fields] Wizard ID: {wiz.id} | Laterality: {laterality} | Customized steps: {customized_step_ids}")

        try:
            xml_view = etree.fromstring(res["arch"])
            xml_static_form = xml_view.xpath("//group[@name='static_form']")[0]

            # Ensure only one dynamic group
            xml_existing = xml_view.xpath("//group[@name='dynamic_form']")
            for g in xml_existing:
                _logger.info("[add_dynamic_fields] Removing existing dynamic_form group to prevent duplication.")
                g.getparent().remove(g)

            xml_dynamic_form = etree.Element("group", colspan="2", name="dynamic_form")
            xml_parent = xml_static_form.getparent()
            xml_parent.insert(xml_parent.index(xml_static_form) + 1, xml_dynamic_form)
        except Exception as exc:
            _logger.exception("[add_dynamic_fields] Failed to prepare XML view structure.")
            raise UserError(_("Could not render dynamic form group")) from exc

        attr_lines = wiz.product_tmpl_id.attribute_line_ids.sorted()
        _logger.info(f"[add_dynamic_fields] Found {len(attr_lines)} attribute lines for template ID {wiz.product_tmpl_id.id}")

        for attr_line in attr_lines:
            attribute = attr_line.attribute_id
            attr_id = attribute.id
            is_custom = attr_line.custom

            # step_lines = wiz.product_tmpl_id.config_step_line_ids.filtered(
            #     lambda step: attr_line.id in step.attribute_line_ids.ids
            # )
            # step_ids = step_lines.ids
            # is_customized_step = bool(set(step_ids) & customized_step_ids)
            
            
            step_lines = wiz.product_tmpl_id.config_step_line_ids.filtered(
                lambda step: attr_line.id in step.attribute_line_ids.ids
            )
            step_ids = set(step_lines.mapped("id"))
            is_customized_step = bool(step_ids & customized_step_ids)
            _logger.debug(f"[fields_get] Step IDs for attr {attr_id}: {step_ids} | Customized Steps: {customized_step_ids} | Is customized: {is_customized_step}")

            _logger.info(f"[add_dynamic_fields] Attr ID: {attr_id} | Attr Name: {attribute.name} | Step IDs: {step_ids} | Customized: {is_customized_step}")


            if laterality in ("left", "right") or not is_customized_step:
                # SHARED FIELD
                field_name = f"{field_prefix}{attr_id}"
                custom_field = f"{custom_field_prefix}{attr_id}"
                domain_field_name = f"{domain_field_prefix}{attr_id}"

                _logger.info(f"[add_dynamic_fields] ➤ Injecting SHARED field: {field_name}")

                attrs, _, _, _, _, _ = self.prepare_attrs_initial(
                    [attr_line], field_prefix, custom_field_prefix, dynamic_fields, wiz
                )
                field_type = dynamic_fields.get(field_name, {}).get("type")
                _logger.debug(f"[add_dynamic_fields] Field type for {field_name}: {field_type}")

                if field_name not in dynamic_fields:
                    _logger.warning(f"[add_dynamic_fields] Field {field_name} not found in dynamic_fields.")
                    continue

                node = etree.Element("field", name=field_name, attrib=attrs)
                node.set("on_change", "1")
                node.set("default_focus", "1")
                if field_type == "many2many":
                    node.set("widget", "many2many_tags")
                node.set("context", str({
                    "show_attribute": False,
                    "show_price_extra": True,
                    "active_id": wiz.product_tmpl_id.id,
                    "wizard_id": wiz.id,
                    "field_name": field_name,
                    "is_m2m": attr_line.multi,
                    "value_ids": attr_line.value_ids.ids,
                }))
                node.set("options", str({
                    "no_create": True,
                    "no_create_edit": True,
                    "no_open": True,
                }))
                xml_dynamic_form.append(node)
                _logger.debug(f"[add_dynamic_fields] Shared field {field_name} appended to XML.")

                domain_node = etree.Element("field", name=domain_field_name)
                domain_node.set("readonly", "1")
                domain_node.set("invisible", "1")
                xml_dynamic_form.append(domain_node)

                if is_custom and custom_field in dynamic_fields:
                    _logger.info(f"[add_dynamic_fields] ➤ Injecting custom SHARED field: {custom_field}")
                    custom_node = etree.Element("field", name=custom_field, attrib=attrs)
                    if attribute.custom_type == "color":
                        custom_node.set("widget", "color")
                    xml_dynamic_form.append(custom_node)

            else:
                # SPLIT FIELDS
                for side in ("left", "right"):
                    field_name = f"{field_prefix}{side}_{attr_id}"
                    custom_field = f"{custom_field_prefix}{side}_{attr_id}"
                    domain_field_name = f"{domain_field_prefix}{attr_id}"

                    _logger.info(f"[add_dynamic_fields] ➤ Injecting SPLIT field: {field_name} (side: {side})")

                    attrs, _, _, _, _, _ = self.prepare_attrs_initial(
                        [attr_line], field_prefix, custom_field_prefix, dynamic_fields, wiz
                    )
                    field_type = dynamic_fields.get(field_name, {}).get("type")
                    _logger.debug(f"[add_dynamic_fields] Field type for {field_name}: {field_type}")

                    if field_name not in dynamic_fields:
                        _logger.warning(f"[add_dynamic_fields] Split field {field_name} not found in dynamic_fields.")
                        continue

                    node = etree.Element("field", name=field_name, attrib=attrs)
                    node.set("on_change", "1")
                    node.set("default_focus", "0")
                    if field_type == "many2many":
                        node.set("widget", "many2many_tags")
                    node.set("context", str({
                        "show_attribute": False,
                        "show_price_extra": True,
                        "active_id": wiz.product_tmpl_id.id,
                        "wizard_id": wiz.id,
                        "field_name": field_name,
                        "is_m2m": attr_line.multi,
                        "value_ids": attr_line.value_ids.ids,
                    }))
                    node.set("options", str({
                        "no_create": True,
                        "no_create_edit": True,
                        "no_open": True,
                    }))
                    xml_dynamic_form.append(node)
                    _logger.debug(f"[add_dynamic_fields] Split field {field_name} appended to XML.")

                    domain_node = etree.Element("field", name=domain_field_name)
                    domain_node.set("readonly", "1")
                    domain_node.set("invisible", "1")
                    xml_dynamic_form.append(domain_node)

                    if is_custom and custom_field in dynamic_fields:
                        _logger.info(f"[add_dynamic_fields] ➤ Injecting custom SPLIT field: {custom_field}")
                        custom_node = etree.Element("field", name=custom_field, attrib=attrs)
                        if attribute.custom_type == "color":
                            custom_node.set("widget", "color")
                        xml_dynamic_form.append(custom_node)

        _logger.info(f"[add_dynamic_fields] ✅ Finished injecting dynamic fields into XML for wizard {wiz.id}")
        return xml_view

    @api.model_create_multi
    def create(self, vals_list):
        """Sets the configuration values of the product_id if given (if any).
        This is used in reconfiguration of an existing variant or for initial template-based configuration.
        """
        for vals in vals_list:
            # Handle reconfiguration from existing product
            if "product_id" in vals and not vals.get("product_tmpl_id"):
                product = self.env["product.product"].browse(vals["product_id"])
                pta_value_ids = product.product_template_attribute_value_ids
                attr_value_ids = pta_value_ids.mapped("product_attribute_value_id")
                vals.update({
                    "product_tmpl_id": product.product_tmpl_id.id,
                    "value_ids": [(6, 0, attr_value_ids.ids)],
                })

            # Ensure product_tmpl_id is present before continuing
            tmpl_id = vals.get("product_tmpl_id")
            if not tmpl_id:
                raise ValueError("Missing product_tmpl_id in configurator create.")

            # Create or get config session if not already set
            if not vals.get("config_session_id"):
                session = self.env["product.config.session"].create_get_session(
                    product_tmpl_id=int(tmpl_id)
                )
                vals["config_session_id"] = session.id

            vals["user_id"] = self.env.uid

            # Reuse session value_ids if none were set explicitly
            session = self.env["product.config.session"].browse(vals["config_session_id"])
            wz_value_ids = vals.get("value_ids", [])
            if session.value_ids and ((wz_value_ids and not wz_value_ids[0][2]) or not wz_value_ids):
                vals["value_ids"] = [(6, 0, session.value_ids.ids)]

        records = super().create(vals_list)

        for record in records:
            _logger.info(f"[create] New configurator created with ID {record.id} for template {record.product_tmpl_id.id}")

        return records

    def read(self, fields=None, load="_classic_read"):
        res = super().read(self._remove_dynamic_fields(fields or []), load=load)

        if not fields:
            return res

        field_prefix = self._prefixes.get("field_prefix")
        custom_prefix = self._prefixes.get("custom_field_prefix")

        for result in res:
            wiz = self.browse(result["id"])
            laterality = wiz.laterality
            customized_steps = set(wiz.customize_step_ids.ids)
            value_ids = {v.id: v for v in wiz.value_ids}
            custom_vals = {v.attribute_id.id: v for v in wiz.custom_value_ids}

            for attr_line in wiz.product_tmpl_id.attribute_line_ids:
                attr = attr_line.attribute_id
                attr_id = attr.id
                is_custom = attr_line.custom
                is_multi = attr_line.multi

                step_lines = wiz.product_tmpl_id.config_step_line_ids.filtered(
                    lambda step: attr_line.id in step.attribute_line_ids.ids
                )
                step_ids = set(step_lines.mapped("id"))
                is_customized = bool(step_ids & customized_steps)

                def _get_val(side=None):
                    if side:
                        return [
                            v.id for v in value_ids.values()
                            if v.attribute_id.id == attr_id and v.name.lower().endswith(f"({side})")
                        ]
                    else:
                        return [
                            v.id for v in value_ids.values()
                            if v.attribute_id.id == attr_id
                        ]

                def _get_custom_val():
                    try:
                        return custom_vals.get(attr_id).eval() if custom_vals.get(attr_id) else False
                    except Exception:
                        return False

                if laterality == "bilateral" and is_customized:
                    for side in ("left", "right"):
                        field_name = f"{field_prefix}{side}_{attr_id}"
                        custom_name = f"{custom_prefix}{side}_{attr_id}"

                        val = _get_val(side)
                        result[field_name] = val if is_multi else (val[0] if val else False)

                        if is_custom:
                            result[custom_name] = _get_custom_val()
                else:
                    field_name = f"{field_prefix}{attr_id}"
                    custom_name = f"{custom_prefix}{attr_id}"

                    val = _get_val()
                    result[field_name] = val if is_multi else (val[0] if val else False)

                    if is_custom:
                        result[custom_name] = _get_custom_val()

                # Inject domain field for UI filtering
                domain_field = f"__domain_{attr_id}"
                available_value_ids = wiz.config_session_id.values_available(
                    check_val_ids=attr_line.value_ids.ids,
                    product_template_attribute_line_id=attr_line.id,
                )
                result[domain_field] = [("id", "in", available_value_ids)]

        return res

    def write(self, vals):
        vals = self._remove_dynamic_fields(vals)  # First, remove old dynamic fields

        wiz = self
        laterality = wiz.laterality
        customized_steps = set(wiz.customize_step_ids.ids)

        attr_val_dict = {}
        custom_val_dict = {}

        # Dynamic prefixes
        field_prefix = self._prefixes.get("field_prefix")
        custom_prefix = self._prefixes.get("custom_field_prefix")

        for attr_line in wiz.product_tmpl_id.attribute_line_ids:
            attr = attr_line.attribute_id
            attr_id = attr.id
            is_multi = attr_line.multi
            is_custom = attr_line.custom

            # step_lines = wiz.product_tmpl_id.config_step_line_ids.filtered(
            #     lambda s: attr_line in s.attribute_line_ids
            # )

            step_lines = wiz.product_tmpl_id.config_step_line_ids.filtered(
                lambda step: attr_line.id in step.attribute_line_ids.ids
            )
            
            customized = bool(set(step_lines.ids) & customized_steps)

            # Handle split laterality
            if laterality == "bilateral" and customized:
                for side in ("left", "right"):
                    field_name = f"{field_prefix}{side}_{attr_id}"
                    custom_name = f"{custom_prefix}{side}_{attr_id}"

                    val = vals.get(field_name)
                    if val:
                        attr_val_dict.setdefault(attr_id, []).append(val if is_multi else [val])

                    if is_custom and custom_name in vals:
                        custom_val_dict[attr_id] = vals[custom_name]

            else:
                field_name = f"{field_prefix}{attr_id}"
                custom_name = f"{custom_prefix}{attr_id}"

                val = vals.get(field_name)
                if val:
                    attr_val_dict[attr_id] = val if is_multi else [val]

                if is_custom and custom_name in vals:
                    custom_val_dict[attr_id] = vals[custom_name]

        # Flatten multi-vals and remove duplicates
        final_attr_vals = {}
        for k, v in attr_val_dict.items():
            flattened = [x for sub in v for x in (sub if isinstance(sub, list) else [sub])]
            final_attr_vals[k] = list(set(flattened))

        self.config_session_id.update_config(attr_val_dict=final_attr_vals, custom_val_dict=custom_val_dict)

        return super().write(vals)

    def action_next_step(self):
        """Proceeds to the next step of the configuration process. This usually
        implies the next configuration step (if any) defined via the
        config_step_line_ids on the product.template.

        More importantly it sets metadata on the context
        variable so the fields_get and fields_view_get methods can generate the
        appropriate dynamic content"""
        wizard_action = self.with_context(
            allow_preset_selection=False
        ).get_wizard_action(wizard=self)

        if not self.product_tmpl_id:
            return wizard_action

        if not self.product_tmpl_id.attribute_line_ids:
            raise ValidationError(
                _("Product Template does not have any attribute lines defined")
            )
        next_step = self.config_session_id.get_next_step(
            state=self.state,
            product_tmpl_id=self.product_tmpl_id,
            value_ids=self.config_session_id.value_ids,
            custom_value_ids=self.config_session_id.custom_value_ids,
        )
        if not next_step:
            return self.action_config_done()
        return self.open_step(step=next_step)

    def action_previous_step(self):
        """Proceeds to the next step of the configuration process. This usually
        implies the next configuration step (if any) defined via the
        config_step_line_ids on the product.template."""
        wizard_action = self.with_context(
            wizard_id=self.id, view_cache=False, allow_preset_selection=False
        ).get_wizard_action(wizard=self)
        cfg_step_lines = self.product_tmpl_id.config_step_line_ids
        if not cfg_step_lines:
            self.state = "select"
            return wizard_action

        try:
            cfg_step_line_id = int(self.state)
            active_cfg_line_id = cfg_step_lines.filtered(
                lambda x: x.id == cfg_step_line_id
            ).id
        except Exception:
            active_cfg_line_id = None

        adjacent_steps = self.config_session_id.get_adjacent_steps(
            active_step_line_id=active_cfg_line_id
        )
        previous_step = adjacent_steps.get("previous_step")
        if previous_step:
            self.state = str(previous_step.id)
        else:
            self.state = "select"
        self.config_session_id.config_step = self.state
        return wizard_action

    def action_reset(self):
        """Delete wizard and configuration session then create
        a new wizard+session and return an action for the new wizard object"""
        try:
            session_product_tmpl_id = self.config_session_id.product_tmpl_id
            self.config_session_id.unlink()
        except Exception as e:
            _logger.error("Error while resetting configuration session: %s", e)
        action = self.with_context(
            wizard_id=None,
            allow_preset_selection=False,
            default_product_tmpl_id=session_product_tmpl_id.id,
        ).get_wizard_action()

        # Now delete the old wizard after returning action
        # self.unlink()

        return action

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
                    self.env.ref("pod_product_configurator.product_configurator_form").id,
                    "form",
                ]
            ],
            "view_mode": "form",
            "context": ctx,
            "target": "new",
        }
        if wizard:
            wizard_action.update({"res_id": wizard.id})
        return wizard_action

    def open_step(self, step):
        """Open wizard step 'step'
        :param step: recordset of product.config.step.line
        """
        wizard_action = self.with_context(
            allow_preset_selection=False
        ).get_wizard_action(wizard=self)
        if not step:
            return wizard_action
        if isinstance(step, type(self.env["product.config.step.line"])):
            step = "%s" % (step.id)
        self.state = step
        self.config_session_id.config_step = step
        return wizard_action

    def action_config_done(self):
        """This method is for the final step which will be taken care by a
        separate module"""
        # This try except is too generic.
        # The create_variant routine could effectively fail for
        # a large number of reasons, including bad programming.
        # It should be refactored.
        # In the meantime, at least make sure that a validation
        # error legitimately raised in a nested routine
        # is passed through.
        step_to_open = self.config_session_id.check_and_open_incomplete_step()
        if step_to_open:
            return self.open_step(step_to_open)
        self.config_session_id.action_confirm()
        variant = self.config_session_id.product_id
        action = {
            "type": "ir.actions.act_window",
            "res_model": "product.product",
            "name": "Product Variant",
            "view_mode": "form",
            "context": dict(self.env.context, custom_create_variant=True),
            "res_id": variant.id,
        }
        return action


# class ProductConfiguratorCustomValue(models.TransientModel):
#     _name = "product.configurator.custom.value"
#     _description = "Product Configurator Custom Value"

#     attachment_ids = fields.Many2many(
#         comodel_name="ir.attachment",
#         column1="config_attachment",
#         column2="attachment_id",
#         string="Attachments",
#     )
#     attribute_id = fields.Many2one(
#         string="Attribute", comodel_name="product.attribute", required=True
#     )
#     user_id = fields.Many2one(
#         string="User",
#         comodel_name="res.users",
#         related="wizard_id.create_uid",
#         required=True,
#     )
#     value = fields.Char(string="Value")
#     wizard_id = fields.Many2one(comodel_name="product.configurator", string="Wizard")
# TODO: Current value ids to save frontend/backend session?
