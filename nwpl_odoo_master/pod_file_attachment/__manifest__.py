{
    "name": "Base Attachment Object Store",
    "summary": "Store attachments on external object store",
    "version": "1.0",
    "license": "AGPL-3",
    "category": "Knowledge Management",
    "depends": ["pod_file_storage"],
    "data": [
        "security/file_gc.xml",
        "views/file_storage.xml",
    ],
    "external_dependencies": {"python": ["python_slugify"]},
    "installable": True,
    "auto_install": False,
    "pre_init_hook": "pre_init_hook",
}
