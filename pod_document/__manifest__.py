

{
    "name": "Podiatry documents",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "depends": [
        "pod_workflow",
        "remote_report_to_printer",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "wizard/pod_document_reference_change_language_views.xml",
        "wizard/pod_document_type_add_language_views.xml",
        "views/pod_request_views.xml",
        "views/pod_document_reference_views.xml",
        "views/pod_document_template_views.xml",
        "views/pod_document_type_views.xml",
        "views/workflow_activity_definition.xml",
        "report/document_report.xml",
    ],
    "website": "https://nwpodiatric.com",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
