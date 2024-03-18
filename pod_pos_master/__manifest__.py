# -*- coding: utf-8 -*-

{
    "name": "NWPL - PoS Master",         
    "author": "NWPL",     
    "website": "https://www.nwpodiatric.com",         
    "category": "Point of Sale",   
    "version": "17.0.0.0.0",       
    "summary": """Full solution for any kind of shop or bussiness.""",          
    "description": """Full solution for any kind of shop or bussiness.""",
    "depends": ["point_of_sale"],
    "data": [
        'data/pod_pos_theme_responsive/data/pos_theme_settings_data.xml',
        
        'pod_pos_theme_responsive/security/ir.model.access.csv',
        'pod_pos_theme_responsive/views/pod_pos_theme_settings_views.xml',
        'data/order_label.xml',
        'views/pos_order.xml',
        'views/res_config_settings.xml',
        'data/pod_pos_keayboard_shortcut/data/pod_keyboard_key_data.xml',
        'security/ir.model.access.csv',

        # varaint
        'pod_pos_product_variant/views/product_template.xml',

        # product suggtion
        'pos_product_suggestion/views/product_view.xml',

        'pod_pos_cash_in_out/views/cash_in_out_menu.xml',

        'pod_pos_product_options/views/pos_category_views.xml',
        'pod_pos_product_options/views/product_product_views.xml',
        'pod_pos_product_options/views/pod_product_options.xml',
        'pod_pos_product_options/views/pod_option_group.xml',

        'pod_base_order_type/security/ir.model.access.csv',
        'pod_pos_order_type/views/pod_order_type_views.xml',
        'pod_pos_order_type/views/pos_order_views.xml',

        'pod_product_multi_barcode/security/ir.model.access.csv',
        'pod_product_multi_barcode/views/product_product_views.xml',
        'pod_product_multi_barcode/views/product_template_views.xml',
        'pod_product_multi_barcode/views/res_config_settings.xml',



    ],
    'assets': {'point_of_sale._assets_pos': [
            # theme
            '/pod_pos_master/static/pod_pos_theme_responsive/static/src/overrides/pos_theme_variables.scss',
            'pod_pos_master/static/pod_pos_theme_responsive/static/src/scss/mixin.scss',
            'pod_pos_master/static/pod_pos_theme_responsive/static/lib/owl.carousel.js',
            'pod_pos_master/static/pod_pos_theme_responsive/static/lib/owl.carousel.css',
            'pod_pos_master/static/pod_pos_theme_responsive/static/lib/owl.theme.default.min.css',
            'pod_pos_master/static/pod_pos_theme_responsive/static/src/overrides/**/*',
            'pod_pos_master/static/pod_pos_theme_responsive/static/src/scss/**/*',

            # pos counter
            'pod_pos_master/static/pod_pos_counter/**/*',

            # create sale order from pos
            'pod_pos_master/static/pod_pos_create_so/static/src/**/*',

            # Create purchase order from pos
            'pod_pos_master/static/pod_pos_create_po/static/src/**/*',

            # pos order label
            'pod_pos_master/static/pod_pos_order_label/static/src/**/*',

            # order list
            'pod_pos_master/static/pod_pos_order_list/static/**/*',

            # Global pos models
            'pod_pos_master/static/global_models/static/src/override/pos_store.js',
            
            # receipt extend
            'pod_pos_master/static/pod_pos_receipt_extend/static/src/**/*',

            # variant merge
            'pod_pos_master/static/pod_pos_product_variant/static/src/**/*',

            # Wh stock
            'pod_pos_master/static/pod_pos_wh_stock/static/src/app/**/*',
            'pod_pos_master/static/pod_pos_wh_stock/static/src/scss/**/*',

            # remove cart item
            'pod_pos_master/static/pod_pos_remove_cart_item/static/src/**/*',

            # keayboard
            'pod_pos_master/static/pod_pos_keyboard_shortcut/static/src/**/*',  

            # discount
            'pod_pos_master/static/pod_pos_order_discount/static/src/**/*',

            # suggestion
            'pod_pos_master/static/pos_product_suggestion/static/src/**/*',

            'pod_pos_master/static/pod_pos_product_code/static/src/**/*',

            'pod_pos_master/static/pod_pos_cash_in_out/static/src/**/*',

            'pod_pos_master/static/pod_pos_product_options/static/src/app/**/*',
            'pod_pos_master/static/pod_pos_product_options/static/src/overrides/components/product_screen/product_screen.js',
            'pod_pos_master/static/pod_pos_product_options/static/src/overrides/models/pos_store.js',
            'pod_pos_master/static/pod_pos_product_options/static/src/overrides/models/models.js',
            'pod_pos_master/static/pod_pos_product_options/static/src/overrides/orderline/orderline.js',
            'pod_pos_master/static/pod_pos_product_options/static/src/overrides/orderline/orderline.scss',
            'pod_pos_master/static/pod_pos_product_options/static/src/overrides/orderline/orderline.xml',

            'pod_pos_master/static/pod_pos_order_type/static/**/*',
            'pod_pos_master/static/pod_pos_multi_barcode/static/src/overrides/**/*'
        ]
    },
    "images": [
        'static/description/splash-screen.gif',
        'static/description/splash-screen_screenshot.gif'

    ],
    "application": True,
    "auto_install": False,
    "license": "OPL-1",
    "price": 210,
    "installable": True,
}
