# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Administration Practitioner Specialty",
    "version": "15.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "category": "Podiatry",
    "website": "https://github.com/tegin/nwp-pod",
    "license": "AGPL-3",
    "depends": ["pod_administration_practitioner_specialty"],
    "data": [
        "data/pod_role.xml",
        "views/res_partner_views.xml",
        "views/pod_role.xml",
        "views/pod_specialty.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
