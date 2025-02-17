import common
from langdetect import detect
from nostrclient.relay_pool import RelayPool
from nostrclient.log import log
from nostrclient.key import PrivateKey,PublicKey
from nostrclient.localStorage import local_storage
from nostrclient.actions import like_event
from nostrclient.key import PublicKey
from nostrclient.nip19 import encode_bech32
from nostrclient import bech32
from nostrclient import nip44,nip04
from nostrclient.event import Event

import db
import dmevent 
import queue
import json
import time
task = queue.Queue()

from config import relays 

Keypriv = local_storage.get("Keyprivpost")
pkey = PrivateKey(Keypriv)

print("Your public key: ",pkey.public_key)
print("Your public key bech32: ",pkey.public_key.bech32())


filters    = {"kinds":[4,1059], "#p": [str(pkey.public_key)],"limit":10}


r = RelayPool(relays)

r.connect(5)


welcome_msg= """你好！

这是来自 Postr 的一则重要消息。有一位匿名用户委托我向您传递一条加密信息，表达了与您结交为友的诚挚意愿。
不知您是否愿意接纳这份友好的邀约呢？倘若您有意结交，只需直接回复此消息，我会即刻为您搭建一条私密的双向通信渠道，
全方位保障您交流内容的安全与隐秘。
若您并无此意，忽略此消息即可。

对方原始消息：

“%s”

-----
From Postr
"""

replymsg="""
你好, 
   我的老板 Postr 安排我为你结识一位新朋友牵线搭桥。我已经把相关信息转达给对方了。待对方给出回应，我会第一时间传达给你。
请放心，后续我会全程做好你们之间的沟通桥梁，及时准确地为你们转发消息。

你的原始消息：
---
“%s”

来自postr的小弟。

"""

def detect_lang(text):
    try:
        return detect(text)
    except:
        return 'en'

# sender :nkey
# receiver: pubkey

def send_message_user1(nkey,pubkey,content):
  
  # 匿名发送
  n1key = PrivateKey() 
  event1059 = dmevent.dmEvent(nkey,pubkey,content,n1key)

  for r1 in r.RelayList:
    r1.Privkey = n1key
  r.Privkey = n1key 
  r.publish(event1059)


def find_new_friend_for_user(content,pubkey,eventid):
  if db.get_event(eventid):
    return 

  lang = detect_lang(content)
  user = db.get_random_user(lang)
  print("转发给一个新用户 https://jumble.social/users/"+str(PublicKey(bytes.fromhex(user[1])).bech32()))
  db.create_event(eventid)

  nkey = PrivateKey()
  db.create_relay(nkey.public_key,pubkey,user[1])
  db.create_newkey(nkey)
  send_message_user1(nkey,user[1],welcome_msg%content)
  send_message_user1(nkey,pubkey,replymsg%content)


def decrypt_1059(e):
    # 匿名 pubkey
    conversation_key = nip44.get_conversation_key(pkey.raw_secret, e['pubkey'])

    encrypt_event = json.loads(nip44.decrypt(e['content'],conversation_key))
    if encrypt_event['kind'] == 13:
        # 真实的 pubkey 发送者的 
        conversation_key = nip44.get_conversation_key(pkey.raw_secret, encrypt_event['pubkey'])
        content = nip44.decrypt(encrypt_event['content'],conversation_key)

        return content,encrypt_event['pubkey']

    return None,None 

def time_since(created_at):
    now = time.time()
    time_difference = now - created_at

    seconds = int(time_difference)
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24

    print(f"信息：{days}天 {hours % 24}小时 {minutes % 60}分钟 {seconds % 60}秒 之前")


def handler_event(e):
   
    if e['kind'] == 4:
      
      content = nip04.decrypt(e['content'],pkey.raw_secret, e['pubkey'])
      log.blue ("msg 4 %s " % e["id"])
      time_since(e['created_at'])
      task.put((e['pubkey'],content,e['id']))

    elif e['kind'] == 1059:
      content,pubkey = decrypt_1059(e)
      event14 = json.loads(content)
      log.blue("收到一个信息: %s" % e['id'])
      time_since(event14['created_at'])
      task.put((pubkey,event14['content'],e['id']))
    else:
      return 
     

subs = r.subscribe (filters)
subs.on("EVENT",handler_event)


while True:  # 死循环
      pubkey, content,eventid = task.get()
      
      find_new_friend_for_user(content,pubkey,eventid)
