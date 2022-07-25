from odoo import api, fields, models


class Patient(models.Model):
    _name = "clinic.patient"
    _description = "Clinic Patient"
    _inherits = {"res.partner": "partner_id"}
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    # patient_number = fields.Char()
    partner_id = fields.Many2one(
        "res.partner", delegate=True, ondelete="cascade", required=True
    )
    patient_number = fields.One2many(
        comodel_name="res.partner.id_number",
        inverse_name="partner_id",
        string="Identification Numbers",
    )

    name = fields.Char(string="Name")
    ref = fields.Char(string="Reference")
    # species_id = fields.Many2one(
    #     "patient.species", string="Species", required=True)
    # breed_id = fields.Many2one("patient.breed", string="Breed", required=True)
    # color_id = fields.Many2one("patient.color", string="Color")
    # size = fields.Char(string="Size")
    weight = fields.Float(string="Weight (in lbs)")
    birth_date = fields.Date(string="Birth Date")
    gender = fields.Selection(
        string="Gender",
        selection=[
            ("female", "Female"),
            ("male", "Male"),
        ],
        default="female",
        required=True,
    )
    active = fields.Boolean(default=True)
    # image = fields.Binary(
    #     "Image", attachment=True, help="This field holds the photo of the patient."
    # )

    # @api.onchange("species_id")
    # def onchange_species(self):
    #     self.breed_id = False

    # @api.onchange("breed_id")
    # def onchange_breed(self):
    #     self.color_id = False

    @api.depends("id_numbers")
    def _compute_identification(self, field_name, category_code):
        """Compute a field that indicates a certain ID type.

        Use this on a field that represents a certain ID type. It will compute
        the desired field as that ID(s).

        This ID can be worked with as if it were a Char field, but it will
        be relating back to a ``res.partner.id_number`` instead.

        Example:

            .. code-block:: python

            social_security = fields.Char(
                compute=lambda s: s._compute_identification(
                    'social_security', 'SSN',
                ),
                inverse=lambda s: s._inverse_identification(
                    'social_security', 'SSN',
                ),
                search=lambda s, *a: s._search_identification(
                    'SSN', *a
                ),
            )

        Args:
            field_name (str): Name of field to set.
            category_code (str): Category code of the Identification type.
        """
        for record in self:
            id_numbers = record.id_numbers.filtered(
                lambda r: r.category_id.code == category_code
            )
            if not id_numbers:
                # As this is used as a compute method
                # we need to assign something
                record[field_name] = False
                continue
            value = id_numbers[0].name
            record[field_name] = value

    def _inverse_identification(self, field_name, category_code):
        """Inverse for an identification field.

        This method will create a new record, or modify the existing one
        in order to allow for the associated field to work like a Char.

        If a category does not exist of the correct code, it will be created
        using `category_code` as both the `name` and `code` values.

        If the value of the target field is unset, the associated ID will
        be deactivated in order to preserve history.

        Example:

            .. code-block:: python

            social_security = fields.Char(
                compute=lambda s: s._compute_identification(
                    'social_security', 'SSN',
                ),
                inverse=lambda s: s._inverse_identification(
                    'social_security', 'SSN',
                ),
                search=lambda s, *a: s._search_identification(
                    'SSN', *a
                ),
            )

        Args:
            field_name (str): Name of field to set.
            category_code (str): Category code of the Identification type.
        """
        for record in self:
            id_number = record.id_numbers.filtered(
                lambda r: r.category_id.code == category_code
            )
            record_len = len(id_number)
            # Record for category is not existent.
            if record_len == 0:
                name = record[field_name]
                if not name:
                    # No value to set
                    continue
                category = self.env["res.partner.id_category"].search(
                    [("code", "=", category_code)]
                )
                if not category:
                    category = self.env["res.partner.id_category"].create(
                        {"code": category_code, "name": category_code}
                    )
                self.env["res.partner.id_number"].create(
                    {"partner_id": record.id, "category_id": category.id, "name": name}
                )
            # There was an identification record singleton found.
            elif record_len == 1:
                value = record[field_name]
                if value:
                    id_number.name = value
                else:
                    id_number.active = False
            # Guard against writing wrong records.
            else:
                raise ValidationError(
                    _(
                        "This %s has multiple IDs of this type (%s), so a write "
                        "via the %s field is not possible. In order to fix this, "
                        "please use the IDs tab."
                    )
                    % (record._name, category_code, field_name)
                )

    @api.model
    def _search_identification(self, category_code, operator, value):
        """Search method for an identification field.

        Example:

            .. code-block:: python

            social_security = fields.Char(
                compute=lambda s: s._compute_identification(
                    'social_security', 'SSN',
                ),
                inverse=lambda s: s._inverse_identification(
                    'social_security', 'SSN',
                ),
                search=lambda s, *a: s._search_identification(
                    'SSN', *a
                ),
            )

        Args:
            category_code (str): Category code of the Identification type.
            operator (str): Operator of domain.
            value (str): Value to search for.

        Returns:
            list: Domain to search with.
        """
        id_numbers = self.env["res.partner.id_number"].search(
            [("name", operator, value), ("category_id.code", "=", category_code)]
        )
        return [("id_numbers.id", "in", id_numbers.ids)]
