import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def post_init_hook(env):
    _logger.warning("[HOOK] post_init_hook triggered on CPQ install")
    """Runs after module install or upgrade (Odoo 17-style env-based hook)."""
    _logger.info("Running CPQ post-init hook...")

    _link_attribute_values_to_options(env)
    _ensure_cpq_attributes_link_product_attributes(env)
    sync_cpq_values_to_product_attribute_values(env)
    check_cpq_value_links(env)
    fix_cpq_links(env)
    repair_cpq_attribute_links(env)
    cleanup_orphaned_product_attr_vals(env)
    env['product.template.attribute.value'].clean_orphaned_records()
    _logger.info("[OK] CPQ post-init hook completed.")

# This ensures everything is properly triangulated:
# cpq.attribute.value → linked_option_id → product.options → option_id → product.attribute
def _link_attribute_values_to_options(env):
    AttributeValue = env['cpq.attribute.value'].sudo()
    ProductOption = env['product.options'].sudo()

    values_to_update = AttributeValue.search([
        ('linked_option_id', '=', False),
        ('code', '!=', False),
    ])

    for val in values_to_update:
        match = ProductOption.search([('code', '=', val.code)], limit=1)
        if match:
            val.linked_option_id = match.id
            _logger.info("Linked Custom value '%s' to option '%s'", val.name, match.name)

            # Also link the option to the correct product.attribute if needed
            cpq_attr = val.attribute_id
            prod_attr = cpq_attr.linked_product_attribute_id
            if prod_attr and not match.option_id:
                match.option_id = prod_attr.id
                _logger.info("Linked product.option '%s' to product.attribute '%s'", match.name, prod_attr.name)

def _ensure_cpq_attributes_link_product_attributes(env):
    CPQAttribute = env['cpq.attribute'].sudo()
    ProductAttribute = env['product.attribute'].sudo()

    for cpq_attr in CPQAttribute.search([]):
        name = cpq_attr.name.strip()
        match = ProductAttribute.search([('name', '=', name)], limit=1)

        if not match:
            match = ProductAttribute.create({
                'name': name,
                'create_variant': 'no_variant',
            })
            _logger.info("[OK] Created new product.attribute for Custom attribute: %s", name)
        else:
            _logger.info("Matched Custom attribute '%s' to existing product.attribute ID %s", name, match.id)

        cpq_attr.linked_product_attribute_id = match.id

def sync_cpq_values_to_product_attribute_values(env):
    _logger = logging.getLogger(__name__)
    CPQVal = env["cpq.attribute.value"].sudo()
    ProdAttrVal = env["product.attribute.value"].sudo()

    created = 0
    skipped = 0

    for cpq_val in CPQVal.search([]):
        cpq_attr = cpq_val.attribute_id
        product_attr = cpq_attr.linked_product_attribute_id

        if not product_attr:
            _logger.warning("! No linked product.attribute for Custom attribute: %s", cpq_attr.name)
            continue

        existing = ProdAttrVal.search([
            ("name", "=", cpq_val.name),
            ("attribute_id", "=", product_attr.id),
        ], limit=1)

        if existing:
            skipped += 1
            continue

        ProdAttrVal.create({
            "name": cpq_val.name,
            "attribute_id": product_attr.id,
            "linked_option_id": cpq_val.linked_option_id.id,
            "cpq_custom_type": cpq_val.cpq_custom_type,
            "cpq_options_relaxed_validation": cpq_val.cpq_options_relaxed_validation,
            "html_color": cpq_val.html_color,
            "is_custom": False if cpq_val.linked_option_id else cpq_val.is_custom,

        })

        created += 1
        _logger.info("[OK] Created product.attribute.value '%s' under '%s'", cpq_val.name, product_attr.name)

    _logger.info("[OK] Sync complete. Created: %s, Skipped: %s", created, skipped)

