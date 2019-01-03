# -*- coding: utf8 -*-
import random
import time
import logging
import tornado.ioloop
import tornado.web
from threading import Thread
from tornado.options import define, options
from tornado.httpserver import HTTPServer
from spider import xici
from check import checkProxy

define("port", default=8080, type=8080, help="server port")


class ProxyApi(tornado.web.RequestHandler):
  def get(self):
    return_dict = {}
    totle = self.get_argument("totle", 0)
    try:
      totle = int(totle)
    except:
      totle = 0
    from db import cacheDB
    proxy_db = cacheDB.proxyDB
    proxy_pool = proxy_db.getValue("proxy_pool")
    if len(proxy_pool) <= totle:
      totle_proxy_list = proxy_pool
    else:
      totle_proxy_list = random.sample(proxy_pool, totle)
    for i, k in enumerate(totle_proxy_list, 1):
      return_dict[i] = k
    self.write(return_dict)

  def post(self):
    self.get()


def proxy_threading():
  """
  爬虫任务进程
  :return:
  """
  # 使用最暴利的方法循环的去执行获取和校验爬虫代理的任务
  while True:
    xici.xici_spider(3)
    checkProxy.verify_proxy_pool()
    # 睡眠15分钟再次执行任务
    time.sleep(60 * 10)


proxyThread = proxy_threading


def run_server():
  """
  服务运行入口
  :return:
  """
  app = tornado.web.Application(
    [(r"/api", ProxyApi)]
  )
  options.parse_command_line()
  http_server = HTTPServer(app)
  http_server.bind(options.port)
  http_server.start()
  # 另外启动一个线程执行爬虫任务
  proxy_thread = Thread(target=proxyThread)
  proxy_thread.start()
  logging.info("Server is running......")
  tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
  run_server()
