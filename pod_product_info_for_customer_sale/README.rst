======================================
Product Info for Customer Sale
======================================

Based on pod_product_info_for_customer, this module loads in every sale order the
customer code defined in the product and allows use the product codes and product name
configured in each products in sale orders.

If you use Advanced price rules with formulas to define your pricing, and
choose that the price should be calculated from the partner prices in the
product form, the quantity in the sales order will be proposed from
the minimum quantity defined in the customerinfo.

Usage
=====

To use this module, you need:

- Go to product and configure *Partner product name* and *Partner product code*
  for each selected customer.

- When add order lines in sale quotation for a customer that has an specific
  name and code in the product, you can search that product with that customer
  name or code. Then, this values will be displayed in product description.

- If product does not have a configuration for customer selected, product will
  be search by its default code.

Known issues / Roadmap
======================

* Putting a minimum qty in a pricelist rule means the system will use the
  option 'list price' instead of any option you chose.
