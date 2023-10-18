{
    "name": "NWPL Prescription Product Configurator",
    "version": "15.0.1.0.0",
    "category": "Podiatry",
    "summary": "Product configuration for prescriptions",
    "author": "NWPL",
    "license": "AGPL-3",
    "website": "https://www.nwpodiatric.com",
    "depends": [
        "pod_order_mgmt", 
        "product_configurator"
        ],
    "data": [
        "security/ir.model.access.csv",
        "data/menu_product.xml",
        "views/pod_prescription_order.xml",
        # "views/pod_product_config.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "pod_product_configurator_prescription/static/src/css/main.css",
        ],
    },
    "demo": [
        "demo/product_template.xml",
        "demo/product_attribute.xml",
        "demo/product_config_domain.xml",
        "demo/product_config_lines.xml",
        "demo/product_config_step.xml",
        "demo/config_image_ids.xml",
    ],
    # "demo": ["demo/res_partner_demo.xml"],
    "installable": True,
    "auto_install": False,
}
