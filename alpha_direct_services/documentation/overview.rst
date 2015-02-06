Overview:
=========

The short-short version:
------------------------

This module is the glue between IP's Odoo instance and the ADS order management system. The main workflow can be
summarised thus:

1. Orders originate in Odoo, via the webshop frontend or CRM backend.
2. When an order has some items available, the order is sent to ADS for further processing.
3. ADS sends back information on the order followup to Odoo.
4. Odoo updates its internal state to match the actions performed by ADS.

Key features are:

* Periodic stock synchronisation with ADS
* Sending of partially available orders to ADS
* Polling the ADS server to check for follow-up information on active orders.

All communication with ADS happens in the form of XML files describing the actions, which are exchanged via FTP. The ADS
FTP server will only allow logins from specific IPs. The production site will work in the PROD folder, all other
instances in TEST. The currently allowed IPs for login are the production instance, the migration server
(migration-test.openerp.com) and the external IP of the Odoo Grand-Rosière office, to facilitate testing.

Within the TEST and PROD folders, there are subfolders named VersADS and VersINCONTINENCEPROTECTION, which are used for
Odoo->ADS and ADS->Odoo communication respectively.


Configuration:
--------------

The FTP server to link against can be configured in Odoo through the system parameters. The parameters are as follows:

**ads_host**::

  The FTP host. Can be an IP or a hostname.
  Prod: ftp.alpha-ds.com

**ads_port**::

  The FTP port.
  Prod: 21. This is also the standard FTP port.

**ads_user**::

  The username for the FTP login.
  Prod: witheld for security reasons; consult the production server.

**ads_password**::

  The password for the FTP login.
  Prod: witheld for security reasons; consult the production server.

**ads_timeout**::

  The timeout for the ADS FTP server, in minuntes.
  Prod: 10.
  Note: the FTP server times out after a couple of minutes, so long operations   which keep the FTP session open are to
  be avoided!

**ads_mode**::

  The mode (ADS FTP folder) under which to operate. Can be TEST or PROD, case insensitive.
  Prod: prod
  Note: extra security is built into the module to ensure we never work on PROD if our database is not the production
  database. The check is naieve in that it only checks on database name, so it is entirely possible to accidentally mess
  with production on a local instance.

**Warning**: DO NOT use the name stored in database_name.txt on the FTP server in the folder
PROD/VersINCONTINENCEPROTECTION/security/ (currently 'incprotect') on non-production machines!!!

**ads_passive**::

  Whether to use passive mode FTP.
  Prod: True

Automation:
-----------

Interaction with ADS happens through cron jobs in Odoo. Currently the following jobs are defined:

**Upload Sales/Purchase Orders to ADS**::

  This job runs every 5 minutes and will upload all relevant Sales/Purchase orders (stock.picking) to ADS.
  Only orders in states "assigned" or "partially_available" are being sent, and only if they have not been sent before.
  Note: this cron job should actually be replaced by an automated upload in the write() method of stock.picking, when
  the state changes to something relevant. The cron job is a temporary workaround for difficulties in migrating the
  original intent to 8.0 during the early migration stage.

**IP Auto Ship Processing**::

  This job runs daily, and processes all auto ships from the ip_web_addons module.

**Poll Alpha Direct Service Server**::

  This job runs every 10 mionutes on PROD. It checks the ADS FTP server for new files, and takes appropriate action on
  them.

  The actions performed by this job are determined by the filename prefix:

MVTS::

  Receipt of purchase order, delivery of Sales Order.

CRET::

  Returns.

FOUR::

  Extract purchase order's picking.

STOC::

  Stock update. ADS only sends one update per day, but we check regardless.

ARTI::

  Extract product.

CMDE/CREX::

  Import/export of Sales Order's Delivery Order.

