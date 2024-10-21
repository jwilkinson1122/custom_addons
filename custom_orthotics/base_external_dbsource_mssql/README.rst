================================
External Database Source - MSSQL
================================

This module extends ``base_external_dbsource``, allowing you to connect to
foreign MSSQL databases using SQLAlchemy.

Installation
============

To install this module, you need to:

* Install & configure FreeTDS driver (tdsodbc package)
* Install ``sqlalchemy`` and ``pymssql`` python libraries
* Install ``base_external_dbsource_sqlite`` Odoo module

Configuration
=============

To configure this module, you need to:

#. Database sources can be configured in Settings > Technical >
   Database Structure > Database sources.

Usage
=====

To use this module:

* Go to Settings > Technical > Database Structure > Database Sources
* Click on Create to enter the following information:

* Datasource name 
* Pasword
* Connector: Choose the database to which you want to connect
* Connection string: Specify how to connect to database

