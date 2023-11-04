# Odoo14 防暴力破解登录密码 https://www.cnblogs.com/watermeloncode/tag/odoo%2014/
# 主要工具：redis
# 实现思路：限制每个用户24小时内登录失败次数。连续超过5次失败后，需要等待一定时间后才能再次尝试登录
# 配置：在你的配置文件中增加redis配置信息(如，我的是myodoo.cfg：./odoo-bin -c myodoo.cfg)
[REDIS]
ODOO_SESSION_REDIS=1
ODOO_SESSION_REDIS_HOST=192.168.31.20
ODOO_SESSION_REDIS_PORT=6379

# 代码
```
# -*- coding: utf-8 -*-
from odoo import models
import contextlib
from odoo.http import request
import logging
from odoo.exceptions import AccessDenied
import datetime
from odoo.tools import collections
from odoo import _
from configparser import ConfigParser
from odoo.tools import config as odoocfg
from odoo.tools.func import lazy_property

_logger = logging.getLogger(__name__)

try:
    import redis
    from redis.sentinel import Sentinel
except ImportError:
    redis = None  # noqa
    _logger.debug("Cannot 'import redis'.")

import threading

class SingletonRedis(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        sentinel_host = self.get_redis_config('ODOO_SESSION_REDIS_SENTINEL_HOST')
        sentinel_port = int(self.get_redis_config('ODOO_SESSION_REDIS_SENTINEL_PORT', 26379))
        password = self.get_redis_config('ODOO_SESSION_REDIS_PASSWORD')
        sentinel_master_name = self.get_redis_config('ODOO_SESSION_REDIS_SENTINEL_MASTER_NAME')
        url = self.get_redis_config('ODOO_SESSION_REDIS_URL')
        host = self.get_redis_config('ODOO_SESSION_REDIS_HOST', 'localhost')
        port = int(self.get_redis_config('ODOO_SESSION_REDIS_PORT', 6379))
        if sentinel_host:
            sentinel = Sentinel([(sentinel_host, sentinel_port)],
                                password=password)
            self.rd = sentinel.master_for(sentinel_master_name)
        elif url:
            self.rd = redis.from_url(url)
        else:
            self.rd = redis.Redis(host=host, port=port, password=password, db=1)

    def get_redis_config(self, pcname, defv=None):
        # print("============================:%s:%s" % (pcname, str(odoocfg.rcfile)))
        config_cfg = odoocfg.rcfile
        conf = ConfigParser()
        conf.read(config_cfg)
        if conf.has_option('REDIS', pcname):
            return conf.get('REDIS', pcname)
        else:
            if defv:
                return defv
            else:
                return None

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(SingletonRedis, "_instance"):
            SingletonRedis._instance = SingletonRedis(*args, **kwargs)
        return SingletonRedis._instance
        # with SingletonRedis._instance_lock:   不用考虑多线程问题，redis会自己解决。所以单例模式到这里就可以了
        #     if not hasattr(SingletonRedis, "_instance"):
        #         SingletonRedis._instance = SingletonRedis(*args, **kwargs)
        # return SingletonRedis._instance


class LoginLimit(models.Model):
    _inherit = 'res.users'

    def _bys_login_success(self, uname):
        rd = SingletonRedis()
        rd.rd.delete(uname)
        rd.rd.delete('bys666888_'+uname)

    def _bys_on_login_cooldown(self, uname):
        # 一天刷新一次，
        # 一天有10次错误的机会，
        # 前5次没有限制，
        # 后5次每次必须隔5分钟后尝试。
        # 10次机会耗尽,只能等24小时后再次尝试
        days = 1
        max_err = 10
        min_err = 5
        interval_sec = 5 * 60

        # 查看redis中有没有数据
        rd = SingletonRedis()
        rd = rd.rd

        # 有的话就拿出数据，并对请求次数判断是否过期
        failures = rd.get(uname)
        print(uname, failures)
        if failures:
            failures = int(failures) + 1
            if failures > max_err:
                raise AccessDenied(_("please wait %s hours before trying again.") % (str(days*24)))
            if failures >= min_err:
                a = rd.ttl('bys666888_'+uname)
                if a > 0:
                    raise AccessDenied(_("please wait %s seconds before trying again.") % (a))
                    # return True
                else:
                    rd.set(name='bys666888_'+uname,value=1,ex=interval_sec)
            rd.set(name=uname,value=failures,ex=86400*days)
        else:
            rd.set(name=uname,value=1,ex=86400*days)


    @contextlib.contextmanager
    def _assert_can_auth(self):
        """ Checks that the current environment even allows the current auth
        request to happen.

        The baseline implementation is a simple linear login cooldown: after
        a number of failures trying to log-in, the user (by login) is put on
        cooldown. During the cooldown period, login *attempts* are ignored
        and logged.

        .. warning::

            The login counter is not shared between workers and not
            specifically thread-safe, the feature exists mostly for
            rate-limiting on large number of login attempts (brute-forcing
            passwords) so that should not be much of an issue.

            For a more complex strategy (e.g. database or distribute storage)
            override this method. To simply change the cooldown criteria
            (configuration, ...) override _on_login_cooldown instead.

        .. note::

            This is a *context manager* so it can be called around the login
            procedure without having to call it itself.
        """
        # needs request for remote address
        if not request:
            yield
            return

        user_name = request.httprequest.form['login']
        if self._bys_on_login_cooldown(user_name):
            raise AccessDenied(_("Too many login failures,1 \r\nplease wait a bit before trying again."))
        try:
            yield
        except AccessDenied:
            # self._bys_login_failures(user_name)
            raise
        else:
            self._bys_login_success(user_name)
```
