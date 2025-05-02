{
    "name": "Recursive Tree View",
    "version": "1.0",
    "summary": "Adds the ability to mark a tree view as recursive, to expand "
    "descendants of a parent record.",
    "category": "Technical",
    "license": "LGPL-3",
    "depends": ["web", "web_enterprise"],
    "data": [],
    "assets": {
       "web.assets_backend": [
            "recursive_tree_view/static/src/js/recursive_record_row.js",
            "recursive_tree_view/static/src/js/list_renderer.js",
            "recursive_tree_view/static/src/js/list_controller.js",
            "recursive_tree_view/static/src/js/relational_model.js",
            "recursive_tree_view/static/src/js/list_arch_parser.js",
            "recursive_tree_view/static/src/css/tree_recursive_styles.css",
            "recursive_tree_view/static/src/xml/recursive_record_row_template.xml",
        ],
    },
    "installable": True,
    "application": False,
    "images": [],
}
