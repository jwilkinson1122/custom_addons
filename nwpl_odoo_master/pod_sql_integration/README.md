---
title: "Integrate SQL data to Odoo"
---

This module help to integrate data from MS SQL to odoo

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

*   Install the ODBC Driver, [version 17](https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16&tabs=alpine18-install%2Cubuntu17-install%2Cdebian8-install%2Credhat7-13-install%2Crhel7-offline#17).
    
