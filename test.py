# coding=utf-8
import requests, weixin, wx_entities
import re
import time
from PIL import Image
import urllib, cStringIO

wx = weixin.weixin()
a=wx.get_uuid()
a=wx.pop_qr()

while not wx.is_login():
    wx.login()

a=wx.init_info()
my_info = wx_entities.load_contact(a['User'])
wx_entities.db_upsert_contact(my_info)

a=wx.get_contact()

x = wx_entities.load_contact_list(a)
for i in x:
    wx_entities.db_upsert_contact(i)

n = 100
while n>0:
    n -= 1
    wx.synccheck()
    a=wx.fetch_message()
    if int(a['AddMsgCount'])==0:
        continue
    x = wx_entities.load_message_list(a)
    for i in x:
        wx_entities.db_insert_message(i)

# n = 30
# while n>0:
#     n -= 1
#     a=wx.synccheck()
#     a=wx.fetch_message()
#     if int(a['AddMsgCount'])==0:
#         continue
#
#     print a['AddMsgList']

#a=wx.send_message('@700e257f3932f766c4918aa70c04c786cbf710ca1f5ccd683267c06844d60023', u'你也好！')

'''
# Settings:
url_get_uuid = 'https://login.wechat.com/jslogin'
url_get_qr = 'https://login.weixin.qq.com/qrcode/'
#url_check_scan = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login'
url_check_scan = 'https://login.wechat.com/cgi-bin/mmwebwx-bin/login'
http_header = {
    'Connection': 'keep-alive',
    'Host': 'login.wechat.com',
    'Referer': 'https://web.wechat.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
}

# Get uuid
par_get_uuid = {'appid': 'wx782c26e4c19acffb',
                #'redirect_uri': 'https%3A%2F%2Fweb.wechat.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage',
                'fun': 'new',
                'lang': 'zh_CN',
                '_': int(time.time()*1000)
                }
r_get_uuid = requests.get(url_get_uuid, params=par_get_uuid)
uuid_search = re.search('window.QRLogin.uuid = "([^"]+)"', r_get_uuid.text)
var_uuid = uuid_search.group(1)
print var_uuid

# Display QR image
img = Image.open(cStringIO.StringIO(urllib.urlopen( url_get_qr+var_uuid).read()))
img.show()
#r_get_qr = requests.get(url_get_qr+var_uuid)

# Check if QR scanned
#url_check_scan = 'https://login.wechat.com/cgi-bin/mmwebwx-bin/login'
par_check_scan = {
    'uuid': var_uuid,
    'tip': 1,
    #'_': int(time.time()*1000)
}
r_check_scan = requests.get(url_check_scan, params=par_check_scan, headers=http_header)
print r_check_scan.text

# Check again
raw_input("Press any key to continue...")
#url_check_scan = 'https://login.wechat.com/cgi-bin/mmwebwx-bin/login'
par_check_scan = {
    'uuid': var_uuid,
    'tip': 1,
    #'_': int(time.time()*1000)
}
r_check_scan = requests.get(url_check_scan, params=par_check_scan, headers=http_header)
print r_check_scan.text

# Check again
raw_input("Press any key to continue...")
#url_check_scan = 'https://login.wechat.com/cgi-bin/mmwebwx-bin/login'
par_check_scan = {
    'uuid': var_uuid,
    'tip': 1,
    #'_': int(time.time()*1000)
}
r_check_scan = requests.get(url_check_scan, params=par_check_scan, headers=http_header)
print r_check_scan.text'''
