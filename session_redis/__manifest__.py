# Copyright 2016-2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


{
    "name": "Sessions in Redis",
    "summary": "Store web sessions in Redis",
    "version": "16.0.1.0.2",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": ["base"],
    "external_dependencies": {
        "python": ["redis"],
    },
    "website": "https://github.com/camptocamp/odoo-cloud-platform",
    "data": [],
    "installable": True,
    "excludes": ["beanus_redis_session",
                 "muk_session_store",
                 ],
    "post_load": "_patch_system",
}
