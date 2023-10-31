from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

DEVICE_TYPES = [
    ('die', "Die"),
    ('counter_die', "Counter Die"),
    ('mold', "Mold"),
]


# TODO: move this to more generic place.
def _get_selection_map(record, fname):
    return dict(record._fields[fname]._description_selection(record.env))


class ProductCategory(models.Model):
    _inherit = 'product.category'

    device_type = fields.Selection(
        DEVICE_TYPES,
        copy=False,
    )
    nearest_device_type = fields.Selection(
        DEVICE_TYPES,
        compute='_compute_nearest_device_type',
        store=True,
    )

    @api.depends(
        'device_type',
        'parent_id.nearest_device_type',
        'child_id.nearest_device_type',
        'parent_id.device_type',
        'child_id.device_type',
    )
    def _compute_nearest_device_type(self):
        for rec in self:
            rec.nearest_device_type = rec.get_nearest_device_type()

    def validate_device_type(self, device_type, raise_err=True):
        """Validate if given device_type matches nearest category type."""
        self.ensure_one()
        if self.nearest_device_type != device_type:
            if raise_err:
                selection_map = _get_selection_map(self, 'device_type')
                label = selection_map[device_type]
                raise ValidationError(
                    _(
                        "%(label)s must have Category (%(categ)s) with %(label)s type!",
                        label=label,
                        categ=self.name,
                    )
                )
            return False
        return True

    def get_nearest_device_type(self):
        self.ensure_one()
        if self.device_type:
            return self.device_type
        if self.parent_id:
            return self.parent_id.get_nearest_device_type()
        return False
