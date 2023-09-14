# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Cb Mgmtsystem Issue",
    "summary": """
        Managemente System Issues""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca",
    "website": "https://github.com/tegin/cb-addons",
    "depends": ["mgmtsystem_nonconformity"],
    "data": [
        "views/res_partner.xml",
        "data/mgmtsystem_sequence.xml",
        "data/nonconformity_sequence_data.xml",
        "security/ir.model.access.csv",
        "security/msmsystem_security.xml",
        "wizards/wizard_create_nonconformity.xml",
        "views/mgmtsystem_quality_issue.xml",
        "views/mgmtsystem_nonconformity.xml",
        "views/mgmtsystem_nonconformity_origin.xml",
    ],
}
