# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Administration Location",
    "version": "15.0.1.0.0",
    "category": "Podiatry",
    "website": "https://github.com/tegin/pod-fhir",
    "author": "CreuBlanca, Eficent",
    "license": "AGPL-3",
    "depends": ["pod_administration_location"],
    "data": [
        "views/res_partner_views.xml",
        "views/pod_menu.xml",
    ],
    "demo": ["demo/pod_demo.xml"],
    "installable": True,
    "application": False,
}
