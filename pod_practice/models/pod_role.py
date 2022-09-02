# Copyright 2017 LasPractices Inc.
# Copyright 2017 Creu Blanca.
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# Copyright 2020 PracticeViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import models, fields


class PodRole(models.Model):
    _name = 'pod.role'
    _description = 'Practitioner Roles'

    name = fields.Char(required=True,)
    description = fields.Char(required=True,)
    active = fields.Boolean(default=True,)
