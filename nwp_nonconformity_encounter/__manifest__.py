

{
    "name": "NWPL Nonconformity Encounter",
    "summary": """
        NWP custom nonconformity management""",
    "version": "15.0.1.1.0",
    "license": "AGPL-3",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "depends": ["nwp_mgmtsystem_issue", "pod_administration_encounter"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/wizard_create_nonconformity_encounter.xml",
        "views/mgmtsystem_nonconformity_origin.xml",
        "views/pod_encounter.xml",
    ],
}
