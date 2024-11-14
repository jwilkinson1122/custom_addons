# -*- coding: utf-8 -*-
from . import controllers, models, wizards
from . import base_user_role
from . import base_user_role_company

# from . import server_environment
# from . import server_environment_ir_config_parameter
from . import pod_file_storage
from . import pod_file_attachment
from . import pod_sql_integration
from . import pod_contacts
from . import pod_brand
from . import pod_product_brand
from . import pod_flexible_bom
from . import pod_product_configurator
from . import pod_product_configurator_sale
from . import pod_prescription_order
from . import pod_product_configurator_prescription_order
from . import pod_product_configurator_mrp

from .hooks import pre_init_hook
from .hooks import post_init_hook
