---
title: "Integrate SQL data to Odoo"
---

[![Email](https://img.shields.io/badge/email-fasilwdr%40hotmail.com-brightgreen.png)](mailto:fasilwdr@hotmail.com) [![License: OPL-1](https://img.shields.io/badge/licence-OPL1-blue.png) ](#) [![/fasilwdr](https://raster.shields.io/badge/github-/fasilwdr-lightgray.png?logo=github)](https://github.com/fasilwdr)

This module help to integrate data from MS SQL to odoo

[Releases](#)
=============

*   **17.0.1.0.3 / 16-April-24 :** Binary fields can be integrated
*   **17.0.1.0.2 / 25-March-24 :** Enhancement
*   **17.0.1.0.1 / 27-March-23 :** First Release

[Supported in](#)
=================

*   ![Odoo Enterprise On-premise](https://img.shields.io/badge/odoo-Enterprice-%23714B67)
*   ![Odoo Community](https://img.shields.io/badge/odoo-Community-71639E)

[Features](#)
=============

*   Integrating data from MSSQL to the Odoo
*   Including the capability to schedule regular data transfers and specify which data sets to transfer.
*   **Integration Types:**
    *   **Create:** Create record forcefully
    *   **Create if not exist:** Create a record if it does not exist in Odoo
    *   **Update:** Update a record
    *   **Update & Create if not exist:** Update the record if it already exists in Odoo, otherwise create a new record.

[Usage](#)
==========

*   Settings --> SQL Integration
*   Provide credentials to connect with SQL
*   Select the model which you want to update
*   Provide domain filter to get unique value from data (for update record)
*   Select Action type (mentioned in features)  
    ![Connection](connection.png)
*   Press the "TEST CONNECTION" button to verify the connection to the SQL.  
    ![Test](test_button.png)
*   Provide the SQL query and execute it (Run Query) to obtain sample data as shown below  
    ![GetData](get_data.png)
*   Map the fields that need to be integrated from the data. Here are some mapping tips to help you with the process  
    ![Mapping](mapping.png)
*   To make everything ready for the integration process, press the 'MAKE IT READY' button
*   Once everything is ready, a green badge will appear as shown in the image below. Then, press 'RUN MANUALLY' to manually run the integration  
    ![Ready](ready.png)
*   If auto integration is required, you can enable it  
    ![Auto](automate.png)
*   Process is completed  
    ![Auto](integrated.png)

[Installation](#)
=================

Python libraries required:
```bash
$ pip3 install pyodbc
```    

Extra dependencies required:

*   Install the ODBC Driver, preferably [version 17](https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16&tabs=alpine18-install%2Cubuntu17-install%2Cdebian8-install%2Credhat7-13-install%2Crhel7-offline#17).
    

[Bug Tracker](#)
================

Bugs are reporting to me directly through [email](mailto:fasilwdr@hotmail.com). In case of trouble, help me smashing it by providing a detailed and welcomed

[Authors](#)
============

*   github/fasilwdr

[Maintainers](#)
================

This module is maintained by fasilwdr@hotmail.com.

[!<img src="https://avatars.githubusercontent.com/u/63807062?v=4" alt="Fasil" style="width: 100px;"/>](mailto:fasilwdr@hotmail.com)

[Contact/Support](#)
====================

Email: [fasilwdr@hotmail.com](mailto:fasilwdr@hotmail.com)  
WhatsApp: [https://wa.me/966538952934](https://wa.me/966538952934)  
Facebook: [https://www.facebook.com/fasilwdr](https://www.facebook.com/fasilwdr)  
Instagram: [https://www.instagram.com/fasilwdr](https://www.instagram.com/fasilwdr)


*Need help with the configuration or want this module to have more functionalities? Please contact me.*