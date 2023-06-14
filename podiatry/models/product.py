import logging
from io import StringIO

from mako.runtime import Context
from mako.template import Template

from odoo import api, fields, exceptions, models, tools, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools import config

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends("product_variant_ids.product_tmpl_id")
    def _compute_product_variant_count(self):
        """For configurable products return the number of variants configured or
        1 as many views and methods trigger only when a template has at least
        one variant attached. Since we create them from the template we should
        have access to them always"""
        super(ProductTemplate, self)._compute_product_variant_count()
        for product_tmpl in self:
            config_ok = product_tmpl.config_ok
            variant_count = product_tmpl.product_variant_count
            if config_ok and not variant_count:
                product_tmpl.product_variant_count = 1

    @api.depends("attribute_line_ids.value_ids")
    def _compute_template_attr_vals(self):
        """Compute all attribute values added in attribute line on
        product template"""
        for product_tmpl in self:
            if product_tmpl.config_ok:
                value_ids = product_tmpl.attribute_line_ids.mapped("value_ids")
                product_tmpl.attribute_line_val_ids = value_ids
            else:
                product_tmpl.attribute_line_val_ids = False

    @api.constrains("attribute_line_ids", "attribute_value_line_ids")
    def check_attr_value_ids(self):
        """Check attribute lines don't have some attribute value that
        is not present in attribute lines of that product template"""
        for product_tmpl in self:
            if not product_tmpl.env.context.get("check_constraint", True):
                continue
            attr_val_lines = product_tmpl.attribute_value_line_ids
            attr_val_ids = attr_val_lines.mapped("value_ids")
            if not attr_val_ids <= product_tmpl.attribute_line_val_ids:
                raise ValidationError(
                    _(
                        "All attribute values used in attribute value lines "
                        "must be defined in the attribute lines of the "
                        "template"
                    )
                )

    @api.constrains("attribute_value_line_ids")
    def _validate_unique_config(self):
        """Check for duplicate configurations for the same
        attribute value in image lines"""
        for template in self:
            attr_val_line_vals = template.attribute_value_line_ids.read(
                ["value_id", "value_ids"], load=False
            )
            attr_val_line_vals = [
                (line["value_id"], tuple(line["value_ids"]))
                for line in attr_val_line_vals
            ]
            if len(set(attr_val_line_vals)) != len(attr_val_line_vals):
                raise ValidationError(
                    _("You cannot have a duplicate configuration for the " "same value")
                )

    config_ok = fields.Boolean(string="Can be Configured")

    config_line_ids = fields.One2many(
        comodel_name="product.config.line",
        inverse_name="product_tmpl_id",
        string="Attribute Dependencies",
        copy=False,
    )

    config_image_ids = fields.One2many(
        comodel_name="product.config.image",
        inverse_name="product_tmpl_id",
        string="Configuration Images",
        copy=True,
    )

    attribute_value_line_ids = fields.One2many(
        comodel_name="product.attribute.value.line",
        inverse_name="product_tmpl_id",
        string="Attribute Value Lines",
        copy=True,
    )

    attribute_line_val_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        compute="_compute_template_attr_vals",
        store=False,
    )

    config_step_line_ids = fields.One2many(
        comodel_name="product.config.step.line",
        inverse_name="product_tmpl_id",
        string="Configuration Lines",
        copy=False,
    )

    mako_tmpl_name = fields.Text(
        string="Variant name",
        help="Generate Name based on Mako Template",
        copy=True,
    )

    # We are calculating weight of variants based on weight of
    # product-template so that no need of compute and inverse on this
    weight = fields.Float(
        compute="_compute_weight",
        inverse="_set_weight",  # pylint: disable=C8110
        search="_search_weight",
        store=False,
    )
    weight_dummy = fields.Float(
        string="Manual Weight",
        digits="Stock Weight",
        help="Manual setting of product template weight",
    )

    def _compute_weight(self):
        config_products = self.filtered(lambda template: template.config_ok)
        for product in config_products:
            product.weight = product.weight_dummy
        standard_products = self - config_products
        super(ProductTemplate, standard_products)._compute_weight()

    def _set_weight(self):
        for product_tmpl in self:
            product_tmpl.weight_dummy = product_tmpl.weight
            if not product_tmpl.config_ok:
                super(ProductTemplate, product_tmpl)._set_weight()

    def _search_weight(self, operator, value):
        return [("weight_dummy", operator, value)]

    def get_product_attribute_values_action(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "podiatry.product_attribute_value_action"
        )
        value_ids = self.attribute_line_ids.mapped("product_template_value_ids").ids
        action["domain"] = [("id", "in", value_ids)]
        context = safe_eval(action["context"], {"active_id": self.id})
        context.update({"active_id": self.id})
        action["context"] = context
        return action

    def _check_default_values(self):
        default_val_ids = (
            self.attribute_line_ids.filtered(lambda l: l.default_val)
            .mapped("default_val")
            .ids
        )

        cfg_session_obj = self.env["product.config.session"]
        try:
            cfg_session_obj.validate_configuration(
                value_ids=default_val_ids, product_tmpl_id=self.id, final=False
            )
        except ValidationError as ex:
            raise ValidationError(ex.name)
        except Exception:
            raise ValidationError(
                _("Default values provided generate an invalid configuration")
            )

    @api.constrains("config_line_ids", "attribute_line_ids")
    def _check_default_value_domains(self):
        for template in self:
            try:
                template._check_default_values()
            except ValidationError as e:
                raise ValidationError(
                    _(
                        "Restrictions added make the current default values "
                        "generate an invalid configuration.\
                      \n%s"
                    )
                    % (e.name)
                )

    def toggle_config(self):
        for record in self:
            record.config_ok = not record.config_ok

    def _create_variant_ids(self):
        """Prevent configurable products from creating variants as these serve
        only as a template for the product configurator"""
        templates = self.filtered(lambda t: not t.config_ok)
        if not templates:
            return None
        return super(ProductTemplate, templates)._create_variant_ids()

    def unlink(self):
        """- Prevent the removal of configurable product templates
            from variants
        - Patch for check access rights of user(configurable products)"""
        configurable_templates = self.filtered(lambda template: template.config_ok)
        if configurable_templates:
            configurable_templates[:1].check_config_user_access()
        for config_template in configurable_templates:
            variant_unlink = config_template.env.context.get(
                "unlink_from_variant", False
            )
            if variant_unlink:
                self -= config_template
        res = super(ProductTemplate, self).unlink()
        return res

    def copy(self, default=None):
        """Copy restrictions, config Steps and attribute lines
        ith product template"""
        if not default:
            default = {}
        self = self.with_context(check_constraint=False)
        res = super(ProductTemplate, self).copy(default=default)

        # Attribute lines
        attribute_line_dict = {}
        for line in res.attribute_line_ids:
            attribute_line_dict.update({line.attribute_id.id: line.id})

        # Restrictions
        for line in self.config_line_ids:
            old_restriction = line.domain_id
            new_restriction = old_restriction.copy()
            config_line_default = {
                "product_tmpl_id": res.id,
                "domain_id": new_restriction.id,
            }
            new_attribute_line_id = attribute_line_dict.get(
                line.attribute_line_id.attribute_id.id, False
            )
            if not new_attribute_line_id:
                continue
            config_line_default.update({"attribute_line_id": new_attribute_line_id})
            line.copy(config_line_default)

        # Config steps
        config_step_line_default = {"product_tmpl_id": res.id}
        for line in self.config_step_line_ids:
            new_attribute_line_ids = [
                attribute_line_dict.get(old_attr_line.attribute_id.id)
                for old_attr_line in line.attribute_line_ids
                if old_attr_line.attribute_id.id in attribute_line_dict
            ]
            if new_attribute_line_ids:
                config_step_line_default.update(
                    {"attribute_line_ids": [(6, 0, new_attribute_line_ids)]}
                )
            line.copy(config_step_line_default)
        return res

    def configure_product(self):
        """launches a product configurator wizard with a linked
        template in order to configure new product."""
        return self.with_context(product_tmpl_id_readonly=True).create_config_wizard(
            click_next=False
        )

    def create_config_wizard(
        self,
        model_name="product.configurator",
        extra_vals=None,
        click_next=True,
    ):
        """create product configuration wizard
        - return action to launch wizard
        - click on next step based on value of click_next"""
        wizard_obj = self.env[model_name]
        wizard_vals = {"product_tmpl_id": self.id}
        if extra_vals:
            wizard_vals.update(extra_vals)
        wizard = wizard_obj.create(wizard_vals)
        if click_next:
            action = wizard.action_next_step()
        else:
            wizard_obj = wizard_obj.with_context(
                wizard_model=model_name,
                allow_preset_selection=True,
            )
            action = wizard_obj.get_wizard_action(wizard=wizard)
        return action

    @api.model
    def _check_config_group_rights(self):
        """Return True/False from system parameter
        - Signals access rights needs to check or not
        :Params: return : boolean"""
        ICPSudo = self.env["ir.config_parameter"].sudo()
        manager_product_configuration_settings = ICPSudo.get_param(
            "podiatry.manager_product_configuration_settings"
        )
        return manager_product_configuration_settings

    @api.model
    def check_config_user_access(self):
        """Check user have access to perform action(create/write/delete)
        on configurable products"""
        if not self._check_config_group_rights():
            return True
        config_manager = self.env.user.has_group(
            "podiatry.group_product_configurator_manager"
        )
        user_root = self.env.ref("base.user_root")
        user_admin = self.env.ref("base.user_admin")
        if (
            config_manager
            or self.env.user.id in [user_root.id, user_admin.id]
            or self.env.su
        ):
            return True
        raise ValidationError(
            _(
                "Sorry, you are not allowed to create/change this kind of "
                "document. For more information please contact your manager."
            )
        )

    @api.model
    def create(self, vals):
        """Patch for check access rights of user(configurable products)"""
        config_ok = vals.get("config_ok", False)
        if config_ok:
            self.check_config_user_access()
        return super(ProductTemplate, self).create(vals)

    def write(self, vals):
        """Patch for check access rights of user(configurable products)"""
        change_config_ok = "config_ok" in vals
        configurable_templates = self.filtered(lambda template: template.config_ok)
        if change_config_ok or configurable_templates:
            self[:1].check_config_user_access()

        return super(ProductTemplate, self).write(vals)

    @api.constrains("config_line_ids")
    def _check_config_line_domain(self):
        attribute_line_ids = self.attribute_line_ids
        tmpl_value_ids = attribute_line_ids.mapped("value_ids")
        tmpl_attribute_ids = attribute_line_ids.mapped("attribute_id")
        error_message = False
        for domain_id in self.config_line_ids.mapped("domain_id"):
            domain_attr_ids = domain_id.domain_line_ids.mapped("attribute_id")
            domain_value_ids = domain_id.domain_line_ids.mapped("value_ids")
            invalid_value_ids = domain_value_ids - tmpl_value_ids
            invalid_attribute_ids = domain_attr_ids - tmpl_attribute_ids
            if not invalid_value_ids and not invalid_value_ids:
                continue
            if not error_message:
                error_message = _(
                    "Following Attribute/Value from restriction "
                    "are not present in template attributes/values. "
                    "Please make sure you are adding right restriction"
                )
            error_message += _("\nRestriction: %s") % (domain_id.name)
            error_message += (
                invalid_attribute_ids
                and _("\nAttribute/s: %s")
                % (", ".join(invalid_attribute_ids.mapped("name")))
                or ""
            )
            error_message += (
                invalid_value_ids
                and _("\nValue/s: %s\n") % (", ".join(invalid_value_ids.mapped("name")))
                or ""
            )
        if error_message:
            raise ValidationError(error_message)

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        domain = args or []
        domain += ["|", ("name", operator, name), ("default_code", operator, name)]
        return self.search(domain, limit=limit).name_get()

