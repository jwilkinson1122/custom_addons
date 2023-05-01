{
    'name': 'Odoo Development Tutorials',
    'version': '12.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Odoo Development Tutorials For Beginners',
    'sequence': '10',
    'license': 'AGPL-3',
    'author': 'Odoo Mates',
    'maintainer': 'Odoo Mates',
    'website': 'odoomates.com',
    'live_test_url': 'https://www.youtube.com/watch?v=BDepk0LhVuI&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=1',
    'depends': ['sale', 'mail', 'board'],
    'qweb': [
        'static/src/xml/web_timeline.xml',
    ],
    'demo': [],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/data.xml',
        'data/cron.xml',
        'wizards/create_appointment.xml',
        'views/patient.xml',
        'views/appointment.xml',
        'views/doctor.xml',
        'views/lab.xml',
        'views/sale_order.xml',
        'views/template.xml',
        'views/settings.xml',
        'views/portal_template.xml',
        'views/dashboard.xml',
        'reports/patient_card.xml',
        'reports/report.xml',
        'reports/sale_report_inherit.xml',
        'reports/appointment.xml',
        'data/mail_template.xml',
        # 'views/web_timeline.xml',
    ],
    "assets": {
        "web.assets_backend": [
            "om_hospital/static/lib/vis/vis-timeline-graph2d.min.css",
            "om_hospital/static/src/css/web_timeline.css",
            "om_hospital/static/lib/vis/vis-timeline-graph2d.min.js",
            "om_hospital/static/src/js/timeline_view.js",
            "om_hospital/static/src/js/timeline_renderer.js",
            "om_hospital/static/src/js/timeline_controller.js",
            "om_hospital/static/src/js/timeline_model.js",
            "om_hospital/static/src/js/timeline_canvas.js",
            ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# Video Explanation: https://www.youtube.com/watch?v=BDepk0LhVuI&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=1


        #   <link rel="stylesheet" href="/om_hospital/static/lib/vis/vis-timeline-graph2d.min.css"/>
        #     <link rel="stylesheet" href="/om_hospital/static/src/css/web_timeline.css"/>

        #     <script type="text/javascript" src="/om_hospital/static/lib/vis/vis-timeline-graph2d.min.js"/>
        #     <script type="text/javascript" src="/om_hospital/static/src/js/timeline_view.js"/>
        #     <script type="text/javascript" src="/om_hospital/static/src/js/timeline_renderer.js"/>
        #     <script type="text/javascript" src="/om_hospital/static/src/js/timeline_controller.js"/>
        #     <script type="text/javascript" src="/om_hospital/static/src/js/timeline_model.js"/>
        #     <script type="text/javascript" src="/om_hospital/static/src/js/timeline_canvas.js"/>