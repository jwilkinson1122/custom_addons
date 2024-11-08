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

  [nwpl_odoo_master.fileprod]
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
