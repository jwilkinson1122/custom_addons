# -*- coding: utf-8 -*-

{
    "name": "NWPL Test",         
    "author": "NWPL",     
    "website": "https://www.nwpodiatric.com",        
    "category": "Sales Management",   
    "version": "18.0.0.0.0",       
    "summary": """Full Custom Orthotics Manufacturing System""",          
    "description": """ Full Custom Orthotics Manufacturing System """,
    "depends": [
        'account',
        'account_check_printing',
        'account_followup',
        'base', 
        'base_automation',
        'base_setup',
        'barcodes', 
        'contacts',
        'mail',
        'mrp',
        'knowledge',
        'point_of_sale',
        'pos_sale',
        'product_expiry',
        'product',
        'sale',
        'sale_management',
        'sale_product_matrix',
        'sale_planning',
        'sale_margin',
        'sale_stock',
        'stock',
        'uom',
        'web',
        'web_studio',
        ],
    "data": [
        'security/pod_security.xml',
        'security/ir.model.access.csv',
        # 'data/base_user_role/data/ir_cron.xml',
        # 'data/base_user_role/data/ir_module_category.xml',
        # 'views/role.xml',
        # 'views/user.xml',
        # 'views/group.xml',
        # 'wizards/create_from_user.xml',
        # 'wizards/wizard_groups_into_role.xml',

        'data/pod_pos_order_label/data/order_label.xml',
        'views/pos_order.xml',
        'views/res_config_settings.xml',
        'views/pos_config_views.xml',
        'data/pod_pos_keyboard_shortcut/data/pod_keyboard_key_data.xml',
        'data/pod_contacts/data/ir_sequence_data.xml',
        'data/pod_contacts/data/contact_practice_type.xml',
        'data/pod_contacts/data/contact_role.xml',
        'pod_contacts/views/barcode_action_view.xml',
        'pod_contacts/views/contact_role.xml',
        'pod_contacts/views/contact_diagnosis.xml',
        'pod_contacts/views/res_partner.xml',
        'pod_contacts/views/contact_practice_type.xml',
        'pod_contacts/views/contact_patient.xml',
        'pod_contacts/views/contact_flag_views.xml',
        'pod_contacts/views/contact_flag_category_views.xml',
        'pod_contacts/views/contact_menu.xml',

        'pod_pos_product_variant/views/product_template.xml',
        'pod_pos_product_suggestion/views/product_view.xml',
        'pod_pos_cash_in_out/views/cash_in_out_menu.xml',

        # product brand
        'pod_brand/security/res_brand.xml',
        'pod_brand/views/res_config_settings.xml',
        'pod_brand/views/res_brand.xml',
        'pod_product_brand/views/product_brand_view.xml',
        'pod_product_brand/reports/sale_report_view.xml',
        'pod_product_brand/reports/account_invoice_report_view.xml',

        # product options
        'pod_pos_product_options/views/pos_category_views.xml',
        'pod_pos_product_options/views/product_product_views.xml',
        'pod_pos_product_options/views/pod_product_options.xml',
        'pod_pos_product_options/views/pod_option_group.xml',

        # order type
        'pod_base_order_type/security/ir.model.access.csv',
        'pod_pos_order_type/views/pod_order_type_views.xml',
        'pod_pos_order_type/views/pos_order_views.xml',

        # product multi barcode
        'pod_product_multi_barcode/security/ir.model.access.csv',
        'pod_product_multi_barcode/views/product_product_views.xml',
        'pod_product_multi_barcode/views/product_template_views.xml',
        'pod_product_multi_barcode/views/res_config_settings.xml',

        # order customizations
        'pod_pos_order_customizations/security/ir.model.access.csv',
        'pod_pos_order_customizations/security/security.xml',
        'data/pod_pos_order_customizations/data/customization_sequence.xml',
        'data/pod_pos_order_customizations/data/ir_attachment.xml',
        'data/pod_pos_order_customizations/data/uom_category.xml',
        'data/pod_pos_order_customizations/data/uom_uom.xml',
        'data/pod_pos_order_customizations/data/ir_attachment.xml',
        'data/pod_pos_order_customizations/data/ir_model.xml',
        'data/pod_pos_order_customizations/data/ir_model_fields.xml',
        'data/pod_pos_order_customizations/data/ir_ui_view.xml',
        'data/pod_pos_order_customizations/data/ir_actions_act_window.xml',
        'data/pod_pos_order_customizations/data/base_automation.xml',
        'data/pod_pos_order_customizations/data/ir_actions_server.xml',
        'data/pod_pos_order_customizations/data/ir_ui_menu.xml',
        'data/pod_pos_order_customizations/data/ir_default.xml',
        'data/pod_pos_order_customizations/data/pos_category.xml',
        'data/pod_pos_order_customizations/data/pos_payment_method.xml',
        'data/pod_pos_order_customizations/data/pos_config.xml',
        'data/pod_pos_order_customizations/data/product_attribute.xml',
        'data/pod_pos_order_customizations/data/product_attribute_value.xml',
        'data/pod_pos_order_customizations/data/product_category.xml',
        'data/pod_pos_order_customizations/data/product_template.xml',
        'data/pod_pos_order_customizations/data/product_pricelist.xml',
        'data/pod_pos_order_customizations/data/product_pricelist_item.xml',
        'data/pod_pos_order_customizations/data/product_template_attribute_line.xml',
        'data/pod_pos_order_customizations/data/product_template_attribute_value.xml',
        'data/pod_pos_order_customizations/data/knowledge_cover.xml',
        'data/pod_pos_order_customizations/data/res_config_settings.xml',
        'data/pod_pos_order_customizations/data/knowledge_article.xml',
        'data/pod_pos_order_customizations/data/knowledge_article_favorite.xml',
        'data/pod_pos_order_customizations/data/mail_message.xml',
        'pod_pos_order_customizations/wizard/wizard_product_variant_configurator_manual_creation_view.xml',

        'pod_pos_order_customizations/views/product_configurator_attribute.xml',
        'pod_pos_order_customizations/views/inherited_product_template_views.xml',
        'pod_pos_order_customizations/views/inherited_product_product_views.xml',
        'pod_pos_order_customizations/views/inherited_product_category_views.xml',
        'pod_pos_order_customizations/views/inherited_product_attribute_views.xml',
        'pod_pos_order_customizations/views/pos_order_customization_view.xml',
        'pod_pos_order_customizations/views/pos_order_view.xml',
        
        # measurements
        'pod_pos_measurements/views/product_template_views.xml',
        'pod_pos_measurements/views/pos_category_view.xml',
        'pod_pos_measurements/views/pos_order_view.xml',
        'pod_pos_measurements/views/res_partner_view.xml',
        'pod_pos_measurements/views/measurement_view.xml',
        'pod_pos_measurements/views/res_config_settings_view.xml',

        # bom
        'pod_flexible_bom/security/ir.model.access.csv',
        'pod_flexible_bom/views/sale_order_line.xml',
        'pod_flexible_bom/views/mrp_bom.xml',
        'pod_flexible_bom/views/product.xml',
        'pod_flexible_bom/wizards/create_bom.xml',

    ],

    "demo": [
      'demo/mail_demo.xml',
      'demo/res_partner.xml',
      'demo/product_brand.xml',
    #   'demo/product_template.xml',
    #   'demo/product_attribute.xml',
    #   'demo/product_config_domain.xml',
    #   'demo/product_config_lines.xml',
    #   'demo/product_config_step.xml',
    #   'demo/config_image_ids.xml',
      'demo/pos_config.xml',
      'demo/pos_session.xml',
      ],

    'assets': {

        'web.assets_backend': [
            'nwpl_pod_master/static/pod_contacts/static/src/css/custom_theme.css',
        ],

        'point_of_sale._assets_pos': [

            # pos counter
            'nwpl_pod_master/static/pod_pos_counter/**/*',

            # create sale order from pos
            'nwpl_pod_master/static/pod_pos_create_so/static/src/**/*',

            # Create purchase order from pos
            'nwpl_pod_master/static/pod_pos_create_po/static/src/**/*',

            # pos order label
            'nwpl_pod_master/static/pod_pos_order_label/static/src/**/*',

            # order list
            'nwpl_pod_master/static/pod_pos_order_list/static/**/*',

            # Global pos models
            'nwpl_pod_master/static/global_models/static/src/override/pos_store.js',
            
            # receipt extend
            'nwpl_pod_master/static/pod_pos_receipt_extend/static/src/**/*',

            # variant merge
            'nwpl_pod_master/static/pod_pos_product_variant/static/src/**/*',

            # Wh stock
            'nwpl_pod_master/static/pod_pos_wh_stock/static/src/app/**/*',
            'nwpl_pod_master/static/pod_pos_wh_stock/static/src/scss/**/*',

            # remove cart item
            'nwpl_pod_master/static/pod_pos_remove_cart_item/static/src/**/*',

            # keyboard
            'nwpl_pod_master/static/pod_pos_keyboard_shortcut/static/src/**/*',  

            # discount
            'nwpl_pod_master/static/pod_pos_order_discount/static/src/**/*',

            # suggestion
            'nwpl_pod_master/static/pod_pos_product_suggestion/static/src/**/*',

            'nwpl_pod_master/static/pod_pos_product_code/static/src/**/*',

            'nwpl_pod_master/static/pod_pos_hide_cash_control/static/src/**/*',

            'nwpl_pod_master/static/pod_pos_cash_in_out/static/src/**/*',

            # 'nwpl_pod_master/static/pod_pos_measurements/static/src/**/*',

            'nwpl_pod_master/static/pod_pos_product_options/static/src/app/**/*',
            'nwpl_pod_master/static/pod_pos_product_options/static/src/overrides/components/product_screen/product_screen.js',
            'nwpl_pod_master/static/pod_pos_product_options/static/src/overrides/models/pos_store.js',
            'nwpl_pod_master/static/pod_pos_product_options/static/src/overrides/models/models.js',
            'nwpl_pod_master/static/pod_pos_product_options/static/src/overrides/orderline/orderline.js',
            'nwpl_pod_master/static/pod_pos_product_options/static/src/overrides/orderline/orderline.scss',
            'nwpl_pod_master/static/pod_pos_product_options/static/src/overrides/orderline/orderline.xml',

            'nwpl_pod_master/static/pod_pos_order_type/static/**/*',
            'nwpl_pod_master/static/pod_pos_product_options/static/src/app/**/*',
            'nwpl_pod_master/static/pod_prescription_order/static/src/**/*',
            
            'nwpl_pod_master/static/pod_pos_multi_barcode/static/src/overrides/**/*',

            # 'nwpl_pod_master/static/pod_pos_order_customizations/static/src/**/*',
            
            'nwpl_pod_master/static/pod_pos_measurements/static/src/**/*',
        


        ]
    },
    "images": ['static/description/icon.png'],
    'post_init_hook': 'post_init_hook',
    # 'post_init_hook': 'set_sale_price_on_variant',
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
    "installable": True,
}