class ProductProduct(models.Model):
    _inherit = ["product.product", "product.configurator"]
    _name = "product.product"
    _rec_name = "config_name"
    
    is_helpdesk = fields.Boolean("Helpdesk Ticket?")
    helpdesk_team = fields.Many2one('helpdesk.team', string='Helpdesk Team')
    helpdesk_assigned_to = fields.Many2one('res.users', string='Assigned to')
    
    product_secondary_uom_id = fields.Many2one('uom.uom', 'Secondary Unit of Measure', 
        related="product_tmpl_id.secondary_uom", domain="[('category_id', '=', product_sec_product_uom_category_id)]",
        help="Default unit of measure used for all stock operations.", readonly=False)
    product_sec_product_uom_qty = fields.Float(string='S-Qty on Hand', digits='Product Unit of Measure',
        compute="_compute_product_sec_product_uom_qty", store=True)    
    product_sec_product_uom_category_id = fields.Many2one(related='product_tmpl_id.secondary_uom.category_id', string="Sec Product Category")
    
    @api.depends('qty_available')
    def _compute_product_sec_product_uom_qty(self):
        for record in self:
            if record.uom_id == record.product_secondary_uom_id:
                record.product_sec_product_uom_qty = record.qty_available
            elif record.product_secondary_uom_id.uom_type == 'reference' and record.uom_id.uom_type == 'bigger':
                record.product_sec_product_uom_qty = (record.product_secondary_uom_id.ratio * record.uom_id.ratio) * record.qty_available

            elif record.product_secondary_uom_id.uom_type == 'bigger' and record.uom_id.uom_type == 'reference':
                record.product_sec_product_uom_qty = (record.uom_id.ratio / record.product_secondary_uom_id.ratio) * record.qty_available

            elif record.product_secondary_uom_id.uom_type == 'smaller' and record.uom_id.uom_type == 'reference':
                record.product_sec_product_uom_qty = (record.product_secondary_uom_id.ratio * record.uom_id.ratio) * record.qty_available

            elif record.product_secondary_uom_id.uom_type == 'reference' and record.uom_id.uom_type == 'smaller':
                record.product_sec_product_uom_qty = (record.product_secondary_uom_id.ratio / record.uom_id.ratio) * record.qty_available 

            elif record.product_secondary_uom_id.uom_type == 'smaller' and record.uom_id.uom_type == 'bigger':
                record.product_sec_product_uom_qty = (record.product_secondary_uom_id.ratio * record.uom_id.ratio) * record.qty_available 
                
            elif record.product_secondary_uom_id.uom_type == 'bigger' and record.uom_id.uom_type == 'smaller':
                record.product_sec_product_uom_qty = (1 / (record.product_secondary_uom_id.ratio * record.uom_id.ratio))* record.qty_available 

            elif record.product_secondary_uom_id.uom_type == 'smaller' and record.uom_id.uom_type == 'smaller':
                record.product_sec_product_uom_qty = (record.product_secondary_uom_id.ratio / record.uom_id.ratio) * record.qty_available
            
            elif record.product_secondary_uom_id.uom_type == 'bigger' and record.uom_id.uom_type == 'bigger':
                record.product_sec_product_uom_qty = (record.uom_id.ratio / record.product_secondary_uom_id.ratio) * record.qty_available

    # @api.onchange('product_sec_product_uom_qty')
    # def _inverse_product_sec_product_uom_qty(self):
    #     for record in self:
    #         if record.uom_id == record.product_secondary_uom_id:
    #             record.qty_available = record.product_sec_product_uom_qty            
    #         elif record.product_secondary_uom_id.uom_type == 'reference' and record.uom_id.uom_type == 'bigger':
    #             record.qty_available = (record.product_secondary_uom_id.ratio / record.uom_id.ratio) * record.product_sec_product_uom_qty
    #         elif record.product_secondary_uom_id.uom_type == 'bigger' and record.uom_id.uom_type == 'reference':
    #             record.qty_available = (record.product_secondary_uom_id.ratio * record.uom_id.ratio) * record.product_sec_product_uom_qty
    #         elif record.product_secondary_uom_id.uom_type == 'smaller' and record.uom_id.uom_type == 'reference':
    #              record.qty_available = (record.uom_id.ratio / record.product_secondary_uom_id.ratio) * record.product_sec_product_uom_qty
    #         elif record.product_secondary_uom_id.uom_type == 'reference' and record.uom_id.uom_type == 'smaller':
    #             record.qty_available = (record.product_secondary_uom_id.ratio * record.uom_id.ratio) * record.product_sec_product_uom_qty
    #         elif record.product_secondary_uom_id.uom_type == 'smaller' and record.uom_id.uom_type == 'bigger':
    #             record.qty_available = (1 / (record.product_secondary_uom_id.ratio * record.uom_id.ratio))* record.product_sec_product_uom_qty
    #         elif record.product_secondary_uom_id.uom_type == 'bigger' and record.uom_id.uom_type == 'smaller':
    #             record.qty_available = (record.product_secondary_uom_id.ratio * record.uom_id.ratio) * record.product_sec_product_uom_qty
    
    

    def _get_conversions_dict(self):
        conversions = {"float": float, "integer": int}
        return conversions

    @api.constrains("product_template_attribute_value_ids")
    def _check_duplicate_product(self):
        """Check for prducts with same attribute values/custom values"""
        for product in self:
            if not product.config_ok:
                continue

            # At the moment, I don't have enough confidence with my
            # understanding of binary attributes, so will leave these
            # as not matching...
            # In theory, they should just work, if they are set to "non search"
            # in custom field def!
            # TODO: Check the logic with binary attributes
            config_session_obj = product.env["product.config.session"]
            ptav_ids = product.product_template_attribute_value_ids.mapped(
                "product_attribute_value_id"
            )
            duplicates = config_session_obj.search_variant(
                product_tmpl_id=product.product_tmpl_id,
                value_ids=ptav_ids.ids,
            ).filtered(lambda p: p.id != product.id)

            if duplicates:
                raise ValidationError(
                    _(
                        "Configurable Products cannot have duplicates "
                        "(identical attribute values)"
                    )
                )

    @api.constrains("product_tmpl_id", "product_template_attribute_value_ids")
    def _check_duplicity(self):
        if not config["test_enable"] or not self.env.context.get(
            "test_check_duplicity"
        ):
            return
        for product in self:
            domain = [("product_tmpl_id", "=", product.product_tmpl_id.id)]
            for value in product.product_template_attribute_value_ids:
                domain.append(("product_template_attribute_value_ids", "=", value.id))
            other_products = self.with_context(active_test=False).search(domain)
            # Filter the product with the exact number of attributes values
            cont = len(product.product_template_attribute_value_ids)
            for other_product in other_products:
                if (
                    len(other_product.product_template_attribute_value_ids) == cont
                    and other_product != product
                ):
                    raise exceptions.ValidationError(
                        _("There's another product with the same attributes.")
                    )

    @api.constrains("product_tmpl_id", "product_template_attribute_value_ids")
    def _check_configuration_validity(self):
        """The method checks that the current selection values are correct.

        As default, the validity means that all the attributes
        with the required flag are set.

        This can be overridden to set another rules.

        :raises: exceptions.ValidationError: If the check is not valid.
        """
        # Creating from template variants attributes are not created at once so
        # we avoid to check the constrain here.
        if self.env.context.get("creating_variants"):
            return
        for product in self:
            req_attrs = product.product_tmpl_id.attribute_line_ids.filtered(
                lambda a: a.required
            ).mapped("attribute_id")
            errors = req_attrs - product.product_template_attribute_value_ids.mapped(
                "attribute_id"
            )
            if errors:
                raise exceptions.ValidationError(
                    _("You have to fill the following attributes:\n%s")
                    % "\n".join(errors.mapped("name"))
                )

    def _get_config_name(self):
        """Name for configured products
        :param: return : String"""
        self.ensure_one()
        return self.name

    def _get_mako_context(self, buf):
        """Return context needed for computing product name based
        on mako-template define on it's product template"""
        self.ensure_one()
        ptav_ids = self.product_template_attribute_value_ids.mapped(
            "product_attribute_value_id"
        )
        return Context(
            buf,
            product=self,
            attribute_values=ptav_ids,
            steps=self.product_tmpl_id.config_step_line_ids,
            template=self.product_tmpl_id,
        )

    def _get_mako_tmpl_name(self):
        """Compute and return product name based on mako-tamplate
        define on it's product template"""
        self.ensure_one()
        if self.mako_tmpl_name:
            try:
                mytemplate = Template(self.mako_tmpl_name or "")
                buf = StringIO()
                ctx = self._get_mako_context(buf)
                mytemplate.render_context(ctx)
                return buf.getvalue()
            except Exception:
                _logger.error(
                    _("Error while calculating mako product name: %s")
                    % self.display_name
                )
        return self.display_name

    def get_product_multiline_description_sale(self):
        """ Compute a multiline description of this product, in the context of sales
                (do not use for purchases or other display reasons that don't intend to use "description_sale").
            It will often be used as the default description of a sale order line referencing this product.
        """
        name = self.display_name
        if self.description_sale:
            name += '\n' + self.description_sale

        return name


    @api.depends("product_template_attribute_value_ids.weight_extra")
    def _compute_product_weight_extra(self):
        for product in self:
            product.weight_extra = sum(
                product.mapped("product_template_attribute_value_ids.weight_extra")
            )

    def _compute_product_weight(self):
        for product in self:
            if product.config_ok:
                tmpl_weight = product.product_tmpl_id.weight
                product.weight = tmpl_weight + product.weight_extra
            else:
                product.weight = product.weight_dummy

    def _search_product_weight(self, operator, value):
        return [("weight_dummy", operator, value)]

    def _inverse_product_weight(self):
        """Store weight in dummy field"""
        self.weight_dummy = self.weight

    config_name = fields.Char(
        string="Configuration Name", compute="_compute_config_name"
    )
    weight_extra = fields.Float(compute="_compute_product_weight_extra")
    weight_dummy = fields.Float(string="Manual Weight", digits="Stock Weight")
    weight = fields.Float(
        compute="_compute_product_weight",
        inverse="_inverse_product_weight",
        search="_search_product_weight",
        store=False,
    )

    # product preset
    config_preset_ok = fields.Boolean(string="Is Preset")

    # Replace action.
    def get_product_attribute_values_action(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "podiatry.product_attribute_value_action"
        )
        value_ids = self.product_template_attribute_value_ids.ids
        action["domain"] = [("id", "in", value_ids)]
        context = safe_eval(action["context"], {"active_id": self.product_tmpl_id.id})
        context.update({"active_id": self.product_tmpl_id.id})
        action["context"] = context
        return action

    def _compute_config_name(self):
        """Compute the name of the configurable products and use template
        name for others"""
        for product in self:
            if product.config_ok:
                product.config_name = product._get_config_name()
            else:
                product.config_name = product.name

    def _get_product_attributes_values_dict(self):
        # Retrieve first the attributes from template to preserve order
        res = self.product_tmpl_id._get_product_attributes_dict()
        for val in res:
            value = self.product_template_attribute_value_ids.filtered(
                lambda x: x.attribute_id.id == val["attribute_id"]
            )
            val["value_id"] = value.product_attribute_value_id.id
        return res

    def _get_product_attributes_values_text(self):
        description = self.product_template_attribute_value_ids.mapped(
            lambda x: "{}: {}".format(x.attribute_id.name, x.name)
        )
        if description:
            return "{}\n{}".format(self.product_tmpl_id.name, "\n".join(description))
        else:
            return self.product_tmpl_id.name

    def reconfigure_product(self):
        """launches a product configurator wizard with a linked
        template and variant in order to re-configure an existing product.
        It is essentially a shortcut to pre-fill configuration
        data of a variant"""
        self.ensure_one()

        extra_vals = {"product_id": self.id}
        return self.product_tmpl_id.create_config_wizard(extra_vals=extra_vals)

    @api.model
    def check_config_user_access(self, mode):
        """Check user have access to perform action(create/write/delete)
        on configurable products"""
        if not self.env["product.template"]._check_config_group_rights():
            return True
        config_manager = self.env.user.has_group(
            "podiatry.group_product_configurator_manager"
        )
        config_user = self.env.user.has_group(
            "podiatry.group_product_configurator"
        )
        user_root = self.env.ref("base.user_root")
        user_admin = self.env.ref("base.user_admin")
        if (
            config_manager
            or (config_user and mode not in ["delete"])
            or self.env.user.id in [user_root.id, user_admin.id]
        ):
            return True
        raise ValidationError(
            _(
                "Sorry, you are not allowed to create/change this kind of "
                "document. For more information please contact your manager."
            )
        )

    @api.model
    def _build_attributes_domain(self, product_template, product_attributes):
        domain = []
        cont = 0
        attributes_ids = []
        if product_template:
            for attr_line in product_attributes:
                if isinstance(attr_line, dict):
                    attributes_ids.append(attr_line.get("attribute_id"))
                else:
                    attributes_ids.append(attr_line.attribute_id.id)
            domain.append(("product_tmpl_id", "=", product_template.id))
            for attr_line in product_attributes:
                if isinstance(attr_line, dict):
                    value_id = attr_line.get("value_id")
                else:
                    value_id = attr_line.value_id.id
                if value_id:
                    ptav = self.env["product.template.attribute.value"].search(
                        [
                            ("product_tmpl_id", "=", product_template.id),
                            ("attribute_id", "in", attributes_ids),
                            ("product_attribute_value_id", "=", value_id),
                        ]
                    )
                    if ptav:
                        domain.append(
                            ("product_template_attribute_value_ids", "=", ptav.id)
                        )
                        cont += 1
        return domain, cont

    def unlink(self):
        """- Signal unlink from product variant through context so
        removal can be stopped for configurable templates
        - check access rights of user(configurable products)"""
        config_product = any(p.config_ok for p in self)
        if config_product:
            self.env["product.product"].check_config_user_access(mode="delete")
        ctx = dict(self.env.context, unlink_from_variant=True)
        self.env.context = ctx
        return super(ProductProduct, self).unlink()

    @api.model
    def create(self, vals):
        """Patch for check access rights of user(configurable products)"""
        config_ok = vals.get("config_ok", False)
        if config_ok:
            self.check_config_user_access(mode="create")
        if vals.get("product_attribute_ids"):
            ptav = (
                self.env["product.template.attribute.value"]
                .search(
                    [
                        (
                            "product_tmpl_id",
                            "in",
                            [
                                x[2]["product_tmpl_id"]
                                for x in vals["product_attribute_ids"]
                            ],
                        ),
                        (
                            "product_attribute_value_id",
                            "in",
                            [
                                x[2]["value_id"]
                                for x in vals["product_attribute_ids"]
                                if x[2]["value_id"]
                            ],
                        ),
                    ]
                )
                .ids
            )
            vals.pop("product_attribute_ids")
            vals["product_template_attribute_value_ids"] = [(4, x) for x in ptav]
        obj = self.with_context(product_name=vals.get("name", ""))
        return super(ProductProduct, obj).create(vals)


    # @api.model
    # def create(self, vals):
    #     """Patch for check access rights of user(configurable products)"""
    #     config_ok = vals.get("config_ok", False)
    #     if config_ok:
    #         self.check_config_user_access(mode="create")
    #     return super(ProductProduct, self).create(vals)

    def write(self, vals):
        """Patch for check access rights of user(configurable products)"""
        change_config_ok = "config_ok" in vals
        configurable_products = self.filtered(lambda product: product.config_ok)
        if change_config_ok or configurable_products:
            self[:1].check_config_user_access(mode="write")

        return super(ProductProduct, self).write(vals)

    def name_get(self):
        """We need to add this for avoiding an odoo.exceptions.AccessError due
        to some refactoring done upstream on read method + variant name_get
        in Odoo. With this, we avoid to call super on the specific case of
        virtual records, providing simply the name, which is acceptable.
        """
        res = []
        for product in self:
            if isinstance(product.id, models.NewId):
                res.append((product.id, product.name))
            else:
                res.append(super(ProductProduct, product).name_get()[0])
        return res

    def _compute_product_price_extra(self):
        standard_products = self.filtered(lambda product: not product.config_ok)
        config_products = self - standard_products
        if standard_products:
            return super(
                ProductProduct, standard_products
            )._compute_product_price_extra()
        for product in config_products:
            attribute_value_obj = self.env["product.attribute.value"]
            value_ids = (
                product.product_template_attribute_value_ids.product_attribute_value_id
            )
            extra_prices = attribute_value_obj.get_attribute_value_extra_prices(
                product_tmpl_id=product.product_tmpl_id.id, pt_attr_value_ids=value_ids
            )
            product.price_extra = sum(extra_prices.values())

