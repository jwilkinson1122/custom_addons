==================================
Product Info for Customers
==================================

This modules allows to use supplier info structure, available in
*Inventory* tab of the product form, also for defining customer information,
allowing to define prices per customer and product.

Configuration
=============

For these prices to be used in sale prices calculations, you will have
to create a pricelist with a rule with option "Based on" with the value
"Partner Prices: Take the price from the customer info on the 'product form')".

Usage
=====

There's a new section on *Sales* tab of the product form called "Customers",
where you can define records for customers with the same structure of the
suppliers.

There's a new option on pricelist items that allows to get the prices from the
supplierinfo at the product form.

Known issues / Roadmap
======================

* Product prices through this method are only guaranteed on the standard sale
  order workflow. Other custom flows maybe don't reflect the price.
* The minimum quantity will neither apply on sale orders.
