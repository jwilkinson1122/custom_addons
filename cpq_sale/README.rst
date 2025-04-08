--------
cpq_sale
--------

Integrate CPQ and sale modules.

Requires the use of `sale_product_configurator`.

Hooks the sale_product_configurator widget to inject the Cpq ConfigureDialog
widget.


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

1. Copy the `cpq_sale/` folder into your Odoo `addons/` directory.
2. Update the Odoo Apps List.
3. Install the **CPQ Sale** module.

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

