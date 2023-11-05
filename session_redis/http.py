# Copyright 2016-2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging
import os
import random
import sys

from odoo import http, tools
from odoo.addons.muk_utils.tools.patch import monkey_patch
from odoo.tools.func import lazy_property

from .session import RedisSessionStore
from .strtobool import strtobool

_logger = logging.getLogger(__name__)
# Import C library Pickle which is used to convert 'data' to stream of bytes
# if sys.version_info > (3,):
#     import _pickle as cPickle
#
#     unicode = str
# else:
#     import cPickle
try:
    import redis
    from redis.sentinel import Sentinel
except ImportError:
    redis = False  # none or false
    _logger.debug("Cannot 'import redis'.")


def is_true(strval):
    return bool(strtobool(strval or "0".lower()))


sentinel_host = tools.config.get("ODOO_SESSION_REDIS_SENTINEL_HOST",False)
sentinel_master_name = tools.config.get("ODOO_SESSION_REDIS_SENTINEL_MASTER_NAME")
if sentinel_host and not sentinel_master_name:
    raise Exception(
        "odoo_session_redis_sentinel_master_name must be defined "
        "when using session_redis"
    )
sentinel_port = int(tools.config.get("ODOO_SESSION_REDIS_SENTINEL_PORT", 26379))
host = tools.config.get("ODOO_SESSION_REDIS_HOST", "localhost")
port = int(tools.config.get("ODOO_SESSION_REDIS_PORT", 6379))
db = int(tools.config.get("ODOO_SESSION_REDIS_DBINDEX", 0)),
prefix = tools.config.get("ODOO_SESSION_REDIS_PREFIX", "")
url = tools.config.get("ODOO_SESSION_REDIS_URL", False)
password = tools.config.get("ODOO_SESSION_REDIS_PASSWORD", None)
expiration = tools.config.get("ODOO_SESSION_REDIS_EXPIRATION")
anon_expiration = tools.config.get("ODOO_SESSION_REDIS_EXPIRATION_ANONYMOUS")


@lazy_property
def session_store(self):
    if sentinel_host:
        sentinel = Sentinel([(sentinel_host, sentinel_port)], password=password)
        redis_client = sentinel.master_for(sentinel_master_name)
    elif url:
        redis_client = redis.from_url(url)
    else:
        redis_client = redis.Redis(host=host, port=port, password=password)
    return RedisSessionStore(
        myredis=redis_client,
        prefix=prefix,
        expiration=expiration,
        anon_expiration=anon_expiration,
        session_class=http.Session,
    )


@monkey_patch(http)
def session_gc(session_store):
    if tools.config.get("session_store_database"):
        if random.random() < 0.001:
            session_store.clean()
    elif tools.config.get("ODOO_SESSION_REDIS"):
        pass
    else:
        session_gc.super(session_store)


def purge_fs_sessions(path):
    for fname in os.listdir(path):
        path = os.path.join(path, fname)
        try:
            os.unlink(path)
        except OSError:
            _logger.warning("OS Error during purge of redis sessions.")


if is_true(tools.config.get("ODOO_SESSION_REDIS")):
    if sentinel_host:
        _logger.debug(
            "HTTP sessions stored in Redis with prefix '%s'. "
            "Using Sentinel on %s:%s",
            prefix or "",
            sentinel_host,
            sentinel_port,
        )
    else:
        _logger.debug(
            "HTTP sessions stored in Redis with prefix '%s' on " "%s:%s",
            prefix or "",
            host,
            port,
        )
    http.Application.session_store = session_store
    # clean the existing sessions on the file system
    purge_fs_sessions(tools.config.session_dir)
