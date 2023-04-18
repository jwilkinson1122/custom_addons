from odoo import fields, models, api
from odoo.exceptions import ValidationError


class HospitalParent(models.Model):
    _name = 'hospital.parent'
    _description = "this is the patient's parents"
    _rec_name = 'parent_name'
    parent_name = fields.Char(string='Parent_name', required=False)
    mobile = fields.Char(string='Mobile', required=False)
    state = fields.Selection(string='State', selection=[('active', 'Active'),
                                                        ('close', 'Close'), ],
                             required=False, )

    compute_parent_name = fields.Char(string='Compute_parent_name',
                                      compute='_compute_title',
                                      inverse='_inverse_title', required=False)

    documents = fields.Binary(string="docs")
    documents_name = fields.Char(string="file name")
    letter = fields.Html(string='parent letter')

    def _compute_title(self):
        for rec in self:
            if rec.parent_name:
                rec.compute_parent_name = rec.parent_name.title()

    def _inverse_title(self):
        for rec in self:
            if rec.parent_name:
                rec.parent_name = rec.compute_parent_name.title()

    # override built-in duplicate method
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('parent_name'):
            if 'copy' in self.parent_name:
                (current_name, copy_number) = self.parent_name.split("#")
                default[
                    'parent_name'] = f"{current_name}#{(int(copy_number) + 1)}"
            else:
                default['parent_name'] = f"{self.parent_name} copy#1"
        return super(HospitalParent, self).copy(default)

    # override built-in delete method
    def unlink(self):
        if self.state == 'active':
            raise ValidationError(
                f"{self.parent_name} is an active parent can't be deleted")
        print(f"{self.parent_name} has been deleted successfully")
        return super(HospitalParent, self).unlink()

    #  user defined constrains
    @api.constrains('parent_name')
    def check_parent_name(self):
        print(self)
        for rec in self:
            matched_patient = self.env['hospital.parent'].search([
                ('parent_name', '=', rec.parent_name), ('id', '!=', rec.id)])
            if matched_patient:
                raise ValidationError("الاسم ده موجود قبل كدة")

    # override _rec_name value
    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.parent_name} [{rec.id}]"
            result.append((rec.id, name))
        return result

    def write(self, values):
        result = super(HospitalParent, self).write(values)
        print("write function called")
        return result
