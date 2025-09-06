===
cpq
===

This module provides the base functionality:

- Prevents the automatic creation of variants
- Extends of product attributes to allow custom options
- Custom options are propagated to variants, preventing the stock system from mixing them up
- An Owl based UI to configure products (read: create variants)

Additional modules should almost always be installed:
- cpq_sale for sale integration
- cpq_mrp for dynamic BoM generation
- cpq_account for accounts integration

-----------------------------------------------------------
Manual Product Creation & Promotion from Custom Configurations 
-----------------------------------------------------------

## Features

Manual promotion of Custom configurations into real products  
Confirmation wizard with product name and internal reference preview  
Batch promotion of multiple sale order lines at once  
Sale order line tree view shows promotion status ("Promoted" or not)  
Print/export Custom configuration summary from confirmation wizard  
Clean chatter logging on order lines and created products  
Full compatibility with Odoo standard flows  
Ready for future improvements: auto-assign category, bulk export, etc.  

## Installation

1. Copy the `cpq_sale/` folder into your Odoo `addons/` directory.
2. Update the Odoo Apps List.
3. Install the **Custom Sale** module.

## Usage

- Open a Sale Order.
- Add a configured Custom product to the order.
- Use the **Create Product from Configuration** button on the order line.
- Alternatively, select multiple lines in the Sale Order Lines list view and use the batch creation action.
- In the wizard, confirm creation. Optionally, print the Custom configuration summary.

## Technical Notes

- This module extends `sale.order.line`.
- Created products will use internal reference format: `CFG-<DATE>-<LINE ID>-<CUSTOMER>`.
- Configuration summary is used as part of the product description.
- All actions are logged in chatter for auditability.

## 🧭 Roadmap

- Batch creation wizard [OK]
- Print/export Custom configuration summary [OK]
- 🔜 Optional auto-assign category or pricelist
- 🔜 Optional advanced security groups
- 🔜 Optional multi-line configuration print/export
- 🔜 Optional PDF merge for bulk printing summaries

## cpq_cleanup_action

Go to Settings → Technical → Automation → Server Actions.
You will see “Cleanup Custom Flags on Product Templates”.
Run it manually any time you want to clean up the Custom flags.
The result will be shown as a popup with the summary of what was done.

🟢 menu item:
Products → Configuration → Custom Cleanup Tool
Opens the product.template list view (tree view).
The server action will run immediately (since it uses code).
You’ll get a popup message showing which templates were cleaned up or skipped.


## Custom Cleanup Tools

| **Action**                  | **Method Called**                | **Helps with Missing `product.attribute.value(35)`?** | **Purpose**                                                                 |
| --------------------------- | -------------------------------- | ----------------------------------------------------- | --------------------------------------------------------------------------- |
| `Repair Custom Links`          | `/cpq/dev/repair_links`          | No                                                  | Likely attempts to relink `cpq.attribute.value` to product/option records.  |
| `Check Custom Links`           | `/cpq/dev/check_links`           | No                                                  | Diagnostic only. May tell you something is wrong, doesn't fix it.           |
| `Cleanup Broken Custom Values` | `model.cleanup_cpq_values_ui()`  | No                                                  | Cleans broken/missing links in `cpq.attribute.value` (not `p.a.v`).         |
| `Cleanup Orphaned PTAVs`    | `model.cleanup_ptavs_ui()`       | Indirectly                                          | Deletes `product.template.attribute.value` with missing PAV/attribute refs. |
| `Fix Custom Links`             | `model.fix_links_ui()`           | No                                                  | Repairs internal Custom links, but not missing base `product.attribute.value`. |
| `Clean Orphaned PTAVs`      | `model.clean_orphaned_records()` | Indirectly                                          | Removes PTAVs with broken `product_attribute_value_id` refs (like 35).      |


## Frontend Files (JavaScript/ESM/XML templates) 
These run in the browser, interact with Owl components, and manage UI logic.

| File                                | Purpose                                                                         |
| ----------------------------------- | ------------------------------------------------------------------------------- |
| `dialog.esm.js`                     | Main CPQ configurator dialog logic (state, slots, UI actions)                   |
| `configurator_summary_panel.esm.js` | Renders the attribute summary panel inside the configurator                     |
| `sale_product_field.esm.js`         | Patches the product field in the sale order line form to launch the dialog      |
| `utils.esm.js`                      | Utility helpers used across your CPQ dialog (e.g., `getSafeConfiguratorValues`) |
| `dialog.xml`                        | Owl template layout for the CPQ dialog (slots, summary, buttons)                |


## Backend Files (Python / XML controller & logic)
These run server-side inside Odoo and process data.

| File                 | Purpose                                                                                            |
| -------------------- | -------------------------------------------------------------------------------------------------- |
| `summary_helper.py`  | Core logic to render summaries, handle `splitByAttrMap`, PTAVs, and price computation              |
| `main.py`            | Your Odoo controller logic (includes the `/configure` route that saves config and renders summary) |
| `sale_order_line.py` | Likely contains model extensions or fields for CPQ configuration                                   |
| `sale_order.xml`     | XML view overrides (e.g., fields like `cpq_configuration_summary`)                                 |
