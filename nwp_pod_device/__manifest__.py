

{
    "name": "NWP Podiatry sequence configuration",
    "version": "15.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "depends": [
        "mrp", 
        "nwp_pod_block_request", 
        "stock_move_line_auto_fill"],
    "data": [
        "data/location_type_data.xml",
        "security/ir.model.access.csv",
        "wizard/pod_encounter_device_views.xml",
        "views/product_category_views.xml",
        "views/pod_encounter_views.xml",
        "views/res_partner_views.xml",
        "views/workflow_plan_definition_action.xml",
        "report/pod_encounter_device_report.xml",
    ],
    "website": "https://github.com/tegin/nwp-pod",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
