# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Pet(models.Model):
    _name = 'pet_clinic.pet'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'rec_name'

    pet_id = fields.Char(string='ID', required=True, copy=False, readonly=True,
                         index=True, default=lambda self: _('New'))
    name = fields.Char(string='Name', required=True)
    rec_name = fields.Char(string='Recname',
                           compute='_compute_fields_rec_name')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], default='male', string="Gender", required=True)
    age = fields.Char(string='Age')
    image = fields.Binary(string='Image')
    description = fields.Text(string='Description')

    # Pet -> Type
    pet_type = fields.Many2one('pet_clinic.pet.type',
                               string='Species')
    pet_type_name = fields.Char(related='pet_type.name',
                                string='Species')

    # Pet -> Breed
    pet_breed = fields.Many2one('pet_clinic.pet.breed', domain="[('pet_type','=',pet_type)]",
                                string='Breed')
    pet_breed_name = fields.Char(related='pet_breed.name',
                                 string='Breed')

    # Owner
    owner = fields.Many2one(
        'pet_clinic.client', string='Owner', store=True, readonly=False)
    owner_id = fields.Integer(
        related='owner.id', string='Pet Owner ID')
    owner_name = fields.Char(
        related='owner.name', string='Owner Name')

    # Appointment
    appointment_count = fields.Integer(compute='compute_appointment_count')

    @api.depends('name', 'pet_type_name', 'pet_breed_name')
    def _compute_fields_rec_name(self):
        for pet in self:
            if(pet.pet_type_name == False and pet.pet_breed_name == False):
                pet.rec_name = '{}'.format(pet.name)
            elif(pet.pet_breed_name == False):
                pet.rec_name = '{} - {}'.format(pet.name,
                                                pet.pet_type_name)
            elif(pet.pet_type_name == False):
                pet.rec_name = '{}'.format(pet.name)
            else:
                pet.rec_name = '{} - {} {}'.format(pet.name,
                                                   pet.pet_type_name, pet.pet_breed_name)

    @api.model
    def create(self, vals):
        if vals.get('pet_id', _('New')) == _('New'):
            vals['pet_id'] = self.env['ir.sequence'].next_by_code(
                'pet.seq') or _('New')
        result = super(Pet, self).create(vals)
        return result

    # Button Pet Handle
    @api.multi
    def open_pet_appointment(self):
        return {
            'name': _('Appointments'),
            'domain': [('pet', '=', self.id)],
            'view_type': 'form',
            'res_model': 'pet_clinic.appointment',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }
    # Button Pet Count

    def compute_appointment_count(self):
        for record in self:
            record.appointment_count = self.env['pet_clinic.appointment'].search_count(
                [('pet', '=', self.id)])


class PetType(models.Model):
    _name = 'pet_clinic.pet.type'
    name = fields.Char(string='Name', required=True)


class PetBreed(models.Model):
    _name = 'pet_clinic.pet.breed'
    name = fields.Char(string='Name', required=True)
    pet_type = fields.Many2one('pet_clinic.pet.type',
                               string='Type', required=True)
