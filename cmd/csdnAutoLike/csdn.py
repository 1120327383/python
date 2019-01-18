import json
import random
import threading
import requests
import bs4
from selenium import webdriver
import time
from pyvirtualdisplay import Display
import os
from elasticsearch import Elasticsearch
import logging

logging.basicConfig(filename='csdn.log', level=logging.WARNING,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')


class Worker:
    def __init__(self):
        self.driver = None
        self.configFile = "csdn.json"
        self.actions = {}

    def getConfig(self, k):
        with open(self.configFile, 'r') as f:
            ct = f.read()
            data = json.loads(ct)
            return data.get(k, None)

    def setConfig(self, k, v):
        with open(self.configFile, "r") as reader:
            ct = reader.read()
            data = json.loads(ct)
            data[k] = v
        with open(self.configFile, 'w+') as writer:
            writer.write(json.dumps(data))

    def run(self):
        self.driver = webdriver.Firefox()
        return self.Login()

    def Login(self):
        self.driver.get("https://passport.csdn.net/login")
        self.driver.implicitly_wait(5)
        input("click when logined")
        return True

    def getUserFromES(self, index):
        es = Elasticsearch()
        result = es.search(
            index='csdn',
            doc_type='user',
            body={
                "from": index,
                "size": 1,
                'query': {
                    "match_all": {}
                }
            }
        )
        return (result["hits"]["hits"][0]['_source']["username"])

    def popUsers(self):
        nextPage = self.getConfig("lastPage") + 1
        logging.warning("start index:{}".format(nextPage))
        user = self.getUserFromES(nextPage)
        logging.warning(("get user:{} from ES".format(user)))
        self.setConfig("lastPage", nextPage)
        return user

    def like(self, u):
        ok,url = self.getArticleUrl(u)
        if ok:
            logging.warning("user:{},firstArticle:{}".format(u, url))
            self.driver.get(url)
            rp=self.driver.page_source
            logging.warning("url:{},ret:{}".format(url, rp))

        else:
            logging.warning("skip user:{}".format(u))
    def _get(self, url):
        script = '''
                function test(){
                var ret; 
                $.ajaxSetup({async:false}); 
                $.getJSON("''' + url + '''", {

                    }, function (data) {
                            ret=JSON.stringify(data);
                    });
                return ret;}
                return ( test());
                '''
        return self.driver.execute_script(script=script)

    def getArticleUrl(self, u):
        try:
            s = requests.Session()
            home = "https://me.csdn.net/{}".format(u)
            ret = s.get(home)
            logging.warning("start User:{}".format(home))
            soup = bs4.BeautifulSoup(ret.content.decode("utf-8"), "html.parser")
            a = soup.select_one(".tab_page_list > dt > h3 > a ")
            logging.warning("article URL:{}".format(a.attrs["href"]))
            id = a.attrs["href"].split("/")[-1]
            url = "https://blog.csdn.net/{}/phoenix/article/digg?ArticleId={}".format(u, id)
            return True,url
        except:
            logging.warning("can't get article from {}".format(home))
            return False,""


def start():
    w = Worker()
    if w.run():
        while True:
            u = w.popUsers()
            w.like(u)
            time.sleep(1)


def main():
    ENV_HOME = os.environ.get("HOME", "")
    if ENV_HOME == "/root":
        display = Display(visible=0, size=(2000, 2000))
        display.start()
    start()

    if ENV_HOME == "/root":
        display.stop()


if __name__ == '__main__':
    main()
