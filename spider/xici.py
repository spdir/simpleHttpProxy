# -*- coding: utf8 -*-
from gevent import monkey

monkey.patch_all()

import logging
import time
import random
import requests
import gevent
from lxml import etree
from db import cacheDB

proxyDB = cacheDB.proxyDB
SpiderName = "xici"
NowTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

keys = [
  'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19',
  'Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
  'Mozilla/5.0 (Li'
  'nux; U; Android 2.2; en-gb; GT-P1000 Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
  'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0',
  'Mozilla/5.0 (Android; Mobile; rv:14.0) Gecko/14.0 Firefox/14.0',
  'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36',
  'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19',
  'Mozilla/5.0 (iPad; CPU OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3',
  'Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/3A101a Safari/419.3'
]

# 伪装浏览器
headers = {
  'User-Agent': keys[random.randint(0, len(keys) - 1)]
}


def get_html(url):
  """
  获取html页面
  :param str url: 获取页面的url地址
  :return:
  """
  try:
    # 使用get方法请求
    response = requests.get(url, headers=headers)
    # 判断请求状态，如果不为200就触发异常
    if response.status_code != 200:
      raise requests.HTTPError
    response.encoding = response.apparent_encoding
    return response.text
  except Exception as e:
    logging.error(e)
  return None


def html_proxy(html_body):
  """
  解析页面获取代理
  :param str html_body: html页面字符串
  :return: None
  """
  if not html_body:
    return
  proxy_list = []
  selector = etree.HTML(html_body)
  for each in selector.xpath("//tr[@class='odd']"):
    ip = each.xpath("./td[2]/text()")[0]
    port = each.xpath("./td[3]/text()")[0]
    proxy = ip + ":" + port
    proxy_list.append(proxy)
  tmp_proxy_list = proxyDB.getValue("tmp_proxy")
  tmp_proxy_list.extend(proxy_list)
  proxyDB.setValue("tmp_proxy", list(set(tmp_proxy_list)))


def get_proxy(url):
  """
  获取代理
  :param str url: 获取页面的url地址
  :return: None
  """
  html_body = get_html(url)
  html_proxy(html_body)


def xici_spider(page_depth):
  """
  获取全部代理地址
  :param int page_depth: 获取页码深度
  :return None: None
  """
  logging.info('[%s] 开始获取%s代理结束' % (NowTime, SpiderName))

  url_list = ['http://www.xicidaili.com/nn/' + str(i) for i in range(1, int(page_depth) + 1) if page_depth]
  try:
    gevent.joinall([gevent.spawn(get_proxy, url) for url in url_list])
  except Exception as e:
    logging.error(e)
  logging.info('[%s] 获取%s代理结束' % (NowTime, SpiderName))
