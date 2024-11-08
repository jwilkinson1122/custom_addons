{
    "name": "pod_sftp_connector",
    "version": "1.0",
    "depends": ["base", "crm", "web"],  # Add 'crm' for customer integration
    "data": [
        "security/ir.model.access.csv",
        "views/customer_sftp_views.xml",
        "views/sftp_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "customer_sftp_connector/static/src/js/sftp_upload.js",
            "customer_sftp_connector/static/src/js/sftp_download.js",
            "customer_sftp_connector/static/src/css/sftp_style.css",
        ],
    },
    "external_dependencies": {
        "python": ["paramiko"],  # Add paramiko for SFTP interaction
    },
}
