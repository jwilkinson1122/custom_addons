{
    "name": "NWPL - SFTP",
    "version": "17.0.0.0.0",
    "summary": "Generic implementation of sftp",
    "category": "Generic Modules",
    "author": "NWPL",
    "website": "https://www.nwpodiatric.com",
    "license": "LGPL-3",
    "depends": [
        "base"
    ],
    "external_dependencies": {
        "python": [
            "paramiko",
            "pytest-sftpserver",
        ]
    },
    "data": [
        "security/ir.model.access.csv",
        "views/ir_sftp_server_views.xml",
        "views/menu_views.xml",
    ],
    "demo": [
        'demo/ir_sftp_server_demo.xml',
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
