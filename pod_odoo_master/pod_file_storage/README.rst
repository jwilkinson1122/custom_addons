==========================
Filesystem Storage Backend
==========================

This addon is a technical addon that allows you to define filesystem like
storage for your data. It's used by other addons to store their data in a
transparent way into different kind of storages.

Through the file.storage record, you get access to an object that implements
the `fsspec.spec.AbstractFileSystem <https://filesystem-spec.readthedocs.io/en/
latest/api.html#fsspec.spec.AbstractFileSystem>`_ interface and therefore give
you an unified interface to access your data whatever the storage protocol you
decide to use.

The list of supported protocols depends on the installed fsspec implementations.
By default, the addon will install the following protocols:

* LocalFileSystem
* MemoryFileSystem
* ZipFileSystem
* TarFileSystem
* FTPFileSystem
* CachingFileSystem
* WholeFileSystem
* SimplCacheFileSystem
* ReferenceFileSystem
* GenericFileSystem
* DirFileSystem
* DatabricksFileSystem
* GitHubFileSystem
* JupiterFileSystem
* OdooFileSystem

The OdooFileSystem is the one that allows you to store your data into a directory
mounted into your Odoo's storage directory. This is the default File Storage
when creating a new file.storage record.

Others protocols are available through the installation of additional
python packages:

* DropboxDriveFileSystem -> `pip install fsspec[dropbox]`
* HTTPFileSystem -> `pip install fsspec[http]`
* HTTPSFileSystem -> `pip install fsspec[http]`
* GCSFileSystem -> `pip install fsspec[gcs]`
* GSFileSystem -> `pip install fsspec[gs]`
* GoogleDriveFileSystem -> `pip install gdrivefile`
* SFTPFileSystem -> `pip install fsspec[sftp]`
* HaddoopFileSystem -> `pip install fsspec[hdfile]`
* S3FileSystem -> `pip install fsspec[s3]`
* WandbFile -> `pip install wandbfile`
* OCIFileSystem -> `pip install fsspec[oci]`
* AsyncLocalFileSystem -> `pip install 'morefile[asynclocalfile]`
* AzureDatalakeFileSystem -> `pip install fsspec[adl]`
* AzureBlobFileSystem -> `pip install fsspec[abfile]`
* DaskWorkerFileSystem -> `pip install fsspec[dask]`
* GitFileSystem -> `pip install fsspec[git]`
* SMBFileSystem -> `pip install fsspec[smb]`
* LibArchiveFileSystem -> `pip install fsspec[libarchive]`
* OSSFileSystem -> `pip install ossfile`
* WebdavFileSystem -> `pip install webdav4`
* DVCFileSystem -> `pip install dvc`
* XRootDFileSystem -> `pip install fsspec-xrootd`

This list of supported protocols is not exhaustive or could change in the future
depending on the fsspec releases. You can find more information about the
supported protocols on the `fsspec documentation
<https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec.spec.AbstractFileSystem>`_.

**Table of contents**

.. contents::
   :local:

Usage
=====

Configuration
~~~~~~~~~~~~~

When you create a new backend, you must specify the following:

* The name of the backend. This is the name that will be used to
  identify the backend into Odoo
* The code of the backend. This code will identify the backend into the store_fname
  field of the ir.attachment model. This code must be unique. It will be used
  as scheme. example of the store_fname field: ``odoofile://abs34Tg11``.
* The protocol used by the backend. The protocol refers to the supported
  protocols of the fsspec python package.
* A directory path. This is a root directory from which the filesystem will
  be mounted. This directory must exist.
* The protocol options. These are the options that will be passed to the
  fsspec python package when creating the filesystem. These options depend
  on the protocol used and are described in the fsspec documentation.
* Resolve env vars. This options resolves the protocol options values starting
  with $ from environment variables
* Check Connection Method. If set, Odoo will always check the connection before using
  a storage and it will remove the file connection from the cache if the check fails.

  * ``Create Marker file`` : create a hidden file on remote and then check it exists with
    Use it if you have write access to the remote and if it is not an issue to leave
    the marker file in the root directory.
  * ``List file`` : list all files from the root directory. You can use it if the directory
    path does not contain a big list of files (for performance reasons)

