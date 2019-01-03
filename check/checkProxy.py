# -*- coding: utf8 -*-
from gevent import monkey

monkey.patch_all()

import logging
import time
import gevent
import requests
from db import cacheDB

proxyDB = cacheDB.proxyDB

NowTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

proxy_pool = []

headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/70.0.3538.67 Safari/537.36'
}


def verify_proxy(proxy):
  """
  校验单个代理可用性
  :param str proxy: 代理地址
  :return: bool
  """

  try:
    response = requests.get('http://www.baidu.com', headers=headers,
                            proxies={"http": proxy, 'https': proxy}, timeout=6)
    if response.status_code == 200:
      return True
    else:
      raise requests.HTTPError
  except Exception:
    return False


def verify_proxy_pool():
  """
  校验http代理池的可用性
  :return: None
  """
  logging.info("[%s] 开始验证代理池可用性" %NowTime)

  def ver_proxy(proxy):
    if verify_proxy(proxy):
      proxy_pool.append(proxy)

  verify_proxy_pool = proxyDB.getValue("tmp_proxy")
  verify_proxy_pool.extend(proxyDB.getValue("proxy_pool"))
  try:
    gevent.joinall([gevent.spawn(ver_proxy, proxy) for proxy in set(verify_proxy_pool)])
  except:
    pass
  proxyDB.setValue("proxy_pool", list(set(proxy_pool)))
  logging.info("[%s] 验证代理池可用性结束" %NowTime)
