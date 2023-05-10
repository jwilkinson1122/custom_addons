# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Web timeline",
    'summary': "Interactive visualization chart to show events in time",
    "version": "12.0.1.1.2",
    "development_status": "Production/Stable",
    'author': 'ACSONE SA/NV, '
              'Tecnativa, '
              'Monk Software, '
              'Onestein, '
              'Odoo Community Association (OCA)',
    "category": "web",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "website": "https://github.com/OCA/web",
    'depends': [
        'web',
    ],
    'qweb': [
        'static/src/xml/web_timeline.xml',
    ],
    'data': [
        # 'views/web_timeline.xml',
    ],
    "assets": {
        "web.assets_backend": [
            "/web_timeline/static/lib/vis/vis-timeline-graph2d.min.css",
            "/web_timeline/static/src/css/web_timeline.css",
            "/web_timeline/static/lib/vis/vis-timeline-graph2d.min.js",
            "/web_timeline/static/src/js/timeline_view.js",
            "/web_timeline/static/src/js/timeline_renderer.js",
            "/web_timeline/static/src/js/timeline_controller.js",
            "/web_timeline/static/src/js/timeline_model.js",
            "/web_timeline/static/src/js/timeline_canvas.js",
        ],
    },
    "maintainers": ["tarteo"],
}

