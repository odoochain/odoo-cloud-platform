# Copyright 2016-2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging
import os
import sys

from odoo import http
from odoo.tools import config
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
    redis = None  # noqa
    _logger.debug("Cannot 'import redis'.")


def is_true(strval):
    return bool(strtobool(strval or "0".lower()))


sentinel_host = config.get("ODOO_SESSION_REDIS_SENTINEL_HOST")
sentinel_master_name = config.get("ODOO_SESSION_REDIS_SENTINEL_MASTER_NAME")
if sentinel_host and not sentinel_master_name:
    raise Exception(
        "odoo_session_redis_sentinel_master_name must be defined "
        "when using session_redis"
    )
sentinel_port = int(config.get("ODOO_SESSION_REDIS_SENTINEL_PORT", 26379))
host = config.get("ODOO_SESSION_REDIS_HOST", "localhost")
port = int(config.get("ODOO_SESSION_REDIS_PORT", 6379))
prefix = config.get("ODOO_SESSION_REDIS_PREFIX")
url = config.get("ODOO_SESSION_REDIS_URL")
password = config.get("ODOO_SESSION_REDIS_PASSWORD", None)
expiration = config.get("ODOO_SESSION_REDIS_EXPIRATION")
anon_expiration = config.get("ODOO_SESSION_REDIS_EXPIRATION_ANONYMOUS")


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
        redis=redis_client,
        prefix=prefix,
        expiration=expiration,
        anon_expiration=anon_expiration,
        session_class=http.Session,
    )


def purge_fs_sessions(path):
    for fname in os.listdir(path):
        path = os.path.join(path, fname)
        try:
            os.unlink(path)
        except OSError:
            _logger.warning("OS Error during purge of redis sessions.")


if is_true(config.get("odoo_session_redis")):
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
    purge_fs_sessions(config.session_dir)
