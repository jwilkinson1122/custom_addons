from odoo import fields, models, api

class Visit(models.Model):
    _name = "animal.visit"
    _description = "Animals visits table"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order ="date desc"

    animal_id = fields.Many2one('animal', string='Animal', required=True)  # Campo de relación Many2one con animal
    date = fields.Datetime(string="Date", required=True)
    name = fields.Char(related="animal_id.name", string="Animal", required=True, readonly=False)
    owner = fields.Many2one(related="animal_id.owner", string="Owner", readonly=True, store=True)
    sex = fields.Selection(related="animal_id.sex", string="Sex", readonly=True, store=True)
    breed = fields.Many2one(related="animal_id.breed", string="Breed", readonly=True, store=True)
    specie = fields.Many2one(related="animal_id.species", string="Specie", readonly=True, store=True)
    reason = fields.Text(string="Reason")
    suggested_treatment = fields.Text(string="Suggested treatment")
    observations = fields.Text(string="Observations")
    sequence = fields.Char(string="Reference", required=True, copy=False, readonly=True, index=True, default=lambda self: 'New')

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('animal.visit.sequence') or 'New'
        return super(Visit, self).create(vals)
