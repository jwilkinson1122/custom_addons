{
    'name': 'Web Chatter', 
    'summary': 'Adds options for the chatter',
    'version': '17.0.1.2.0',
    'category': 'Tools/UI',
    'license': 'LGPL-3', 
    'depends': [
        'mail',
    ],
    'data': [
        'views/res_users.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            (
                'after', 
                'web/static/src/scss/primary_variables.scss', 
                'pod_web_chatter/static/src/scss/variables.scss'
            ),
        ],
        'web.assets_backend': [
            'pod_web_chatter/static/src/core/**/*.js',
            'pod_web_chatter/static/src/core/**/*.xml',
            'pod_web_chatter/static/src/core/**/*.scss',
            (
                'after', 
                'mail/static/src/views/web/form/form_compiler.js', 
                'pod_web_chatter/static/src/views/form/form_compiler.js'
            ),
            'pod_web_chatter/static/src/views/form/form_renderer.js',
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
