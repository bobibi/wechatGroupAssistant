# coding=utf-8
import requests, re, urllib, time, cStringIO, json
from PIL import Image
__author__ = 'yongbo'

class weixin:
    uuid = None
    wxuin = None
    wxsid = None
    deviceid = 'e225227494371042'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',

    def get_uuid(self):
        url = 'https://login.weixin.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN'
        r = requests.get(url)
        uuid_search = re.search('window.QRLogin.uuid = "([^"]+)"', r.text)
        self.uuid = uuid_search.group(1)
        #print 'uuid=[%s]'%self.uuid
        return self.uuid

    # UUID is valid? TODO: expiration
    def is_valid_uuid(self):
        return self.uuid is not None

    # popup display QR image
    def pop_qr(self):
        if not self.is_valid_uuid():
            raise 'uuid is invalid'
        url = 'https://login.weixin.qq.com/qrcode/'+self.uuid
        img = Image.open(cStringIO.StringIO(urllib.urlopen( url).read()))
        img.show()
        return url

    def login(self):
        url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?uuid='+self.uuid+'&tip=1'
        r = requests.get(url)
        url_search = re.search('window.redirect_uri="([^"]+)"', r.text)
        if url_search:
            url = url_search.group(1)
            r = requests.head(url)
            self.wxuin = r.cookies['wxuin']
            self.wxsid = r.cookies['wxsid']
            #print 'wxuin=[%s]\nwxsid=[%s]\n'%(self.wxuin, self.wxsid)
            self.cookie = r.cookies
            return True
        print r.text
        return False

    def is_login(self):
        return self.wxuin is not None and self.wxsid is not None

    def init_info(self):
        if not self.is_login():
            raise 'you have not logged in'
        payload = {
            'BaseRequest': {
                'Uin': self.wxuin,
                'Sid': self.wxsid,
                'Skey': '',
                'DeviceID': self.deviceid,
            }
        }
        url = 'https://web2.wechat.com/cgi-bin/mmwebwx-bin/webwxinit'
        r = requests.post(url, json = payload, cookies=self.cookie)
        rjson = json.loads(r.content.decode('utf-8', 'replace'))
        #print rjson
        self.user = rjson['User']
        self.skey = rjson['SKey']
        self.synckey = self.gen_synckey(rjson['SyncKey'])
        self.synckey_json = rjson['SyncKey']
        print 'Weixin init completed!\nUserName:%s\nNickName:%s\n'%(rjson['User']['UserName'], rjson['User']['NickName'])
        return rjson

    def gen_synckey(self, synckey):
        return '|'.join(['%d_%d'%(k,v) for L in synckey['List'] for v,k in [(L['Val'],L['Key'])]])

    def get_contact(self):
        url = 'https://web2.wechat.com/cgi-bin/mmwebwx-bin/webwxgetcontact'
        headers = {
            'ContentType': 'application/json; charset=UTF-8'
        }
        r = requests.post(url, json={'skey': self.skey}, cookies=self.cookie, headers=headers)
        data = r.content
        data = data.decode('utf-8', 'replace')
        dic = json.loads(data)
        #print r.json()
        #print '%d contacts found' % dic['MemberCount']
        #for c in dic['MemberList']:
        #    print '=> NN(%s)UN{%s}PY[%s]'%(c['NickName'],c['UserName'],c['PYQuanPin'])
        return dic

    def synccheck(self):
        url = 'https://webpush2.wechat.com/cgi-bin/mmwebwx-bin/synccheck'
        params = {
            'sid': self.wxsid,
            'uin': self.wxuin,
            'deviceid': self.deviceid,
            'synckey': self.synckey,
        }
        r = requests.get(url, params=params, cookies=self.cookie)
        #print r.text
        val_search = re.search('retcode:"([^"]+)"', r.text)
        retcode = val_search.group(1)
        val_search = re.search('selector:"([^"]+)"', r.text)
        selector = val_search.group(1)
        if selector is not '2':
            print 'You have new message!'
        return retcode, selector

    def fetch_message(self):
        url = 'https://web2.wechat.com/cgi-bin/mmwebwx-bin/webwxsync?sid=%s&skey=%s'%(self.wxsid, self.skey)
        data = {
            "BaseRequest" : {
                "Uin": self.wxuin,
                "Sid": self.wxsid,
            },
            "SyncKey" : self.synckey_json,
        }
        headers = {
            'ContentType': 'application/json; charset=UTF-8'
        }
        r = requests.post(url, json=data, cookies=self.cookie)
        data = r.content
        data = data.decode('utf-8', 'replace')
        dic = json.loads(data)

        self.synckey = self.gen_synckey(dic['SyncKey'])
        self.synckey_json = dic['SyncKey']
        #print r.json()
        print '%d messages fetched!'%dic['AddMsgCount']
        for m in dic['AddMsgList']:
            print 'From: %s\nMessage: %s\n'%(m['FromUserName'], m['Content'])
        return dic

    def gen_local_id(self):
        return int(time.time()*1000)

    def send_message(self, to, msg):
        url = 'https://web2.wechat.com/cgi-bin/mmwebwx-bin/webwxsendmsg'
        data = {
            u"BaseRequest":{
                u"DeviceID" : self.deviceid,
                u"Sid" : self.wxsid,
                u"Skey" : self.skey,
                u"Uin" : self.wxuin
            },
            u"Msg" : {
                u"ClientMsgId" : self.gen_local_id(),
                u"Content" : msg,
                u"FromUserName" : self.user[u'UserName'],
                u"LocalID" : self.gen_local_id(),
                u"ToUserName" : to,
                u"Type" : 1
            },
        }
        #print repr(data)
        headers = {
            'ContentType': 'application/json; charset=UTF-8'
        }
        r = requests.post(url, data=json.dumps(data, ensure_ascii=False).encode('utf-8'), cookies=self.cookie, headers=headers)
        #print r.text
        return r.text

    def get_chatrooms_info(self, usernames):
        url = 'https://web2.wechat.com/cgi-bin/mmwebwx-bin/webwxbatchgetcontact?type=ex'
        if not isinstance(usernames, list):
            usernames = [usernames]
        data = {
            "BaseRequest":{
                "Uin": self.wxuin,
                "Sid": self.wxsid,
                "Skey": self.skey,
                "DeviceID": self.deviceid
            },
            "Count": len(usernames),
            "List":[{"UserName": un, "EncryChatRoomId":""} for un in usernames]
        }
        r = requests.post(url, json = data, cookies=self.cookie)
        rjson = json.loads(r.content.decode('utf-8', 'replace'))
        return rjson
