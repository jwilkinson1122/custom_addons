# -*- coding: utf-8 -*-

{
    'name': "Product Multi variant",
    'version': '15.0.1.0.1',
    'summary': """Product with multi-variants""",
    'description': """Configure products having variants in Product""",
    'author': 'NWPL',
    'website': "https://www.nwpodiatric.com",
    'category': 'Products',
    'depends': ['base',
                'podiatry_manager',
                ],
    'data': ['views/product_variants.xml',
             'security/ir.model.access.csv',
             ],

    'assets': {
        'podiatry_manager.assets': [
            'product_multi_variant/static/src/css/label.css',
            'product_multi_variant/static/src/js/models.js',
            'product_multi_variant/static/src/js/ProductPopup.js',
            'product_multi_variant/static/src/js/ProductScreen.js'
        ],
        'web.assets_qweb': [
            'product_multi_variant/static/src/xml/label.xml',
            'product_multi_variant/static/src/xml/popup.xml'
        ],
    },

    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,



    'auto_install': False,
}
