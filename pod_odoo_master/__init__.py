# -*- coding: utf-8 -*-
# from . import controllers, models, wizards
from . import controllers, models
from . import pod_access_control
from . import pod_base_multi_company
# from . import pod_log
from . import pod_web_appsbar
from . import pod_checklists
# from . import pod_user_utilities
from . import pod_recycle_bin
from . import pod_file_storage
from . import pod_file_attachment
from . import pod_sql_integration
from . import amazon_s3_connector
from . import pod_contacts
from . import pod_login_as
from . import pod_web_chatter
from . import pod_hierarchy
from . import pod_product_brand
# from . import pod_product_secondary_uom
from . import pod_flexible_bom
from . import pod_sale_invoice_detail
from . import pod_merge_quotations
from . import pod_product_configurator
from . import pod_automated_sale_order
# from . import pod_sale_order_helpdesk_ticket
# from . import pod_sale_delivery_address
from . import pod_sale_attached_product
from . import pod_customer_statement
from . import pod_shopify_sync

from .hooks import pre_init_hook
from .hooks import post_init_hook
from .hooks import uninstall_hook

