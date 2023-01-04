{
    "name": "Podiatry ERP",
    "version": "15.0.1.0.0",
    "category": "Generic Modules/Base",
    "summary": "Base for custom orthotics manufacturing",
    "author": "NWPL",
    "license": "AGPL-3",
    "website": "https://nwpodiatrtic.com",
    "depends": ["account"],
    "data": [
        "security/configurator_security.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings_view.xml",
        "data/menu_configurable_product.xml",
        "data/product_attribute.xml",
        "data/ir_sequence_data.xml",
        "data/ir_config_parameter_data.xml",
        "views/product_view.xml",
        "views/product_attribute_view.xml",
        "views/product_config_view.xml",
        "wizard/product_configurator_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/podiatry/static/scss/form_widget.scss",
            "/podiatry/static/js/form_widgets.js",
            "/podiatry/static/js/data_manager.js",
            "/podiatry/static/js/relational_fields.js",
        ]
    },
    "demo": [
        "demo/product_template.xml",
        "demo/product_attribute.xml",
        "demo/product_config_domain.xml",
        "demo/product_config_lines.xml",
        "demo/product_config_step.xml",
        "demo/config_image_ids.xml",
    ],
    "images": ["static/description/icon.png"],
    "post_init_hook": "post_init_hook",
    "qweb": ["static/xml/create_button.xml"],
    "development_status": "Beta",
    "maintainers": ["NWPL"],
    "installable": True,
    "application": True,
    "auto_install": False,
    "external_dependencies": {"python": ["mako"]},
}
