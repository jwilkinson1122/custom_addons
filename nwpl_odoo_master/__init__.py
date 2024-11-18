# -*- coding: utf-8 -*-
from . import controllers, models, wizards
from . import base_user_role
from . import base_user_role_company

from . import pod_file_storage
from . import pod_file_attachment
from . import pod_sql_integration
from . import amazon_s3_connector
from . import pod_contacts

# from . import pod_brand
from . import pod_product_brand
from . import pod_product_options
from . import pod_flexible_bom
from . import pod_product_configurator
from . import pod_product_configurator_sale
from . import pod_prescription_order
from . import pod_product_configurator_prescription_order
from . import pod_product_configurator_mrp
from . import pod_automated_sale_order
from . import pod_sale_reorder
from . import pod_sale_order_helpdesk_ticket

# from . import pod_sale_delivery_address
from . import pod_sale_attached_product

from . import pod_customer_statement

from .hooks import pre_init_hook
from .hooks import post_init_hook
from .hooks import uninstall_hook
