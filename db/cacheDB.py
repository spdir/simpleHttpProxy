# -*- coding: utf8 -*-
import os
from jdb2 import NoSql

__db_file = os.path.join(os.getcwd(), "db", "proxy.json")

__noDB_obj = NoSql(dump=True, nosqlFile=__db_file, dumpTime=10)

proxyDB = __noDB_obj.createDB("proxy_pool")

proxyDB.setValue("tmp_proxy", [])
proxyDB.setValue("proxy_pool", [])
