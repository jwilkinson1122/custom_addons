# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    animal_ids = fields.One2many('clinic.animal', 'owner_id')

    @api.model
    def rpc_create(self, values):
        animal_obj = self.env['clinic.animal']
        if values.get('name'):
            if 'animals' in values:
                animals_values = values.pop('animals')
            else:
                animals_values = []

            partners = self.search([('name', '=like', values['name'])])
            if partners:
                partner = partners[0]
                partner.write(values)
            else:
                partner = self.create(values)

            if partner:
                for animal_values in animals_values:
                    animal_values['owner_id'] = partner.id
                    animals = animal_obj.search([('name', '=like', animal_values['name'])])
                    if animals:
                        animal = animals[0]
                        animal.write(animal_values)
                    else:
                        animal_obj.create(animal_values)
                return True
            else:
                return False
        else:
            return False

    @api.model
    def rpc_create2(self, values):
        animal_obj = self.env['clinic.animal']

        if values.get('name'):
            if 'animals' in values:
                animals_values = values.pop('animals')
                values['animal_ids'] = []
            else:
                animals_values = False

            partners = self.search([('name', '=like', values['name'])])
            partner = partners and partners[0] or False

            for animal_values in animals_values:
                animals = animal_obj.search([('name', '=like', animal_values['name'])])
                animal = animals and animals[0]
                if animal:
                    values['animal_ids'].append(
                        (1, animal.id, animal_values)
                    )
                else:
                    values['animal_ids'].append(
                        (0, False, animal_values)
                    )

            if partner:
                partner.write(values)
            else:
                self.create(values)

            return True
        else:
            return False
