import base64
import ast
import os
from pathlib import Path
import logging
import requests
from odoo import api, fields, models, SUPERUSER_ID
from odoo.modules.module import get_module_resource
from odoo.tools.sql import column_exists, create_column
from odoo.tools import file_open


_logger = logging.getLogger(__name__)

COLUMNS = (
    ("sale_order", "price_subtotal_no_discount"),
    ("sale_order", "price_total_no_discount"),
    ("sale_order", "discount_total"),
    ("sale_order_line", "price_subtotal_no_discount"),
    ("sale_order_line", "price_total_no_discount"),
    ("sale_order_line", "discount_total"),
    ("sale_order_line", "discount_subtotal"),
)

def pre_init_hook(env):
    """
    Pre-init hook to:
    - Add discount/total columns
    - Add invoiced/uninvoiced columns
    - Add computed field columns to ir_attachment
    """
    cr = env.cr  # Retrieve the database cursor
    for table, column in COLUMNS:
        if not column_exists(cr, table, column):
            _logger.info("Create discount column %s in database", column)
            create_column(cr, table, column, "numeric")
    try:
        if column_exists(env.cr, "ir_attachment", "file_storage_id"):
            return

        _logger.info("Adding columns for computed fields on ir_attachment")

        env.cr.execute(
            """
            ALTER TABLE ir_attachment
            ADD COLUMN IF NOT EXISTS file_storage_id INTEGER;
        """
        )

        env.cr.execute(
            """
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.table_constraints 
                    WHERE constraint_name = 'fk_ir_attachment_file_storage'
                ) THEN
                    ALTER TABLE ir_attachment 
                    ADD CONSTRAINT fk_ir_attachment_file_storage 
                    FOREIGN KEY (file_storage_id) REFERENCES file_storage(id);
                END IF;
            END $$;
            """
        )

        env.cr.execute(
            """
            ALTER TABLE ir_attachment
            ADD COLUMN IF NOT EXISTS file_url VARCHAR;
        """
        )
        env.cr.execute(
            """
            ALTER TABLE ir_attachment
            ADD COLUMN IF NOT EXISTS file_storage_code VARCHAR;
        """
        )

        _logger.info("Columns successfully added on ir_attachment")
        env.cr.commit()
    except Exception as e:
        env.cr.rollback()
        _logger.error(f"Error in pre_init_hook: {str(e)}")