def check_cpq_value_links(env):
    CPQVal = env["cpq.attribute.value"].sudo()
    ProductAttrVal = env["product.attribute.value"].sudo()

    issues = []

    for val in CPQVal:
        option_ok = bool(val.linked_option_id)
        prod_attr = val.attribute_id.linked_product_attribute_id
        prod_attr_ok = bool(prod_attr)

        actual_val = ProductAttrVal.search([
            ("name", "=", val.name),
        ])

        # Detect same-name records under the wrong attribute
        mislinked = any(
            pav.attribute_id.id != prod_attr.id
            for pav in actual_val if prod_attr
        )

        if not option_ok or not prod_attr_ok or mislinked:
            issues.append({
                "id": val.id,
                "name": val.name,
                "attribute": val.attribute_id.name,
                "option_ok": option_ok,
                "prod_attr_ok": prod_attr_ok,
                "mislinked": mislinked,
            })

    if not issues:
        return "<p style='color: green; font-weight: bold;'>All Custom attribute values are properly linked.</p>"

    table = """
    <style>
        table.cpq-report { border-collapse: collapse; width: 100%; }
        table.cpq-report th, table.cpq-report td { border: 1px solid #ccc; padding: 8px; }
        table.cpq-report th { background: #f4f4f4; text-align: left; }
        .bad { color: red; font-weight: bold; }
        .warn { color: orange; font-weight: bold; }
        .ok { color: green; }
    </style>
    <h3 style="color: #c00;">! Found %s Custom value(s) with linking issues</h3>
    <table class="cpq-report">
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Custom Attribute</th>
            <th>Option Linked</th>
            <th>Product Attr Linked</th>
            <th>Mislinked PAV</th>
        </tr>
    """ % len(issues)

    for issue in issues:
        table += f"""
        <tr>
            <td>{issue['id']}</td>
            <td>{issue['name']}</td>
            <td>{issue['attribute']}</td>
            <td class="{'ok' if issue['option_ok'] else 'bad'}">{'ok' if issue['option_ok'] else 'X'}</td>
            <td class="{'ok' if issue['prod_attr_ok'] else 'bad'}">{'ok' if issue['prod_attr_ok'] else 'X'}</td>
            <td class="{'warn' if issue['mislinked'] else 'ok'}">{'!' if issue['mislinked'] else 'ok'}</td>
        </tr>
        """

    table += "</table>"
    return table

def fix_cpq_links(env):
    _logger = logging.getLogger(__name__)

    CPQAttr = env["cpq.attribute"].sudo()
    CPQVal = env["cpq.attribute.value"].sudo()
    ProductAttr = env["product.attribute"].sudo()
    ProductVal = env["product.attribute.value"].sudo()
    Option = env["product.options"].sudo()

    # Step 1: Ensure all Custom Attributes are linked to a product.attribute
    for cpq_attr in CPQAttr.search([("linked_product_attribute_id", "=", False)]):
        match = ProductAttr.search([("name", "=", cpq_attr.name)], limit=1)
        if not match:
            match = ProductAttr.create({
                "name": cpq_attr.name,
                "create_variant": "no_variant",
            })
            _logger.info("[*] Created product.attribute for Custom attribute: %s", cpq_attr.name)
        cpq_attr.linked_product_attribute_id = match.id

    # Step 2: Ensure all Custom Values are linked to product.attribute.value
    for val in CPQVal.search([]):
        attr = val.attribute_id
        prod_attr = attr.linked_product_attribute_id
        if not prod_attr:
            _logger.warning("! Skipping value %s — attribute %s not linked", val.name, attr.name)
            continue

        # Try to auto-link to product.options by code
        if not val.linked_option_id and val.code:
            opt_match = Option.search([("code", "=", val.code)], limit=1)
            if opt_match:
                val.linked_option_id = opt_match.id
                _logger.info("[*] Linked Custom value '%s' to option '%s'", val.name, opt_match.name)

        # Look up existing product.attribute.value
        prod_val = ProductVal.search([
            ("name", "=", val.name),
            ("attribute_id", "=", prod_attr.id),
        ], limit=1)

        # If exists and linked_option_id is missing, update it
        if prod_val:
            if val.linked_option_id and not prod_val.linked_option_id:
                prod_val.linked_option_id = val.linked_option_id.id
                _logger.info("[OK] Linked PAV '%s' to option '%s'", prod_val.name, val.linked_option_id.name)
        else:
            # If doesn't exist, create it
            prod_val = ProductVal.create({
                "name": val.name,
                "attribute_id": prod_attr.id,
                "linked_option_id": val.linked_option_id.id if val.linked_option_id else False,
                "cpq_custom_type": val.cpq_custom_type,
                "cpq_options_relaxed_validation": val.cpq_options_relaxed_validation,
                "html_color": val.html_color,
                "is_custom": False if val.linked_option_id else val.is_custom,

            })
            _logger.info("[*] Created product.attribute.value for Custom value: %s", val.name)

        # No need to write reverse link unless you're tracking that explicitly
        # val.product_attribute_value_id = prod_val.id  # <-- skip unless needed