Some protocols defined in the fsspec package are wrappers around other
protocols. For example, the SimpleCacheFileSystem protocol is a wrapper
around any local filesystem protocol. In such cases, you must specify into the
protocol options the protocol to be wrapped and the options to be passed to
the wrapped protocol.

For example, if you want to create a backend that uses the SimpleCacheFileSystem
protocol, after selecting the SimpleCacheFileSystem protocol, you must specify
the protocol options as follows:

.. code-block:: python

    {
        "directory_path": "/tmp/my_backend",
        "target_protocol": "odoofile",
        "target_options": {...},
    }

In this example, the SimpleCacheFileSystem protocol will be used as a wrapper
around the odoofile protocol.

Server Environment
~~~~~~~~~~~~~~~~~~

To ease the management of the filesystem storages configuration accross the different
environments, the configuration of the filesystem storages can be defined in
environment files or directly in the main configuration file. For example, the
configuration of a filesystem storage with the code `fileprod` can be provided in the
main configuration file as follows:

.. code-block:: ini

  [pod_odoo_master.fileprod]
  protocol=s3
  options={"endpoint_url": "https://my_s3_server/", "key": "KEY", "secret": "SECRET"}
  directory_path=my_bucket

To work, a `storage.backend` record must exist with the code `fileprod` into the database.
In your configuration section, you can specify the value for the following fields:

* `protocol`
* `options`
* `directory_path`

Migration from storage_backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The file_storage addon can be used to replace the storage_backend addon. (It has
been designed to be a drop-in replacement for the storage_backend addon). To
ease the migration, the `file.storage` model defines the high-level methods
available in the storage_backend model. These methods are:

* `add`
* `get`
* `list_files`
* `find_files`
* `move_files`
* `delete`

These methods are wrappers around the methods of the `fsspec.AbstractFileSystem`
class (see https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec.spec.AbstractFileSystem).
These methods are marked as deprecated and will be removed in a future version (V18)
of the addon. You should use the methods of the `fsspec.AbstractFileSystem` class
instead since they are more flexible and powerful. You can access the instance
of the `fsspec.AbstractFileSystem` class using the `file` property of a `file.storage`
record.

Known issues / Roadmap
======================

* Transactions: fsspec comes with a transactional mechanism that once started,
  gathers all the files created during the transaction, and if the transaction
  is committed, moves them to their final locations. It would be useful to
  bridge this with the transactional mechanism of odoo. This would allow to
  ensure that all the files created during a transaction are either all
  moved to their final locations, or all deleted if the transaction is rolled
  back. This mechanism is only valid for files created during the transaction
  by a call to the `open` method of the file system. It is not valid for others
  operations, such as `rm`, `mv_file`, ... .


======================================
server configuration environment files
======================================

This module provides a way to define an environment in the main Odoo
configuration file and to read some configurations from files depending
on the configured environment: you define the environment in the main
configuration file, and the values for the various possible environments
are stored in the ``server_environment_files`` companion module.

The ``server_environment_files`` module is optional, the values can be
set using an environment variable with a fallback on default values in
the database.

The configuration read from the files are visible under the
Configuration menu. If you are not in the 'dev' environment you will not
be able to see the values contained in the defined secret keys (by
default : '*passw*', '*key*', '*secret*' and '*token*').

**Table of contents**

.. contents::
   :local:

Installation
============

By itself, this module does little. See for instance the
``mail_environment`` addon which depends on this one to allow
configuring the incoming and outgoing mail servers depending on the
environment.

You can store your configuration values in a companion module called
``server_environment_files``. You can copy and customize the provided
``server_environment_files_sample`` module for this purpose.
Alternatively, you can provide them in environment variables
``SERVER_ENV_CONFIG`` and ``SERVER_ENV_CONFIG_SECRET``.

Configuration
=============

To configure this module, you need to edit the main configuration file
of your instance, and add a directive called ``running_env``. Commonly
used values are 'dev', 'test', 'production':

::

   [options]
   running_env=dev

Or set the ``RUNNING_ENV`` or ``ODOO_STAGE`` environment variable. If
both all are set config file will take the precedence on environment and
``RUNNING_ENV`` over ``ODOO_STAGE``.

``ODOO_STAGE`` is used for odoo.sh platform where we can't set
``RUNNING_ENV``, possible observed values are ``production``,
``staging`` and ``dev``

Values associated to keys containing 'passw' are only displayed in the
'dev' environment.

