import json
from selenium import webdriver
import time
from pyvirtualdisplay import Display
import os

class MMWorker:
    def __init__(self):
        self.driver = None
        self.configFile = "mm.json"

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
        self.Login()
        self.Prepare()
        self.getAuth()
        return True

    def getAuth(self):
        url = "https://maimai.cn/contact/visit_history?jsononly=1&limit=9"
        script = '''
        function test(){
        var ret; 
        $.ajaxSetup({async:false}); 
        $.getJSON("''' + url + ''''", {

            }, function (data) {
                    ret=JSON.stringify(data);
            });
        return ret;}
        return ( test());
        '''
        ret = self.driver.execute_script(script=script)
        self.auth = json.loads(ret)
        self.cookies = self.auth["auth_info"]
        self.cookies["uid"]=self.cookies["uid"].replace("\"","").strip()
        self.cookies["token"]=self.cookies["token"].replace("\"","").strip()

    def loadJquery(self):
        script = '''
        var headID =document.getElementsByTagName("head")[0];
        var newScript = document.createElement('script');
        newScript.type = 'text/javascript';
        newScript.src ='https://apps.bdimg.com/libs/jquery/2.1.4/jquery.min.js';
        headID.appendChild(newScript);
        '''
        self.driver.execute_script(script=script)
        time.sleep(2)

    def getUsers(self, page):
        baseUrl = "https://maimai.cn/sdk/web/feed_list?u={u}&channel=www&version=4.0.0&_csrf={_csrf}&access_token={access_token}&uid={uid}&token={token}&page={page}&hash=feed_explore&jsononly=1"
        url = baseUrl.format(page=page, uid=self.cookies["uid"],u=self.cookies["u"], token=self.cookies["token"],_csrf=self.cookies["_csrf"],access_token=self.cookies["access_token"])
        script = '''
        function test(){
        var ret; 
        $.ajaxSetup({async:false}); 
        $.getJSON("''' + url + ''''", {
             
            }, function (data) {
                    ret=JSON.stringify(data);
            });
        return ret;}
        return ( test());
        '''
        return self.driver.execute_script(script=script)

    def Login(self):
        self.driver.get("https://acc.maimai.cn/login")
        self.driver.implicitly_wait(5)
        self.driver.find_element_by_class_name("loginPhoneInput").send_keys(self.getConfig("mobile"))
        self.driver.find_element_by_id("login_pw").send_keys(self.getConfig("pwd"))
        self.driver.find_element_by_class_name("loginBtn").click()
        self.driver.implicitly_wait(5)
        if u"登录" in self.driver.page_source:
            input("click when logined")
            time.sleep(2)
            return True
        else:
            return True

    def Prepare(self):
        self.driver.get("https://maimai.cn/web/feed_explore")
        self.driver.implicitly_wait(10)
        self.loadJquery()

    def popUsers(self):
        nextPage = self.getConfig("lastPage") + 1
        data = json.loads(self.getUsers(nextPage))
        if data.get("count", None):
            self.setConfig("lastPage", nextPage)
            return data['feeds']
        else:
            print("resp:{}".format(data))
            return []

    def comment(self, feed):
        ret = self.getHotComment(feed)
        data = json.loads(ret)
        if len(data["comments"]["hot_comments"]) < 1:
            resp = u"支持下"
        else:
            resp = data["comments"]["hot_comments"][0]["t"]
        rp = self.postComment(feed, resp)
        print("url:https://maimai.cn/web/feed_detail?fid={},post:{},ret:{}".format(feed["id"], resp, rp))

    def getHotComment(self, feed):
        baseUrl = "https://maimai.cn/sdk/web/feed/getcmts?fid={fid}&page=1&count=20&u=-1&channel=&version=0.0.0&_csrf={_csrf}&access_token={access_token}&uid=&token="
        url = baseUrl.format(fid=feed["id"],_csrf=self.cookies["_csrf"],access_token=self.cookies["access_token"])
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

    def postComment(self, feed, resp):
        baseUrl = 'https://open.taou.com/maimai/feed/v3/addcmt?fr=&u={u}&channel=www&version=4.0.0&_csrf={_csrf}&access_token={access_token}&uid="{uid}"&token="{token}"'
        url = baseUrl.format(u=self.cookies["u"],uid=self.cookies["uid"], token=self.cookies["token"],_csrf=self.cookies["_csrf"],access_token=self.cookies["access_token"])
        data = json.dumps({
            "fid": "{}".format(feed["id"]),
            "u2": "{}".format(self.cookies["u"]),
            "text": resp,
            "at_user_info": {},
            "reply_to": 0
        })
        script = '''
        function test(){
        var ret="nok"; $.ajax({
        contentType: "application/x-www-form-urlencoded",
        cache: false, 
        async: false, 
        type: 'POST',
        data:''' + data + ''',
        url: \'''' + url + '''\',
        success: function (data, status) {
            ret= "ok";
        }
        }); return ret}
        return ( test());
        '''
        return self.driver.execute_script(script=script)


def start():
    w = MMWorker()
    if w.run():
        while True:
            for u in w.popUsers():
                w.comment(u)
                time.sleep(2)
            time.sleep(10)


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
