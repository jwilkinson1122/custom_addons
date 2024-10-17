{
    'name': 'Custom Orthotics Manufacturing',
    'version': '18.0.0.0.0',
    'category': 'Sales',
    'description': """ """,
    'depends': [
        'base', 
        'base_automation',
        'base_setup',
        'account',
        'contacts',
        'knowledge',
        'product',
        'point_of_sale',
        'pos_sale',
        'sale',
        'sale_management',
    ],
    'data': [
        # 'data/res_config_settings.xml',
        'data/ir_attachment_pre.xml',
        'data/product_category.xml',
        'data/pos_category.xml',
        'data/product_template.xml',
        'data/product_attribute.xml',
        'data/product_attribute_value.xml',
        'data/pos_payment_method.xml',
        'data/pos_config.xml',
        'data/product_template_attribute_line.xml',
        'data/product_template_attribute_value.xml',
        'data/product_product.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/mail_message.xml',
        # 'data/knowledge_tour.xml',
        'views/pos_config.xml',
    ],
    'demo': [
        'demo/res_config_settings.xml',
        'demo/res_partner.xml',
        # 'demo/product_template.xml',
        'demo/pos_session.xml',

    ],
    'license': 'OPL-1',
    'assets': {
        'web.assets_backend': [
            # 'custom_orthotics/static/src/js/my_tour.js',
        ],

        'point_of_sale._assets_pos': [

            'custom_orthotics/static/pod_pos_hide_cash_control/static/src/js/pos_store.js',

        ]
    
    },
    'author': 'NWPL',
    "cloc_exclude": [
        "data/knowledge_article.xml",
        # "static/src/js/my_tour.js",
    ],
    'images': ['images/main.png'],
}
