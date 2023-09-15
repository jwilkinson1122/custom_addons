

{
    "name": "PoS Validation",
    "version": "15.0.1.0.0",
    "category": "Reporting",
    "website": "https://nwpodiatric.com",
    "author": "NWPL",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Validation of Careplans once they are assigned to a Session",
    "depends": [
        "pos_safe_box",
        "barcode_action",
        "nwp_pod_cancel",
        "web_flagbox",
        "web_ir_actions_act_multi",
        "nwp_pod_clinical_laboratory",
        "web_history_back",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "wizards/pod_encounter_validation_add_service.xml",
        "wizards/sale_order_line_cancel.xml",
        "data/pod_invoice_group.xml",
        "views/pod_encounter_view.xml",
        "views/administration_menu.xml",
        "views/pos_session_views.xml",
        # "templates/templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "pos_validation/static/src/js/action.js",
        ],
    },
}
