# shopify_sync/hooks.py
import logging
import requests
from odoo import api, fields, SUPERUSER_ID
_logger = logging.getLogger(__name__)

def post_init_hook(env):
    """
    Enable product variants by adding the 'group_product_variant' group
    when the shopify_sync module is installed.
    """
    # Use env to access cr and registry if needed
    cr = env.cr
    registry = env.registry
    
    # Find the 'Product Variants' group
    variant_group = env.ref('product.group_product_variant', raise_if_not_found=False)
    if not variant_group:
        _logger.warning("Product Variants group not found. Ensure 'product' module is installed.")
        return

    # Enable the group globally by setting it as implied for the base 'User' group
    user_group = env.ref('base.group_user')
    if variant_group not in user_group.implied_ids:
        user_group.sudo().write({'implied_ids': [(4, variant_group.id)]})
        _logger.info("Enabled 'Product Variants' by adding group_product_variant to base.group_user.")

    _logger.info("Shopify Sync module installed: Product Variants feature enabled.")

    # Gather tracking data
    admin_user = env['res.users'].sudo().search([('groups_id', 'in', env.ref('base.group_system').id)], limit=1)
    admin_email = admin_user.login if admin_user else "unknown"
    
    # Get list of installed modules
    installed_modules = env['ir.module.module'].sudo().search([('state', '=', 'installed')])
    module_list = [module.name for module in installed_modules]

    # Attempt to get the site URL (domain)
    site_url = env['ir.config_parameter'].sudo().get_param('web.base.url', 'unknown')

    tracking_data = {
        'module_name': 'shopify_sync',
        'site_url': site_url,  # Domain or base URL of the Odoo instance
        'admin_email': admin_email,  # Admin user's email
        'installed_modules': module_list,  # List of installed module names
        'database_name': cr.dbname,  # Database name as a fallback identifier
        'company_name': env.company.name,
        'install_date': fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }

    # Send tracking data to your external server
    try:
        response = requests.post(
            # 'https://shopify-sync.synat.app/track-install',  # Replace with your server URL
            json=tracking_data,
            timeout=5
        )
        response.raise_for_status()
        _logger.info("Tracking data sent successfully: %s", tracking_data)
    except Exception as e:
        _logger.error("Failed to send tracking data: %s", str(e))

    _logger.info("Shopify Sync module installed successfully.")
    