# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import threading
import base64
from datetime import datetime
import re

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError


class AbstractPartnerEntity(models.AbstractModel):
    _name = 'clv.abstract.partner_entity'
    _description = 'Abstract Partner Entity'
    _inherits = {'res.partner': 'partner_id'}
    # _inherit = ['mail.thread']

    _order = 'name'
    
    def _default_category(self):
        return self.env['res.partner.category'].browse(self._context.get('category_id'))
    
    def _lang_get(self):
        return self.env['res.lang'].get_installed()


    partner_id = fields.Many2one(
        string='Related Partner',
        comodel_name='res.partner',
        required=True,
        ondelete='cascade',
        index=True,
    )

    type = fields.Selection(
        default=lambda s: s._name,
        related='partner_id.type',
    )
    # name = fields.Char(index=True)
    name = fields.Char(string='Title', required=False, translate=True)
    code = fields.Char(string='Partner Entity Code', required=False)
    email = fields.Char()
    is_company = fields.Boolean(string='Is a Company', default=False,
        help="Check if the contact is a company, otherwise it is a person")
    title = fields.Many2one('res.partner.title')

    parent_id = fields.Many2one('res.partner', string='Related Company', index=True)
    user_ids = fields.One2many('res.users', 'partner_id', string='Users', auto_join=True)

    # address fields
    street = fields.Char()
    street2 = fields.Char()
    street_name = fields.Char(
        'Street Name', compute='_compute_street_data', inverse='_inverse_street_data', store=True)
    street_number = fields.Char(
        'House', compute='_compute_street_data', inverse='_inverse_street_data', store=True)
    street_number2 = fields.Char(
        'Door', compute='_compute_street_data', inverse='_inverse_street_data', store=True)

    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    country_code = fields.Char(related='country_id.code', string="Country Code")
    partner_latitude = fields.Float(string='Geo Latitude', digits=(10, 7))
    partner_longitude = fields.Float(string='Geo Longitude', digits=(10, 7))
    phone = fields.Char()
    mobile = fields.Char()
    lang = fields.Selection(_lang_get, string='Language',
                            help="All the emails and documents sent to this contact will be translated in this language.")
    category_id = fields.Many2many('res.partner.category', column1='partner_id', column2='category_id', string='Tags', default=_default_category)

    date_inclusion = fields.Datetime(
        string="Inclusion Date", required=False, readonly=False,
        default=lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

    contact_info_is_unavailable = fields.Boolean(
        string='Contact Information is unavailable',
        default=False,
    )

    # Redefine `active` so that it is managed independently from partner.
    active = fields.Boolean(
        default=True,
    )

    related_partner_id = fields.Integer(
        string='Related Partner ID',
        compute='_compute_related_partner_id'
    )

    @api.depends('partner_id')
    def _compute_related_partner_id(self):
        for register in self:
            if register.partner_id.id is not False:
                register.related_partner_id = register.partner_id.id
            else:
                register.related_partner_id = False

    _sql_constraints = [
        ('code_uniq',
         'UNIQUE (code)',
         u'Error! The Code must be unique!'),
    ]
    
    def _inverse_street_data(self):
        """Updates the street field.
        Writes the `street` field on the partners when one of the sub-fields in STREET_FIELDS
        has been touched"""
        street_fields = self._get_street_fields()
        for partner in self:
            street_format = (partner.country_id.street_format or
                '%(street_number)s/%(street_number2)s %(street_name)s')
            previous_field = None
            previous_pos = 0
            street_value = ""
            separator = ""
            # iter on fields in street_format, detected as '%(<field_name>)s'
            for re_match in re.finditer(r'%\(\w+\)s', street_format):
                # [2:-2] is used to remove the extra chars '%(' and ')s'
                field_name = re_match.group()[2:-2]
                field_pos = re_match.start()
                if field_name not in street_fields:
                    raise UserError(_("Unrecognized field %s in street format.", field_name))
                if not previous_field:
                    # first iteration: add heading chars in street_format
                    if partner[field_name]:
                        street_value += street_format[0:field_pos] + partner[field_name]
                else:
                    # get the substring between 2 fields, to be used as separator
                    separator = street_format[previous_pos:field_pos]
                    if street_value and partner[field_name]:
                        street_value += separator
                    if partner[field_name]:
                        street_value += partner[field_name]
                previous_field = field_name
                previous_pos = re_match.end()

            # add trailing chars in street_format
            street_value += street_format[previous_pos:]
            partner.street = street_value

    @api.depends('street')
    def _compute_street_data(self):
        """Splits street value into sub-fields.
        Recomputes the fields of STREET_FIELDS when `street` of a partner is updated"""
        street_fields = self._get_street_fields()
        for partner in self:
            if not partner.street:
                for field in street_fields:
                    partner[field] = None
                continue

            street_format = (partner.country_id.street_format or
                '%(street_number)s/%(street_number2)s %(street_name)s')
            street_raw = partner.street
            vals = self._split_street_with_params(street_raw, street_format)
            # assign the values to the fields
            for k, v in vals.items():
                partner[k] = v
            for k in set(street_fields) - set(vals):
                partner[k] = None

    def _split_street_with_params(self, street_raw, street_format):
        street_fields = self._get_street_fields()
        vals = {}
        previous_pos = 0
        field_name = None
        # iter on fields in street_format, detected as '%(<field_name>)s'
        for re_match in re.finditer(r'%\(\w+\)s', street_format):
            field_pos = re_match.start()
            if not field_name:
                #first iteration: remove the heading chars
                street_raw = street_raw[field_pos:]

            # get the substring between 2 fields, to be used as separator
            separator = street_format[previous_pos:field_pos]
            field_value = None
            if separator and field_name:
                #maxsplit set to 1 to unpack only the first element and let the rest untouched
                tmp = street_raw.split(separator, 1)
                if previous_greedy in vals:
                    # attach part before space to preceding greedy field
                    append_previous, sep, tmp[0] = tmp[0].rpartition(' ')
                    street_raw = separator.join(tmp)
                    vals[previous_greedy] += sep + append_previous
                if len(tmp) == 2:
                    field_value, street_raw = tmp
                    vals[field_name] = field_value
            if field_value or not field_name:
                previous_greedy = None
                if field_name == 'street_name' and separator == ' ':
                    previous_greedy = field_name
                # select next field to find (first pass OR field found)
                # [2:-2] is used to remove the extra chars '%(' and ')s'
                field_name = re_match.group()[2:-2]
            else:
                # value not found: keep looking for the same field
                pass
            if field_name not in street_fields:
                raise UserError(_("Unrecognized field %s in street format.", field_name))
            previous_pos = re_match.end()

        # last field value is what remains in street_raw minus trailing chars in street_format
        trailing_chars = street_format[previous_pos:]
        if trailing_chars and street_raw.endswith(trailing_chars):
            vals[field_name] = street_raw[:-len(trailing_chars)]
        else:
            vals[field_name] = street_raw
        return vals

    def write(self, vals):
        res = super(AbstractPartnerEntity, self).write(vals)
        if 'country_id' in vals and 'street' not in vals:
            self._inverse_street_data()
        return res

    def _formatting_address_fields(self):
        """Returns the list of address fields usable to format addresses."""
        return super(AbstractPartnerEntity, self)._formatting_address_fields() + self._get_street_fields()

    def _get_street_fields(self):
        """Returns the fields that can be used in a street format.
        Overwrite this function if you want to add your own fields."""
        return ['street_name', 'street_number', 'street_number2']


    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        vals = self._create_vals(vals)
        return super().create(vals)

    # @api.multi
    def toggle_active(self):
        """ It toggles entity and partner activation. """
        for record in self:
            super().toggle_active()
            if record.active:
                record.partner_id.active = True
            else:
                entities = record.env[record._name].search([
                    ('partner_id', 'child_of', record.partner_id.id),
                    ('parent_id', 'child_of', record.partner_id.id),
                    ('active', '=', True),
                ])
                if not entities:
                    record.partner_id.active = False

    @api.model
    def _create_vals(self, vals):
        """ Override this in child classes in order to add default values. """
        if self._allow_image_create(vals):
            vals['image_1920'] = self._get_default_image_encoded(vals)
        return vals

    # @api.model_cr_context
    def _allow_image_create(self, vals):
        """ It determines if conditions are present that should stop image gen.

        This is implemented so that tests aren't wildly creating images left
         and right for no reason. Child classes could also inherit this to
         provide custom rules for image generation.

        Note that this method explicitly allows image generation if
         ``__image_create_allow`` is a ``True`` value in the context. Any
         child that chooses to provide custom rules shall also adhere to this
         context, unless there is a documented reason to not do so.
        """
        if vals.get('image_1920'):
            return False
        if any((getattr(threading.currentThread(), 'testing', False),
                self._context.get('install_mode'))):
            if not self.env.context.get('__image_create_allow'):
                return False
        return True

    # @api.model_cr_context
    def _create_default_image(self, vals):
        base64_image = self._get_default_image_encoded(vals)
        if not base64_image:
            return
        return tools.image_resize_image_big(base64_image)

    def _get_default_image_encoded(self, vals):
        """ It returns the base64 encoded image string for the default avatar.

        Args:
            vals (dict): Values dict as passed to create.

        Returns:
            str: A base64 encoded image.
            NoneType: None if no result.
        """
        colorize, image_path, image = False, False, False

        image_path = self._get_default_image_path(vals)
        if not image_path:
            return

        if image_path:
            with open(image_path, 'rb') as f:
                image = f.read()

        if image and colorize:
            image = tools.image_colorize(image)

        return base64.b64encode(image)

    # @api.model_cr_context
    def _get_default_image_path(self, vals):
        """ Overload this in child classes in order to add a default image.

        Example:

            .. code-block:: python

            @api.model
            def _get_default_image_path(self, vals):
                res = super()._get_default_image_path(vals)
                if res:
                    return res
                image_path = odoo.modules.get_module_resource(
                    'base', 'static/src/img', 'patient-avatar.png',
                )
                return image_path

        Args:
            vals (dict): Values dict as passed to create.

        Returns:
            str: A file path to the image on disk.
            bool: False if error.
            NoneType: None if no result.
        """
        return  # pragma: no cover

    def toggle(self, attr):
        if getattr(self, attr) is True:
            self.write({attr: False})
        elif getattr(self, attr) is False:
            self.write({attr: True})

    # @api.multi
    # def do_set_contact_info_as_unavailable(self):

    #     for record in self:

    #         data_values = {}

    #         data_values['contact_info_is_unavailable'] = True

    #         data_values['street_name'] = False
    #         data_values['street2'] = False
    #         data_values['zip'] = False
    #         data_values['city'] = False
    #         data_values['state_id'] = False
    #         data_values['country_id'] = False
    #         # data_values['phone'] = False
    #         # data_values['mobile'] = False

    #         record.write(data_values)

    #     return True
