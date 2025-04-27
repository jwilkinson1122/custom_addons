===
cpq
===

This module provides the base functionality:

- Prevents the automatic creation of variants
- Extends of product attributes to allow custom options
- Custom options are propagated to variants, preventing the stock system from mixing them up
- An Owl based UI to configure products (read: create variants)

Additional modules should almost always be installed:
- cpq for sale integration
- cpq_mrp for dynamic BoM generation
- cpq_account for accounts integration

-----------------------------------------------------------
Manual Product Creation & Promotion from CPQ Configurations 
-----------------------------------------------------------

## 📦 Features

✅ Manual promotion of CPQ configurations into real products  
✅ Confirmation wizard with product name and internal reference preview  
✅ Batch promotion of multiple sale order lines at once  
✅ Sale order line tree view shows promotion status ("Promoted" or not)  
✅ Print/export CPQ configuration summary from confirmation wizard  
✅ Clean chatter logging on order lines and created products  
✅ Full compatibility with Odoo standard flows  
✅ Ready for future improvements: auto-assign category, bulk export, etc.  

## 🛠️ Installation

1. Copy the `cpq/` folder into your Odoo `addons/` directory.
2. Update the Odoo Apps List.
3. Install the **CPQ** module.

## 🔍 Usage

- Open a Sale Order.
- Add a configured CPQ product to the order.
- Use the **Create Product from Configuration** button on the order line.
- Alternatively, select multiple lines in the Sale Order Lines list view and use the batch creation action.
- In the wizard, confirm creation. Optionally, print the CPQ configuration summary.

## 🧩 Technical Notes

- This module extends `sale.order.line`.
- Created products will use internal reference format: `CFG-<DATE>-<LINE ID>-<CUSTOMER>`.
- Configuration summary is used as part of the product description.
- All actions are logged in chatter for auditability.

## 🧭 Roadmap

- ✅ Batch creation wizard ✅
- ✅ Print/export CPQ configuration summary ✅
- 🔜 Optional auto-assign category or pricelist
- 🔜 Optional advanced security groups
- 🔜 Optional multi-line configuration print/export
- 🔜 Optional PDF merge for bulk printing summaries

## 🛠️ cpq_cleanup_action

Go to Settings → Technical → Automation → Server Actions.
You will see “Cleanup CPQ Flags on Product Templates”.
Run it manually any time you want to clean up the CPQ flags.
The result will be shown as a popup with the summary of what was done.

🟢 menu item:
Products → Configuration → CPQ Cleanup Tool
Opens the product.template list view (tree view).
The server action will run immediately (since it uses code).
You’ll get a popup message showing which templates were cleaned up or skipped.