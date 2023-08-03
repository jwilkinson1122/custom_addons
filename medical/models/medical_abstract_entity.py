# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import threading
import base64
from datetime import datetime
import re

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError

class ImageMixin(models.AbstractModel):
    _name = 'image.mixin'
    _description = "Image Mixin"

    # all image fields are base64 encoded and PIL-supported

    image_1920 = fields.Image("Image", max_width=1920, max_height=1920)

    # resized fields stored (as attachment) for performance
    image_1024 = fields.Image("Image 1024", related="image_1920", max_width=1024, max_height=1024, store=True)
    image_512 = fields.Image("Image 512", related="image_1920", max_width=512, max_height=512, store=True)
    image_256 = fields.Image("Image 256", related="image_1920", max_width=256, max_height=256, store=True)
    image_128 = fields.Image("Image 128", related="image_1920", max_width=128, max_height=128, store=True)


class MedicalAbstractEntity(models.AbstractModel):
    _name = 'medical.abstract.entity'
    _description = 'Medical Abstract Entity'
    _inherits = {'res.partner': 'partner_id'}
    _inherit = ['mail.thread', 'image.mixin']
    # _rec_name = 'name'
    
    def _default_category(self):
            return self.env['res.partner.category'].browse(self._context.get('category_id'))
    
    def _lang_get(self):
        return self.env['res.lang'].get_installed()


    # Redefine ``active`` so that it is managed independently from partner.
    active = fields.Boolean(
        default=True,
    )
    partner_id = fields.Many2one(
        string='Related Partner',
        comodel_name='res.partner',
        required=True,
        ondelete='cascade',
        index=True,
    )
    child_ids = fields.One2many('res.partner', 'parent_id', string='Contact', domain=[('active', '=', True)])  # force "active_test" domain to bypass _search() override

    type = fields.Selection(
        default=lambda s: s._name,
        related='partner_id.type',
    )
     # name = fields.Char(index=True)
    name = fields.Char(string='Title', required=False, translate=True)
    display_name = fields.Char(compute='_compute_display_name', recursive=True, store=True, index=True)
    code = fields.Char(string='Partner Entity Code', required=False)
    email = fields.Char()
    is_company = fields.Boolean(string='Is a Company', default=False,
        help="Check if the contact is a company, otherwise it is a person")
    company_name = fields.Char('Company Name')

    title = fields.Many2one('res.partner.title')

    parent_id = fields.Many2one('res.partner', string='Related Company', index=True)
    user_ids = fields.One2many('res.users', 'partner_id', string='Users', auto_join=True)
    function = fields.Char(string='Job Position')
    type = fields.Selection(
        [('contact', 'Contact'),
         ('invoice', 'Invoice Address'),
         ('delivery', 'Delivery Address'),
         ('other', 'Other Address'),
         ("private", "Private Address"),
        ], string='Address Type',
        default='contact',
        help="Invoice & Delivery addresses are used in sales orders. Private addresses are only visible by authorized users.")
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
    gender = fields.Selection(
        [('M', 'Male'),
         ('F', 'Female'),
         ('O', 'Other'),
         ], string='Gender'
    )
    comment = fields.Html(string='Notes')
    color = fields.Integer(string='Color Index', default=0)
    
    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        vals = self._create_vals(vals)
        return super(MedicalAbstractEntity, self).create(vals)
    
    @api.depends('is_company', 'name', 'parent_id.display_name', 'type', 'company_name')
    def _compute_display_name(self):
        diff = dict(show_address=None, show_address_only=None, show_email=None, html_format=None, show_vat=None)
        names = dict(self.with_context(**diff).name_get())
        for partner in self:
            partner.display_name = names.get(partner.id)

    def toggle_active(self):
        """ It toggles patient and partner activation. """
        for record in self:
            super(MedicalAbstractEntity, self).toggle_active()
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
            vals['image_256'] = self._get_default_image_encoded(vals)
        return vals

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
        if vals.get('image_256'):
            return False
        if any((getattr(threading.currentThread(), 'testing', False),
                self._context.get('install_mode'))):
            if not self.env.context.get('__image_create_allow'):
                return False
        return True

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
        image_path = self._get_default_image_path(vals)
        if not image_path:
            return
        with open(image_path, 'rb') as image:
            # return image.read().encode('base64')
            return base64.b64encode(image.read())

    def _get_default_image_path(self, vals):
        """ Overload this in child classes in order to add a default image.

        Example:

            .. code-block:: python

            @api.model
            def _get_default_image_path(self, vals):
                res = super(MedicalPatient, self)._get_default_image_path(vals)
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
    
    def open_parent(self):
        """Utility method used to add an "Open Parent" button in partner
        views"""
        self.ensure_one()
        address_form_id = self.env.ref("base.view_partner_address_form").id
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "view_mode": "form",
            "views": [(address_form_id, "form")],
            "res_id": self.parent_id.id,
            "target": "new",
            "flags": {"form": {"action_buttons": True}},
        }


    def toggle(self, attr):
        if getattr(self, attr) is True:
            self.write({attr: False})
        elif getattr(self, attr) is False:
            self.write({attr: True})
