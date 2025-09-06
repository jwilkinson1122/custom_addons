**Shopify Sync** provides integration between multiple Shopify stores and Odoo, ensuring real-time synchronization of inventory and sales orders. Unlike traditional connectors that create duplicate products for each store, this module maintains a **single product record** in Odoo, even if it exists across multiple Shopify stores.  


### **Key Features**  
**Multi-Store Product Sync**  
- Products with the same SKU in different Shopify stores are mapped to a single product in Odoo.  
- Avoids duplicate product records for each store.  

**Real-Time Inventory Updates**  
- Whenever stock updates occur in any Shopify store, the updated quantity is synced to Odoo and all connected Shopify stores.  
- Prevents overselling and ensures inventory consistency.  

**Shopify Sales Order Sync to Odoo**  
- Sales orders from any Shopify store are automatically created in Odoo.  
- Odoo updates the inventory accordingly across all linked Shopify stores.  
- **Note:** The module does **not** create sales orders in other stores, only inventory updates occur.  

**Bidirectional Inventory Sync**  
- Inventory changes made in Odoo (manual updates, purchase orders, stock adjustments) are pushed to all Shopify stores.  
- Sales orders from Shopify trigger inventory updates in Odoo and subsequently across all stores.  

**Automated Scheduled Actions**  
- Background jobs ensure stock levels remain up-to-date without manual intervention.  
- Configurable cron jobs for periodic synchronization.  

**Easy Setup & Configuration**  
- Simple UI to connect and manage multiple Shopify stores.  
- User-friendly interface for store-specific settings and inventory controls.  

---

### ** **  
🔹 Eliminates duplicate product creation across stores.  
🔹 Prevents inventory mismatches and ensures accurate stock levels.  
🔹 Automates Shopify-to-Odoo sales order creation.  
🔹 Works in real-time with minimal manual effort.  
🔹 Supports businesses managing multiple Shopify stores under one Odoo system.  

---

### **Dependencies**  
This module depends on the following Odoo apps:  
- **Stock Management** (`stock`)  
- **Sales Management** (`sale`)  

---