If you don't provide any value, test is used as a safe default.

You have several possibilities to set configuration values:

server_environment_files
------------------------

You can edit the settings you need in the ``server_environment_files``
addon. The ``server_environment_files_sample`` can be used as an
example:

-  values common to all / most environments can be stored in the
   ``default/`` directory using the .ini file syntax;
-  each environment you need to define is stored in its own directory
   and can override or extend default values;
-  you can override or extend values in the main configuration file of
   your instance;

Environment variable
--------------------

You can define configuration in the environment variable
``SERVER_ENV_CONFIG`` and/or ``SERVER_ENV_CONFIG_SECRET``. The 2
variables are handled the exact same way, this is only a convenience for
the deployment where you can isolate the secrets in a different,
encrypted, file. They are multi-line environment variables in the same
configparser format than the files. If you used options in
``server_environment_files``, the options set in the environment
variable override them.

The options in the environment variable are not dependent of
``running_env``, the content of the variable must be set accordingly to
the running environment.

Example of setup:

A public file, containing that will contain public variables:

::

   # These variables are not odoo standard variables,
   # they are there to represent what your file could look like
   export WORKERS='8'
   export MAX_CRON_THREADS='1'
   export LOG_LEVEL=info
   export LOG_HANDLER=":INFO"
   export DB_MAXCONN=5

   # server environment options
   export SERVER_ENV_CONFIG="
   [storage_backend.my_sftp]
   sftp_server=10.10.10.10
   sftp_login=foo
   sftp_port=22200
   directory_path=Odoo
   "

A second file which is encrypted and contains secrets:

::

   # This variable is not an odoo standard variable,
   # it is there to represent what your file could look like
   export DB_PASSWORD='xxxxxxxxx'
   # server environment options
   export SERVER_ENV_CONFIG_SECRET="
   [storage_backend.my_sftp]
   sftp_password=xxxxxxxxx
   "

**WARNING**

   my_sftp must match the name of the record. If you want something more
   reliable use server.env.techname.mixin and use tech_name field to
   reference records. See "USAGE".

Default values
--------------

When using the ``server.env.mixin`` mixin, for each env-computed field,
a companion field ``<field>_env_default`` is created. This field is not
environment-dependent. It's a fallback value used when no key is set in
configuration files / environment variable.

When the default field is used, the field is made editable on Odoo.

Note: empty environment keys always take precedence over default fields

Server environment integration
------------------------------

Read the documentation of the class
`models/server_env_mixin.py <models/server_env_mixin.py>`__.

Usage
=====

You can include a mixin in your model and configure the env-computed
fields by an override of ``_server_env_fields``.

::

   class StorageBackend(models.Model):
       _name = "storage.backend"
       _inherit = ["storage.backend", "server.env.mixin"]

       @property
       def _server_env_fields(self):
           return {"directory_path": {}}

Read the documentation of the class and methods in
`models/server_env_mixin.py <models/server_env_mixin.py>`__.

If you want to have a technical name to reference:

::

   class StorageBackend(models.Model):
       _name = "storage.backend"
       _inherit = ["storage.backend", "server.env.techname.mixin", "server.env.mixin"]

       [...]

Known issues / Roadmap
======================

-  it is not possible to set the environment from the command line. A
   configuration file must be used.
-  the module does not allow to set low level attributes such as
   database server, etc.
-  server.env.techname.mixin's tech_name field could leverage the new
   option for computable / writable fields and get rid of some onchange
   / read / write code.

 
======================================
Server Environment Ir Config Parameter
======================================

Configuration
=============

To configure this module, you need to add a section
``[ir.config_parameter]`` to you server_environment_files
configurations, where the keys are the same as would normally be set in
the Systems Parameter Odoo menu.

When first using a value, the system will read it from the configuration
file and override any value that would be present in the database, so
the configuration file has precedence.

When creating or modifying values that are in the configuration file,
the module replace changes, enforcing the configuration value.

For example you can use this module in combination with
web_environment_ribbon:

::

   [ir.config_parameter]
   ribbon.name=DEV

Usage
=====

Before using this module, you must be familiar with the
server_environment module.

Known issues / Roadmap
======================

When the user modifies System Parameters that are defined in the config
file, the changes are ignored. It would be nice to display which system
parameters come from the config file and possibly make their key and
value readonly in the user interface.

 