class ProductWithWeightInKg(models.Model):
    """Rename the field weight to `Weight in kg`."""

    _inherit = 'product.product'

    weight = fields.Float(string='Weight in kg')

class ProductWithWeightWithTrackVisibility(models.Model):
    """Add track_visibility to the field weight."""

    _inherit = 'product.product'

    weight = fields.Float(tracking=True)

class ProductWithWeightInUoM(models.Model):
    """Add the fields weight_in_uom and specific_weight_uom_id to products.

    The weight can not be negative.
    """

    _inherit = 'product.product'

    weight_in_uom = fields.Float(
        'Weight', digits='Stock Weight',
        tracking=True)

    specific_weight_uom_id = fields.Many2one(
        'uom.uom', 'Weight UoM', ondelete='restrict',
        tracking=True)

    @api.constrains('weight_in_uom')
    def _check_weight_is_not_negative(self):
        """Check that dimensions are strictly positive."""
        for product in self:
            if product.weight_in_uom < 0:
                raise ValidationError(_(
                    'The weight of a product ({product}) can not be negative.'
                ).format(product=product.display_name))

    @api.model
    def create(self, vals):
        """After creating a product, synchronize its weight in Kg with its weight in uom.

        A product can be created with either the weight in Kg or the weight in the
        product's unit of measure.
        """
        vals_copy = vals.copy()
        res = super().create(vals)

        if vals_copy.get('weight_in_uom'):
            res.update_weight_from_weight_in_uom()

        elif vals_copy.get('weight'):
            res.update_weight_in_uom_from_weight()

        return res

    def write(self, vals):
        """Synchronize the weight in Kg and the weight in the uom of the product.

        Changing the value of one of the 2 fields should update the value for the other.
        """
        vals_copy = vals.copy()
        super().write(vals)

        updating_weight_in_uom = 'weight_in_uom' in vals_copy or 'specific_weight_uom_id' in vals_copy
        updating_weight_in_uom_from_weight = self._context.get(
            'updating_weight_in_uom_from_weight')

        updating_weight = 'weight' in vals_copy
        updating_weight_from_weight_in_uom = self._context.get(
            'updating_weight_from_weight_in_uom')

        if updating_weight_in_uom and not updating_weight_in_uom_from_weight:
            for record in self:
                record.update_weight_from_weight_in_uom()

        elif updating_weight and not updating_weight_from_weight_in_uom:
            for record in self:
                record.update_weight_in_uom_from_weight()

        return True

    def update_weight_from_weight_in_uom(self):
        """Update the weight in kg from the weight in uom."""
        uom_kg = self.env.ref('uom.product_uom_kgm')
        weight = self.specific_weight_uom_id._compute_quantity(
            self.weight_in_uom, uom_kg)
        self.with_context(updating_weight_from_weight_in_uom=True).write(
            {'weight': weight})

    def update_weight_in_uom_from_weight(self):
        """Update the weight in uom from the weight in kg."""
        uom_kg = self.env.ref('uom.product_uom_kgm')
        uom = self.specific_weight_uom_id or uom_kg
        weight_in_uom = uom_kg._compute_quantity(self.weight, uom)
        self.with_context(updating_weight_in_uom_from_weight=True).write({
            'weight_in_uom': weight_in_uom,
            'specific_weight_uom_id': uom.id,
        })

