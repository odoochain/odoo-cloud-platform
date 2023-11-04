Sessions in Redis
=================

This addon allows to store the web sessions in Redis.

Configuration
-------------

The storage of sessions in Redis is activated using environment variables.

* ``ODOO_SESSION_REDIS`` has to be ``1`` or ``true``
* ``ODOO_SESSION_REDIS_HOST`` is the redis hostname (default is ``localhost``)
* ``ODOO_SESSION_REDIS_PORT`` is the redis port (default is ``6379``)
* ``ODOO_SESSION_REDIS_PASSWORD`` is the password for the AUTH command
  (optional)
* ``ODOO_SESSION_REDIS_URL`` is an alternative way to define the Redis server
  address. It's the preferred way when you're using the ``rediss://`` protocol.
* ``ODOO_SESSION_REDIS_PREFIX`` is the prefix for the session keys (optional)
* ``ODOO_SESSION_REDIS_EXPIRATION`` is the time in seconds before expiration of
  the sessions (default is 7 days)
* ``ODOO_SESSION_REDIS_EXPIRATION_ANONYMOUS`` is the time in seconds before expiration of
  the anonymous sessions (default is 3 hours)


The keys are set to ``session:<session id>``.
When a prefix is defined, the keys are ``session:<prefix>:<session id>``

This addon must be added in the server wide addons with (``--load`` option):

``--load=base,web,session_redis``

Limitations
-----------

* The server has to be restarted in order for the sessions to be stored in
  Redis.
* All the users will have to login again as their previous session will be
  dropped.
* The addon monkey-patch ``odoo.http.Root.session_store`` with a custom
  method when the Redis mode is active, so incompatibilities with other addons
  is possible if they do the same.

Usage
-------------------------

If windows suggest install memurai !

To use Redis, install this module and please add "ODOO_SESSION_REDIS = True" option and add bean_redis_session as a wide module "server_wide_modules = base,web,bean_redis_session" in configuration file.

Example setting in configuration file


[options]

odoo_session_redis = true
odoo_session_redis_host      = localhost      # redis ip. default: locahost
odoo_session_redis_port      = 6379           # redis port, default: 6379
odoo_session_redis_dbindex   = 1              # redis database index, default: 1
#odoo_session_redis_password     =                # redis password, default: none
server_wide_modules = base,web,session_redis
odoo_session_redis_prefix = t000
#odoo_session_redis_url =
#odoo_session_redis_expiration =
#odoo_session_redis_expiration_anonymous =
#odoo_session_redis_sentinel_host =
#odoo_session_redis_sentinel_master_name =


TODO
-------------------------
dev.md 防暴力
