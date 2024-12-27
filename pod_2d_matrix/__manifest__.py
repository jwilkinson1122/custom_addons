{
    "name": "2D matrix for x2many fields",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "summary": "Show list fields as a matrix",
    "depends": ["base", "web", "sale", "sale_management", "product"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/laterality_wizard.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "assets": {
        "web.assets_backend": [
            "pod_2d_matrix/static/src/components/x2many_2d_matrix_renderer/x2many_2d_matrix_renderer.esm.js",
            "pod_2d_matrix/static/src/components/x2many_2d_matrix_renderer/x2many_2d_matrix_renderer.xml",
            "pod_2d_matrix/static/src/components/x2many_2d_matrix_field/x2many_2d_matrix_field.esm.js",
            "pod_2d_matrix/static/src/components/x2many_2d_matrix_field/x2many_2d_matrix_field.xml",
            "pod_2d_matrix/static/src/components/x2many_2d_matrix_field/x2many_2d_matrix_field.scss",
        ],
    },
}