class ProductWithDimensions(models.Model):
    """Add dimension fields to products."""

    _inherit = 'product.product'

    height = fields.Float(
        'Height',
        tracking=True,
        digits='Product Dimension',
    )

    length = fields.Float(
        'Length',
        tracking=True,
        digits='Product Dimension',
    )

    width = fields.Float(
        'Width',
        tracking=True,
        digits='Product Dimension',
    )

    dimension_uom_id = fields.Many2one(
        'uom.uom', 'Dimension UoM', ondelete='restrict',
        tracking=True)

    @api.constrains('height')
    def _check_height_is_not_negative(self):
        """Check that dimensions are strictly positive."""
        for product in self:
            if product.height < 0:
                raise ValidationError(_(
                    'The height of a product ({product}) can not be negative.'
                ).format(product=product.display_name))

    @api.constrains('length')
    def _check_length_is_not_negative(self):
        """Check that dimensions are strictly positive."""
        for product in self:
            if product.length < 0:
                raise ValidationError(_(
                    'The length of a product ({product}) can not be negative.'
                ).format(product=product.display_name))

    @api.constrains('width')
    def _check_width_is_not_negative(self):
        """Check that dimensions are strictly positive."""
        for product in self:
            if product.width < 0:
                raise ValidationError(_(
                    'The width of a product ({product}) can not be negative.'
                ).format(product=product.display_name))

