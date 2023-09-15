

{
    "name": "Podiatry Encounter Careplan",
    "summary": "Joins careplans and encounters",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "category": "Podiatry",
    "license": "LGPL-3",
    "depends": [
        "pod_administration_encounter",
        "pod_clinical_careplan",
    ],
    "data": [
        "views/pod_encounter_view.xml",
        "views/pod_request_views.xml",
    ],
    "demo": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
