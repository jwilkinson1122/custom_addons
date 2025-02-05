from odoo import fields, models, api, _

class ResPartner(models.Model):
    _inherit = "res.partner"

    # ---------------------------------------------------------------------
    # Affiliates - is_company = True, company_type: company
    # ---------------------------------------------------------------------

    affiliate_ids = fields.One2many(
        'res.partner',
        'parent_id',   
        string='Affiliates',
        compute='_compute_affiliates',
        help="Direct and indirect affiliates",
        compute_sudo=True,
        store=True
    )
    
    affiliate_all_count = fields.Integer('Indirect Affiliates Count',
        compute='_compute_affiliates', recursive=True, store=False, compute_sudo=True)


    @api.depends('parent_id')
    def _compute_affiliates(self):
        for partner in self:
            # Skip computation when record is being written
            if self._context.get('skip_affiliate_compute'):
                continue
            
            affiliates = partner._get_affiliates(parents=self.env['res.partner'])
            partner.affiliate_ids = affiliates.filtered(lambda a: a.parent_id == partner)
            partner.affiliate_all_count = len(affiliates)


    def _get_affiliates(self, parents=None, visited=None):
        if visited is None:
            visited = self.env['res.partner']
        if not parents:
            parents = self.env[self._name]

        indirect_affiliates = self.env[self._name]
        parents |= self

        direct_affiliates = self.env['res.partner'].search([
            ('parent_id', '=', self.id),
            ('is_company', '=', True)
        ]) - parents

        direct_affiliates = direct_affiliates - visited
        visited |= direct_affiliates

        child_affiliates = direct_affiliates._get_affiliates(parents=parents, visited=visited) if direct_affiliates else self.browse()
        indirect_affiliates |= child_affiliates
        return indirect_affiliates | direct_affiliates


    def open_affiliate_form(self):
        """Open affiliate contact form from the parent partner form view"""
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }

    # ---------------------------------------------------------------------
    # Contacts / Patients - is_company = False, company_type: person
    # ---------------------------------------------------------------------

    is_patient = fields.Boolean(string='Is a Patient', default=False)
    patient_ids = fields.One2many('res.partner', 'responsible_contact_id', string='Patients')
    responsible_contact_id = fields.Many2one('res.partner', string='Responsible Contact')

    child_ids = fields.One2many(
        'res.partner',
        'parent_id',  
        string='Contacts',
        compute='_compute_children',
        help="Direct and Indirect Contacts",
        compute_sudo=True,
        store=True
    )

    child_all_count = fields.Integer('Indirect Contacts Count',
        compute='_compute_children', recursive=True, store=False, compute_sudo=True)

    @api.depends('child_ids', 'child_ids.child_all_count')
    def _compute_children(self):
        for partner in self:
            partner.child_ids = partner._get_children()
            partner.child_all_count = len(partner.child_ids)

    @api.depends('patient_ids')
    def _compute_patients(self):
        for partner in self:
            partner.direct_patients = partner.patient_ids
            partner.indirect_patients = partner.patient_ids.mapped('patient_ids')

    def _get_children(self, parents=None, visited=None):
        if visited is None:
            visited = self.env['res.partner']
        if not parents:
            parents = self.env[self._name]

        indirect_children = self.env[self._name]
        parents |= self

        # Only include persons (is_company=False)
        direct_children = self.child_ids.filtered(lambda c: not c.is_company) - parents
        direct_children = direct_children - visited
        visited |= direct_children

        child_children = direct_children._get_children(parents=parents, visited=visited) if direct_children else self.browse()
        indirect_children |= child_children
        return indirect_children | direct_children

    def open_child_form(self):
        """Open child contact form from the parent partner form view"""
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }
    

    def write(self, vals):
        if 'parent_id' in vals:
            self = self.with_context(skip_affiliate_compute=True)
        return super(ResPartner, self).write(vals)


 

    