class ProductWithVolumeDecimalPrecision(models.Model):
    """Add a decimal precision to the volume of a product."""

    _inherit = 'product.product'

    volume = fields.Float(digits='Product Volume')

class ProductWithVolumeComputedFromDimensions(models.Model):
    """Compute the field volume from dimension fields."""

    _inherit = 'product.product'

    volume = fields.Float(compute='_compute_volume', store=True)

    def _get_volume_without_rounding(self):
        """Get the volume of the product without rounding the result."""
        meter = self.env.ref('uom.product_uom_meter')

        def to_meter(from_uom, dimension):
            """Convert a dimension from a given uom to meter.

            :param from_uom: the unit of measure of the dimension to convert
            :param dimension: the dimension to convert
            :return: the dimension in meter
            """
            return from_uom._compute_quantity(dimension, meter, round=False)

        height_in_meter = to_meter(self.dimension_uom_id, self.height)
        length_in_meter = to_meter(self.dimension_uom_id, self.length)
        width_in_meter = to_meter(self.dimension_uom_id, self.width)

        return height_in_meter * length_in_meter * width_in_meter

    @api.depends('height', 'length', 'width', 'dimension_uom_id')
    def _compute_volume(self):
        """Compute the volume of the product."""
        for product in self:
            product.volume = product._get_volume_without_rounding()

class ProductWithDensity(models.Model):
    """Add the field density to products."""

    _inherit = 'product.product'

    density = fields.Float(
        'Density',
        compute='_compute_density',
        digits='Product Density',
        store=True,
    )

    @api.depends('weight', 'height', 'length', 'width', 'dimension_uom_id')
    def _compute_density(self):
        """Compute the density of the product.

        For computing the volume, we use the volume without rounding.
        A very small volume will result in a very high density.
        Therefore, the precision in units of measure has an important impact on
        the result.
        """
        for product in self:
            volume = product._get_volume_without_rounding()
            product.density = product.weight / volume if volume else None