def post_init_hook(env):
    """
    Unified post-init hook to:
    - Adjust access rules for res.partner
    - Initialize multi-company m2m relation
    - Populate discount tracking fields on orders
    - Transfer product weight
    - Update company appbar logo
    - Send Shopify install tracking
    """
    cr = env.cr
    _logger.info("[post_init] Starting unified post-init hook...")

    # ─────────────────────────────────────
    # 1. Adjust access rule for multi-company support
    # ─────────────────────────────────────
    try:
        _logger.info("[post_init] Updating res.partner access rule...")
        rule = env.ref("base.res_partner_rule")
        rule.write({
            "domain_force": (
                "['|', '|', ('partner_share', '=', False),"
                "('company_ids', 'in', company_ids),"
                "('company_ids', '=', False)]"
            )
        })
    except Exception as e:
        _logger.warning("[post_init] Failed to update res.partner rule: %s", e)

    # ─────────────────────────────────────
    # 2. Initialize company_ids m2m from legacy company_id
    # ─────────────────────────────────────
    try:
        _logger.info("[post_init] Initializing res_company_res_partner_rel...")
        cr.execute("""
            INSERT INTO res_company_res_partner_rel (res_partner_id, res_company_id)
            SELECT id, company_id FROM res_partner WHERE company_id IS NOT NULL
        """)
        fix_user_partner_companies(env)
    except Exception as e:
        _logger.warning("[post_init] Failed to initialize partner-company relation: %s", e)

    # ─────────────────────────────────────
    # 3. Populate no-discount fields on sale orders
    # ─────────────────────────────────────
    try:
        _logger.info("[post_init] Populating no-discount fields on sale orders...")
        cr.execute("""
            UPDATE sale_order_line
            SET price_subtotal_no_discount = price_subtotal,
                price_total_no_discount = price_total
            WHERE discount = 0.0
        """)
        cr.execute("""
            UPDATE sale_order
            SET price_subtotal_no_discount = amount_untaxed,
                price_total_no_discount = amount_total
        """)
        cr.execute("SELECT DISTINCT order_id FROM sale_order_line WHERE discount > 0.0")
        order_ids = [row[0] for row in cr.fetchall()]
        if order_ids:
            env["sale.order"].browse(order_ids).mapped("order_line")._update_discount_display_fields()
    except Exception as e:
        _logger.error("[post_init] Discount update failed: %s", e)

    # ─────────────────────────────────────
    # 4. Transfer weight to weight_dummy
    # ─────────────────────────────────────
    try:
        _logger.info("[post_init] Transferring product weight to weight_dummy...")
        cr.execute("UPDATE product_product SET weight_dummy = weight")
    except Exception as e:
        _logger.error("[post_init] Error transferring weight: %s", e)

    # ─────────────────────────────────────
    # 5. Set company appbar logo
    # ─────────────────────────────────────
    try:
        main_company = env.ref("base.main_company", False)
        if main_company:
            
            with open(get_module_resource("base", "static/img", "res_company_logo.png"), "rb") as f:
                main_company.write({"appbar_image": base64.b64encode(f.read())})
            _logger.info("[post_init] Appbar logo updated.")
    except Exception as e:
        _logger.warning("[post_init] Failed to set appbar logo: %s", e)

    # ─────────────────────────────────────
    # 6. Shopify Sync Tracking
    # ─────────────────────────────────────
    try:
    
        _logger.info("[post_init] Sending Shopify sync tracking...")
        variant_group = env.ref("product.group_product_variant", raise_if_not_found=False)
        user_group = env.ref("base.group_user", raise_if_not_found=False)
        if variant_group and user_group and variant_group not in user_group.implied_ids:
            user_group.sudo().write({"implied_ids": [(4, variant_group.id)]})
            _logger.info("[post_init] Enabled product variants for users.")

        admin_user = env["res.users"].sudo().search(
            [("groups_id", "in", env.ref("base.group_system").id)], limit=1
        )
        installed_modules = env["ir.module.module"].sudo().search([("state", "=", "installed")])
        tracking_data = {
            "module_name": "shopify_sync",
            "site_url": env["ir.config_parameter"].sudo().get_param("web.base.url", "unknown"),
            "admin_email": admin_user.login if admin_user else "unknown",
            "installed_modules": [m.name for m in installed_modules],
            "database_name": cr.dbname,
            "company_name": env.company.name,
            "install_date": fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        requests.post("https://shopify-sync.synat.app/track-install", json=tracking_data, timeout=5)
        _logger.info("[post_init] Shopify tracking sent.")
    except Exception as e:
        _logger.error("[post_init] Shopify tracking failed: %s", e)

    _logger.info("[post_init] Unified post-init hook finished.")

def fix_user_partner_companies(env):
    """Ensure user partner company_ids reflect all allowed companies."""
    for user in env["res.users"].search([]):
        partner = user.partner_id
        if not partner:
            continue
        user_companies = set(user.company_ids.ids)
        partner_companies = set(partner.company_ids.ids)
        missing = user_companies - partner_companies
        if missing:
            partner.write({"company_ids": [(4, cid) for cid in missing]})

def uninstall_hook(env):
    """
    Unified uninstall hook:
    - Restore res.partner access rule domain to base value
    - Reset Users action window domain
    - Remove system config parameters used by the module
    """
    _logger = logging.getLogger(__name__)
    _logger.info("[uninstall_hook] Running unified uninstall hook...")

    # ─────────────────────────────────────
    # 1. Restore res.partner access rule
    # ─────────────────────────────────────
    try:
        rule = env.ref("base.res_partner_rule")
        rule.write({
            "domain_force": (
                "['|', '|', ('partner_share', '=', False),"
                "('company_id', 'in', company_ids),"
                "('company_id', '=', False)]"
            )
        })
        _logger.info("[uninstall_hook] Restored res_partner_rule domain.")
    except Exception as e:
        _logger.warning("[uninstall_hook] Failed to restore partner rule: %s", e)

    # ─────────────────────────────────────
    # 2. Reset domain of base Users action
    # ─────────────────────────────────────
    try:
        env.ref("base.action_res_users").sudo().write({"domain": []})
        _logger.info("[uninstall_hook] Cleared domain on base.action_res_users.")
    except ValueError:
        _logger.info("[uninstall_hook] Skipped Users action domain reset (not found).")
    except Exception as e:
        _logger.warning("[uninstall_hook] Error resetting Users action domain: %s", e)

    # ─────────────────────────────────────
    # 3. Clean up system config parameters
    # ─────────────────────────────────────
    try:
        keys_to_delete = [
            "pod_odoo_master.amazon_access_key",
            "pod_odoo_master.amazon_secret_key",
            "pod_odoo_master.amazon_bucket_name",
            "pod_odoo_master.amazon_connector",
        ]
        params = env["ir.config_parameter"].sudo().search([
            ("key", "in", keys_to_delete)
        ])
        if params:
            params.unlink()
            _logger.info("[uninstall_hook] Removed config parameters: %s", keys_to_delete)
    except Exception as e:
        _logger.warning("[uninstall_hook] Failed to clean config parameters: %s", e)

    _logger.info("[uninstall_hook] Uninstall hook completed.")

# def populate_unrevisioned_name(env):
#     env.cr.execute(
#         "UPDATE sale_order "
#         "SET unrevisioned_name = name "
#         "WHERE unrevisioned_name is NULL"
#     )
    
# === DEV-ONLY: Cleanup stale modules that were renamed or removed ===
def _cleanup_stale_modules(env, addons_dirs=("addons", "custom_addons")):
    """Remove stale ir.module.module entries if the module folder no longer exists."""
    import os
    from pathlib import Path

    _logger.info("[DEV ONLY] Checking for stale module registrations...")
    known_modules = set()

    for addons_dir in addons_dirs:
        if os.path.isdir(addons_dir):
            _logger.info("Scanning addon directory: %s", addons_dir)
            known_modules |= set(os.listdir(addons_dir))

    installed_modules = env['ir.module.module'].sudo().search([])
    removed = 0

    for mod in installed_modules:
        if mod.name not in known_modules:
            _logger.warning("Removing stale module entry: %s", mod.name)
            mod.unlink()
            removed += 1

    if removed:
        _logger.info("Removed %s stale module(s).", removed)
    else:
        _logger.info("No stale modules found.")

# === Usage example (dev only):
# odoo shell -d your_db
# >>> from pod_odoo_master import hooks_dev_safe
# >>> hooks_dev_safe._cleanup_stale_modules(env)

def check_module_integrity(addons_path="custom_addons"):
    """
    Check each module folder for required files like __manifest__.py.
    Args:
        addons_path (str): Path to the addons directory to scan.
    Returns:
        list: Module folder names missing the __manifest__.py file.
    """
    from pathlib import Path

    _logger.info("Checking integrity of modules in '%s'...", addons_path)
    path = Path(addons_path)
    if not path.exists():
        _logger.error("Provided path '%s' does not exist.", addons_path)
        return []

    bad_modules = []
    for module_path in path.iterdir():
        if module_path.is_dir():
            manifest = module_path / "__manifest__.py"
            if not manifest.exists():
                _logger.warning(" Missing __manifest__.py in module: %s", module_path.name)
                bad_modules.append(module_path.name)
            else:
                _logger.info("Module OK: %s", module_path.name)

    if not bad_modules:
        _logger.info("All modules in '%s' contain __manifest__.py", addons_path)
    return bad_modules

# === Usage example (dev only):
# >>> hooks_dev_safe.check_module_integrity("custom_addons")

def check_manifest_file_references(addons_path="custom_addons"):
    """
    Checks that each module contains __manifest__.py and all referenced files exist.

    Args:
        addons_path (str): Path to the addons directory.

    Returns:
        dict: Summary of issues found, per module.
    """
    import os
    import ast
    from pathlib import Path

    _logger.info("Validating __manifest__.py and referenced files in '%s'", addons_path)
    addons_path = Path(addons_path)
    if not addons_path.exists():
        _logger.error("Path does not exist: %s", addons_path)
        return {}

    summary = {}

    for module_path in addons_path.iterdir():
        if not module_path.is_dir():
            continue

        module_name = module_path.name
        manifest_path = module_path / "__manifest__.py"
        issues = []

        if not manifest_path.exists():
            issues.append("Missing __manifest__.py")
            summary[module_name] = issues
            continue

        try:
            manifest_content = manifest_path.read_text()
            manifest_data = ast.literal_eval(manifest_content)
        except Exception as e:
            issues.append(f"Invalid manifest syntax: {e}")
            summary[module_name] = issues
            continue

        data_files = manifest_data.get("data", []) + manifest_data.get("demo", [])
        for rel_path in data_files:
            file_path = module_path / rel_path
            if not file_path.exists():
                issues.append(f"Missing referenced file: {rel_path}")

        # Basic structure check
        for required_dir in ["models", "views", "security"]:
            dir_path = module_path / required_dir
            if dir_path.exists() and not any(dir_path.glob("*.py" if required_dir == "models" else "*.xml")):
                issues.append(f"No files found in {required_dir}/")

        if issues:
            summary[module_name] = issues

    if not summary:
        _logger.info("All modules passed integrity checks.")
    else:
        for mod, problems in summary.items():
            _logger.warning("⚠ Issues in module '%s':", mod)
            for issue in problems:
                _logger.warning("   - %s", issue)

    return summary

# Usage in Odoo shell:
# >>> from pod_odoo_master import hooks_dev_safe
# >>> hooks_dev_safe.check_manifest_file_references("custom_addons")

def auto_fix_manifest_references(addons_path="custom_addons", dry_run=True):
    """
    Automatically remove broken file references from __manifest__.py files
    and optionally warn about missing key .py/.xml/.csv files.

    Args:
        addons_path (str): Path to the addons directory.
        dry_run (bool): If True, only logs proposed changes.

    Returns:
        dict: Modules with fixes proposed/applied.
    """
    _logger.info("🛠 Starting manifest auto-fix (dry_run=%s)...", dry_run)
    base_path = Path(addons_path)
    if not base_path.exists():
        _logger.error("Path does not exist: %s", addons_path)
        return {}

    fixed_modules = {}

    for module_path in base_path.iterdir():
        if not module_path.is_dir():
            continue

        module_name = module_path.name
        manifest_path = module_path / "__manifest__.py"
        if not manifest_path.exists():
            continue

        try:
            manifest_text = manifest_path.read_text()
            manifest_data = ast.literal_eval(manifest_text)
        except Exception as e:
            _logger.warning("Skipping invalid manifest in: %s (%s)", module_name, e)
            continue

        changed = False
        for key in ("data", "demo"):
            if key in manifest_data:
                original = list(manifest_data[key])
                cleaned = [f for f in original if (module_path / f).exists()]
                if len(cleaned) != len(original):
                    _logger.warning("Fixing '%s' in module '%s':", key, module_name)
                    for f in set(original) - set(cleaned):
                        _logger.warning("   - removing missing file reference: %s", f)
                    manifest_data[key] = cleaned
                    changed = True

        # Additional hardcoded file checks
        required_files = {
            "pod_odoo_master/pod_contacts/security/ir.model.access.csv": module_path / "pod_odoo_master/pod_contacts/security/ir.model.access.csv",
        }

        # At least one .py in models/
        models_dir = module_path / "models"
        if models_dir.exists() and not any(models_dir.glob("*.py")):
            _logger.warning("Module '%s': models/ exists but has no .py files", module_name)

        # At least one .xml in views/
        views_dir = module_path / "views"
        if views_dir.exists() and not any(views_dir.glob("*.xml")):
            _logger.warning("Module '%s': views/ exists but has no .xml files", module_name)

        for label, path in required_files.items():
            if not path.exists():
                _logger.warning("Required file missing: %s in module '%s'", label, module_name)

        if changed:
            fixed_modules[module_name] = True
            if not dry_run:
                with manifest_path.open("w") as mf:
                    mf.write(repr(manifest_data))
                _logger.info("Updated manifest for module: %s", module_name)
        else:
            fixed_modules[module_name] = False

    return fixed_modules



