# Copyright 2008 Luis Falcon <falcon@gnuhealth.org>
# Copyright 2017 LasLabs Inc.
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import api, fields, models


class MedicalMedicament(models.Model):
    _inherit = ['mail.thread']
    _inherits = {'product.product': 'product_id'}
    _name = 'medical.medicament'
    _description = 'Inherits product model to medical medicament'

    def onchange_type(self, _type):
        return self.product_id.onchange_type(_type)

    def onchange_uom(self, uom_id, uom_po_id):
        return self.product_id.onchange_uom(uom_id, uom_po_id)

    def name_get(self):
        res = []
        for rec in self:
            name = '%s - %s' % (rec.product_id.name, rec.drug_form_id.name)
            res.append((rec.id, name))
        return res

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='products',
        required=True,
        ondelete="cascade"
    )
    drug_form_id = fields.Many2one(
        comodel_name='medical.drug.form',
        string='Drug Form',
        required=True
    )
    drug_route_id = fields.Many2one(
        comodel_name='medical.drug.route',
        string='Drug Route'
    )
    active_component = fields.Char(string='Active Component')
    indications = fields.Text(string='Indications')
    therapeutic_action = fields.Char(string='Therapeutic Action')
    pregnancy_category = fields.Selection(
        [
            ('a', 'A'),
            ('b', 'B'),
            ('c', 'C'),
            ('d', 'D'),
            ('x', 'X'),
            ('n', 'N'),
        ],
        help='** FDA Pregancy Categories ***\n'
        'CATEGORY A: Adequate and well-controlled human studies have '
        'failed to demonstrate a risk to the fetus in the first '
        'trimester of pregnancy (and there is no evidence of risk in '
        'later trimesters).\n\n'
        'CATEGORY B: Animal reproduction studies have failed to '
        'demonstrate a risk to the fetus and there are no adequate '
        'and well-controlled studies in pregnant women OR Animal '
        'studies have shown an adverse effect, but adequate and '
        'well-controlled studies in pregnant women '
        'have failed to demonstrate a risk to the fetus in any '
        'trimester.\n\n'
        'CATEGORY C: Animal reproduction studies have shown an '
        'adverse effect on the fetus and there are no adequate and '
        'well-controlled  studies in humans, but potential benefits '
        'may warrant use of the drug in pregnant women despite '
        'potential risks. \n\n '
        'CATEGORY D: There is positive evidence of human fetal '
        'risk based on adverse reaction data from investigational '
        'or marketing experience or studies in humans, but potential '
        'benefits may warrant use of the drug in pregnant women '
        'despite potential risks.\n\n'
        'CATEGORY X: Studies in animals or humans have demonstrated '
        'fetal abnormalities and/or there is positive evidence of '
        'human fetal risk based on adverse reaction data from '
        'investigational or marketing experience, and the risks '
        'involved in use of the drug in pregnant '
        'women clearly outweigh potential benefits.\n\n'
        'CATEGORY N: Not yet classified.'
    )
    is_pregnant = fields.Boolean(
        string='Pregnancy warning',
        help='The drug represents risk to pregnancy or lactancy'
    )
    dosage_instruction = fields.Text(string='Dosage Instructions')
    pregnancy = fields.Text(string='Pregnancy and Lactancy')
    notes = fields.Text(string='notes')
    overdosage = fields.Text(string='Overdosage')
    storage = fields.Text(string='storage')
    adverse_reaction = fields.Text(string='Adverse Reaction')
    presentation = fields.Text(string='Presentation')
    composition = fields.Text(string='Composition')

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        vals['is_medicament'] = True
        return super(MedicalMedicament, self).create(vals)