def repair_cpq_attribute_links(env):
    _logger = logging.getLogger(__name__)
    CPQAttrVal = env['cpq.attribute.value'].sudo()
    ProdAttr = env['product.attribute'].sudo()
    ProdAttrVal = env['product.attribute.value'].sudo()

    fixed = []
    created = []
    skipped = []
    fixed_set = set()

    for val in CPQAttrVal.search([]):
        cpq_attr = val.attribute_id
        if not cpq_attr or not cpq_attr.exists():
            _logger.warning("Skipping Custom value ID %s ('%s') — missing attribute_id", val.id, val.name)
            continue

        name = cpq_attr.name.strip()
        product_attr = ProdAttr.search([('name', '=', name)], limit=1)

        if not product_attr:
            product_attr = ProdAttr.create({
                'name': name,
                'create_variant': 'no_variant',
            })
            created.append(product_attr.name)
        else:
            fixed_set.add(product_attr.name)

        prod_attr_val = ProdAttrVal.search([
            ('name', '=', val.name),
            ('attribute_id', '=', product_attr.id),
        ], limit=1)

        if not prod_attr_val:
            ProdAttrVal.create({
                'name': val.name,
                'attribute_id': product_attr.id,
                'linked_option_id': val.linked_option_id.id,
                'cpq_custom_type': val.cpq_custom_type,
                'cpq_options_relaxed_validation': val.cpq_options_relaxed_validation,
                'html_color': val.html_color,
                "is_custom": False if val.linked_option_id else val.is_custom,

            })
            created.append(val.name)
        else:
            skipped.append(val.name)

    return {
        "attributes_fixed": sorted(fixed_set),
        "values_created": created,
        "values_skipped_existing": skipped,
    }

def cleanup_orphaned_product_attr_vals(env):
    ProductAttrVal = env['product.attribute.value'].sudo()
    orphans = ProductAttrVal.search([('attribute_id', '!=', False)]).filtered(lambda v: not v.attribute_id.exists())
    orphans.unlink()

def cleanup_broken_cpq_values(env, auto_delete=False):
    CPQVal = env["cpq.attribute.value"].sudo()
    broken = CPQVal.search([]).filtered(lambda val: not val.attribute_id or not val.attribute_id.exists())

    if not broken:
        _logger.info("No broken cpq.attribute.value records found.")
        return []

    _logger.warning("⚠ Found %s broken cpq.attribute.value records with missing attribute_id", len(broken))
    for val in broken:
        _logger.warning("- ID %s: name='%s', attribute_id=%s", val.id, val.name, val.attribute_id)

    if auto_delete:
        broken.unlink()
        _logger.info("Deleted %s broken Custom value records.", len(broken))

    return broken.ids

def bulk_fix_is_custom_flags(env):
    ProductValue = env["product.attribute.value"].sudo()
    broken_vals = ProductValue.search([
        ("linked_option_id", "!=", False),
        ("is_custom", "=", True),
    ])
    broken_vals.write({"is_custom": False})
    return len(broken_vals)
