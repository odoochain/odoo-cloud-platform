Base class for attachments on external object store
===================================================

This is a base addon that regroup common code used by addons targeting specific object store

这是一个基本插件，用于重组针对特定对象存储的插件使用的通用代码

Configuration
-------------

Object storage may be slow, and for this reason, we want to store
some files in the database whatever.

Small images (128, 256) are used in Odoo in list / kanban views. We
want them to be fast to read.
They are generally < 50KB (default configuration) so they don't take
that much space in database, but they'll be read much faster than from
the object storage.

对象存储可能很慢，因此，我们希望在数据库中存储一些文件。Odoo在列表看板视图中使用小图像（128256）。

我们希望他们能快速阅读。它们通常小于50KB（默认配置），因此在数据库中不会占用太多空间，但读取速度会比从对象存储中快得多。

The assets (application/javascript, text/css) are stored in database
as well whatever their size is:

* a database doesn't have thousands of them
* of course better for performance
* better portability of a database: when replicating a production
  instance for dev, the assets are included

This storage configuration can be modified in the system parameter
``ir_attachment.storage.force.database``, as a JSON value, for instance::

    {"image/": 51200, "application/javascript": 0, "text/css": 0}

Where the key is the beginning of the mimetype to configure and the
value is the limit in size below which attachments are kept in DB.
0 means no limit.

Default configuration means:

* images mimetypes (image/png, image/jpeg, ...) below 50KB are
  stored in database
* application/javascript are stored in database whatever their size
* text/css are stored in database whatever their size

Disable attachment storage I/O
------------------------------

Define a environment variable `DISABLE_ATTACHMENT_STORAGE` set to `1`
This will prevent any kind of exceptions and read/write on storage attachments.
