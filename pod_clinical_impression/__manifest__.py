# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Podiatry Clinical Impression",
    "summary": """
        Podiatry Clinical Impression based on FHIR""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca,Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/pod-fhir",
    "depends": [
        "pod_workflow",
        "pod_clinical_condition",
        "pod_administration_practitioner_specialty",
    ],
    "data": [
        "views/assets.xml",
        "security/pod_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "wizards/create_impression_from_patient.xml",
        "wizards/create_impression_from_encounter.xml",
        "views/pod_clinical_impression.xml",
        "views/pod_encounter.xml",
        "views/pod_patient.xml",
        "views/pod_clinical_finding.xml",
        "views/pod_family_member_history.xml",
        "reports/pod_impression_report.xml",
    ],
    "qweb": ["static/src/xml/widget_warning_dropdown.xml"],
    "demo": ["demo/pod_demo.xml"],
}
