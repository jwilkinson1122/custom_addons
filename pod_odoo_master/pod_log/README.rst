====================
Logging in database
====================

This module adds a logs handler writing to database.

Notice

    * Following code will create a log in db with a unique pid per logger:
        from odoo.pod_addons.pod_log.tools import PodDBLogger
        logger = PodDBLogger(self._cr.dbname, model'res.partner', self.id, self._uid)
        logger.info(your_message)

Features :

* Create logs when executing an action.
* Archive and delete old logs from database.
* Give users access right to see logs.

Configuration
=============

* Developer adds ``import logging`` to his python file.
* Developer must add following code to his action and specify 
the database, the model name, the res_id, and uid. Then give a message to log for information:

.. code-block:: python

  logger = PodDBLogger(self._cr.dbname, model'res.partner', self.id, self._uid)
  logger.info(your_message)

* Administrator must create a ``Scheduled Action`` to call the function ``archive_and_delete_old_logs``, 
configure archiving path and the number of days to archive and delete logs.

Usage
=====
To add Logs handler to an action :

    1. Import PodDBLogger to your python code and add code lines as shown in following example :
    2. Add ``pod_log`` to your module dependence:

    3. Now execute the action.:

    4. Go to ``Settings > Technical > Logging``> Logs menu to see logs.


Administrator can give access right to users, to see logs, by checking ``Logs / User``.

To create the scheduled action:
    1. Go to ``Settings > Technical > Automation > Scheduled Actions`` and fill fields as follow:


        ``(Make sure that the given folder has a write access!)``

    2. After running the action, the extracted logs file in csv format is as shown in next figure:





