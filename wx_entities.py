# coding=utf-8
import time, json, datetime
from sqlalchemy import Column, String, Integer, ForeignKey, SmallInteger, Text, BigInteger, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, exc
from sqlalchemy.sql import func
__author__ = 'yongbo'

db_base = declarative_base()
db_engine = create_engine("mysql://wxzs:sjhrzjh500@localhost/wxzs?charset=utf8", encoding = 'utf-8', echo=False)
db_session = sessionmaker()
db_session.configure(bind=db_engine)
s = db_session()


def row_to_json(obj, skip=[]):
    ks = [k for k in obj.__dict__.keys() if k[0].isupper() and k not in skip]
    return {k:obj.__dict__[k] for k in ks}


class WxChatroomship(db_base):
    __tablename__ = 'wx_chatroomship'

    ChatroomNickName = Column(String(32), primary_key=True)
    MemberNickName = Column(String(32), primary_key=True)
    JoinTime = Column(DateTime(), default=func.now())
    QuitTime = Column(DateTime())
    Valid = Column(Boolean(), default=True)

    def __str__(self):
        return ('[%s] %s is in {%s}'
                % ('V' if self.Valid else 'X', self.MemberNickName, self.ChatroomNickName)).encode('utf-8')


class WxContact(db_base):
    __tablename__ = 'wx_contact'

    IsMyFriend = Column(Boolean, default=False)
    City = Column(String(32))
    DisplayName = Column(String(32))
    HeadImgUrl = Column(String(400))
    NickName = Column(String(32), primary_key=True) # TODO: NickName may not be unique and can be changed, next step use remarkname as pk
    PYInitial = Column(String(32))
    PYQuanPin = Column(String(256))
    Province = Column(String(80))
    RemarkName = Column(String(32))
    RemarkPYInitial = Column(String(32))
    RemarkPYQuanPin = Column(String(256))
    Sex = Column(SmallInteger)
    Signature = Column(String(60))
    Statues = Column(SmallInteger)
    UserName = Column(String(256))
    VerifyFlag = Column(SmallInteger)

    def __str__(self):
        return ('[%s] NickName=%s; RemarkName=%s; UserName=%s'
                % (u'男' if self.Sex==1 else u'女', self.NickName, self.RemarkName, self.UserName)).encode('utf-8')

    def __repr__(self):
        return ('[%s] NickName=%s; RemarkName=%s; UserName=%s'
                % (u'男' if self.Sex==1 else u'女', self.NickName, self.RemarkName, self.UserName)).encode('utf-8')

    def is_chatroom(self):
        return self.UserName[0:2] == '@@'


class WxMessage(db_base):
    __tablename__ = 'wx_message'

    IsGroupChat = Column(Boolean, default=False)
    Content = Column(Text)
    CreateTime = Column(BigInteger, primary_key=True)
    FileName = Column(String(256))
    FileSize = Column(String(10))
    ForwardFlag = Column(SmallInteger)
    FromUserName = Column(String(32), primary_key=True) # converted based on wx_contact table
    HasProductId = Column(SmallInteger)
    ImgHeight = Column(Integer)
    ImgStatus = Column(SmallInteger)
    ImgWidth = Column(Integer)
    MediaId = Column(String(256))
    MsgId = Column(String(19))
    MsgType = Column(Integer)
    NewMsgId = Column(String(19))
    PlayLength = Column(Integer)
    RecommendInfo = Column(Text)
    Status = Column(SmallInteger)
    StatusNotifyCode = Column(SmallInteger)
    StatusNotifyUserName = Column(String(256))
    SubMsgType = Column(SmallInteger)
    Ticket = Column(String(128))
    ToUserName = Column(String(32)) # converted based on wx_contact table
    Url = Column(String(512))
    VoiceLength = Column(Integer)

    def __str__(self):
        return ('[%s] %s -> %s: %s' % (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.CreateTime)),
            self.FromUserName,
            self.ToUserName,
            self.Content
        )).encode('utf-8')

    def __repr__(self):
        return ('[%s] %s -> %s: %s' % (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.CreateTime)),
            self.FromUserName,
            self.ToUserName,
            self.Content
        )).encode('utf-8')


db_base.metadata.create_all(db_engine)


def load_contact(dic, is_my_friend=False):
    return WxContact(
        UserName=dic['UserName'],
        City=dic['City'] if 'City' in dic.keys() else None,
        DisplayName=dic['DisplayName'] if 'DisplayName' in dic.keys() else None,
        HeadImgUrl=dic['HeadImgUrl'],
        NickName=dic['NickName'],
        PYInitial=dic['PYInitial'],
        PYQuanPin=dic['PYQuanPin'],
        Province=dic['Province'] if 'Province' in dic.keys() else None,
        RemarkName=dic['RemarkName'],
        RemarkPYInitial=dic['RemarkPYInitial'],
        RemarkPYQuanPin=dic['RemarkPYQuanPin'],
        Sex=int(dic['Sex']),
        Signature=dic['Signature'],
        Statues=int(dic['Statues']) if 'Statues' in dic.keys() else None,
        VerifyFlag=int(dic['VerifyFlag']),
        IsMyFriend=is_my_friend
    )


def load_message(dic):
    from_user = contact_username_to_nickname(dic['FromUserName'])
    to_user = contact_username_to_nickname(dic['ToUserName'])
    from_user = from_user if from_user is not None else dic['FromUserName'][-32:]
    to_user = to_user if to_user is not None else dic['ToUserName'][-32:]
    return WxMessage(
        IsGroupChat=dic['ToUserName'][0:2] == '@@',
        Content=dic['Content'],
        CreateTime=int(dic['CreateTime']),
        FileName=dic['FileName'],
        FileSize=dic['FileSize'],
        ForwardFlag=int(dic['ForwardFlag']),
        FromUserName=from_user,
        HasProductId=int(dic['HasProductId']),
        ImgHeight=int(dic['ImgHeight']),
        ImgStatus=int(dic['ImgStatus']),
        ImgWidth=int(dic['ImgWidth']),
        MediaId=dic['MediaId'],
        MsgId=dic['MsgId'],
        MsgType=int(dic['MsgType']),
        NewMsgId=dic['NewMsgId'],
        PlayLength=int(dic['PlayLength']),
        RecommendInfo=json.dumps(dic['RecommendInfo']),
        Status=int(dic['Status']),
        StatusNotifyCode=int(dic['StatusNotifyCode']),
        StatusNotifyUserName=dic['StatusNotifyUserName'],
        SubMsgType=int(dic['SubMsgType']),
        Ticket=dic['Ticket'],
        ToUserName=to_user,
        Url=dic['Url'],
        VoiceLength=int(dic['VoiceLength'])
    )


def load_message_list(dics):
    for dic in dics['AddMsgList']:
        yield load_message(dic)


def contact_username_to_nickname(username):
    global s
    try:
        c = s.query(WxContact).filter(WxContact.UserName == username).one()
    except exc.NoResultFound:
        return None
    return c.NickName


def load_contact_list(dics):
    for dic in dics['MemberList']:
        yield load_contact(dic)


def db_upsert_contact(ct):
    global s
    try:
        old_ct = s.query(WxContact).filter(WxContact.NickName == ct.NickName).all()
        if len(old_ct) == 1:  # update
            s.query(WxContact).filter(WxContact.NickName == ct.NickName).update(row_to_json(ct))
        else:
            s.add(ct)
        s.commit()
    except:
        s.rollback()
        raise


def db_insert_message(msg):
    global s
    try:
        s.add(msg)
        s.commit()
    except:
        s.rollback()
        raise
