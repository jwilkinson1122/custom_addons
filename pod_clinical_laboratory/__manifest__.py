# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Laboratory",
    "version": "15.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "depends": ["pod_workflow", "pod_base"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/pod_request_views.xml",
        "views/pod_laboratory_event_view.xml",
        "views/pod_laboratory_request_view.xml",
    ],
    "website": "https://github.com/tegin/nwp-pod",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
