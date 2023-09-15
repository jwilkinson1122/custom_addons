=================
Sales commissions
=================

This module allows to define sales agents with their commissions and assign
them in customers and sales orders.

You can then make the settlements of these commissions, and generate the
corresponding supplier invoices to pay their commissions fees.

You can define which base amount is going to be taken into account: net amount
(based on margin) or gross amount (line subtotal amount)

Configuration
=============

For adding commissions:

#. Go to *Sales > Commission Management > Commission types*.
#. Edit or create a new record.
#. Select a name for distinguishing that type.
#. Select the percentage type of the commission:

   * **Fixed percentage**: all commissions are computed with a fixed
     percentage. You can fill the percentage in the field "Fixed percentage".
   * **By sections**: percentage varies depending amount intervals. You can
     fill intervals and percentages in the section "Rate definition".

#. Select the base amount for computing the percentage:

   * **Gross Amount**: percentage is computed from the amount put on
     sales order/invoice.
   * **Net Amount**: percentage is computed from the profit only, taken the
     cost from the product.

#. Select the invoice status for settling the commissions:

   * **Invoice Based**: Commissions are settled when the invoice is issued.
   * **Payment Based**: Commissions are settled when the invoice is paid.

For adding new agents:

#. Go to *Sales > Commission Management > Agents*. You can also access from
   *Contacts > Contacts* or *Sales > Orders > Customers*.
#. Edit or create a new record.
#. On "Sales & Purchases" page, mark "Agent" check. It should be checked if
   you have accessed from first menu option.
#. There's a new page called "Agent information". In it, you can set following
   data:

   * The agent type, being in this base module "External agent" the only
     existing configuration. It can be extended with `hr_commission` module
     for setting an "Employee" agent type.
   * The associated commission type.
   * The settlement period, where you can select:
   *
     * Monthly: the settlement will be done for the whole past month.
     * Bi-weekly: there will be 2 settlement per month, one covering the first
       15 days, and the other for the rest of the month.
     * Quaterly: the settlement will cover a quarter of the year (3 months).
     * Semi-annual: there will be 2 settlements for each year, each one
       covering 6 months.
     * Annual: only one settlement per year.

   You will also be able to see the settlements that have been made to this
   agent from this page.

Usage
=====

For setting default agents in customers:

#. Go to *Sales > Orders > Customers* or *Contacts > Contacts*.
#. Edit or create a new record.
#. On "Sales & Purchases" page, you will see a field called "Agents" where
   they can be added. You can put the number of agents you want, but you can't
   select specific commission for each partner in this base module.

For adding commissions on sales orders:

#. Go to *Sales > Orders > Quotations*.
#. Edit or create a new record.
#. When you have selected a partner, each new quotation line you add will have
   the agents and commissions set at customer level.
#. You can add, modify or delete these agents discretely clicking on the
   icon with several persons represented, next to the "Commission" field in the
   list. This icon will be available only if the line hasn't been invoiced yet.
#. If you have configured your system for editing lines in a popup window,
   agents will appear also in this window.
#. You have a button "Recompute lines agents" on the bottom of the page
   "Order Lines" for forcing a recompute of all agents from the partner setup.
   This is needed for example when you have changed the partner on the
   quotation having already inserted lines.

For adding commissions on invoices:

#. Go to *Invoicing > Sales > Customer Invoices*.
#. Follow the same steps as in sales orders.
#. The agents icon will be in this ocassion visible when the line hasn't been
   settled.
#. Take into account that invoices sales orders will transfer agents
   information when being invoiced.

For settling the commissions to agents:

#. Go to *Sales > Commissions Management > Settle commissions*.
#. On the window that appears, you should select the date up to which you
   want to create commissions. It should be at least one day after the last
   period date. For example, if you settlements are monthly, you have to put
   at least the first day of the following month.
#. You can settle only certain agents if you select them on the "Agents"
   section. Leave it empty for settling all.
#. Click on "Make settlements" button.
#. If there are new settlements, they will be shown after this.

For invoicing the settlements (only for external agents):

#. Go to *Sales > Commissions Management > Create commission invoices*.
#. On the window that appears, you can select following data:

   * Product. It should be a service product for being coherent.
   * Journal: To be selected between existing purchase journals.
   * Date: If you want to choose a specific invoice date. You can leave it
     blank if you prefer.
   * Settlements: For selecting specific settlements to invoice. You can leave
     it blank as well for invoicing all the pending settlements.

#. If you want to invoice a specific settlement, you can navigate to it in
   *Sales > Commissions Management > Settlements*, and click on "Make invoice"
   button.

Known issues / Roadmap
======================

* Make it totally multi-company aware.
* Be multi-currency aware for settlements.
* Allow to calculate and pay in other currency different from company one.
* Allow to group by agent when generating invoices.
* Set agent popup window with a kanban view with richer information and
  mobile friendly.

